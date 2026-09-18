#include <BRepAdaptor_Surface.hxx>
#include <BRepAlgoAPI_Cut.hxx>
#include <BRepBndLib.hxx>
#include <BRepCheck_Analyzer.hxx>
#include <BRepGProp.hxx>
#include <BRepPrimAPI_MakeBox.hxx>
#include <BRepPrimAPI_MakeCone.hxx>
#include <BRepPrimAPI_MakeCylinder.hxx>
#include <Bnd_Box.hxx>
#include <DESTEP_Parameters.hxx>
#include <GProp_GProps.hxx>
#include <GeomAbs_SurfaceType.hxx>
#include <IFSelect_ReturnStatus.hxx>
#include <STEPControl_Writer.hxx>
#include <ShapeUpgrade_UnifySameDomain.hxx>
#include <TopExp_Explorer.hxx>
#include <TopoDS.hxx>
#include <TopoDS_Compound.hxx>
#include <TopoDS_Shape.hxx>
#include <TopoDS_Solid.hxx>
#include <TopoDS_Shell.hxx>
#include <BRep_Builder.hxx>
#include <gp_Ax2.hxx>
#include <gp_Dir.hxx>
#include <gp_Pnt.hxx>

#include <algorithm>
#include <cmath>
#include <cstdlib>
#include <filesystem>
#include <iomanip>
#include <iostream>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

namespace {

struct Fixture {
  std::string id;
  TopoDS_Shape shape;
  TopoDS_Shape pre_heal_shape;
  bool has_pre_heal = false;
};

std::string json_escape(const std::string& s) {
  std::ostringstream o;
  for (char c : s) {
    switch (c) {
      case '\\': o << "\\\\"; break;
      case '"': o << "\\\""; break;
      case '\n': o << "\\n"; break;
      case '\r': o << "\\r"; break;
      case '\t': o << "\\t"; break;
      default: o << c;
    }
  }
  return o.str();
}

TopoDS_Shape compound_of(const std::vector<TopoDS_Shape>& shapes) {
  BRep_Builder builder;
  TopoDS_Compound compound;
  builder.MakeCompound(compound);
  for (const auto& s : shapes) builder.Add(compound, s);
  return compound;
}

Fixture make_fixture(const std::string& id) {
  if (id == "metric_block" || id == "inch_equivalent") {
    return {id, BRepPrimAPI_MakeBox(25.4, 12.7, 6.35).Shape(), {}, false};
  }
  if (id == "metric_cylinder") {
    return {id, BRepPrimAPI_MakeCylinder(10.0, 25.0).Shape(), {}, false};
  }
  if (id == "analytic_cone") {
    return {id, BRepPrimAPI_MakeCone(12.0, 5.0, 30.0).Shape(), {}, false};
  }
  if (id == "through_hole") {
    auto stock = BRepPrimAPI_MakeBox(40.0, 30.0, 10.0).Shape();
    auto tool = BRepPrimAPI_MakeCylinder(gp_Ax2(gp_Pnt(20.0, 15.0, -1.0), gp_Dir(0,0,1)), 4.0, 12.0).Shape();
    return {id, BRepAlgoAPI_Cut(stock, tool).Shape(), {}, false};
  }
  if (id == "blind_bore") {
    auto stock = BRepPrimAPI_MakeBox(40.0, 30.0, 10.0).Shape();
    auto tool = BRepPrimAPI_MakeCylinder(gp_Ax2(gp_Pnt(20.0, 15.0, 6.0), gp_Dir(0,0,1)), 4.0, 5.0).Shape();
    return {id, BRepAlgoAPI_Cut(stock, tool).Shape(), {}, false};
  }
  if (id == "two_body_parting") {
    auto stock = BRepPrimAPI_MakeCylinder(20.0, 80.0).Shape();
    auto tool = BRepPrimAPI_MakeBox(gp_Pnt(-25.0,-25.0,39.0), 50.0, 50.0, 2.0).Shape();
    return {id, BRepAlgoAPI_Cut(stock, tool).Shape(), {}, false};
  }
  if (id == "accepted_lathe") {
    auto stock = BRepPrimAPI_MakeCylinder(20.0, 80.0).Shape();
    auto trim = BRepPrimAPI_MakeCylinder(gp_Ax2(gp_Pnt(0,0,55), gp_Dir(0,0,1)), 20.0, 25.0).Shape();
    auto core = BRepPrimAPI_MakeCylinder(gp_Ax2(gp_Pnt(0,0,55), gp_Dir(0,0,1)), 12.0, 25.0).Shape();
    auto annulus = BRepAlgoAPI_Cut(trim, core).Shape();
    return {id, BRepAlgoAPI_Cut(stock, annulus).Shape(), {}, false};
  }
  if (id == "accepted_mill") {
    auto stock = BRepPrimAPI_MakeBox(40.0, 30.0, 10.0).Shape();
    auto tool = BRepPrimAPI_MakeBox(gp_Pnt(19.0,-1.0,-1.0), 2.0, 32.0, 12.0).Shape();
    return {id, BRepAlgoAPI_Cut(stock, tool).Shape(), {}, false};
  }
  if (id == "healed_reconciled") {
    auto a = BRepPrimAPI_MakeBox(20.0, 20.0, 10.0).Shape();
    auto b = BRepPrimAPI_MakeBox(gp_Pnt(20.0,0,0), 20.0, 20.0, 10.0).Shape();
    TopoDS_Shape joined = compound_of({a,b});
    ShapeUpgrade_UnifySameDomain unify(joined, true, true, false);
    unify.Build();
    return {id, unify.Shape(), joined, true};
  }
  if (id == "trimmed_analytic") {
    auto stock = BRepPrimAPI_MakeCylinder(15.0, 20.0).Shape();
    auto notch = BRepPrimAPI_MakeBox(gp_Pnt(10.0,-5.0,5.0), 10.0, 10.0, 10.0).Shape();
    return {id, BRepAlgoAPI_Cut(stock, notch).Shape(), {}, false};
  }
  if (id == "open_shell") {
    TopoDS_Shape box = BRepPrimAPI_MakeBox(10.0, 10.0, 10.0).Shape();
    for (TopExp_Explorer ex(box, TopAbs_SHELL); ex.More(); ex.Next()) {
      return {id, TopoDS::Shell(ex.Current()), {}, false};
    }
    throw std::runtime_error("box produced no shell");
  }
  throw std::runtime_error("unknown fixture: " + id);
}

std::vector<TopoDS_Solid> solids_of(const TopoDS_Shape& shape) {
  std::vector<TopoDS_Solid> solids;
  for (TopExp_Explorer ex(shape, TopAbs_SOLID); ex.More(); ex.Next()) solids.push_back(TopoDS::Solid(ex.Current()));
  return solids;
}

std::string metrics_json(const TopoDS_Shape& shape) {
  const auto solids = solids_of(shape);
  GProp_GProps props;
  double volume = 0.0;
  bool valid = !solids.empty();
  for (const auto& solid : solids) {
    BRepCheck_Analyzer check(solid, true);
    valid = valid && check.IsValid();
    BRepGProp::VolumeProperties(solid, props);
    volume += std::abs(props.Mass());
  }
  Bnd_Box box;
  BRepBndLib::Add(shape, box);
  double xmin=0,ymin=0,zmin=0,xmax=0,ymax=0,zmax=0;
  if (!box.IsVoid()) box.Get(xmin,ymin,zmin,xmax,ymax,zmax);
  int planes=0,cylinders=0,cones=0,spheres=0,tori=0,other=0;
  for (TopExp_Explorer ex(shape, TopAbs_FACE); ex.More(); ex.Next()) {
    BRepAdaptor_Surface s(TopoDS::Face(ex.Current()), true);
    switch (s.GetType()) {
      case GeomAbs_Plane: ++planes; break;
      case GeomAbs_Cylinder: ++cylinders; break;
      case GeomAbs_Cone: ++cones; break;
      case GeomAbs_Sphere: ++spheres; break;
      case GeomAbs_Torus: ++tori; break;
      default: ++other; break;
    }
  }
  std::ostringstream o;
  o << std::setprecision(17)
    << "{\"body_count\":" << solids.size()
    << ",\"valid\":" << (valid ? "true":"false")
    << ",\"volume_mm3\":" << volume
    << ",\"bbox_mm\":[" << xmin << ',' << ymin << ',' << zmin << ',' << xmax << ',' << ymax << ',' << zmax << ']'
    << ",\"analytic_faces\":{\"plane\":" << planes << ",\"cylinder\":" << cylinders
    << ",\"cone\":" << cones << ",\"sphere\":" << spheres << ",\"torus\":" << tori
    << ",\"other\":" << other << "}}";
  return o.str();
}

int run(int argc, char** argv) {
  if (argc < 4) {
    std::cerr << "usage: rcs022_step_worker export <fixture> <output.step> [--unit mm|inch] [--omit-last-body]\n";
    return 2;
  }
  const std::string cmd = argv[1];
  if (cmd != "export") throw std::runtime_error("only export is supported");
  const std::string fixture_id = argv[2];
  const std::filesystem::path out = argv[3];
  std::string unit = fixture_id == "inch_equivalent" ? "inch" : "mm";
  bool omit_last = false;
  for (int i=4;i<argc;++i) {
    const std::string a = argv[i];
    if (a == "--omit-last-body") omit_last = true;
    else if (a == "--unit" && i+1<argc) unit = argv[++i];
    else throw std::runtime_error("unknown argument: " + a);
  }

  Fixture fixture = make_fixture(fixture_id);
  auto solids = solids_of(fixture.shape);
  if (solids.empty()) {
    std::cerr << "RCS022_REFUSAL VOID_OR_CONNECTIVITY_MISMATCH: fixture contains no solid bodies\n";
    return 20;
  }
  for (const auto& solid : solids) {
    if (!BRepCheck_Analyzer(solid, true).IsValid()) {
      std::cerr << "RCS022_REFUSAL VOID_OR_CONNECTIVITY_MISMATCH: invalid B-rep solid\n";
      return 20;
    }
  }
  if (omit_last && solids.size() > 1) solids.pop_back();

  DESTEP_Parameters p;
  p.WriteSchema = DESTEP_Parameters::WriteMode_StepSchema_AP242DIS;
  p.WriteModelType = STEPControl_ManifoldSolidBrep;
  p.WriteTessellated = DESTEP_Parameters::RWMode_Tessellated_Off;
  p.WriteAssembly = DESTEP_Parameters::WriteMode_Assembly_Off;
  p.WritePrecisionMode = DESTEP_Parameters::WriteMode_PrecisionMode_Average;
  p.WritePrecisionVal = 0.0001;
  p.WriteSurfaceCurMode = true;
  p.WriteNonmanifold = false;
  p.CleanDuplicates = false;
  p.WriteUnit = unit == "inch" ? UnitsMethods_LengthUnit_Inch : UnitsMethods_LengthUnit_Millimeter;

  STEPControl_Writer writer;
  for (const auto& solid : solids) {
    IFSelect_ReturnStatus st = writer.Transfer(solid, STEPControl_ManifoldSolidBrep, p);
    if (st != IFSelect_RetDone) throw std::runtime_error("STEP Transfer failed");
  }
  std::filesystem::create_directories(out.parent_path());
  if (writer.Write(out.string().c_str()) != IFSelect_RetDone) throw std::runtime_error("STEP Write failed");

  std::cout << "{\"fixture\":\"" << json_escape(fixture_id) << "\",\"unit\":\"" << unit
            << "\",\"omitted_body\":" << (omit_last?"true":"false")
            << ",\"metrics\":" << metrics_json(fixture.shape);
  if (fixture.has_pre_heal) std::cout << ",\"pre_heal_metrics\":" << metrics_json(fixture.pre_heal_shape);
  std::cout << "}\n";
  return 0;
}

} // namespace

int main(int argc, char** argv) {
  try { return run(argc, argv); }
  catch (const std::exception& e) { std::cerr << "RCS022_ERROR: " << e.what() << '\n'; return 1; }
}
