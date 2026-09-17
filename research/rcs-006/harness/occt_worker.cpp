#include <BRepAdaptor_Curve.hxx>
#include <BRepAlgoAPI_Cut.hxx>
#include <BRepBndLib.hxx>
#include <BRepCheck_Analyzer.hxx>
#include <BRepGProp.hxx>
#include <BRepPrimAPI_MakeBox.hxx>
#include <BRepPrimAPI_MakeCylinder.hxx>
#include <BRep_Tool.hxx>
#include <Bnd_Box.hxx>
#include <DESTEP_Parameters.hxx>
#include <GProp_GProps.hxx>
#include <GeomAbs_CurveType.hxx>
#include <GeomAbs_SurfaceType.hxx>
#include <GeomAdaptor_Surface.hxx>
#include <IFSelect_ReturnStatus.hxx>
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
#include <gp_Ax2.hxx>
#include <gp_Dir.hxx>
#include <gp_Pnt.hxx>

#include <algorithm>
#include <chrono>
#include <cmath>
#include <cstdint>
#include <filesystem>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <limits>
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

std::string quote(const std::string& value)
{
  return "\"" + json_escape(value) + "\"";
}

double param_double(const std::map<std::string, std::string>& params,
                    const std::string& key,
                    double fallback)
{
  const auto it = params.find(key);
  return it == params.end() ? fallback : std::stod(it->second);
}

int param_int(const std::map<std::string, std::string>& params,
              const std::string& key,
              int fallback)
{
  const auto it = params.find(key);
  return it == params.end() ? fallback : std::stoi(it->second);
}

std::string param_string(const std::map<std::string, std::string>& params,
                         const std::string& key,
                         const std::string& fallback)
{
  const auto it = params.find(key);
  return it == params.end() ? fallback : it->second;
}

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
  if (getrusage(RUSAGE_SELF, &usage) != 0)
  {
    return -1;
  }
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
  double surface_area_mm2 = 0.0;
  double min_face_area_mm2 = 0.0;
  double min_edge_length_mm = 0.0;
  double xmin = 0.0;
  double ymin = 0.0;
  double zmin = 0.0;
  double xmax = 0.0;
  double ymax = 0.0;
  double zmax = 0.0;
  std::map<std::string, int> surface_types;
  std::map<std::string, int> curve_types;
};

int count_subshapes(const TopoDS_Shape& shape, TopAbs_ShapeEnum type)
{
  int count = 0;
  for (TopExp_Explorer explorer(shape, type); explorer.More(); explorer.Next())
  {
    ++count;
  }
  return count;
}

Metrics measure_shape(const TopoDS_Shape& shape)
{
  Metrics metrics;
  metrics.is_null = shape.IsNull();
  if (metrics.is_null)
  {
    return metrics;
  }

  BRepCheck_Analyzer analyzer(shape, true, false, true);
  metrics.valid = analyzer.IsValid();
  metrics.vertices = count_subshapes(shape, TopAbs_VERTEX);
  metrics.edges = count_subshapes(shape, TopAbs_EDGE);
  metrics.faces = count_subshapes(shape, TopAbs_FACE);
  metrics.shells = count_subshapes(shape, TopAbs_SHELL);
  metrics.solids = count_subshapes(shape, TopAbs_SOLID);

  GProp_GProps volume_props;
  BRepGProp::VolumeProperties(shape, volume_props);
  metrics.volume_mm3 = volume_props.Mass();

  GProp_GProps surface_props;
  BRepGProp::SurfaceProperties(shape, surface_props);
  metrics.surface_area_mm2 = surface_props.Mass();

  Bnd_Box box;
  BRepBndLib::Add(shape, box);
  if (!box.IsVoid())
  {
    box.Get(metrics.xmin, metrics.ymin, metrics.zmin,
            metrics.xmax, metrics.ymax, metrics.zmax);
  }

  double min_face_area = std::numeric_limits<double>::infinity();
  for (TopExp_Explorer explorer(shape, TopAbs_FACE); explorer.More(); explorer.Next())
  {
    const TopoDS_Face face = TopoDS::Face(explorer.Current());
    GProp_GProps props;
    BRepGProp::SurfaceProperties(face, props);
    if (props.Mass() > 0.0)
    {
      min_face_area = std::min(min_face_area, props.Mass());
    }

    const auto surface = BRep_Tool::Surface(face);
    if (!surface.IsNull())
    {
      GeomAdaptor_Surface adaptor(surface);
      ++metrics.surface_types[surface_type_name(adaptor.GetType())];
    }
  }
  if (std::isfinite(min_face_area))
  {
    metrics.min_face_area_mm2 = min_face_area;
  }

  double min_edge_length = std::numeric_limits<double>::infinity();
  for (TopExp_Explorer explorer(shape, TopAbs_EDGE); explorer.More(); explorer.Next())
  {
    const TopoDS_Edge edge = TopoDS::Edge(explorer.Current());
    GProp_GProps props;
    BRepGProp::LinearProperties(edge, props);
    if (props.Mass() > 0.0)
    {
      min_edge_length = std::min(min_edge_length, props.Mass());
    }

    try
    {
      BRepAdaptor_Curve adaptor(edge);
      ++metrics.curve_types[curve_type_name(adaptor.GetType())];
    }
    catch (const Standard_Failure&)
    {
      ++metrics.curve_types["unclassified_curve"];
    }
  }
  if (std::isfinite(min_edge_length))
  {
    metrics.min_edge_length_mm = min_edge_length;
  }

  return metrics;
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
      << "\"surface_area_mm2\":" << m.surface_area_mm2 << ","
      << "\"min_face_area_mm2\":" << m.min_face_area_mm2 << ","
      << "\"min_edge_length_mm\":" << m.min_edge_length_mm << ","
      << "\"bbox_mm\":{"
      << "\"xmin\":" << m.xmin << ",\"ymin\":" << m.ymin << ",\"zmin\":" << m.zmin << ","
      << "\"xmax\":" << m.xmax << ",\"ymax\":" << m.ymax << ",\"zmax\":" << m.zmax << "},"
      << "\"analytic_surfaces\":" << map_json(m.surface_types) << ","
      << "\"analytic_curves\":" << map_json(m.curve_types)
      << "}";
  return out.str();
}

TopoDS_Shape boolean_cut(const TopoDS_Shape& object,
                         const TopoDS_Shape& tool,
                         double fuzzy_mm,
                         std::string& report)
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
  cut.SetFuzzyValue(fuzzy_mm);
  cut.Build();

  std::ostringstream messages;
  if (cut.HasErrors()) cut.DumpErrors(messages);
  if (cut.HasWarnings()) cut.DumpWarnings(messages);
  report = messages.str();

  if (!cut.IsDone() || cut.HasErrors() || cut.Shape().IsNull())
  {
    throw std::runtime_error("OCCT Boolean cut failed: " + report);
  }
  return cut.Shape();
}

struct CaseResult
{
  TopoDS_Shape input;
  TopoDS_Shape result;
  std::string algorithm_report;
  int boolean_operations = 0;
};

CaseResult build_case(const std::string& case_id,
                      const std::map<std::string, std::string>& params)
{
  const double fuzzy = param_double(params, "fuzzy_mm", 0.0);
  CaseResult output;

  if (case_id == "coincident_face")
  {
    const double offset = param_double(params, "offset_mm", 0.0);
    output.input = BRepPrimAPI_MakeBox(gp_Pnt(0, 0, 0), 20, 20, 10).Shape();
    const TopoDS_Shape tool = BRepPrimAPI_MakeBox(gp_Pnt(0, 0, 10 + offset), 20, 20, 5).Shape();
    output.result = boolean_cut(output.input, tool, fuzzy, output.algorithm_report);
    output.boolean_operations = 1;
  }
  else if (case_id == "tangent_contact")
  {
    const double offset = param_double(params, "offset_mm", 0.0);
    output.input = BRepPrimAPI_MakeBox(gp_Pnt(0, 0, 0), 20, 20, 10).Shape();
    const gp_Ax2 axis(gp_Pnt(25 + offset, 10, -1), gp_Dir(0, 0, 1));
    const TopoDS_Shape tool = BRepPrimAPI_MakeCylinder(axis, 5.0, 12.0).Shape();
    output.result = boolean_cut(output.input, tool, fuzzy, output.algorithm_report);
    output.boolean_operations = 1;
  }
  else if (case_id == "thin_skim")
  {
    const double depth = param_double(params, "depth_mm", 0.0001);
    if (depth <= 0.0 || depth >= 5.0) throw std::runtime_error("depth_mm out of range");
    output.input = BRepPrimAPI_MakeBox(gp_Pnt(0, 0, 0), 20, 20, 10).Shape();
    const TopoDS_Shape tool = BRepPrimAPI_MakeBox(gp_Pnt(-1, -1, 10 - depth), 22, 22, 2 + depth).Shape();
    output.result = boolean_cut(output.input, tool, fuzzy, output.algorithm_report);
    output.boolean_operations = 1;
  }
  else if (case_id == "repeated_slot")
  {
    const int count = param_int(params, "count", 10);
    if (count < 1 || count > 100000) throw std::runtime_error("count out of range");
    output.input = BRepPrimAPI_MakeBox(gp_Pnt(0, 0, 0), 40, 30, 10).Shape();
    const TopoDS_Shape tool = BRepPrimAPI_MakeBox(gp_Pnt(15, 5, 5), 10, 20, 6).Shape();
    TopoDS_Shape current = output.input;
    std::ostringstream reports;
    for (int i = 0; i < count; ++i)
    {
      std::string report;
      current = boolean_cut(current, tool, fuzzy, report);
      if (!report.empty()) reports << "operation " << i << ": " << report << "\n";
    }
    output.result = current;
    output.algorithm_report = reports.str();
    output.boolean_operations = count;
  }
  else if (case_id == "overlapping_slots")
  {
    output.input = BRepPrimAPI_MakeBox(gp_Pnt(0, 0, 0), 40, 40, 10).Shape();
    const TopoDS_Shape first = BRepPrimAPI_MakeBox(gp_Pnt(5, 14, 4), 30, 8, 7).Shape();
    const TopoDS_Shape second = BRepPrimAPI_MakeBox(gp_Pnt(14, 5, 4), 8, 30, 7).Shape();
    std::string first_report;
    std::string second_report;
    const TopoDS_Shape intermediate = boolean_cut(output.input, first, fuzzy, first_report);
    output.result = boolean_cut(intermediate, second, fuzzy, second_report);
    output.algorithm_report = first_report + second_report;
    output.boolean_operations = 2;
  }
  else if (case_id == "lathe_od_finish")
  {
    const double depth = param_double(params, "depth_mm", 0.1);
    const double target_radius = 20.0 - depth;
    if (target_radius <= 0.0 || target_radius > 20.0) throw std::runtime_error("depth_mm out of range");
    const gp_Ax2 axis(gp_Pnt(0, 0, 0), gp_Dir(0, 0, 1));
    output.input = BRepPrimAPI_MakeCylinder(axis, 20.0, 60.0).Shape();
    const TopoDS_Shape outer = BRepPrimAPI_MakeCylinder(axis, 25.0, 60.0).Shape();
    const TopoDS_Shape inner = BRepPrimAPI_MakeCylinder(axis, target_radius, 60.0).Shape();
    std::string ring_report;
    const TopoDS_Shape ring = boolean_cut(outer, inner, fuzzy, ring_report);
    std::string stock_report;
    output.result = boolean_cut(output.input, ring, fuzzy, stock_report);
    output.algorithm_report = ring_report + stock_report;
    output.boolean_operations = 2;
  }
  else if (case_id == "lathe_parting")
  {
    const double width = param_double(params, "tool_width_mm", 2.0);
    if (width <= 0.0 || width >= 20.0) throw std::runtime_error("tool_width_mm out of range");
    const gp_Ax2 axis(gp_Pnt(0, 0, 0), gp_Dir(0, 0, 1));
    output.input = BRepPrimAPI_MakeCylinder(axis, 20.0, 80.0).Shape();
    const TopoDS_Shape tool = BRepPrimAPI_MakeBox(gp_Pnt(-25, -25, 40 - width / 2.0), 50, 50, width).Shape();
    output.result = boolean_cut(output.input, tool, fuzzy, output.algorithm_report);
    output.boolean_operations = 1;
  }
  else if (case_id == "mill_cut_through")
  {
    const double width = param_double(params, "slot_width_mm", 2.0);
    if (width <= 0.0 || width >= 20.0) throw std::runtime_error("slot_width_mm out of range");
    output.input = BRepPrimAPI_MakeBox(gp_Pnt(0, 0, 0), 40, 20, 10).Shape();
    const TopoDS_Shape tool = BRepPrimAPI_MakeBox(gp_Pnt(20 - width / 2.0, -1, -1), width, 22, 12).Shape();
    output.result = boolean_cut(output.input, tool, fuzzy, output.algorithm_report);
    output.boolean_operations = 1;
  }
  else if (case_id == "step_cylinder")
  {
    const gp_Ax2 axis(gp_Pnt(0, 0, 0), gp_Dir(0, 0, 1));
    output.input = BRepPrimAPI_MakeCylinder(axis, 12.7, 50.8).Shape();
    output.result = output.input;
  }
  else if (case_id == "step_block")
  {
    output.input = BRepPrimAPI_MakeBox(gp_Pnt(0, 0, 0), 25.4, 12.7, 6.35).Shape();
    output.result = output.input;
  }
  else
  {
    throw std::runtime_error("unknown case: " + case_id);
  }

  return output;
}

std::string read_text_file(const std::filesystem::path& path)
{
  std::ifstream stream(path, std::ios::binary);
  std::ostringstream contents;
  contents << stream.rdbuf();
  return contents.str();
}

std::string to_upper(std::string value)
{
  std::transform(value.begin(), value.end(), value.begin(),
                 [](unsigned char ch) { return static_cast<char>(std::toupper(ch)); });
  return value;
}

std::string fnv1a64_hex(const std::string& data)
{
  std::uint64_t hash = 14695981039346656037ULL;
  for (const unsigned char byte : data)
  {
    hash ^= static_cast<std::uint64_t>(byte);
    hash *= 1099511628211ULL;
  }
  std::ostringstream out;
  out << std::hex << std::setw(16) << std::setfill('0') << hash;
  return out.str();
}

struct StepResult
{
  bool attempted = false;
  std::string unit;
  std::string transfer_status = "not_attempted";
  std::string write_status = "not_attempted";
  std::string read_status = "not_attempted";
  bool readback_transferred = false;
  Metrics readback_metrics;
  double bbox_max_abs_delta_mm = 0.0;
  double volume_abs_delta_mm3 = 0.0;
  double volume_rel_delta = 0.0;
  std::string schema_excerpt;
  bool serialized_mentions_inch = false;
  bool serialized_mentions_millimeter = false;
  std::string file_digest_fnv1a64;
};

std::vector<TopoDS_Solid> collect_solids(const TopoDS_Shape& shape)
{
  std::vector<TopoDS_Solid> solids;
  for (TopExp_Explorer explorer(shape, TopAbs_SOLID); explorer.More(); explorer.Next())
  {
    solids.push_back(TopoDS::Solid(explorer.Current()));
  }
  return solids;
}

StepResult step_roundtrip(const TopoDS_Shape& shape,
                          const Metrics& source_metrics,
                          const std::filesystem::path& file_path,
                          const std::string& unit)
{
  StepResult result;
  result.attempted = true;
  result.unit = unit;

  DESTEP_Parameters params;
  params.WriteSchema = DESTEP_Parameters::WriteMode_StepSchema_AP242DIS;
  params.WriteTessellated = DESTEP_Parameters::RWMode_Tessellated_Off;
  params.WriteModelType = STEPControl_ManifoldSolidBrep;
  params.WriteAssembly = DESTEP_Parameters::WriteMode_Assembly_Auto;
  if (unit == "inch")
  {
    params.WriteUnit = UnitsMethods_LengthUnit_Inch;
  }
  else if (unit == "millimeter")
  {
    params.WriteUnit = UnitsMethods_LengthUnit_Millimeter;
  }
  else
  {
    throw std::runtime_error("unsupported STEP unit: " + unit);
  }

  STEPControl_Writer writer;
  const auto solids = collect_solids(shape);
  if (solids.empty())
  {
    throw std::runtime_error("STEP export requires at least one solid");
  }

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
  if (aggregate != IFSelect_RetDone)
  {
    return result;
  }

  std::filesystem::create_directories(file_path.parent_path());
  const IFSelect_ReturnStatus write_status = writer.Write(file_path.string().c_str());
  result.write_status = status_name(write_status);
  if (write_status != IFSelect_RetDone)
  {
    return result;
  }

  const std::string file_text = read_text_file(file_path);
  result.file_digest_fnv1a64 = fnv1a64_hex(file_text);
  const std::string upper = to_upper(file_text);
  result.serialized_mentions_inch = upper.find("INCH") != std::string::npos;
  result.serialized_mentions_millimeter =
    upper.find(".MILLI.") != std::string::npos && upper.find(".METRE.") != std::string::npos;
  const std::size_t schema_start = upper.find("FILE_SCHEMA");
  if (schema_start != std::string::npos)
  {
    const std::size_t schema_end = upper.find(';', schema_start);
    result.schema_excerpt = file_text.substr(schema_start,
      schema_end == std::string::npos ? std::string::npos : schema_end - schema_start + 1);
  }

  STEPControl_Reader reader;
  const IFSelect_ReturnStatus read_status = reader.ReadFile(file_path.string().c_str());
  result.read_status = status_name(read_status);
  if (read_status != IFSelect_RetDone)
  {
    return result;
  }

  result.readback_transferred = reader.TransferRoots() > 0;
  if (!result.readback_transferred)
  {
    return result;
  }

  const TopoDS_Shape readback = reader.OneShape();
  result.readback_metrics = measure_shape(readback);
  const Metrics& rb = result.readback_metrics;
  result.bbox_max_abs_delta_mm = std::max({
    std::abs(source_metrics.xmin - rb.xmin), std::abs(source_metrics.ymin - rb.ymin),
    std::abs(source_metrics.zmin - rb.zmin), std::abs(source_metrics.xmax - rb.xmax),
    std::abs(source_metrics.ymax - rb.ymax), std::abs(source_metrics.zmax - rb.zmax)});
  result.volume_abs_delta_mm3 = std::abs(source_metrics.volume_mm3 - rb.volume_mm3);
  const double denom = std::max(std::abs(source_metrics.volume_mm3), 1.0e-30);
  result.volume_rel_delta = result.volume_abs_delta_mm3 / denom;
  return result;
}

std::string step_json(const StepResult& step)
{
  std::ostringstream out;
  out << std::setprecision(17);
  out << "{"
      << "\"attempted\":" << (step.attempted ? "true" : "false") << ","
      << "\"unit\":" << quote(step.unit) << ","
      << "\"transfer_status\":" << quote(step.transfer_status) << ","
      << "\"write_status\":" << quote(step.write_status) << ","
      << "\"read_status\":" << quote(step.read_status) << ","
      << "\"readback_transferred\":" << (step.readback_transferred ? "true" : "false") << ","
      << "\"readback_metrics\":" << metrics_json(step.readback_metrics) << ","
      << "\"bbox_max_abs_delta_mm\":" << step.bbox_max_abs_delta_mm << ","
      << "\"volume_abs_delta_mm3\":" << step.volume_abs_delta_mm3 << ","
      << "\"volume_rel_delta\":" << step.volume_rel_delta << ","
      << "\"schema_excerpt\":" << quote(step.schema_excerpt) << ","
      << "\"serialized_mentions_inch\":" << (step.serialized_mentions_inch ? "true" : "false") << ","
      << "\"serialized_mentions_millimeter\":" << (step.serialized_mentions_millimeter ? "true" : "false") << ","
      << "\"file_digest_fnv1a64\":" << quote(step.file_digest_fnv1a64)
      << "}";
  return out.str();
}

std::map<std::string, std::string> parse_params(int argc, char** argv,
                                                 std::string& case_id,
                                                 std::string& step_file,
                                                 std::string& unit)
{
  std::map<std::string, std::string> params;
  unit = "millimeter";
  for (int i = 1; i < argc; ++i)
  {
    const std::string arg = argv[i];
    if (arg == "--case" && i + 1 < argc)
    {
      case_id = argv[++i];
    }
    else if (arg == "--param" && i + 1 < argc)
    {
      const std::string token = argv[++i];
      const std::size_t equals = token.find('=');
      if (equals == std::string::npos || equals == 0)
      {
        throw std::runtime_error("--param requires key=value");
      }
      params[token.substr(0, equals)] = token.substr(equals + 1);
    }
    else if (arg == "--step-file" && i + 1 < argc)
    {
      step_file = argv[++i];
    }
    else if (arg == "--unit" && i + 1 < argc)
    {
      unit = argv[++i];
    }
    else
    {
      throw std::runtime_error("unknown or incomplete argument: " + arg);
    }
  }
  if (case_id.empty()) throw std::runtime_error("--case is required");
  return params;
}

std::string params_json(const std::map<std::string, std::string>& params)
{
  std::ostringstream out;
  out << "{";
  bool first = true;
  for (const auto& item : params)
  {
    if (!first) out << ",";
    first = false;
    out << quote(item.first) << ":" << quote(item.second);
  }
  out << "}";
  return out.str();
}
} // namespace

int main(int argc, char** argv)
{
  const auto started = std::chrono::steady_clock::now();
  std::string case_id;
  std::string step_file;
  std::string unit;
  std::map<std::string, std::string> params;

  try
  {
    if (std::string(OCC_VERSION_COMPLETE) != kExpectedOcctVersion)
    {
      throw std::runtime_error(std::string("unexpected OCCT runtime version: ") + OCC_VERSION_COMPLETE);
    }

    params = parse_params(argc, argv, case_id, step_file, unit);
    const auto geometry_started = std::chrono::steady_clock::now();
    const CaseResult built = build_case(case_id, params);
    const auto geometry_finished = std::chrono::steady_clock::now();

    const Metrics input_metrics = measure_shape(built.input);
    const Metrics result_metrics = measure_shape(built.result);

    StepResult step;
    if (!step_file.empty())
    {
      step = step_roundtrip(built.result, result_metrics, step_file, unit);
    }

    const auto finished = std::chrono::steady_clock::now();
    const double geometry_ms =
      std::chrono::duration<double, std::milli>(geometry_finished - geometry_started).count();
    const double total_ms =
      std::chrono::duration<double, std::milli>(finished - started).count();

    std::ostringstream out;
    out << std::setprecision(17);
    out << "{"
        << "\"worker_schema\":\"rcs-006-occt-worker/1.0\","
        << "\"case_id\":" << quote(case_id) << ","
        << "\"parameters\":" << params_json(params) << ","
        << "\"backend\":{"
        << "\"id\":\"occt\","
        << "\"version\":" << quote(OCC_VERSION_COMPLETE) << ","
        << "\"expected_commit\":" << quote(kExpectedOcctCommit) << ","
        << "\"run_parallel\":false,\"non_destructive\":true},"
        << "\"algorithm_report\":" << quote(built.algorithm_report) << ","
        << "\"boolean_operations\":" << built.boolean_operations << ","
        << "\"input_metrics\":" << metrics_json(input_metrics) << ","
        << "\"result_metrics\":" << metrics_json(result_metrics) << ","
        << "\"material_volume_removed_mm3\":"
        << (input_metrics.volume_mm3 - result_metrics.volume_mm3) << ","
        << "\"step\":" << step_json(step) << ","
        << "\"timing\":{"
        << "\"geometry_ms\":" << geometry_ms << ",\"total_ms\":" << total_ms << "},"
        << "\"max_rss_kb\":" << max_rss_kb()
        << "}";
    std::cout << out.str() << std::endl;
    return 0;
  }
  catch (const Standard_Failure& failure)
  {
    std::cerr << "OCCT Standard_Failure: " << failure.GetMessageString() << std::endl;
    return 20;
  }
  catch (const std::exception& error)
  {
    std::cerr << "worker error: " << error.what() << std::endl;
    return 21;
  }
  catch (...)
  {
    std::cerr << "worker error: unknown exception" << std::endl;
    return 22;
  }
}
