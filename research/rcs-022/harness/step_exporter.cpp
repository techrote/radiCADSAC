#include <BRepAdaptor_Surface.hxx>
#include <BRepAlgoAPI_Cut.hxx>
#include <BRepAlgoAPI_Fuse.hxx>
#include <BRepBndLib.hxx>
#include <BRepCheck_Analyzer.hxx>
#include <BRepGProp.hxx>
#include <BRepPrimAPI_MakeBox.hxx>
#include <BRepPrimAPI_MakeCone.hxx>
#include <BRepPrimAPI_MakeCylinder.hxx>
#include <BRep_Tool.hxx>
#include <Bnd_Box.hxx>
#include <DESTEP_Parameters.hxx>
#include <GProp_GProps.hxx>
#include <IFSelect_ReturnStatus.hxx>
#include <Interface_Static.hxx>
#include <ShapeUpgrade_UnifySameDomain.hxx>
#include <STEPControl_Reader.hxx>
#include <STEPControl_Writer.hxx>
#include <Standard_Version.hxx>
#include <TopExp_Explorer.hxx>
#include <TopoDS.hxx>
#include <TopoDS_Compound.hxx>
#include <TopoDS_Shape.hxx>
#include <TopoDS_Solid.hxx>
#include <UnitsMethods_LengthUnit.hxx>
#include <gp_Ax2.hxx>
#include <gp_Dir.hxx>
#include <gp_Pnt.hxx>

#include <algorithm>
#include <cmath>
#include <filesystem>
#include <iomanip>
#include <iostream>
#include <limits>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

namespace {
constexpr const char* kOcctVersion = "8.0.1";
constexpr const char* kOcctCommit = "b8f597c677811d1f9f4d8a97f5ae2825c0353a42";
constexpr double kWritePrecision = 0.0001; // file-unit value; profile pins Greatest mode.

struct Metrics {
  bool valid = false;
  int solids = 0;
  double volume = 0.0;
  double xmin = 0.0, ymin = 0.0, zmin = 0.0, xmax = 0.0, ymax = 0.0, zmax = 0.0;
  int planes = 0, cylinders = 0, cones = 0, spheres = 0, tori = 0, bsplines = 0, other = 0;
  double max_tolerance = 0.0;
};

std::string json_escape(const std::string& s) {
  std::ostringstream out;
  for (const char c : s) {
    switch (c) {
      case '\\': out << "\\\\"; break;
      case '"': out << "\\\""; break;
      case '\n': out << "\\n"; break;
      case '\r': out << "\\r"; break;
      case '\t': out << "\\t"; break;
      default: out << c; break;
    }
  }
  return out.str();
}

std::vector<TopoDS_Solid> solids_of(const TopoDS_Shape& shape) {
  std::vector<TopoDS_Solid> solids;
  for (TopExp_Explorer ex(shape, TopAbs_SOLID); ex.More(); ex.Next()) {
    solids.push_back(TopoDS::Solid(ex.Current()));
  }
  return solids;
}

Metrics measure(const TopoDS_Shape& shape) {
  Metrics m;
  BRepCheck_Analyzer analyzer(shape, true);
  m.valid = analyzer.IsValid();
  const auto solids = solids_of(shape);
  m.solids = static_cast<int>(solids.size());
  GProp_GProps props;
  BRepGProp::VolumeProperties(shape, props);
  m.volume = props.Mass();
  Bnd_Box box;
  BRepBndLib::Add(shape, box);
  if (!box.IsVoid()) box.Get(m.xmin, m.ymin, m.zmin, m.xmax, m.ymax, m.zmax);
  for (TopExp_Explorer ex(shape, TopAbs_FACE); ex.More(); ex.Next()) {
    BRepAdaptor_Surface surface(TopoDS::Face(ex.Current()), true);
    switch (surface.GetType()) {
      case GeomAbs_Plane: ++m.planes; break;
      case GeomAbs_Cylinder: ++m.cylinders; break;
      case GeomAbs_Cone: ++m.cones; break;
      case GeomAbs_Sphere: ++m.spheres; break;
      case GeomAbs_Torus: ++m.tori; break;
      case GeomAbs_BSplineSurface: ++m.bsplines; break;
      default: ++m.other; break;
    }
    m.max_tolerance = std::max(m.max_tolerance, BRep_Tool::Tolerance(TopoDS::Face(ex.Current())));
  }
  for (TopExp_Explorer ex(shape, TopAbs_EDGE); ex.More(); ex.Next())
    m.max_tolerance = std::max(m.max_tolerance, BRep_Tool::Tolerance(TopoDS::Edge(ex.Current())));
  for (TopExp_Explorer ex(shape, TopAbs_VERTEX); ex.More(); ex.Next())
    m.max_tolerance = std::max(m.max_tolerance, BRep_Tool::Tolerance(TopoDS::Vertex(ex.Current())));
  return m;
}

TopoDS_Shape cut(const TopoDS_Shape& a, const TopoDS_Shape& b) {
  BRepAlgoAPI_Cut op(a, b);
  op.Build();
  if (!op.IsDone()) throw std::runtime_error("BRepAlgoAPI_Cut failed");
  return op.Shape();
}

TopoDS_Shape fuse(const TopoDS_Shape& a, const TopoDS_Shape& b) {
  BRepAlgoAPI_Fuse op(a, b);
  op.Build();
  if (!op.IsDone()) throw std::runtime_error("BRepAlgoAPI_Fuse failed");
  return op.Shape();
}

TopoDS_Shape build_case(const std::string& id, Metrics* pre_heal) {
  if (id == "metric-block" || id == "inch-equivalent") {
    return BRepPrimAPI_MakeBox(25.4, 12.7, 6.35).Shape();
  }
  if (id == "analytic-cylinder") {
    return BRepPrimAPI_MakeCylinder(gp_Ax2(gp_Pnt(0,0,0), gp_Dir(0,0,1)), 12.7, 50.8).Shape();
  }
  if (id == "analytic-cone") {
    return BRepPrimAPI_MakeCone(gp_Ax2(gp_Pnt(0,0,0), gp_Dir(0,0,1)), 12.7, 6.35, 25.4).Shape();
  }
  if (id == "through-hole") {
    const auto stock = BRepPrimAPI_MakeBox(40.0, 30.0, 10.0).Shape();
    const auto tool = BRepPrimAPI_MakeCylinder(gp_Ax2(gp_Pnt(20,15,-1), gp_Dir(0,0,1)), 5.0, 12.0).Shape();
    return cut(stock, tool);
  }
  if (id == "blind-hole") {
    const auto stock = BRepPrimAPI_MakeBox(40.0, 30.0, 10.0).Shape();
    const auto tool = BRepPrimAPI_MakeCylinder(gp_Ax2(gp_Pnt(20,15,5), gp_Dir(0,0,1)), 5.0, 6.0).Shape();
    return cut(stock, tool);
  }
  if (id == "two-body-parting") {
    const auto stock = BRepPrimAPI_MakeCylinder(gp_Ax2(gp_Pnt(0,0,0), gp_Dir(0,0,1)), 20.0, 80.0).Shape();
    const auto tool = BRepPrimAPI_MakeBox(gp_Pnt(-25,-25,39), 50.0, 50.0, 2.0).Shape();
    return cut(stock, tool);
  }
  if (id == "mill-cut-through") {
    const auto stock = BRepPrimAPI_MakeBox(40.0, 30.0, 10.0).Shape();
    const auto tool = BRepPrimAPI_MakeBox(gp_Pnt(19,-1,-1), 2.0, 32.0, 12.0).Shape();
    return cut(stock, tool);
  }
  if (id == "lathe-accepted-r020") {
    // Conventional B-rep representative of the RCS-020 qualified fixed-axis
    // material-domain class: one axisymmetric result with a reduced central OD.
    auto left = BRepPrimAPI_MakeCylinder(gp_Ax2(gp_Pnt(0,0,0), gp_Dir(0,0,1)), 10.0, 8.0).Shape();
    auto mid = BRepPrimAPI_MakeCylinder(gp_Ax2(gp_Pnt(0,0,8), gp_Dir(0,0,1)), 9.2, 24.0).Shape();
    auto right = BRepPrimAPI_MakeCylinder(gp_Ax2(gp_Pnt(0,0,32), gp_Dir(0,0,1)), 10.0, 8.0).Shape();
    return fuse(fuse(left, mid), right);
  }
  if (id == "healed-same-domain") {
    auto a = BRepPrimAPI_MakeBox(20.0, 20.0, 10.0).Shape();
    auto b = BRepPrimAPI_MakeBox(gp_Pnt(20,0,0), 20.0, 20.0, 10.0).Shape();
    auto raw = fuse(a, b);
    if (pre_heal) *pre_heal = measure(raw);
    ShapeUpgrade_UnifySameDomain unify(raw, true, true, true);
    unify.Build();
    return unify.Shape();
  }
  if (id == "trimmed-curved") {
    auto cyl = BRepPrimAPI_MakeCylinder(gp_Ax2(gp_Pnt(0,0,0), gp_Dir(0,0,1)), 10.0, 20.0).Shape();
    auto notch = BRepPrimAPI_MakeBox(gp_Pnt(4,-12,5), 12.0, 24.0, 10.0).Shape();
    return cut(cyl, notch);
  }
  if (id == "invalid-open-shell") {
    TopoDS_Shape box = BRepPrimAPI_MakeBox(10.0, 10.0, 10.0).Shape();
    TopExp_Explorer ex(box, TopAbs_FACE);
    if (!ex.More()) throw std::runtime_error("box had no face");
    return ex.Current();
  }
  throw std::runtime_error("unknown case: " + id);
}

void print_metrics(std::ostream& out, const Metrics& m) {
  out << std::setprecision(17)
      << "{\"valid_brep\":" << (m.valid ? "true" : "false")
      << ",\"body_count\":" << m.solids
      << ",\"volume_mm3\":" << m.volume
      << ",\"bbox_mm\":[" << m.xmin << ',' << m.ymin << ',' << m.zmin << ',' << m.xmax << ',' << m.ymax << ',' << m.zmax << ']'
      << ",\"max_tolerance_mm\":" << m.max_tolerance
      << ",\"analytic_surfaces\":{\"plane\":" << m.planes
      << ",\"cylinder\":" << m.cylinders << ",\"cone\":" << m.cones
      << ",\"sphere\":" << m.spheres << ",\"torus\":" << m.tori
      << ",\"bspline\":" << m.bsplines << ",\"other\":" << m.other << "}}";
}

int main_impl(int argc, char** argv) {
  std::string case_id, step_file, unit = "mm";
  for (int i = 1; i < argc; ++i) {
    const std::string arg = argv[i];
    auto take = [&](std::string& dst) {
      if (++i >= argc) throw std::runtime_error("missing value for " + arg);
      dst = argv[i];
    };
    if (arg == "--case") take(case_id);
    else if (arg == "--step-file") take(step_file);
    else if (arg == "--unit") take(unit);
    else throw std::runtime_error("unknown argument: " + arg);
  }
  if (case_id.empty() || step_file.empty()) throw std::runtime_error("--case and --step-file are required");
  if (unit != "mm" && unit != "inch") throw std::runtime_error("--unit must be mm or inch");
  if (std::string(OCC_VERSION_COMPLETE) != kOcctVersion)
    throw std::runtime_error("unexpected OCCT runtime version: " + std::string(OCC_VERSION_COMPLETE));

  Metrics pre_heal{};
  const TopoDS_Shape shape = build_case(case_id, &pre_heal);
  const Metrics before = measure(shape);

  const bool refuse = !before.valid || before.solids < 1 || !(before.volume > 0.0) || before.max_tolerance > 0.005;
  if (refuse) {
    std::cout << "{\"schema\":\"rcs-022-exporter/1.0\",\"case_id\":\"" << json_escape(case_id)
              << "\",\"status\":\"refused\",\"failure_code\":\"PREEXPORT_SOLID_CONTRACT_FAILED\",\"pre_export\":";
    print_metrics(std::cout, before);
    std::cout << "}\n";
    return 0;
  }

  std::filesystem::create_directories(std::filesystem::path(step_file).parent_path());
  DESTEP_Parameters params;
  params.WriteSchema = DESTEP_Parameters::WriteMode_StepSchema_AP242DIS;
  params.WriteTessellated = DESTEP_Parameters::RWMode_Tessellated_Off;
  params.WriteModelType = STEPControl_ManifoldSolidBrep;
  params.WriteAssembly = DESTEP_Parameters::WriteMode_Assembly_Auto;
  params.WritePrecisionMode = DESTEP_Parameters::WriteMode_PrecisionMode_Greatest;
  params.WritePrecisionVal = kWritePrecision;
  params.WriteSurfaceCurMode = true;
  params.WriteNonmanifold = false;
  params.WriteUnit = unit == "inch" ? UnitsMethods_LengthUnit_Inch : UnitsMethods_LengthUnit_Millimeter;

  STEPControl_Writer writer;
  bool transfer_ok = true;
  for (const auto& solid : solids_of(shape)) {
    transfer_ok = transfer_ok && (writer.Transfer(solid, STEPControl_ManifoldSolidBrep, params, true) == IFSelect_RetDone);
  }
  const bool write_ok = transfer_ok && (writer.Write(step_file.c_str()) == IFSelect_RetDone);
  if (!write_ok) {
    std::cout << "{\"schema\":\"rcs-022-exporter/1.0\",\"case_id\":\"" << json_escape(case_id)
              << "\",\"status\":\"failed\",\"failure_code\":\"STEP_WRITE_FAILED\"}\n";
    return 0;
  }

  STEPControl_Reader reader;
  const bool read_ok = reader.ReadFile(step_file.c_str()) == IFSelect_RetDone && reader.TransferRoots() > 0;
  Metrics roundtrip{};
  if (read_ok) roundtrip = measure(reader.OneShape());

  std::cout << std::setprecision(17)
            << "{\"schema\":\"rcs-022-exporter/1.0\",\"case_id\":\"" << json_escape(case_id)
            << "\",\"status\":\"exported\",\"unit\":\"" << unit << "\",\"profile\":{"
            << "\"occt_version\":\"" << kOcctVersion << "\",\"occt_commit\":\"" << kOcctCommit
            << "\",\"schema_mode\":\"AP242DIS\",\"model_type\":\"ManifoldSolidBrep\",\"tessellated\":false,"
            << "\"assembly\":\"auto\",\"precision_mode\":\"greatest\",\"precision_value_file_unit\":" << kWritePrecision << "},"
            << "\"pre_export\":";
  print_metrics(std::cout, before);
  std::cout << ",\"layer_c_readback\":{" << "\"read_ok\":" << (read_ok ? "true" : "false") << ",\"metrics\":";
  print_metrics(std::cout, roundtrip);
  std::cout << "}";
  if (case_id == "healed-same-domain") {
    std::cout << ",\"pre_heal\":";
    print_metrics(std::cout, pre_heal);
  }
  std::cout << "}\n";
  return 0;
}
} // namespace

int main(int argc, char** argv) {
  try { return main_impl(argc, argv); }
  catch (const std::exception& e) {
    std::cerr << "rcs022 exporter error: " << e.what() << '\n';
    return 2;
  }
}
