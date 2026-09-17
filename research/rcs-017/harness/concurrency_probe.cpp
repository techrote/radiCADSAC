#include <BOPAlgo_Options.hxx>
#include <BRepAlgoAPI_Cut.hxx>
#include <BRepCheck_Analyzer.hxx>
#include <BRepGProp.hxx>
#include <BRepPrimAPI_MakeBox.hxx>
#include <DESTEP_Parameters.hxx>
#include <GProp_GProps.hxx>
#include <IFSelect_ReturnStatus.hxx>
#include <Standard_Failure.hxx>
#include <Standard_Version.hxx>
#include <STEPControl_Reader.hxx>
#include <STEPControl_Writer.hxx>
#include <TopoDS_Shape.hxx>
#include <UnitsMethods_LengthUnit.hxx>
#include <gp_Pnt.hxx>

#include <algorithm>
#include <atomic>
#include <chrono>
#include <filesystem>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <mutex>
#include <sstream>
#include <stdexcept>
#include <string>
#include <thread>
#include <vector>

namespace {
constexpr const char* kExpectedVersion = "8.0.1";
constexpr const char* kExpectedCommit = "b8f597c677811d1f9f4d8a97f5ae2825c0353a42";

std::string esc(const std::string& s) {
  std::ostringstream o;
  for (char c : s) {
    if (c == '\\' || c == '"') o << '\\' << c;
    else if (c == '\n') o << "\\n";
    else if (c == '\r') o << "\\r";
    else o << c;
  }
  return o.str();
}
std::string q(const std::string& s) { return "\"" + esc(s) + "\""; }

std::string read_file(const std::filesystem::path& p) {
  std::ifstream f(p, std::ios::binary);
  std::ostringstream s; s << f.rdbuf(); return s.str();
}

double volume(const TopoDS_Shape& s) {
  GProp_GProps p; BRepGProp::VolumeProperties(s, p); return p.Mass();
}

struct Result {
  int job = -1;
  int iter = -1;
  bool ok = false;
  std::string config;
  std::string error;
  std::string schema;
  bool inch_marker = false;
  bool mm_marker = false;
  bool valid = false;
  bool instance_parallel = false;
  bool global_parallel_observed = false;
  double source_volume = 0.0;
  double readback_volume = 0.0;
  double cut_volume = 0.0;
  double elapsed_ms = 0.0;
};

std::string schema_excerpt(const std::string& text) {
  std::string upper = text;
  std::transform(upper.begin(), upper.end(), upper.begin(), [](unsigned char c){ return static_cast<char>(std::toupper(c)); });
  auto p = upper.find("FILE_SCHEMA");
  if (p == std::string::npos) return "";
  auto e = upper.find(';', p);
  return text.substr(p, e == std::string::npos ? std::string::npos : e - p + 1);
}

Result run_job(int job, int iter, const std::filesystem::path& out_dir, const TopoDS_Shape& shared_stock) {
  Result r; r.job = job; r.iter = iter;
  const auto started = std::chrono::steady_clock::now();
  try {
    const bool inch = (job % 2) != 0;
    r.config = inch ? "inch-ap203" : "mm-ap242";
    r.instance_parallel = ((job + iter) % 2) != 0;
    r.global_parallel_observed = BOPAlgo_Options::GetParallelMode();
    r.source_volume = volume(shared_stock);

    const TopoDS_Shape tool = BRepPrimAPI_MakeBox(gp_Pnt(10.0, -1.0, -1.0), 5.0, 22.0, 12.0).Shape();
    BRepAlgoAPI_Cut cut;
    cut.SetArguments({shared_stock});
    cut.SetTools({tool});
    cut.SetNonDestructive(true);
    cut.SetRunParallel(r.instance_parallel);
    cut.Build();
    if (!cut.IsDone() || cut.HasErrors() || cut.Shape().IsNull()) throw std::runtime_error("boolean cut failed");
    r.cut_volume = volume(cut.Shape());

    DESTEP_Parameters params;
    params.WriteTessellated = DESTEP_Parameters::RWMode_Tessellated_Off;
    params.WriteModelType = STEPControl_ManifoldSolidBrep;
    params.WritePrecisionMode = DESTEP_Parameters::WriteMode_PrecisionMode_Greatest;
    params.WritePrecisionVal = inch ? 0.001 : 0.00001;
    if (inch) {
      params.WriteUnit = UnitsMethods_LengthUnit_Inch;
      params.WriteSchema = DESTEP_Parameters::WriteMode_StepSchema_AP203;
    } else {
      params.WriteUnit = UnitsMethods_LengthUnit_Millimeter;
      params.WriteSchema = DESTEP_Parameters::WriteMode_StepSchema_AP242DIS;
    }

    STEPControl_Writer writer;
    if (writer.Transfer(cut.Shape(), STEPControl_ManifoldSolidBrep, params, true) != IFSelect_RetDone)
      throw std::runtime_error("STEP transfer failed");
    std::filesystem::create_directories(out_dir);
    const auto path = out_dir / ("job-" + std::to_string(job) + "-iter-" + std::to_string(iter) + ".step");
    if (writer.Write(path.string().c_str()) != IFSelect_RetDone) throw std::runtime_error("STEP write failed");

    const std::string text = read_file(path);
    std::string upper = text;
    std::transform(upper.begin(), upper.end(), upper.begin(), [](unsigned char c){ return static_cast<char>(std::toupper(c)); });
    r.schema = schema_excerpt(text);
    r.inch_marker = upper.find("INCH") != std::string::npos;
    r.mm_marker = upper.find(".MILLI.") != std::string::npos && upper.find(".METRE.") != std::string::npos;

    STEPControl_Reader reader;
    if (reader.ReadFile(path.string().c_str()) != IFSelect_RetDone) throw std::runtime_error("STEP read failed");
    if (reader.TransferRoots() <= 0) throw std::runtime_error("STEP root transfer failed");
    const TopoDS_Shape rb = reader.OneShape();
    r.valid = !rb.IsNull() && BRepCheck_Analyzer(rb, true, false, true).IsValid();
    r.readback_volume = volume(rb);
    r.ok = r.valid;
  } catch (const Standard_Failure& e) {
    r.error = e.GetMessageString() ? e.GetMessageString() : "Standard_Failure";
  } catch (const std::exception& e) {
    r.error = e.what();
  }
  r.elapsed_ms = std::chrono::duration<double, std::milli>(std::chrono::steady_clock::now() - started).count();
  return r;
}

void emit(const Result& r) {
  std::cout << std::setprecision(17)
    << "{\"type\":\"job\",\"occt_version\":" << q(OCC_VERSION_COMPLETE)
    << ",\"occt_commit\":" << q(kExpectedCommit)
    << ",\"job\":" << r.job << ",\"iteration\":" << r.iter
    << ",\"config\":" << q(r.config) << ",\"ok\":" << (r.ok ? "true" : "false")
    << ",\"error\":" << q(r.error) << ",\"schema\":" << q(r.schema)
    << ",\"inch_marker\":" << (r.inch_marker ? "true" : "false")
    << ",\"mm_marker\":" << (r.mm_marker ? "true" : "false")
    << ",\"valid_brep\":" << (r.valid ? "true" : "false")
    << ",\"instance_parallel\":" << (r.instance_parallel ? "true" : "false")
    << ",\"global_parallel_observed\":" << (r.global_parallel_observed ? "true" : "false")
    << ",\"source_volume_mm3\":" << r.source_volume
    << ",\"cut_volume_mm3\":" << r.cut_volume
    << ",\"readback_volume_mm3\":" << r.readback_volume
    << ",\"elapsed_ms\":" << r.elapsed_ms << "}\n";
}

int main(int argc, char** argv) {
  if (std::string(OCC_VERSION_COMPLETE) != kExpectedVersion) {
    std::cerr << "unexpected OCCT version " << OCC_VERSION_COMPLETE << "\n"; return 2;
  }
  std::string mode = "sequential";
  std::filesystem::path out_dir = ".results/rcs017-worker";
  int jobs = 4, iterations = 4;
  for (int i = 1; i < argc; ++i) {
    std::string a = argv[i];
    if (a == "--mode" && i + 1 < argc) mode = argv[++i];
    else if (a == "--jobs" && i + 1 < argc) jobs = std::stoi(argv[++i]);
    else if (a == "--iterations" && i + 1 < argc) iterations = std::stoi(argv[++i]);
    else if (a == "--out-dir" && i + 1 < argc) out_dir = argv[++i];
    else { std::cerr << "bad arg " << a << "\n"; return 2; }
  }

  if (mode == "global-race") {
    std::atomic<int> mismatches{0};
    std::vector<std::thread> threads;
    for (int j = 0; j < jobs; ++j) {
      threads.emplace_back([j, iterations, &mismatches]() {
        for (int i = 0; i < iterations * 100; ++i) {
          const bool desired = ((j + i) % 2) != 0;
          BOPAlgo_Options::SetParallelMode(desired);
          std::this_thread::yield();
          if (BOPAlgo_Options::GetParallelMode() != desired) ++mismatches;
        }
      });
    }
    for (auto& t : threads) t.join();
    std::cout << "{\"type\":\"global_parallel_probe\",\"mismatches\":" << mismatches.load()
              << ",\"attempts\":" << jobs * iterations * 100
              << ",\"final_value\":" << (BOPAlgo_Options::GetParallelMode() ? "true" : "false") << "}\n";
    return 0;
  }

  BOPAlgo_Options::SetParallelMode(false);
  const TopoDS_Shape shared_stock = BRepPrimAPI_MakeBox(gp_Pnt(0, 0, 0), 40.0, 20.0, 10.0).Shape();
  std::vector<Result> results(static_cast<size_t>(jobs * iterations));
  auto one = [&](int j, int i) { results[static_cast<size_t>(j * iterations + i)] = run_job(j, i, out_dir, shared_stock); };

  if (mode == "threads") {
    std::vector<std::thread> threads;
    for (int j = 0; j < jobs; ++j) threads.emplace_back([&, j]() { for (int i = 0; i < iterations; ++i) one(j, i); });
    for (auto& t : threads) t.join();
  } else if (mode == "sequential") {
    for (int j = 0; j < jobs; ++j) for (int i = 0; i < iterations; ++i) one(j, i);
  } else {
    std::cerr << "unknown mode\n"; return 2;
  }

  for (const auto& r : results) emit(r);
  const double final_shared_volume = volume(shared_stock);
  std::cout << "{\"type\":\"summary\",\"mode\":" << q(mode)
            << ",\"jobs\":" << jobs << ",\"iterations\":" << iterations
            << ",\"shared_shape_volume_mm3\":" << final_shared_volume
            << ",\"global_parallel_final\":" << (BOPAlgo_Options::GetParallelMode() ? "true" : "false") << "}\n";
  return 0;
}
