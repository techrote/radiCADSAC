#include <BRepAlgoAPI_Cut.hxx>
#include <BRepCheck_Analyzer.hxx>
#include <BRepGProp.hxx>
#include <BRepPrimAPI_MakeCylinder.hxx>
#include <GProp_GProps.hxx>
#include <NCollection_List.hxx>
#include <Standard_Failure.hxx>
#include <Standard_Version.hxx>
#include <TopAbs_ShapeEnum.hxx>
#include <TopExp_Explorer.hxx>
#include <TopoDS_Shape.hxx>
#include <gp_Ax2.hxx>
#include <gp_Dir.hxx>
#include <gp_Pnt.hxx>

#include <algorithm>
#include <chrono>
#include <cmath>
#include <iomanip>
#include <iostream>
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
constexpr double kStockRadiusMm = 20.0;
constexpr double kStockLengthMm = 60.0;
constexpr double kToolOuterRadiusMm = 25.0;

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

int count_subshapes(const TopoDS_Shape& shape, TopAbs_ShapeEnum type)
{
  int count = 0;
  for (TopExp_Explorer explorer(shape, type); explorer.More(); explorer.Next())
  {
    ++count;
  }
  return count;
}

struct Metrics
{
  bool valid = false;
  int solids = 0;
  int faces = 0;
  int edges = 0;
  double volume_mm3 = 0.0;
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
  GProp_GProps props;
  BRepGProp::VolumeProperties(shape, props);
  metrics.volume_mm3 = props.Mass();
  return metrics;
}

TopoDS_Shape boolean_cut(const TopoDS_Shape& object,
                         const TopoDS_Shape& tool,
                         double fuzzy_mm)
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
  if (!cut.IsDone() || cut.HasErrors() || cut.Shape().IsNull())
  {
    std::ostringstream report;
    if (cut.HasErrors()) cut.DumpErrors(report);
    if (cut.HasWarnings()) cut.DumpWarnings(report);
    throw std::runtime_error("OCCT Boolean cut failed: " + report.str());
  }
  return cut.Shape();
}

TopoDS_Shape annular_tool(double target_radius_mm, double fuzzy_mm)
{
  if (!(target_radius_mm > 0.0 && target_radius_mm < kToolOuterRadiusMm))
  {
    throw std::runtime_error("target radius out of range");
  }
  const gp_Ax2 axis(gp_Pnt(0, 0, 0), gp_Dir(0, 0, 1));
  const TopoDS_Shape outer =
    BRepPrimAPI_MakeCylinder(axis, kToolOuterRadiusMm, kStockLengthMm).Shape();
  const TopoDS_Shape inner =
    BRepPrimAPI_MakeCylinder(axis, target_radius_mm, kStockLengthMm).Shape();
  return boolean_cut(outer, inner, fuzzy_mm);
}

struct Args
{
  std::string mode;
  std::string order = "ascending";
  int repeat_count = 1;
  double depth_mm = 0.001;
  double increment_mm = 0.00001;
  double fuzzy_mm = 0.0;
};

Args parse_args(int argc, char** argv)
{
  Args args;
  for (int i = 1; i < argc; ++i)
  {
    const std::string token = argv[i];
    auto require_value = [&](const char* name) -> std::string
    {
      if (i + 1 >= argc)
      {
        throw std::runtime_error(std::string(name) + " requires a value");
      }
      return argv[++i];
    };

    if (token == "--mode")
    {
      args.mode = require_value("--mode");
    }
    else if (token == "--order")
    {
      args.order = require_value("--order");
    }
    else if (token == "--repeat-count")
    {
      args.repeat_count = std::stoi(require_value("--repeat-count"));
    }
    else if (token == "--depth-mm")
    {
      args.depth_mm = std::stod(require_value("--depth-mm"));
    }
    else if (token == "--increment-mm")
    {
      args.increment_mm = std::stod(require_value("--increment-mm"));
    }
    else if (token == "--fuzzy-mm")
    {
      args.fuzzy_mm = std::stod(require_value("--fuzzy-mm"));
    }
    else
    {
      throw std::runtime_error("unknown argument: " + token);
    }
  }

  if (args.mode != "repeated" && args.mode != "chain")
  {
    throw std::runtime_error("--mode must be repeated or chain");
  }
  if (args.repeat_count < 1 || args.repeat_count > 10000)
  {
    throw std::runtime_error("--repeat-count out of range");
  }
  if (args.fuzzy_mm < 0.0)
  {
    throw std::runtime_error("--fuzzy-mm must be non-negative");
  }
  if (args.mode == "repeated" && !(args.depth_mm > 0.0 && args.depth_mm < kStockRadiusMm))
  {
    throw std::runtime_error("--depth-mm out of range");
  }
  if (args.mode == "chain")
  {
    if (!(args.increment_mm > 0.0))
    {
      throw std::runtime_error("--increment-mm must be positive");
    }
    if (args.increment_mm * args.repeat_count >= kStockRadiusMm)
    {
      throw std::runtime_error("chain removes entire stock radius");
    }
    if (args.order != "ascending" && args.order != "descending")
    {
      throw std::runtime_error("--order must be ascending or descending");
    }
  }
  return args;
}

std::vector<int> order_indices(const Args& args)
{
  std::vector<int> indices;
  indices.reserve(static_cast<std::size_t>(args.repeat_count));
  for (int i = 1; i <= args.repeat_count; ++i)
  {
    indices.push_back(i);
  }
  if (args.order == "descending")
  {
    std::reverse(indices.begin(), indices.end());
  }
  return indices;
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

    const Args args = parse_args(argc, argv);
    const gp_Ax2 axis(gp_Pnt(0, 0, 0), gp_Dir(0, 0, 1));
    const TopoDS_Shape stock =
      BRepPrimAPI_MakeCylinder(axis, kStockRadiusMm, kStockLengthMm).Shape();
    TopoDS_Shape current = stock;
    int boolean_operations = 0;

    const auto started = std::chrono::steady_clock::now();

    double final_radius_mm = kStockRadiusMm;
    if (args.mode == "repeated")
    {
      final_radius_mm = kStockRadiusMm - args.depth_mm;
      const TopoDS_Shape tool = annular_tool(final_radius_mm, args.fuzzy_mm);
      ++boolean_operations;
      for (int i = 0; i < args.repeat_count; ++i)
      {
        current = boolean_cut(current, tool, args.fuzzy_mm);
        ++boolean_operations;
      }
    }
    else
    {
      final_radius_mm = kStockRadiusMm - args.increment_mm * args.repeat_count;
      for (const int index : order_indices(args))
      {
        const double target_radius = kStockRadiusMm - args.increment_mm * index;
        const TopoDS_Shape tool = annular_tool(target_radius, args.fuzzy_mm);
        ++boolean_operations;
        current = boolean_cut(current, tool, args.fuzzy_mm);
        ++boolean_operations;
      }
    }

    const auto finished = std::chrono::steady_clock::now();
    const double geometry_ms =
      std::chrono::duration<double, std::milli>(finished - started).count();

    const Metrics metrics = measure(current);
    const double expected_volume_mm3 =
      3.141592653589793238462643383279502884 *
      final_radius_mm * final_radius_mm * kStockLengthMm;
    const double volume_abs_error_mm3 =
      std::abs(metrics.volume_mm3 - expected_volume_mm3);

    std::ostringstream out;
    out << std::setprecision(17);
    out << "{"
        << "\"worker_schema\":\"rcs-007-finish-worker/1.0\","
        << "\"backend\":{"
        << "\"id\":\"occt\","
        << "\"version\":" << quote(OCC_VERSION_COMPLETE) << ","
        << "\"expected_commit\":" << quote(kExpectedOcctCommit) << ","
        << "\"run_parallel\":false,"
        << "\"non_destructive\":true},"
        << "\"mode\":" << quote(args.mode) << ","
        << "\"order\":" << quote(args.order) << ","
        << "\"repeat_count\":" << args.repeat_count << ","
        << "\"depth_mm\":" << args.depth_mm << ","
        << "\"increment_mm\":" << args.increment_mm << ","
        << "\"fuzzy_mm\":" << args.fuzzy_mm << ","
        << "\"boolean_operations\":" << boolean_operations << ","
        << "\"final_radius_mm\":" << final_radius_mm << ","
        << "\"valid_brep\":" << (metrics.valid ? "true" : "false") << ","
        << "\"solids\":" << metrics.solids << ","
        << "\"faces\":" << metrics.faces << ","
        << "\"edges\":" << metrics.edges << ","
        << "\"volume_mm3\":" << metrics.volume_mm3 << ","
        << "\"expected_volume_mm3\":" << expected_volume_mm3 << ","
        << "\"volume_abs_error_mm3\":" << volume_abs_error_mm3 << ","
        << "\"geometry_ms\":" << geometry_ms << ","
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
}
