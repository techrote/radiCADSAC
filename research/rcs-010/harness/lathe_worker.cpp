#include <BRepAdaptor_Curve.hxx>
#include <BRepAlgoAPI_Cut.hxx>
#include <BRepBndLib.hxx>
#include <BRepBuilderAPI_MakeFace.hxx>
#include <BRepBuilderAPI_MakePolygon.hxx>
#include <BRepCheck_Analyzer.hxx>
#include <BRepGProp.hxx>
#include <BRepPrimAPI_MakeCylinder.hxx>
#include <BRepPrimAPI_MakeRevol.hxx>
#include <BRep_Tool.hxx>
#include <Bnd_Box.hxx>
#include <DESTEP_Parameters.hxx>
#include <GProp_GProps.hxx>
#include <GeomAbs_CurveType.hxx>
#include <GeomAbs_SurfaceType.hxx>
#include <GeomAdaptor_Surface.hxx>
#include <IFSelect_ReturnStatus.hxx>
#include <NCollection_List.hxx>
#include <Standard_Failure.hxx>
#include <Standard_Version.hxx>
#include <STEPControl_Reader.hxx>
#include <STEPControl_Writer.hxx>
#include <TopAbs_ShapeEnum.hxx>
#include <TopExp_Explorer.hxx>
#include <TopoDS.hxx>
#include <TopoDS_Edge.hxx>
#include <TopoDS_Face.hxx>
#include <TopoDS_Shape.hxx>
#include <TopoDS_Solid.hxx>
#include <UnitsMethods_LengthUnit.hxx>
#include <gp_Ax1.hxx>
#include <gp_Ax2.hxx>
#include <gp_Dir.hxx>
#include <gp_Pnt.hxx>

#include <algorithm>
#include <cctype>
#include <chrono>
#include <cmath>
#include <filesystem>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <map>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

#ifndef _WIN32
#include <sys/resource.h>
#endif

namespace
{
constexpr const char* kExpectedOcctVersion = "8.0.1";
constexpr const char* kExpectedOcctCommit = "b8f597c677811d1f9f4d8a97f5ae2825c0353a42";
constexpr double kPi = 3.141592653589793238462643383279502884;

std::string json_escape(const std::string& value)
{
  std::ostringstream out;
  for (const unsigned char ch : value)
  {
    switch (ch)
    {
      case '"': out << "\\\""; break;
      case '\\': out << "\\\\"; break;
      case '\b': out << "\\b"; break;
      case '\f': out << "\\f"; break;
      case '\n': out << "\\n"; break;
      case '\r': out << "\\r"; break;
      case '\t': out << "\\t"; break;
      default:
        if (ch < 0x20)
        {
          out << "\\u" << std::hex << std::setw(4) << std::setfill('0') << static_cast<int>(ch)
              << std::dec << std::setfill(' ');
        }
        else
        {
          out << static_cast<char>(ch);
        }
    }
  }
  return out.str();
}

std::string quote(const std::string& value) { return "\"" + json_escape(value) + "\""; }

std::string status_name(IFSelect_ReturnStatus status)
{
  switch (status)
  {
    case IFSelect_RetVoid: return "void";
    case IFSelect_RetDone: return "done";
    case IFSelect_RetError: return "error";
    case IFSelect_RetFail: return "fail";
    case IFSelect_RetStop: return "stop";
    default: return "unknown";
  }
}

std::string surface_type_name(GeomAbs_SurfaceType type)
{
  switch (type)
  {
    case GeomAbs_Plane: return "plane";
    case GeomAbs_Cylinder: return "cylinder";
    case GeomAbs_Cone: return "cone";
    case GeomAbs_Sphere: return "sphere";
    case GeomAbs_Torus: return "torus";
    case GeomAbs_BezierSurface: return "bezier_surface";
    case GeomAbs_BSplineSurface: return "bspline_surface";
    case GeomAbs_SurfaceOfRevolution: return "surface_of_revolution";
    case GeomAbs_SurfaceOfExtrusion: return "surface_of_extrusion";
    case GeomAbs_OffsetSurface: return "offset_surface";
    default: return "other_surface";
  }
}

std::string curve_type_name(GeomAbs_CurveType type)
{
  switch (type)
  {
    case GeomAbs_Line: return "line";
    case GeomAbs_Circle: return "circle_or_arc";
    case GeomAbs_Ellipse: return "ellipse";
    case GeomAbs_Hyperbola: return "hyperbola";
    case GeomAbs_Parabola: return "parabola";
    case GeomAbs_BezierCurve: return "bezier_curve";
    case GeomAbs_BSplineCurve: return "bspline_curve";
    case GeomAbs_OffsetCurve: return "offset_curve";
    default: return "other_curve";
  }
}

long max_rss_kb()
{
#ifdef _WIN32
  return -1;
#else
  struct rusage usage {};
  if (getrusage(RUSAGE_SELF, &usage) != 0) return -1;
#if defined(__APPLE__)
  return static_cast<long>(usage.ru_maxrss / 1024);
#else
  return static_cast<long>(usage.ru_maxrss);
#endif
#endif
}

struct Metrics
{
  bool is_null = true;
  bool valid = false;
  int vertices = 0;
  int edges = 0;
  int faces = 0;
  int shells = 0;
  int solids = 0;
  double volume_mm3 = 0.0;
  double area_mm2 = 0.0;
  double xmin = 0.0, ymin = 0.0, zmin = 0.0;
  double xmax = 0.0, ymax = 0.0, zmax = 0.0;
  std::map<std::string, int> surfaces;
  std::map<std::string, int> curves;
};

int count_subshapes(const TopoDS_Shape& shape, TopAbs_ShapeEnum type)
{
  int count = 0;
  for (TopExp_Explorer explorer(shape, type); explorer.More(); explorer.Next()) ++count;
  return count;
}

Metrics measure(const TopoDS_Shape& shape)
{
  Metrics m;
  m.is_null = shape.IsNull();
  if (m.is_null) return m;

  BRepCheck_Analyzer analyzer(shape, true, false, true);
  m.valid = analyzer.IsValid();
  m.vertices = count_subshapes(shape, TopAbs_VERTEX);
  m.edges = count_subshapes(shape, TopAbs_EDGE);
  m.faces = count_subshapes(shape, TopAbs_FACE);
  m.shells = count_subshapes(shape, TopAbs_SHELL);
  m.solids = count_subshapes(shape, TopAbs_SOLID);

  GProp_GProps vp;
  BRepGProp::VolumeProperties(shape, vp);
  m.volume_mm3 = vp.Mass();
  GProp_GProps sp;
  BRepGProp::SurfaceProperties(shape, sp);
  m.area_mm2 = sp.Mass();

  Bnd_Box box;
  BRepBndLib::Add(shape, box);
  if (!box.IsVoid()) box.Get(m.xmin, m.ymin, m.zmin, m.xmax, m.ymax, m.zmax);

  for (TopExp_Explorer ex(shape, TopAbs_FACE); ex.More(); ex.Next())
  {
    const TopoDS_Face face = TopoDS::Face(ex.Current());
    const auto surface = BRep_Tool::Surface(face);
    if (!surface.IsNull())
    {
      GeomAdaptor_Surface adaptor(surface);
      ++m.surfaces[surface_type_name(adaptor.GetType())];
    }
  }
  for (TopExp_Explorer ex(shape, TopAbs_EDGE); ex.More(); ex.Next())
  {
    try
    {
      BRepAdaptor_Curve adaptor(TopoDS::Edge(ex.Current()));
      ++m.curves[curve_type_name(adaptor.GetType())];
    }
    catch (const Standard_Failure&)
    {
      ++m.curves["unclassified_curve"];
    }
  }
  return m;
}

std::string map_json(const std::map<std::string, int>& values)
{
  std::ostringstream out;
  out << "{";
  bool first = true;
  for (const auto& entry : values)
  {
    if (!first) out << ",";
    first = false;
    out << quote(entry.first) << ":" << entry.second;
  }
  out << "}";
  return out.str();
}

std::string metrics_json(const Metrics& m)
{
  std::ostringstream out;
  out << std::setprecision(17);
  out << "{"
      << "\"is_null\":" << (m.is_null ? "true" : "false") << ","
      << "\"valid_brep\":" << (m.valid ? "true" : "false") << ","
      << "\"topology\":{"
      << "\"vertices\":" << m.vertices << ","
      << "\"edges\":" << m.edges << ","
      << "\"faces\":" << m.faces << ","
      << "\"shells\":" << m.shells << ","
      << "\"solids\":" << m.solids << "},"
      << "\"volume_mm3\":" << m.volume_mm3 << ","
      << "\"surface_area_mm2\":" << m.area_mm2 << ","
      << "\"bbox_mm\":{"
      << "\"xmin\":" << m.xmin << ",\"ymin\":" << m.ymin << ",\"zmin\":" << m.zmin << ","
      << "\"xmax\":" << m.xmax << ",\"ymax\":" << m.ymax << ",\"zmax\":" << m.zmax << "},"
      << "\"analytic_surfaces\":" << map_json(m.surfaces) << ","
      << "\"analytic_curves\":" << map_json(m.curves)
      << "}";
  return out.str();
}

std::vector<TopoDS_Solid> collect_solids(const TopoDS_Shape& shape)
{
  std::vector<TopoDS_Solid> solids;
  for (TopExp_Explorer ex(shape, TopAbs_SOLID); ex.More(); ex.Next())
    solids.push_back(TopoDS::Solid(ex.Current()));
  return solids;
}

TopoDS_Shape cut_shape(const TopoDS_Shape& object, const TopoDS_Shape& tool, std::string& report)
{
  BRepAlgoAPI_Cut cut;
  NCollection_List<TopoDS_Shape> objects;
  NCollection_List<TopoDS_Shape> tools;
  objects.Append(object);
  tools.Append(tool);
  cut.SetArguments(objects);
  cut.SetTools(tools);
  cut.SetNonDestructive(true);
  cut.SetRunParallel(false);
  cut.SetFuzzyValue(0.0);
  cut.Build();

  std::ostringstream messages;
  if (cut.HasErrors()) cut.DumpErrors(messages);
  if (cut.HasWarnings()) cut.DumpWarnings(messages);
  report = messages.str();
  if (!cut.IsDone() || cut.HasErrors() || cut.Shape().IsNull())
    throw std::runtime_error("OCCT cut failed: " + report);
  return cut.Shape();
}

std::vector<std::pair<double, double>> parse_profile(const std::string& encoded)
{
  std::vector<std::pair<double, double>> points;
  std::stringstream stream(encoded);
  std::string token;
  while (std::getline(stream, token, ';'))
  {
    const auto comma = token.find(',');
    if (comma == std::string::npos) throw std::runtime_error("profile point lacks comma");
    points.emplace_back(std::stod(token.substr(0, comma)), std::stod(token.substr(comma + 1)));
  }
  if (points.size() < 4) throw std::runtime_error("profile needs at least four points");
  if (std::abs(points.front().first - points.back().first) < 1e-15 &&
      std::abs(points.front().second - points.back().second) < 1e-15)
    points.pop_back();
  return points;
}

TopoDS_Shape revolve_profile(const std::vector<std::pair<double, double>>& points)
{
  BRepBuilderAPI_MakePolygon polygon;
  for (const auto& point : points)
  {
    const double radius = point.first;
    const double z = point.second;
    if (radius < -1e-12) throw std::runtime_error("negative radius in profile");
    polygon.Add(gp_Pnt(radius, 0.0, z));
  }
  polygon.Close();
  if (!polygon.IsDone()) throw std::runtime_error("failed to construct profile wire");

  BRepBuilderAPI_MakeFace make_face(polygon.Wire());
  if (!make_face.IsDone()) throw std::runtime_error("failed to construct profile face");

  const gp_Ax1 axis(gp_Pnt(0.0, 0.0, 0.0), gp_Dir(0.0, 0.0, 1.0));
  BRepPrimAPI_MakeRevol revolve(make_face.Face(), axis, 2.0 * kPi, true);
  if (!revolve.IsDone()) throw std::runtime_error("failed to revolve axisymmetric profile");
  return revolve.Shape();
}

struct StepResult
{
  bool attempted = false;
  std::string transfer_status = "not_attempted";
  std::string write_status = "not_attempted";
  std::string read_status = "not_attempted";
  bool readback_transferred = false;
  bool serialized_ap242 = false;
  bool serialized_mm = false;
  Metrics readback;
  double volume_delta = 0.0;
  double bbox_delta = 0.0;
  std::string error;
};

std::string read_text(const std::filesystem::path& path)
{
  std::ifstream in(path, std::ios::binary);
  std::ostringstream out;
  out << in.rdbuf();
  return out.str();
}

double bbox_delta(const Metrics& a, const Metrics& b)
{
  return std::max({
    std::abs(a.xmin - b.xmin), std::abs(a.ymin - b.ymin), std::abs(a.zmin - b.zmin),
    std::abs(a.xmax - b.xmax), std::abs(a.ymax - b.ymax), std::abs(a.zmax - b.zmax)
  });
}

StepResult step_roundtrip(const TopoDS_Shape& shape, const std::filesystem::path& path)
{
  StepResult result;
  result.attempted = true;
  try
  {
    DESTEP_Parameters params;
    params.WriteSchema = DESTEP_Parameters::WriteMode_StepSchema_AP242DIS;
    params.WriteTessellated = DESTEP_Parameters::RWMode_Tessellated_Off;
    params.WriteModelType = STEPControl_ManifoldSolidBrep;
    params.WriteAssembly = DESTEP_Parameters::WriteMode_Assembly_Auto;
    params.WriteUnit = UnitsMethods_LengthUnit_Millimeter;

    STEPControl_Writer writer;
    const auto solids = collect_solids(shape);
    if (solids.empty()) throw std::runtime_error("STEP export requires at least one solid");

    IFSelect_ReturnStatus aggregate = IFSelect_RetDone;
    for (const TopoDS_Solid& solid : solids)
    {
      const IFSelect_ReturnStatus status =
        writer.Transfer(solid, STEPControl_ManifoldSolidBrep, params, true);
      if (status != IFSelect_RetDone)
      {
        aggregate = status;
        break;
      }
    }
    result.transfer_status = status_name(aggregate);
    if (aggregate != IFSelect_RetDone) return result;

    const IFSelect_ReturnStatus write_status = writer.Write(path.string().c_str());
    result.write_status = status_name(write_status);
    if (write_status != IFSelect_RetDone) return result;

    std::string text = read_text(path);
    std::transform(text.begin(), text.end(), text.begin(),
                   [](unsigned char c) { return static_cast<char>(std::toupper(c)); });
    result.serialized_ap242 = text.find("AP242") != std::string::npos;
    result.serialized_mm = text.find(".MILLI.") != std::string::npos && text.find(".METRE.") != std::string::npos;

    STEPControl_Reader reader;
    const IFSelect_ReturnStatus read_status = reader.ReadFile(path.string().c_str());
    result.read_status = status_name(read_status);
    if (read_status != IFSelect_RetDone) return result;
    result.readback_transferred = reader.TransferRoots() > 0;
    if (!result.readback_transferred) return result;

    const TopoDS_Shape readback = reader.OneShape();
    result.readback = measure(readback);
    const Metrics original = measure(shape);
    result.volume_delta = std::abs(original.volume_mm3 - result.readback.volume_mm3);
    result.bbox_delta = bbox_delta(original, result.readback);
  }
  catch (const Standard_Failure& failure)
  {
    result.error = failure.GetMessageString();
  }
  catch (const std::exception& error)
  {
    result.error = error.what();
  }
  return result;
}

std::string step_json(const StepResult& s)
{
  std::ostringstream out;
  out << std::setprecision(17);
  out << "{"
      << "\"attempted\":" << (s.attempted ? "true" : "false") << ","
      << "\"transfer_status\":" << quote(s.transfer_status) << ","
      << "\"write_status\":" << quote(s.write_status) << ","
      << "\"read_status\":" << quote(s.read_status) << ","
      << "\"readback_transferred\":" << (s.readback_transferred ? "true" : "false") << ","
      << "\"serialized_mentions_ap242\":" << (s.serialized_ap242 ? "true" : "false") << ","
      << "\"serialized_mentions_millimeter\":" << (s.serialized_mm ? "true" : "false") << ","
      << "\"volume_abs_delta_mm3\":" << s.volume_delta << ","
      << "\"bbox_max_abs_delta_mm\":" << s.bbox_delta << ","
      << "\"readback_metrics\":" << metrics_json(s.readback) << ","
      << "\"error\":" << quote(s.error)
      << "}";
  return out.str();
}

struct Strategy
{
  std::string status = "not_run";
  std::string error;
  std::string report;
  int material_boolean_operations = 0;
  double preparation_ms = 0.0;
  double update_ms = 0.0;
  double conceptual_total_ms = 0.0;
  Metrics metrics;
  StepResult step;
};

std::string strategy_json(const Strategy& s)
{
  std::ostringstream out;
  out << std::setprecision(17);
  out << "{"
      << "\"status\":" << quote(s.status) << ","
      << "\"error\":" << quote(s.error) << ","
      << "\"report\":" << quote(s.report) << ","
      << "\"material_boolean_operations\":" << s.material_boolean_operations << ","
      << "\"preparation_ms\":" << s.preparation_ms << ","
      << "\"update_ms\":" << s.update_ms << ","
      << "\"conceptual_total_ms\":" << s.conceptual_total_ms << ","
      << "\"metrics\":" << metrics_json(s.metrics) << ","
      << "\"step\":" << step_json(s.step)
      << "}";
  return out.str();
}

template <typename F>
double timed_ms(F&& fn)
{
  const auto start = std::chrono::steady_clock::now();
  fn();
  const auto end = std::chrono::steady_clock::now();
  return std::chrono::duration<double, std::milli>(end - start).count();
}

} // namespace

int main(int argc, char** argv)
{
  try
  {
    std::string case_id;
    std::string profile_encoded;
    std::filesystem::path step_dir;
    double stock_z0 = 0.0;
    double stock_z1 = 40.0;
    double stock_radius = 10.0;
    int event_count = 1;

    for (int i = 1; i < argc; ++i)
    {
      const std::string arg = argv[i];
      auto require_value = [&](const char* name) -> std::string {
        if (i + 1 >= argc) throw std::runtime_error(std::string("missing value for ") + name);
        return argv[++i];
      };
      if (arg == "--case-id") case_id = require_value("--case-id");
      else if (arg == "--profile") profile_encoded = require_value("--profile");
      else if (arg == "--stock-z0") stock_z0 = std::stod(require_value("--stock-z0"));
      else if (arg == "--stock-z1") stock_z1 = std::stod(require_value("--stock-z1"));
      else if (arg == "--stock-radius") stock_radius = std::stod(require_value("--stock-radius"));
      else if (arg == "--event-count") event_count = std::stoi(require_value("--event-count"));
      else if (arg == "--step-dir") step_dir = require_value("--step-dir");
      else throw std::runtime_error("unknown argument: " + arg);
    }

    if (case_id.empty() || profile_encoded.empty()) throw std::runtime_error("case-id and profile are required");
    if (event_count < 1) throw std::runtime_error("event-count must be >= 1");
    if (std::string(OCC_VERSION_COMPLETE) != kExpectedOcctVersion)
      throw std::runtime_error(std::string("unexpected OCCT runtime version: ") + OCC_VERSION_COMPLETE);

    const auto points = parse_profile(profile_encoded);
    TopoDS_Shape target;
    const double target_build_ms = timed_ms([&] { target = revolve_profile(points); });
    const Metrics target_metrics = measure(target);

    const gp_Ax2 stock_axis(gp_Pnt(0.0, 0.0, stock_z0), gp_Dir(0.0, 0.0, 1.0));
    const TopoDS_Shape stock = BRepPrimAPI_MakeCylinder(stock_axis, stock_radius, stock_z1 - stock_z0).Shape();
    const Metrics stock_metrics = measure(stock);

    TopoDS_Shape removal;
    std::string envelope_report;
    const double envelope_ms = timed_ms([&] { removal = cut_shape(stock, target, envelope_report); });
    const Metrics removal_metrics = measure(removal);

    TopoDS_Shape repeated_shape;
    TopoDS_Shape batched_shape;

    Strategy repeated;
    repeated.status = "measured";
    repeated.preparation_ms = envelope_ms;
    repeated.material_boolean_operations = event_count;
    try
    {
      repeated_shape = stock;
      repeated.update_ms = timed_ms([&] {
        for (int index = 0; index < event_count; ++index)
        {
          std::string report;
          repeated_shape = cut_shape(repeated_shape, removal, report);
          if (!report.empty()) repeated.report += report;
        }
      });
      repeated.metrics = measure(repeated_shape);
      repeated.conceptual_total_ms = repeated.preparation_ms + repeated.update_ms;
    }
    catch (const std::exception& error)
    {
      repeated.status = "error";
      repeated.error = error.what();
    }

    Strategy batched;
    batched.status = "measured";
    batched.preparation_ms = envelope_ms;
    batched.material_boolean_operations = 1;
    try
    {
      batched.update_ms = timed_ms([&] {
        std::string report;
        batched_shape = cut_shape(stock, removal, report);
        batched.report = report;
      });
      batched.metrics = measure(batched_shape);
      batched.conceptual_total_ms = batched.preparation_ms + batched.update_ms;
    }
    catch (const std::exception& error)
    {
      batched.status = "error";
      batched.error = error.what();
    }

    Strategy axisymmetric;
    axisymmetric.status = "measured";
    axisymmetric.material_boolean_operations = 0;
    axisymmetric.update_ms = target_build_ms;
    axisymmetric.conceptual_total_ms = target_build_ms;
    axisymmetric.metrics = target_metrics;

    if (!step_dir.empty())
    {
      std::filesystem::create_directories(step_dir);
      if (repeated.status == "measured")
        repeated.step = step_roundtrip(repeated_shape, step_dir / (case_id + "-repeated.step"));
      if (batched.status == "measured")
        batched.step = step_roundtrip(batched_shape, step_dir / (case_id + "-batched.step"));
      axisymmetric.step = step_roundtrip(target, step_dir / (case_id + "-axis2d.step"));
    }

    std::ostringstream out;
    out << std::setprecision(17);
    out << "{"
        << "\"schema\":\"rcs-010-worker/1.0\","
        << "\"case_id\":" << quote(case_id) << ","
        << "\"backend\":{\"id\":\"occt\",\"version\":\"" << kExpectedOcctVersion
        << "\",\"commit\":\"" << kExpectedOcctCommit << "\"},"
        << "\"profile_polygon_points\":" << points.size() << ","
        << "\"event_count\":" << event_count << ","
        << "\"target_build_ms\":" << target_build_ms << ","
        << "\"envelope_build_ms\":" << envelope_ms << ","
        << "\"peak_rss_kb\":" << max_rss_kb() << ","
        << "\"stock_metrics\":" << metrics_json(stock_metrics) << ","
        << "\"target_metrics\":" << metrics_json(target_metrics) << ","
        << "\"removal_envelope_metrics\":" << metrics_json(removal_metrics) << ","
        << "\"envelope_report\":" << quote(envelope_report) << ","
        << "\"strategies\":{"
        << "\"repeated_3d\":" << strategy_json(repeated) << ","
        << "\"batched_3d\":" << strategy_json(batched) << ","
        << "\"axisymmetric_2d\":" << strategy_json(axisymmetric)
        << "}"
        << "}";
    std::cout << out.str() << "\n";
    return 0;
  }
  catch (const Standard_Failure& failure)
  {
    std::cerr << "OCCT failure: " << failure.GetMessageString() << "\n";
    return 3;
  }
  catch (const std::exception& error)
  {
    std::cerr << error.what() << "\n";
    return 2;
  }
}
