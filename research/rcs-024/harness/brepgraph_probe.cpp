#include <BRepGraph.hxx>
#include <BRepGraph_Iterator.hxx>
#include <BRepGraph_LayerHistory.hxx>
#include <BRepGraph_LayerRegistry.hxx>
#include <BRepGraph_ShapesView.hxx>
#include <BRepGraph_UIDsView.hxx>
#include <BRepGraph_VersionStamp.hxx>
#include <BRepPrimAPI_MakeBox.hxx>
#include <NCollection_Array1.hxx>
#include <Standard_Version.hxx>

#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>

#ifndef RCS024_EXPECTED_VERSION
#error RCS024_EXPECTED_VERSION required
#endif
#ifndef RCS024_EXPECTED_COMMIT
#error RCS024_EXPECTED_COMMIT required
#endif
#ifndef RCS024_LABEL
#error RCS024_LABEL required
#endif

int main(){
  try{
    if(std::string(OCC_VERSION_STRING_EXT)!=RCS024_EXPECTED_VERSION) throw std::runtime_error("version mismatch");
    const TopoDS_Shape box=BRepPrimAPI_MakeBox(10.,20.,30.).Shape();
    BRepGraph graph;
    const auto add_result=graph.Shapes().Add(box);
    if(!add_result.IsOk()) throw std::runtime_error("box graph ingestion failed");
    std::vector<BRepGraph_FaceId> faces;
    for(BRepGraph_FaceIterator it(graph);it.More();it.Next()) faces.push_back(it.CurrentId());
    if(faces.size()<4) throw std::runtime_error("box graph lacks four faces");
    auto history=graph.LayerRegistry().Ensure<BRepGraph_LayerHistory>(); history->SetEnabled(true);

    NCollection_Array1<BRepGraph_NodeId> split(1,2); split.SetValue(1,faces[1]); split.SetValue(2,faces[2]);
    history->Record("rcs024-split",faces[0],split,BRepGraph_LayerHistory::Kind::Modified);
    const auto* split_images=history->FindModified(faces[0]);
    const std::size_t split_image_count=split_images?split_images->Size():0;

    NCollection_Array1<BRepGraph_NodeId> merge1(1,1); merge1.SetValue(1,faces[3]);
    history->Record("rcs024-merge-a",faces[1],merge1,BRepGraph_LayerHistory::Kind::Modified);
    NCollection_Array1<BRepGraph_NodeId> merge2(1,1); merge2.SetValue(1,faces[3]);
    history->Record("rcs024-merge-b",faces[2],merge2,BRepGraph_LayerHistory::Kind::Modified);
    const auto* merge_origins=history->FindOriginals(faces[3]);
    const std::size_t merge_origin_count=merge_origins?merge_origins->Size():0;

    // History lookup APIs return borrowed pointers into layer-owned containers.
    // Snapshot observable counts before any subsequent Record/Clear operation can
    // mutate or destroy those containers; never carry the borrowed pointers across
    // a graph mutation boundary.
    if(split_image_count!=2 || merge_origin_count!=2) throw std::runtime_error("BRepGraph history cardinality mismatch");

    const auto stamp=graph.UIDs().StampOf(faces[0]);
    const auto uid=stamp.ItemUID();
    graph.Clear();
    const bool stale_after_clear=graph.UIDs().IsStale(stamp);

    BRepGraph replay;
    const auto replay_add_result=replay.Shapes().Add(box);
    if(!replay_add_result.IsOk()) throw std::runtime_error("replay graph ingestion failed");
    BRepGraph_FaceIterator replay_it(replay);
    if(!replay_it.More()) throw std::runtime_error("replay has no face");
    const auto replay_stamp=replay.UIDs().StampOf(replay_it.CurrentId()); const auto replay_uid=replay_stamp.ItemUID();
    const bool numerical_uid_collision=(uid==replay_uid);

    std::cout<<"{\"probe\":\"brepgraph\",\"label\":\""<<RCS024_LABEL<<"\",\"version\":\""<<OCC_VERSION_STRING_EXT
      <<"\",\"commit\":\""<<RCS024_EXPECTED_COMMIT<<"\",\"face_count\":"<<faces.size()
      <<",\"split_image_count\":"<<split_image_count
      <<",\"merge_origin_count\":"<<merge_origin_count
      <<",\"stamp_valid\":"<<(stamp.IsValid()?"true":"false")
      <<",\"stale_after_clear\":"<<(stale_after_clear?"true":"false")
      <<",\"replay_uid_valid\":"<<(replay_uid.IsValid()?"true":"false")
      <<",\"numerical_uid_collision_across_graph_rebuild\":"<<(numerical_uid_collision?"true":"false")<<"}\n";
    return 0;
  }catch(const std::exception&e){std::cerr<<e.what()<<"\n";return 21;}
}
