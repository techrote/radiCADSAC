#include <BRepAdaptor_Surface.hxx>
#include <BRepAlgoAPI_Cut.hxx>
#include <BRepAlgoAPI_Fuse.hxx>
#include <BRepBndLib.hxx>
#include <BRepCheck_Analyzer.hxx>
#include <BRepGProp.hxx>
#include <BRepPrimAPI_MakeBox.hxx>
#include <BRepPrimAPI_MakeCylinder.hxx>
#include <BRepTools_History.hxx>
#include <Bnd_Box.hxx>
#include <GProp_GProps.hxx>
#include <NCollection_List.hxx>
#include <ShapeUpgrade_UnifySameDomain.hxx>
#include <Standard_Failure.hxx>
#include <Standard_Version.hxx>
#include <TopAbs_ShapeEnum.hxx>
#include <TopExp_Explorer.hxx>
#include <TopoDS.hxx>
#include <TopoDS_Face.hxx>
#include <TopoDS_Shape.hxx>
#include <gp_Ax2.hxx>
#include <gp_Dir.hxx>
#include <gp_Pnt.hxx>

#include <algorithm>
#include <chrono>
#include <cmath>
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

std::string quote(const std::string& value)
{
  std::ostringstream out;
  out << '"';
  for (const unsigned char ch : value)
  {
    switch (ch)
    {
      case '"': out << "\\\""; break;
      case '\\': out << "\\\\"; break;
      case '\n': out << "\\n"; break;
      case '\r': out << "\\r"; break;
      case '\t': out << "\\t"; break;
      default: out << static_cast<char>(ch); break;
    }
  }
  out << '"';
  return out.str();
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

int count_subshapes(const TopoDS_Shape& shape, const TopAbs_ShapeEnum type)
{
  int count = 0;
  for (TopExp_Explorer explorer(shape, type); explorer.More(); explorer.Next())
  {
    ++count;
  }
  return count;
}

std::vector<TopoDS_Shape> subshapes(const TopoDS_Shape& shape, const TopAbs_ShapeEnum type)
{
  std::vector<TopoDS_Shape> result;
  for (TopExp_Explorer explorer(shape, type); explorer.More(); explorer.Next())
  {
    result.push_back(explorer.Current());
  }
  return result;
}

struct Metrics
{
  bool valid = false;
  int solids = 0;
  int faces = 0;
  int edges = 0;
  double volume_mm3 = 0.0;
  double area_mm2 = 0.0;
  double xmin = 0.0;
  double ymin = 0.0;
  double zmin = 0.0;
  double xmax = 0.0;
  double ymax = 0.0;
  double zmax = 0.0;
  std::map<int, int> surface_types;
};

Metrics measure(const TopoDS_Shape& shape)
{
  Metrics metrics;
  if (shape.IsNull())
  {
    return metrics;
  }

  BRepCheck_Analyzer analyzer(shape, true, false, true);
  metrics.valid = analyzer.IsValid();
  metrics.solids = count_subshapes(shape, TopAbs_SOLID);
  metrics.faces = count_subshapes(shape, TopAbs_FACE);
  metrics.edges = count_subshapes(shape, TopAbs_EDGE);

  GProp_GProps volume_props;
  BRepGProp::VolumeProperties(shape, volume_props);
  metrics.volume_mm3 = volume_props.Mass();

  GProp_GProps area_props;
  BRepGProp::SurfaceProperties(shape, area_props);
  metrics.area_mm2 = area_props.Mass();

  Bnd_Box box;
  BRepBndLib::Add(shape, box);
  if (!box.IsVoid())
  {
    box.Get(metrics.xmin, metrics.ymin, metrics.zmin,
            metrics.xmax, metrics.ymax, metrics.zmax);
  }

  for (const TopoDS_Shape& item : subshapes(shape, TopAbs_FACE))
  {
    const TopoDS_Face face = TopoDS::Face(item);
    BRepAdaptor_Surface surface(face, true);
    ++metrics.surface_types[static_cast<int>(surface.GetType())];
  }
  return metrics;
}

bool metric_equivalent(const Metrics& a, const Metrics& b)
{
  constexpr double kVolumeTol = 1.0e-8;
  constexpr double kAreaTol = 1.0e-8;
  constexpr double kBoundTol = 1.0e-9;
  return a.valid == b.valid
      && a.solids == b.solids
      && a.faces == b.faces
      && a.edges == b.edges
      && std::abs(a.volume_mm3 - b.volume_mm3) <= kVolumeTol
      && std::abs(a.area_mm2 - b.area_mm2) <= kAreaTol
      && std::abs(a.xmin - b.xmin) <= kBoundTol
      && std::abs(a.ymin - b.ymin) <= kBoundTol
      && std::abs(a.zmin - b.zmin) <= kBoundTol
      && std::abs(a.xmax - b.xmax) <= kBoundTol
      && std::abs(a.ymax - b.ymax) <= kBoundTol
      && std::abs(a.zmax - b.zmax) <= kBoundTol
      && a.surface_types == b.surface_types;
}

int same_face_matches(const TopoDS_Shape& a, const TopoDS_Shape& b)
{
  const std::vector<TopoDS_Shape> a_faces = subshapes(a, TopAbs_FACE);
  const std::vector<TopoDS_Shape> b_faces = subshapes(b, TopAbs_FACE);
  int matches = 0;
  for (const TopoDS_Shape& af : a_faces)
  {
    for (const TopoDS_Shape& bf : b_faces)
    {
      if (af.IsSame(bf))
      {
        ++matches;
        break;
      }
    }
  }
  return matches;
}

struct OperationResult
{
  TopoDS_Shape shape;
  occ::handle<BRepTools_History> history;
};

OperationResult cut_shape(const TopoDS_Shape& object, const TopoDS_Shape& tool)
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
  cut.SetToFillHistory(true);
  cut.Build();
  if (!cut.IsDone() || cut.HasErrors() || cut.Shape().IsNull())
  {
    std::ostringstream report;
    if (cut.HasErrors()) cut.DumpErrors(report);
    if (cut.HasWarnings()) cut.DumpWarnings(report);
    throw std::runtime_error("OCCT cut failed: " + report.str());
  }
  return {cut.Shape(), cut.History()};
}

OperationResult fuse_shape(const TopoDS_Shape& a, const TopoDS_Shape& b)
{
  BRepAlgoAPI_Fuse fuse;
  NCollection_List<TopoDS_Shape> objects;
  NCollection_List<TopoDS_Shape> tools;
  objects.Append(a);
  tools.Append(b);
  fuse.SetArguments(objects);
  fuse.SetTools(tools);
  fuse.SetNonDestructive(true);
  fuse.SetRunParallel(false);
  fuse.SetFuzzyValue(0.0);
  fuse.SetToFillHistory(true);
  fuse.Build();
  if (!fuse.IsDone() || fuse.HasErrors() || fuse.Shape().IsNull())
  {
    std::ostringstream report;
    if (fuse.HasErrors()) fuse.DumpErrors(report);
    if (fuse.HasWarnings()) fuse.DumpWarnings(report);
    throw std::runtime_error("OCCT fuse failed: " + report.str());
  }
  return {fuse.Shape(), fuse.History()};
}

struct HistoryStats
{
  int source_faces = 0;
  int modified_face_relations = 0;
  int generated_face_relations = 0;
  int removed_source_faces = 0;
  int one_to_many_source_faces = 0;
  int many_to_one_descendants = 0;
  int identity_preserved_source_faces = 0;
};

HistoryStats history_stats(const TopoDS_Shape& source,
                           const TopoDS_Shape& result,
                           const occ::handle<BRepTools_History>& history)
{
  HistoryStats stats;
  const std::vector<TopoDS_Shape> sources = subshapes(source, TopAbs_FACE);
  const std::vector<TopoDS_Shape> result_faces = subshapes(result, TopAbs_FACE);
  stats.source_faces = static_cast<int>(sources.size());

  std::vector<std::vector<TopoDS_Shape>> descendants;
  descendants.resize(sources.size());

  for (std::size_t i = 0; i < sources.size(); ++i)
  {
    const TopoDS_Shape& src = sources[i];
    for (const TopoDS_Shape& dst : result_faces)
    {
      if (src.IsSame(dst))
      {
        ++stats.identity_preserved_source_faces;
        break;
      }
    }

    if (history.IsNull())
    {
      continue;
    }
    if (history->IsRemoved(src))
    {
      ++stats.removed_source_faces;
    }

    const NCollection_List<TopoDS_Shape>& modified = history->Modified(src);
    for (NCollection_List<TopoDS_Shape>::Iterator it(modified); it.More(); it.Next())
    {
      if (it.Value().ShapeType() == TopAbs_FACE)
      {
        ++stats.modified_face_relations;
        descendants[i].push_back(it.Value());
      }
    }

    const NCollection_List<TopoDS_Shape>& generated = history->Generated(src);
    for (NCollection_List<TopoDS_Shape>::Iterator it(generated); it.More(); it.Next())
    {
      if (it.Value().ShapeType() == TopAbs_FACE)
      {
        ++stats.generated_face_relations;
        descendants[i].push_back(it.Value());
      }
    }
    if (descendants[i].size() > 1)
    {
      ++stats.one_to_many_source_faces;
    }
  }

  std::vector<TopoDS_Shape> counted_many_to_one;
  for (std::size_t i = 0; i < descendants.size(); ++i)
  {
    for (const TopoDS_Shape& child : descendants[i])
    {
      bool has_other_parent = false;
      for (std::size_t j = 0; j < descendants.size() && !has_other_parent; ++j)
      {
        if (i == j) continue;
        for (const TopoDS_Shape& other_child : descendants[j])
        {
          if (child.IsSame(other_child))
          {
            has_other_parent = true;
            break;
          }
        }
      }
      if (has_other_parent)
      {
        bool already = false;
        for (const TopoDS_Shape& counted : counted_many_to_one)
        {
          if (child.IsSame(counted))
          {
            already = true;
            break;
          }
        }
        if (!already)
        {
          counted_many_to_one.push_back(child);
          ++stats.many_to_one_descendants;
        }
      }
    }
  }
  return stats;
}

void write_surface_histogram(std::ostream& out, const std::map<int, int>& histogram)
{
  out << "{";
  bool first = true;
  for (const auto& item : histogram)
  {
    if (!first) out << ',';
    first = false;
    out << quote(std::to_string(item.first)) << ':' << item.second;
  }
  out << "}";
}

void write_metrics(std::ostream& out, const Metrics& m)
{
  out << "{"
      << "\"valid_brep\":" << (m.valid ? "true" : "false") << ','
      << "\"solids\":" << m.solids << ','
      << "\"faces\":" << m.faces << ','
      << "\"edges\":" << m.edges << ','
      << "\"volume_mm3\":" << m.volume_mm3 << ','
      << "\"area_mm2\":" << m.area_mm2 << ','
      << "\"bounds_mm\":[" << m.xmin << ',' << m.ymin << ',' << m.zmin << ','
      << m.xmax << ',' << m.ymax << ',' << m.zmax << "],"
      << "\"surface_types\":";
  write_surface_histogram(out, m.surface_types);
  out << "}";
}

void write_history_stats(std::ostream& out, const HistoryStats& h)
{
  out << "{"
      << "\"source_faces\":" << h.source_faces << ','
      << "\"modified_face_relations\":" << h.modified_face_relations << ','
      << "\"generated_face_relations\":" << h.generated_face_relations << ','
      << "\"removed_source_faces\":" << h.removed_source_faces << ','
      << "\"one_to_many_source_faces\":" << h.one_to_many_source_faces << ','
      << "\"many_to_one_descendants\":" << h.many_to_one_descendants << ','
      << "\"identity_preserved_source_faces\":" << h.identity_preserved_source_faces
      << "}";
}

TopoDS_Shape lathe_stock()
{
  const gp_Ax2 axis(gp_Pnt(0, 0, 0), gp_Dir(0, 0, 1));
  return BRepPrimAPI_MakeCylinder(axis, 20.0, 60.0).Shape();
}

TopoDS_Shape annular_tool(const double target_radius)
{
  const gp_Ax2 axis(gp_Pnt(0, 0, 0), gp_Dir(0, 0, 1));
  const TopoDS_Shape outer = BRepPrimAPI_MakeCylinder(axis, 25.0, 60.0).Shape();
  const TopoDS_Shape inner = BRepPrimAPI_MakeCylinder(axis, target_radius, 60.0).Shape();
  return cut_shape(outer, inner).shape;
}

std::string run_replay_cut()
{
  const TopoDS_Shape stock_a = BRepPrimAPI_MakeBox(40.0, 30.0, 20.0).Shape();
  const TopoDS_Shape tool_a = BRepPrimAPI_MakeBox(gp_Pnt(5.0, 7.0, 8.0), 30.0, 16.0, 15.0).Shape();
  const OperationResult result_a = cut_shape(stock_a, tool_a);

  const TopoDS_Shape stock_b = BRepPrimAPI_MakeBox(40.0, 30.0, 20.0).Shape();
  const TopoDS_Shape tool_b = BRepPrimAPI_MakeBox(gp_Pnt(5.0, 7.0, 8.0), 30.0, 16.0, 15.0).Shape();
  const OperationResult result_b = cut_shape(stock_b, tool_b);

  const Metrics a = measure(result_a.shape);
  const Metrics b = measure(result_b.shape);
  const bool equivalent = metric_equivalent(a, b);
  const int same_faces = same_face_matches(result_a.shape, result_b.shape);

  std::ostringstream out;
  out << std::setprecision(17)
      << "\"engineering_equivalent\":" << (equivalent ? "true" : "false") << ','
      << "\"same_face_identity_matches\":" << same_faces << ','
      << "\"result_a\":";
  write_metrics(out, a);
  out << ",\"result_b\":";
  write_metrics(out, b);
  return out.str();
}

std::string run_split_cut()
{
  const TopoDS_Shape stock = BRepPrimAPI_MakeBox(40.0, 20.0, 20.0).Shape();
  const TopoDS_Shape tool = BRepPrimAPI_MakeBox(gp_Pnt(19.0, -1.0, -1.0), 2.0, 22.0, 22.0).Shape();
  const OperationResult result = cut_shape(stock, tool);
  const Metrics metrics = measure(result.shape);
  const HistoryStats stats = history_stats(stock, result.shape, result.history);

  std::ostringstream out;
  out << std::setprecision(17) << "\"result\":";
  write_metrics(out, metrics);
  out << ",\"history\":";
  write_history_stats(out, stats);
  return out.str();
}

std::string run_overlap_cuts()
{
  const TopoDS_Shape stock = BRepPrimAPI_MakeBox(50.0, 30.0, 15.0).Shape();
  const TopoDS_Shape first_tool = BRepPrimAPI_MakeBox(gp_Pnt(5.0, 8.0, 8.0), 30.0, 12.0, 10.0).Shape();
  const TopoDS_Shape second_tool = BRepPrimAPI_MakeBox(gp_Pnt(20.0, 8.0, 8.0), 25.0, 12.0, 10.0).Shape();
  const OperationResult first = cut_shape(stock, first_tool);
  const OperationResult second = cut_shape(first.shape, second_tool);
  const Metrics before = measure(first.shape);
  const Metrics after = measure(second.shape);
  const HistoryStats stats = history_stats(first.shape, second.shape, second.history);

  std::ostringstream out;
  out << std::setprecision(17) << "\"before_second_cut\":";
  write_metrics(out, before);
  out << ",\"after_second_cut\":";
  write_metrics(out, after);
  out << ",\"history\":";
  write_history_stats(out, stats);
  return out.str();
}

std::string run_same_domain_merge()
{
  const TopoDS_Shape left = BRepPrimAPI_MakeBox(20.0, 20.0, 10.0).Shape();
  const TopoDS_Shape right = BRepPrimAPI_MakeBox(gp_Pnt(20.0, 0.0, 0.0), 20.0, 20.0, 10.0).Shape();
  const OperationResult fused = fuse_shape(left, right);
  const Metrics before = measure(fused.shape);

  ShapeUpgrade_UnifySameDomain unifier(fused.shape, true, true, false);
  unifier.SetSafeInputMode(true);
  unifier.Build();
  const TopoDS_Shape unified = unifier.Shape();
  if (unified.IsNull())
  {
    throw std::runtime_error("same-domain unification produced null shape");
  }
  const Metrics after = measure(unified);
  const HistoryStats stats = history_stats(fused.shape, unified, unifier.History());

  std::ostringstream out;
  out << std::setprecision(17) << "\"before_unify\":";
  write_metrics(out, before);
  out << ",\"after_unify\":";
  write_metrics(out, after);
  out << ",\"history\":";
  write_history_stats(out, stats);
  return out.str();
}

std::string run_repeated_finish()
{
  const TopoDS_Shape stock = lathe_stock();
  const TopoDS_Shape tool = annular_tool(19.999);
  const OperationResult first = cut_shape(stock, tool);
  const OperationResult second = cut_shape(first.shape, tool);
  const Metrics a = measure(first.shape);
  const Metrics b = measure(second.shape);
  const bool equivalent = metric_equivalent(a, b);
  const HistoryStats stats = history_stats(first.shape, second.shape, second.history);

  std::ostringstream out;
  out << std::setprecision(17)
      << "\"engineering_equivalent\":" << (equivalent ? "true" : "false") << ','
      << "\"same_face_identity_matches\":" << same_face_matches(first.shape, second.shape) << ','
      << "\"first_result\":";
  write_metrics(out, a);
  out << ",\"second_result\":";
  write_metrics(out, b);
  out << ",\"history\":";
  write_history_stats(out, stats);
  return out.str();
}

std::string parse_mode(const int argc, char** argv)
{
  for (int i = 1; i < argc; ++i)
  {
    const std::string token = argv[i];
    if (token == "--mode")
    {
      if (i + 1 >= argc) throw std::runtime_error("--mode requires a value");
      return argv[i + 1];
    }
  }
  throw std::runtime_error("--mode is required");
}

} // namespace

int main(int argc, char** argv)
{
  try
  {
    if (std::string(OCC_VERSION_COMPLETE) != kExpectedOcctVersion)
    {
      throw std::runtime_error(std::string("unexpected OCCT runtime version: ") + OCC_VERSION_COMPLETE);
    }

    const std::string mode = parse_mode(argc, argv);
    const auto started = std::chrono::steady_clock::now();
    std::string payload;
    if (mode == "replay_cut") payload = run_replay_cut();
    else if (mode == "split_cut") payload = run_split_cut();
    else if (mode == "overlap_cuts") payload = run_overlap_cuts();
    else if (mode == "same_domain_merge") payload = run_same_domain_merge();
    else if (mode == "repeated_finish") payload = run_repeated_finish();
    else throw std::runtime_error("unsupported mode: " + mode);
    const auto finished = std::chrono::steady_clock::now();
    const double wall_ms = std::chrono::duration<double, std::milli>(finished - started).count();

    std::cout << std::setprecision(17)
              << "{\"worker_schema\":\"rcs-008-provenance-worker/1.0\","
              << "\"backend\":{\"id\":\"occt\",\"version\":" << quote(OCC_VERSION_COMPLETE)
              << ",\"expected_commit\":" << quote(kExpectedOcctCommit)
              << ",\"run_parallel\":false,\"non_destructive\":true},"
              << "\"mode\":" << quote(mode) << ','
              << payload << ','
              << "\"wall_ms\":" << wall_ms << ','
              << "\"max_rss_kb\":" << max_rss_kb() << "}"
              << std::endl;
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
}
