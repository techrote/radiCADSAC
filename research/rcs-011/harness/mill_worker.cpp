#include <BRepAdaptor_Surface.hxx>
#include <BRepAlgoAPI_Cut.hxx>
#include <BRepBndLib.hxx>
#include <BRepCheck_Analyzer.hxx>
#include <BRepGProp.hxx>
#include <BRepPrimAPI_MakeBox.hxx>
#include <BRepPrimAPI_MakeCylinder.hxx>
#include <BRepPrimAPI_MakeSphere.hxx>
#include <Bnd_Box.hxx>
#include <DESTEP_Parameters.hxx>
#include <GProp_GProps.hxx>
#include <GeomAbs_SurfaceType.hxx>
#include <IFSelect_ReturnStatus.hxx>
#include <NCollection_List.hxx>
#include <Standard_Failure.hxx>
#include <Standard_Version.hxx>
#include <STEPControl_Reader.hxx>
#include <STEPControl_Writer.hxx>
#include <TopAbs_ShapeEnum.hxx>
#include <TopExp_Explorer.hxx>
#include <TopoDS.hxx>
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
#include <filesystem>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <map>
#include <sstream>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

#ifndef _WIN32
#include <sys/resource.h>
#endif

namespace
{
constexpr const char* kExpectedOcctVersion = "8.0.1";
constexpr const char* kExpectedOcctCommit = "b8f597c677811d1f9f4d8a97f5ae2825c0353a42";
constexpr double kStockX = 40.0;
constexpr double kStockY = 30.0;
constexpr double kStockZ = 10.0;
constexpr double kToolTop = 12.0;
constexpr double kEps = 1e-12;

struct Pose { double x = 0.0; double y = 0.0; double z = 0.0; };
enum class ToolKind { Flat, Drill, Ball };
struct CaseSpec { std::string id; ToolKind tool = ToolKind::Flat; double radius = 2.5; std::vector<std::vector<Pose>> paths; };

std::string json_escape(const std::string& value)
{
  std::ostringstream out;
  for (unsigned char ch : value)
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
          out << "\\u" << std::hex << std::setw(4) << std::setfill('0') << static_cast<int>(ch) << std::dec << std::setfill(' ');
        else
          out << static_cast<char>(ch);
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
  bool is_null = true; bool valid = false;
  int vertices = 0, edges = 0, faces = 0, shells = 0, solids = 0;
  double volume_mm3 = 0.0, area_mm2 = 0.0;
  double xmin = 0.0, ymin = 0.0, zmin = 0.0, xmax = 0.0, ymax = 0.0, zmax = 0.0;
  std::map<std::string, int> surfaces;
};

int count_subshapes(const TopoDS_Shape& shape, TopAbs_ShapeEnum type)
{
  int count = 0;
  for (TopExp_Explorer ex(shape, type); ex.More(); ex.Next()) ++count;
  return count;
}

Metrics measure(const TopoDS_Shape& shape)
{
  Metrics m; m.is_null = shape.IsNull(); if (m.is_null) return m;
  BRepCheck_Analyzer analyzer(shape, true, false, true); m.valid = analyzer.IsValid();
  m.vertices = count_subshapes(shape, TopAbs_VERTEX); m.edges = count_subshapes(shape, TopAbs_EDGE);
  m.faces = count_subshapes(shape, TopAbs_FACE); m.shells = count_subshapes(shape, TopAbs_SHELL); m.solids = count_subshapes(shape, TopAbs_SOLID);
  GProp_GProps vp; BRepGProp::VolumeProperties(shape, vp); m.volume_mm3 = vp.Mass();
  GProp_GProps sp; BRepGProp::SurfaceProperties(shape, sp); m.area_mm2 = sp.Mass();
  Bnd_Box box; BRepBndLib::Add(shape, box); if (!box.IsVoid()) box.Get(m.xmin, m.ymin, m.zmin, m.xmax, m.ymax, m.zmax);
  for (TopExp_Explorer ex(shape, TopAbs_FACE); ex.More(); ex.Next())
  {
    try { BRepAdaptor_Surface adaptor(TopoDS::Face(ex.Current()), true); ++m.surfaces[surface_type_name(adaptor.GetType())]; }
    catch (const Standard_Failure&) { ++m.surfaces["unclassified_surface"]; }
  }
  return m;
}

std::string map_json(const std::map<std::string, int>& values)
{
  std::ostringstream out; out << "{"; bool first = true;
  for (const auto& entry : values) { if (!first) out << ","; first = false; out << quote(entry.first) << ":" << entry.second; }
  out << "}"; return out.str();
}

std::string metrics_json(const Metrics& m)
{
  std::ostringstream out; out << std::setprecision(17);
  out << "{" << "\"is_null\":" << (m.is_null ? "true" : "false") << "," << "\"valid_brep\":" << (m.valid ? "true" : "false") << ","
      << "\"topology\":{" << "\"vertices\":" << m.vertices << ",\"edges\":" << m.edges << ",\"faces\":" << m.faces << ",\"shells\":" << m.shells << ",\"solids\":" << m.solids << "},"
      << "\"volume_mm3\":" << m.volume_mm3 << ",\"surface_area_mm2\":" << m.area_mm2 << ","
      << "\"bbox_mm\":{" << "\"xmin\":" << m.xmin << ",\"ymin\":" << m.ymin << ",\"zmin\":" << m.zmin << ",\"xmax\":" << m.xmax << ",\"ymax\":" << m.ymax << ",\"zmax\":" << m.zmax << "},"
      << "\"analytic_surfaces\":" << map_json(m.surfaces) << "}";
  return out.str();
}

std::vector<TopoDS_Solid> collect_solids(const TopoDS_Shape& shape)
{
  std::vector<TopoDS_Solid> solids;
  for (TopExp_Explorer ex(shape, TopAbs_SOLID); ex.More(); ex.Next()) solids.push_back(TopoDS::Solid(ex.Current()));
  return solids;
}

TopoDS_Shape cut_many(const TopoDS_Shape& object, const std::vector<TopoDS_Shape>& tools, std::string& report)
{
  if (tools.empty()) return object;
  BRepAlgoAPI_Cut cut; NCollection_List<TopoDS_Shape> objects; NCollection_List<TopoDS_Shape> tool_list;
  objects.Append(object); for (const auto& tool : tools) tool_list.Append(tool);
  cut.SetArguments(objects); cut.SetTools(tool_list); cut.SetNonDestructive(true); cut.SetRunParallel(false); cut.SetFuzzyValue(0.0); cut.Build();
  std::ostringstream messages; if (cut.HasErrors()) cut.DumpErrors(messages); if (cut.HasWarnings()) cut.DumpWarnings(messages); report = messages.str();
  if (!cut.IsDone() || cut.HasErrors() || cut.Shape().IsNull()) throw std::runtime_error("OCCT cut failed: " + report);
  return cut.Shape();
}

double distance3(const Pose& a, const Pose& b)
{
  const double dx = b.x - a.x, dy = b.y - a.y, dz = b.z - a.z; return std::sqrt(dx * dx + dy * dy + dz * dz);
}
bool same_pose(const Pose& a, const Pose& b) { return distance3(a, b) <= kEps; }

TopoDS_Shape flat_pose_tool(const Pose& p, double radius)
{
  const double height = std::max(kEps, kToolTop - p.z);
  return BRepPrimAPI_MakeCylinder(gp_Ax2(gp_Pnt(p.x, p.y, p.z), gp_Dir(0.0, 0.0, 1.0)), radius, height).Shape();
}
TopoDS_Shape ball_pose_tool(const Pose& p, double radius) { return BRepPrimAPI_MakeSphere(gp_Pnt(p.x, p.y, p.z), radius).Shape(); }

std::vector<TopoDS_Shape> exact_flat_segment(const Pose& a, const Pose& b, double radius)
{
  std::vector<TopoDS_Shape> tools; const double dx = b.x - a.x, dy = b.y - a.y, dxy = std::hypot(dx, dy);
  if (dxy <= kEps) { tools.push_back(flat_pose_tool(a.z < b.z ? a : b, radius)); return tools; }
  if (std::abs(a.z - b.z) > 1e-10) throw std::runtime_error("flat exact sweep currently requires horizontal XY segment or pure plunge");
  tools.push_back(flat_pose_tool(a, radius)); tools.push_back(flat_pose_tool(b, radius));
  const double ux = dx / dxy, uy = dy / dxy, yx = -uy, yy = ux;
  const gp_Pnt origin(a.x - yx * radius, a.y - yy * radius, a.z);
  const gp_Ax2 axes(origin, gp_Dir(0.0, 0.0, 1.0), gp_Dir(ux, uy, 0.0));
  tools.push_back(BRepPrimAPI_MakeBox(axes, dxy, 2.0 * radius, std::max(kEps, kToolTop - a.z)).Shape());
  return tools;
}

std::vector<TopoDS_Shape> exact_ball_segment(const Pose& a, const Pose& b, double radius)
{
  std::vector<TopoDS_Shape> tools; const double length = distance3(a, b);
  if (length <= kEps) { tools.push_back(ball_pose_tool(a, radius)); return tools; }
  tools.push_back(ball_pose_tool(a, radius)); tools.push_back(ball_pose_tool(b, radius));
  tools.push_back(BRepPrimAPI_MakeCylinder(gp_Ax2(gp_Pnt(a.x, a.y, a.z), gp_Dir(b.x - a.x, b.y - a.y, b.z - a.z)), radius, length).Shape());
  return tools;
}

std::vector<Pose> simplify_path(const std::vector<Pose>& input)
{
  std::vector<Pose> dedup; for (const Pose& p : input) if (dedup.empty() || !same_pose(dedup.back(), p)) dedup.push_back(p);
  if (dedup.size() <= 2) return dedup;
  std::vector<Pose> output; output.push_back(dedup.front());
  for (std::size_t i = 1; i + 1 < dedup.size(); ++i)
  {
    const Pose& a = output.back(); const Pose& b = dedup[i]; const Pose& c = dedup[i + 1];
    const double abx = b.x - a.x, aby = b.y - a.y, abz = b.z - a.z, bcx = c.x - b.x, bcy = c.y - b.y, bcz = c.z - b.z;
    const double cx = aby * bcz - abz * bcy, cy = abz * bcx - abx * bcz, cz = abx * bcy - aby * bcx;
    const double cross_norm = std::sqrt(cx * cx + cy * cy + cz * cz); const double dot = abx * bcx + aby * bcy + abz * bcz;
    if (cross_norm <= 1e-10 && dot >= 0.0) continue; output.push_back(b);
  }
  output.push_back(dedup.back()); return output;
}

std::vector<TopoDS_Shape> exact_envelope_for_path(const std::vector<Pose>& path, ToolKind kind, double radius)
{
  if (path.empty()) throw std::runtime_error("empty path"); std::vector<TopoDS_Shape> tools;
  if (path.size() == 1) { tools.push_back(kind == ToolKind::Ball ? ball_pose_tool(path.front(), radius) : flat_pose_tool(path.front(), radius)); return tools; }
  for (std::size_t i = 0; i + 1 < path.size(); ++i)
  {
    auto segment = kind == ToolKind::Ball ? exact_ball_segment(path[i], path[i + 1], radius) : exact_flat_segment(path[i], path[i + 1], radius);
    tools.insert(tools.end(), segment.begin(), segment.end());
  }
  return tools;
}

std::vector<TopoDS_Shape> sampled_envelope_for_path(const std::vector<Pose>& path, ToolKind kind, double radius, double spacing)
{
  if (path.empty()) throw std::runtime_error("empty path"); std::vector<TopoDS_Shape> tools;
  auto add_pose = [&](const Pose& p) { tools.push_back(kind == ToolKind::Ball ? ball_pose_tool(p, radius) : flat_pose_tool(p, radius)); };
  if (path.size() == 1) { add_pose(path.front()); return tools; }
  for (std::size_t i = 0; i + 1 < path.size(); ++i)
  {
    const Pose& a = path[i]; const Pose& b = path[i + 1]; const int steps = std::max(1, static_cast<int>(std::ceil(distance3(a, b) / spacing)));
    for (int step = 0; step <= steps; ++step)
    {
      const double t = static_cast<double>(step) / static_cast<double>(steps);
      add_pose({a.x + (b.x - a.x) * t, a.y + (b.y - a.y) * t, a.z + (b.z - a.z) * t});
    }
  }
  return tools;
}

CaseSpec make_case(const std::string& id)
{
  CaseSpec spec; spec.id = id;
  if (id == "drill-explicit") { spec.tool = ToolKind::Drill; spec.radius = 2.0; spec.paths = {{{20.0,15.0,12.0},{20.0,15.0,4.0}}}; }
  else if (id == "slot-clean") { spec.radius = 2.5; spec.paths = {{{5.0,15.0,7.0},{35.0,15.0,7.0}}}; }
  else if (id == "overlapping-slots") { spec.radius = 2.5; spec.paths = {{{5.0,13.0,7.0},{35.0,13.0,7.0}},{{5.0,16.0,7.0},{35.0,16.0,7.0}}}; }
  else if (id == "face-skim-zero") { spec.radius = 5.0; spec.paths = {{{5.0,15.0,10.0},{35.0,15.0,10.0}}}; }
  else if (id == "face-skim-positive") { spec.radius = 5.0; spec.paths = {{{5.0,15.0,9.9},{35.0,15.0,9.9}}}; }
  else if (id == "plunge-1um") { spec.radius = 2.5; spec.paths = {{{20.0,15.0,12.0},{20.0,15.0,9.999999}}}; }
  else if (id == "self-cross") { spec.radius = 2.0; spec.paths = {{{8.0,8.0,7.0},{32.0,22.0,7.0},{8.0,22.0,7.0},{32.0,8.0,7.0}}}; }
  else if (id == "retrace-exact") { spec.radius = 2.5; spec.paths = {{{5.0,15.0,7.0},{35.0,15.0,7.0},{5.0,15.0,7.0}}}; }
  else if (id == "retrace-jitter") { spec.radius = 2.5; spec.paths = {{{5.0,15.0,7.0},{35.0,15.0,7.0}},{{35.0,15.001,7.0},{5.0,15.001,7.0}}}; }
  else if (id == "tangent-zero") { spec.radius = 2.5; spec.paths = {{{-5.0,-2.5,7.0},{15.0,-2.5,7.0}}}; }
  else if (id == "tangent-overlap") { spec.radius = 2.5; spec.paths = {{{-5.0,-2.499,7.0},{15.0,-2.499,7.0}}}; }
  else if (id == "stationary-engaged") { spec.radius = 2.5; std::vector<Pose> p; for (int i=0;i<11;++i) p.push_back({20.0,15.0,7.0}); spec.paths = {p}; }
  else if (id == "ball-path") { spec.tool = ToolKind::Ball; spec.radius = 2.0; spec.paths = {{{5.0,15.0,9.0},{35.0,15.0,9.0}}}; }
  else if (id == "cut-through") { spec.radius = 1.5; spec.paths = {{{20.0,-5.0,-0.1},{20.0,35.0,-0.1}}}; }
  else if (id == "high-segment-line") { spec.radius = 2.0; std::vector<Pose> p; constexpr int segments=50; for(int i=0;i<=segments;++i) p.push_back({5.0+30.0*static_cast<double>(i)/segments,15.0,7.0}); spec.paths={p}; }
  else throw std::runtime_error("unknown case: " + id);
  return spec;
}

struct StepResult
{
  bool attempted=false; std::string transfer_status="not_attempted", write_status="not_attempted", read_status="not_attempted";
  bool readback_transferred=false, serialized_ap242=false, serialized_mm=false; Metrics readback; double volume_delta_mm3=0.0, bbox_delta_mm=0.0; std::string error;
};
std::string read_text(const std::filesystem::path& path) { std::ifstream in(path,std::ios::binary); std::ostringstream out; out<<in.rdbuf(); return out.str(); }
double bbox_delta(const Metrics& a,const Metrics& b) { return std::max({std::abs(a.xmin-b.xmin),std::abs(a.ymin-b.ymin),std::abs(a.zmin-b.zmin),std::abs(a.xmax-b.xmax),std::abs(a.ymax-b.ymax),std::abs(a.zmax-b.zmax)}); }

StepResult step_roundtrip(const TopoDS_Shape& shape,const std::filesystem::path& path)
{
  StepResult result; result.attempted=true;
  try
  {
    DESTEP_Parameters params; params.WriteSchema=DESTEP_Parameters::WriteMode_StepSchema_AP242DIS; params.WriteTessellated=DESTEP_Parameters::RWMode_Tessellated_Off; params.WriteModelType=STEPControl_ManifoldSolidBrep; params.WriteAssembly=DESTEP_Parameters::WriteMode_Assembly_Auto; params.WriteUnit=UnitsMethods_LengthUnit_Millimeter;
    STEPControl_Writer writer; const auto solids=collect_solids(shape); if(solids.empty()) throw std::runtime_error("STEP export requires at least one solid");
    IFSelect_ReturnStatus aggregate=IFSelect_RetDone; for(const TopoDS_Solid& solid:solids){const auto status=writer.Transfer(solid,STEPControl_ManifoldSolidBrep,params,true); if(status!=IFSelect_RetDone){aggregate=status;break;}}
    result.transfer_status=status_name(aggregate); if(aggregate!=IFSelect_RetDone) return result;
    const auto write_status=writer.Write(path.string().c_str()); result.write_status=status_name(write_status); if(write_status!=IFSelect_RetDone) return result;
    const std::string serialized=read_text(path); result.serialized_ap242=serialized.find("AP242")!=std::string::npos; result.serialized_mm=serialized.find("MILLI")!=std::string::npos&&serialized.find("METRE")!=std::string::npos;
    STEPControl_Reader reader; const auto read_status=reader.ReadFile(path.string().c_str()); result.read_status=status_name(read_status); if(read_status!=IFSelect_RetDone) return result;
    result.readback_transferred=reader.TransferRoots()>0; if(!result.readback_transferred) return result; result.readback=measure(reader.OneShape()); const Metrics before=measure(shape); result.volume_delta_mm3=result.readback.volume_mm3-before.volume_mm3; result.bbox_delta_mm=bbox_delta(result.readback,before);
  }
  catch(const Standard_Failure& f){result.error=f.GetMessageString()?f.GetMessageString():"OCCT STEP failure";} catch(const std::exception& f){result.error=f.what();}
  return result;
}

std::string step_json(const StepResult& s)
{
  std::ostringstream out; out<<std::setprecision(17)<<"{"<<"\"attempted\":"<<(s.attempted?"true":"false")<<",\"transfer_status\":"<<quote(s.transfer_status)<<",\"write_status\":"<<quote(s.write_status)<<",\"read_status\":"<<quote(s.read_status)<<",\"readback_transferred\":"<<(s.readback_transferred?"true":"false")<<",\"serialized_ap242\":"<<(s.serialized_ap242?"true":"false")<<",\"serialized_mm\":"<<(s.serialized_mm?"true":"false")<<",\"readback\":"<<metrics_json(s.readback)<<",\"volume_delta_mm3\":"<<s.volume_delta_mm3<<",\"bbox_delta_mm\":"<<s.bbox_delta_mm<<",\"error\":"<<quote(s.error)<<"}"; return out.str();
}

struct RunResult { TopoDS_Shape shape; int material_booleans=0,envelope_primitives=0,input_segments=0,canonical_segments=0; double approximation_bound_mm=0.0; std::vector<std::string> reports; };
int segment_count(const std::vector<std::vector<Pose>>& paths){int total=0;for(const auto& path:paths) total+=path.size()>1?static_cast<int>(path.size()-1):1;return total;}

RunResult execute_strategy(const CaseSpec& spec,const std::string& strategy)
{
  RunResult result; result.shape=BRepPrimAPI_MakeBox(kStockX,kStockY,kStockZ).Shape(); result.input_segments=segment_count(spec.paths);
  auto exact_tools_for=[&](const std::vector<Pose>& path){return exact_envelope_for_path(path,spec.tool,spec.radius);};
  if(strategy=="explicit_analytic")
  {
    std::vector<TopoDS_Shape> tools; for(const auto& path:spec.paths){auto part=exact_tools_for(simplify_path(path));tools.insert(tools.end(),part.begin(),part.end());}
    result.envelope_primitives=static_cast<int>(tools.size()); result.canonical_segments=segment_count(spec.paths); std::string report; result.shape=cut_many(result.shape,tools,report); result.reports.push_back(report); result.material_booleans=tools.empty()?0:1;
  }
  else if(strategy=="segment_sweep")
  {
    for(const auto& path:spec.paths)
    {
      if(path.size()==1){auto tools=exact_tools_for(path);result.envelope_primitives+=static_cast<int>(tools.size());std::string report;result.shape=cut_many(result.shape,tools,report);result.reports.push_back(report);++result.material_booleans;++result.canonical_segments;continue;}
      for(std::size_t i=0;i+1<path.size();++i){std::vector<Pose> segment{path[i],path[i+1]};auto tools=exact_tools_for(segment);result.envelope_primitives+=static_cast<int>(tools.size());std::string report;result.shape=cut_many(result.shape,tools,report);result.reports.push_back(report);++result.material_booleans;++result.canonical_segments;}
    }
  }
  else if(strategy=="canonical_batch"||strategy=="freehand_batch")
  {
    std::vector<TopoDS_Shape> tools; for(const auto& original:spec.paths){const auto path=strategy=="canonical_batch"?simplify_path(original):original;result.canonical_segments+=path.size()>1?static_cast<int>(path.size()-1):1;auto part=exact_tools_for(path);result.envelope_primitives+=static_cast<int>(part.size());tools.insert(tools.end(),part.begin(),part.end());}
    std::string report; result.shape=cut_many(result.shape,tools,report); result.reports.push_back(report); result.material_booleans=tools.empty()?0:1;
  }
  else if(strategy=="sampled_fallback")
  {
    constexpr double spacing=0.25; std::vector<TopoDS_Shape> tools; for(const auto& path:spec.paths){result.canonical_segments+=path.size()>1?static_cast<int>(path.size()-1):1;auto part=sampled_envelope_for_path(path,spec.tool,spec.radius,spacing);result.envelope_primitives+=static_cast<int>(part.size());tools.insert(tools.end(),part.begin(),part.end());}
    std::string report;result.shape=cut_many(result.shape,tools,report);result.reports.push_back(report);result.material_booleans=tools.empty()?0:1;const double half=spacing*0.5;result.approximation_bound_mm=spec.radius>half?spec.radius-std::sqrt(spec.radius*spec.radius-half*half):spacing;
  }
  else throw std::runtime_error("unknown strategy: "+strategy);
  return result;
}

std::string reports_json(const std::vector<std::string>& reports){std::ostringstream out;out<<"[";for(std::size_t i=0;i<reports.size();++i){if(i)out<<",";out<<quote(reports[i]);}out<<"]";return out.str();}
void usage(){std::cerr<<"usage: rcs011_mill_worker --case ID --strategy ID [--step PATH]\n";}
}

int main(int argc,char** argv)
{
  std::string case_id,strategy; std::filesystem::path step_path; bool do_step=false;
  for(int i=1;i<argc;++i){const std::string arg=argv[i];if(arg=="--case"&&i+1<argc)case_id=argv[++i];else if(arg=="--strategy"&&i+1<argc)strategy=argv[++i];else if(arg=="--step"&&i+1<argc){step_path=argv[++i];do_step=true;}else{usage();return 64;}}
  if(case_id.empty()||strategy.empty()){usage();return 64;}
  const auto started=std::chrono::steady_clock::now();
  try
  {
    const std::string runtime_version=OCC_VERSION_COMPLETE; if(runtime_version!=kExpectedOcctVersion) throw std::runtime_error("OCCT runtime version "+runtime_version+" != expected "+kExpectedOcctVersion);
    const CaseSpec spec=make_case(case_id); RunResult run=execute_strategy(spec,strategy); const Metrics metrics=measure(run.shape); StepResult step;
    if(do_step){std::filesystem::create_directories(step_path.parent_path());step=step_roundtrip(run.shape,step_path);}
    const auto elapsed=std::chrono::duration<double,std::milli>(std::chrono::steady_clock::now()-started);
    std::cout<<std::setprecision(17)<<"{"<<"\"schema\":\"rcs-011-worker/1.0\","<<"\"occt_version\":"<<quote(runtime_version)<<",\"occt_commit\":"<<quote(kExpectedOcctCommit)<<",\"case_id\":"<<quote(case_id)<<",\"strategy\":"<<quote(strategy)<<",\"success\":true,\"error\":\"\","<<"\"input_segments\":"<<run.input_segments<<",\"canonical_segments\":"<<run.canonical_segments<<",\"material_booleans\":"<<run.material_booleans<<",\"envelope_primitives\":"<<run.envelope_primitives<<",\"approximation_bound_mm\":"<<run.approximation_bound_mm<<",\"runtime_ms\":"<<elapsed.count()<<",\"peak_rss_kb\":"<<max_rss_kb()<<",\"geometry\":"<<metrics_json(metrics)<<",\"step\":"<<step_json(step)<<",\"reports\":"<<reports_json(run.reports)<<"}\n"; return 0;
  }
  catch(const Standard_Failure& f){const auto elapsed=std::chrono::duration<double,std::milli>(std::chrono::steady_clock::now()-started);const std::string error=f.GetMessageString()?f.GetMessageString():"OCCT Standard_Failure";std::cout<<"{\"schema\":\"rcs-011-worker/1.0\",\"case_id\":"<<quote(case_id)<<",\"strategy\":"<<quote(strategy)<<",\"success\":false,\"runtime_ms\":"<<elapsed.count()<<",\"error\":"<<quote(error)<<"}\n";return 2;}
  catch(const std::exception& f){const auto elapsed=std::chrono::duration<double,std::milli>(std::chrono::steady_clock::now()-started);std::cout<<"{\"schema\":\"rcs-011-worker/1.0\",\"case_id\":"<<quote(case_id)<<",\"strategy\":"<<quote(strategy)<<",\"success\":false,\"runtime_ms\":"<<elapsed.count()<<",\"error\":"<<quote(f.what())<<"}\n";return 2;}
}
