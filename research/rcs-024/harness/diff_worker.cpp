#include <BOPAlgo_Options.hxx>
#include <BRepAlgoAPI_Cut.hxx>
#include <BRepCheck_Analyzer.hxx>
#include <BRepGProp.hxx>
#include <BRepPrimAPI_MakeBox.hxx>
#include <BRepPrimAPI_MakeCylinder.hxx>
#include <DESTEP_Parameters.hxx>
#include <GProp_GProps.hxx>
#include <IFSelect_ReturnStatus.hxx>
#include <NCollection_List.hxx>
#include <Standard_Failure.hxx>
#include <Standard_Version.hxx>
#include <STEPControl_Reader.hxx>
#include <STEPControl_Writer.hxx>
#include <TopoDS_Shape.hxx>
#include <UnitsMethods_LengthUnit.hxx>
#include <gp_Ax2.hxx>
#include <gp_Dir.hxx>
#include <gp_Pnt.hxx>

#include <algorithm>
#include <atomic>
#include <chrono>
#include <cmath>
#include <filesystem>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <sstream>
#include <stdexcept>
#include <string>
#include <thread>
#include <vector>

#ifndef RCS024_EXPECTED_VERSION
#error RCS024_EXPECTED_VERSION must be defined
#endif
#ifndef RCS024_EXPECTED_COMMIT
#error RCS024_EXPECTED_COMMIT must be defined
#endif
#ifndef RCS024_LABEL
#error RCS024_LABEL must be defined
#endif

namespace {
constexpr double PI = 3.141592653589793238462643383279502884;
struct Pose { double x, y, z; };

std::string q(const std::string& s) {
  std::ostringstream o; o << '"';
  for (char c : s) { if (c == '\\' || c == '"') o << '\\'; o << c; }
  o << '"'; return o.str();
}
double volume(const TopoDS_Shape& s) { GProp_GProps p; BRepGProp::VolumeProperties(s,p); return p.Mass(); }
bool valid(const TopoDS_Shape& s) { return !s.IsNull() && BRepCheck_Analyzer(s,true,false,true).IsValid(); }

TopoDS_Shape cut_many(const TopoDS_Shape& object, const std::vector<TopoDS_Shape>& tools, double fuzzy=0.0) {
  BRepAlgoAPI_Cut cut; NCollection_List<TopoDS_Shape> os, ts; os.Append(object); for (const auto& t:tools) ts.Append(t);
  cut.SetArguments(os); cut.SetTools(ts); cut.SetNonDestructive(true); cut.SetRunParallel(false); cut.SetFuzzyValue(fuzzy); cut.Build();
  if (!cut.IsDone() || cut.HasErrors() || cut.Shape().IsNull()) throw std::runtime_error("Boolean cut failed");
  return cut.Shape();
}
TopoDS_Shape cut_one(const TopoDS_Shape& o,const TopoDS_Shape& t,double f=0.0){return cut_many(o,{t},f);}

TopoDS_Shape annular_tool(double target_radius, double fuzzy) {
  const gp_Ax2 ax(gp_Pnt(0,0,0),gp_Dir(0,0,1));
  auto outer=BRepPrimAPI_MakeCylinder(ax,25.0,60.0).Shape();
  auto inner=BRepPrimAPI_MakeCylinder(ax,target_radius,60.0).Shape();
  return cut_one(outer,inner,fuzzy);
}

std::string read_text(const std::filesystem::path& p){std::ifstream f(p,std::ios::binary);std::ostringstream s;s<<f.rdbuf();return s.str();}
double serialized_uncertainty(const std::string& text){
  const std::string key="UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE("; auto b=text.find(key); if(b==std::string::npos)return -1.0;
  b+=key.size(); auto e=text.find(')',b); if(e==std::string::npos)return -1.0; return std::stod(text.substr(b,e-b));
}
struct StepObs { bool ok=false, valid_brep=false; double uncertainty=-1.0, readback_volume=0.0; };
DESTEP_Parameters step_params(bool inch){
  DESTEP_Parameters p; p.WriteTessellated=DESTEP_Parameters::RWMode_Tessellated_Off; p.WriteModelType=STEPControl_ManifoldSolidBrep;
  p.WritePrecisionMode=DESTEP_Parameters::WriteMode_PrecisionMode_Greatest; p.WritePrecisionVal=inch?0.001:0.00001;
  p.WriteUnit=inch?UnitsMethods_LengthUnit_Inch:UnitsMethods_LengthUnit_Millimeter;
  p.WriteSchema=inch?DESTEP_Parameters::WriteMode_StepSchema_AP203:DESTEP_Parameters::WriteMode_StepSchema_AP242DIS; return p;
}
StepObs transfer_write(STEPControl_Writer& w,const TopoDS_Shape& shape,bool inch,const std::filesystem::path& path){
  StepObs o; auto p=step_params(inch); if(w.Transfer(shape,STEPControl_ManifoldSolidBrep,p,true)!=IFSelect_RetDone)return o;
  if(w.Write(path.string().c_str())!=IFSelect_RetDone)return o; const std::string text=read_text(path); o.uncertainty=serialized_uncertainty(text);
  STEPControl_Reader r; if(r.ReadFile(path.string().c_str())!=IFSelect_RetDone||r.TransferRoots()<=0)return o; auto rb=r.OneShape();o.valid_brep=valid(rb);o.readback_volume=volume(rb);o.ok=o.valid_brep;return o;
}

void probe_step(const std::filesystem::path& out){
  std::filesystem::create_directories(out); auto shape=BRepPrimAPI_MakeBox(40.0,20.0,10.0).Shape();
  STEPControl_Writer sa; sa.SetTolerance(0.00001); auto a=transfer_write(sa,shape,false,out/"seq-mm.step");
  STEPControl_Writer sb; sb.SetTolerance(0.001); auto b=transfer_write(sb,shape,true,out/"seq-inch.step");
  STEPControl_Writer ca,cb; ca.SetTolerance(0.00001); cb.SetTolerance(0.001);
  auto cross_a=transfer_write(ca,shape,false,out/"cross-mm-after-inch-set.step");
  auto cross_b=transfer_write(cb,shape,true,out/"cross-inch.step");
  std::cout<<std::setprecision(17)<<"{\"probe\":\"step\",\"label\":"<<q(RCS024_LABEL)
    <<",\"version\":"<<q(OCC_VERSION_STRING_EXT)<<",\"commit\":"<<q(RCS024_EXPECTED_COMMIT)
    <<",\"seq_mm\":"<<a.uncertainty<<",\"seq_inch\":"<<b.uncertainty
    <<",\"cross_mm\":"<<cross_a.uncertainty<<",\"cross_inch\":"<<cross_b.uncertainty
    <<",\"seq_valid\":"<<(a.ok&&b.ok?"true":"false")<<",\"cross_valid\":"<<(cross_a.ok&&cross_b.ok?"true":"false")<<"}\n";
}

void probe_parallel(){
  BOPAlgo_Options::SetParallelMode(false); const bool initial=BOPAlgo_Options::GetParallelMode();
  auto stock=BRepPrimAPI_MakeBox(10.,10.,10.).Shape(); auto tool=BRepPrimAPI_MakeBox(gp_Pnt(2,2,-1),6.,6.,12.).Shape();
  BRepAlgoAPI_Cut cut(stock,tool); cut.SetRunParallel(true); cut.Build(); const bool after_instance=BOPAlgo_Options::GetParallelMode();
  std::atomic<int> phase{0}; bool crossed=false;
  std::thread t1([&]{BOPAlgo_Options::SetParallelMode(false);phase.store(1);while(phase.load()<2)std::this_thread::yield();crossed=BOPAlgo_Options::GetParallelMode();});
  std::thread t2([&]{while(phase.load()<1)std::this_thread::yield();BOPAlgo_Options::SetParallelMode(true);phase.store(2);}); t1.join();t2.join();
  std::cout<<"{\"probe\":\"parallel\",\"label\":"<<q(RCS024_LABEL)<<",\"initial_global\":"<<(initial?"true":"false")
    <<",\"global_after_instance_true\":"<<(after_instance?"true":"false")<<",\"thread_a_observed_thread_b_global\":"<<(crossed?"true":"false")
    <<",\"result_valid\":"<<(valid(cut.Shape())?"true":"false")<<"}\n";
}

void probe_fuzzy(){
  const gp_Ax2 ax(gp_Pnt(0,0,0),gp_Dir(0,0,1)); auto stock=BRepPrimAPI_MakeCylinder(ax,20.0,60.0).Shape();
  const double depth=0.000001, target=20.0-depth, fuzzy=0.0001; auto tool=annular_tool(target,fuzzy); auto result=cut_one(stock,tool,fuzzy);
  const double expected=PI*(20.0*20.0-target*target)*60.0; const double removed=volume(stock)-volume(result);
  std::cout<<std::setprecision(17)<<"{\"probe\":\"fuzzy\",\"label\":"<<q(RCS024_LABEL)<<",\"depth_mm\":"<<depth<<",\"fuzzy_mm\":"<<fuzzy
    <<",\"expected_removed_mm3\":"<<expected<<",\"measured_removed_mm3\":"<<removed<<",\"valid_brep\":"<<(valid(result)?"true":"false")<<"}\n";
}

struct ChainObs {double vol=0,err=0;bool ok=false;};
ChainObs chain(bool descending){
  const gp_Ax2 ax(gp_Pnt(0,0,0),gp_Dir(0,0,1)); auto cur=BRepPrimAPI_MakeCylinder(ax,20.0,60.0).Shape();
  std::vector<int> ids; for(int i=1;i<=100;++i)ids.push_back(i);if(descending)std::reverse(ids.begin(),ids.end());
  for(int i:ids){double r=20.0-0.00001*i;auto tool=annular_tool(r,0.0001);cur=cut_one(cur,tool,0.0001);} double target=19.999;
  ChainObs o;o.vol=volume(cur);o.err=std::abs(o.vol-PI*target*target*60.0);o.ok=valid(cur);return o;
}
void probe_chain(){auto a=chain(false),d=chain(true);std::cout<<std::setprecision(17)<<"{\"probe\":\"chain\",\"label\":"<<q(RCS024_LABEL)
  <<",\"ascending_error_mm3\":"<<a.err<<",\"descending_error_mm3\":"<<d.err<<",\"order_delta_mm3\":"<<std::abs(a.vol-d.vol)
  <<",\"both_valid\":"<<(a.ok&&d.ok?"true":"false")<<"}\n";}

TopoDS_Shape flat_pose(const Pose&p,double radius){return BRepPrimAPI_MakeCylinder(gp_Ax2(gp_Pnt(p.x,p.y,p.z),gp_Dir(0,0,1)),radius,std::max(1e-12,12.0-p.z)).Shape();}
std::vector<TopoDS_Shape> flat_segment(const Pose&a,const Pose&b,double radius){
  std::vector<TopoDS_Shape> t;double dx=b.x-a.x,dy=b.y-a.y,d=std::hypot(dx,dy);if(d<=1e-12){t.push_back(flat_pose(a,radius));return t;}
  t.push_back(flat_pose(a,radius));t.push_back(flat_pose(b,radius));double ux=dx/d,uy=dy/d,yx=-uy,yy=ux;
  gp_Pnt origin(a.x-yx*radius,a.y-yy*radius,a.z);gp_Ax2 axes(origin,gp_Dir(0,0,1),gp_Dir(ux,uy,0));
  t.push_back(BRepPrimAPI_MakeBox(axes,d,2*radius,std::max(1e-12,12.0-a.z)).Shape());return t;
}
TopoDS_Shape retrace(bool batch){
  auto stock=BRepPrimAPI_MakeBox(40.,30.,10.).Shape();const double r=2.5;std::vector<std::pair<Pose,Pose>> segs={{{5,15,7},{35,15,7}},{{35,15.001,7},{5,15.001,7}}};
  if(batch){std::vector<TopoDS_Shape> all;for(auto&s:segs){auto x=flat_segment(s.first,s.second,r);all.insert(all.end(),x.begin(),x.end());}return cut_many(stock,all);}
  auto cur=stock;for(auto&s:segs){cur=cut_many(cur,flat_segment(s.first,s.second,r));}return cur;
}
void probe_mill(){auto ref=retrace(false),bat=retrace(true);std::cout<<std::setprecision(17)<<"{\"probe\":\"mill\",\"label\":"<<q(RCS024_LABEL)
  <<",\"segment_volume_mm3\":"<<volume(ref)<<",\"batch_volume_mm3\":"<<volume(bat)<<",\"delta_mm3\":"<<std::abs(volume(ref)-volume(bat))
  <<",\"segment_valid\":"<<(valid(ref)?"true":"false")<<",\"batch_valid\":"<<(valid(bat)?"true":"false")<<"}\n";}

void probe_sampled(){
  auto stock=BRepPrimAPI_MakeBox(40.,30.,10.).Shape();std::vector<TopoDS_Shape> tools;const Pose a{5,15,7},b{35,15,7};const double spacing=.25,r=2.5;
  int steps=static_cast<int>(std::ceil(30.0/spacing));for(int i=0;i<=steps;++i){double t=double(i)/steps;tools.push_back(flat_pose({a.x+(b.x-a.x)*t,15,7},r));}
  auto started=std::chrono::steady_clock::now();auto result=cut_many(stock,tools);double ms=std::chrono::duration<double,std::milli>(std::chrono::steady_clock::now()-started).count();
  std::cout<<std::setprecision(17)<<"{\"probe\":\"sampled\",\"label\":"<<q(RCS024_LABEL)<<",\"tool_count\":"<<tools.size()<<",\"runtime_ms\":"<<ms<<",\"valid_brep\":"<<(valid(result)?"true":"false")<<"}\n";
}
}

int main(int argc,char**argv){
  try{
    if(std::string(OCC_VERSION_STRING_EXT)!=RCS024_EXPECTED_VERSION)throw std::runtime_error(std::string("version mismatch: ")+OCC_VERSION_STRING_EXT);
    std::string probe,out=".results/rcs024-worker";for(int i=1;i<argc;++i){std::string a=argv[i];if(a=="--probe"&&i+1<argc)probe=argv[++i];else if(a=="--out-dir"&&i+1<argc)out=argv[++i];else throw std::runtime_error("bad args");}
    if(probe=="step")probe_step(out);else if(probe=="parallel")probe_parallel();else if(probe=="fuzzy")probe_fuzzy();else if(probe=="chain")probe_chain();else if(probe=="mill")probe_mill();else if(probe=="sampled")probe_sampled();else throw std::runtime_error("unknown probe");return 0;
  }catch(const Standard_Failure&f){std::cerr<<"OCCT failure: "<<(f.GetMessageString()?f.GetMessageString():"")<<"\n";return 20;}catch(const std::exception&e){std::cerr<<e.what()<<"\n";return 21;}
}
