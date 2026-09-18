use std::env;
use vcad_kernel_step::read_step_with_report;
use vcad_kernel_tessellate::{compute_mesh_properties, tessellate_solid, TessellationParams};

fn esc(s: &str) -> String {
    s.replace('\\', "\\\\").replace('"', "\\\"").replace('\n', "\\n").replace('\r', "\\r")
}

fn main() {
    let path = env::args().nth(1).expect("usage: rcs022-vcad-probe FILE.step");
    let read = match read_step_with_report(&path) {
        Ok(v) => v,
        Err(e) => {
            println!("{{\"schema\":\"rcs-022-vcad-probe/1.0\",\"product\":\"vcad-kernel-step\",\"version\":\"0.10.0\",\"source_commit\":\"eba7a2e6a89ff06801776fbc599d5c8a64036168\",\"status\":\"rejected\",\"error\":\"{}\"}}", esc(&format!("{e:?}")));
            return;
        }
    };
    let mut faces = 0usize;
    let mut edges = 0usize;
    let mut vertices = 0usize;
    let mut volume = 0.0f64;
    let mut triangles = 0usize;
    let mut bmin = [f64::INFINITY; 3];
    let mut bmax = [f64::NEG_INFINITY; 3];
    let params = TessellationParams::default();
    for solid in &read.solids {
        faces += solid.topology.faces.len();
        edges += solid.topology.edges.len();
        vertices += solid.topology.vertices.len();
        let mesh = tessellate_solid(solid, &params);
        let props = compute_mesh_properties(&mesh.vertices, &mesh.indices);
        volume += props.volume;
        triangles += props.triangles;
        for k in 0..3 {
            bmin[k] = bmin[k].min(props.bbox.min[k]);
            bmax[k] = bmax[k].max(props.bbox.max[k]);
        }
    }
    if read.solids.is_empty() {
        bmin = [0.0; 3];
        bmax = [0.0; 3];
    }
    println!(
        "{{\"schema\":\"rcs-022-vcad-probe/1.0\",\"product\":\"vcad-kernel-step\",\"version\":\"0.10.0\",\"source_commit\":\"eba7a2e6a89ff06801776fbc599d5c8a64036168\",\"status\":\"accepted\",\"solid_count\":{},\"clean_import\":{},\"skipped_faces\":{},\"topology\":{{\"faces\":{},\"edges\":{},\"vertices\":{}}},\"mesh_diagnostic\":{{\"volume_mm3\":{:.17},\"bbox_mm\":[{:.17},{:.17},{:.17},{:.17},{:.17},{:.17}],\"triangles\":{}}}}}",
        read.solids.len(), if read.report.is_clean() {"true"} else {"false"}, read.report.total_skipped_faces(),
        faces, edges, vertices, volume, bmin[0], bmin[1], bmin[2], bmax[0], bmax[1], bmax[2], triangles
    );
}
