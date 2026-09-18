use std::env;
use std::fs;

fn esc(s: &str) -> String {
    s.replace('\\', "\\\\").replace('"', "\\\"").replace('\n', "\\n").replace('\r', "\\r")
}

fn main() {
    let path = env::args().nth(1).expect("usage: rcs022-stepio-probe FILE.step");
    let bytes = fs::read(&path).expect("read STEP file");
    let (model, _report) = match step_io::read(&bytes) {
        Ok(v) => v,
        Err(e) => {
            println!("{{\"schema\":\"rcs-022-stepio-probe/1.0\",\"product\":\"step-io\",\"version\":\"0.2.4\",\"status\":\"rejected\",\"error\":\"{}\"}}", esc(&format!("{e:?}")));
            return;
        }
    };
    let scene = model.scene();
    let mut solids = 0usize;
    let mut faces = 0usize;
    let mut plane = 0usize;
    let mut cylinder = 0usize;
    let mut cone = 0usize;
    let mut sphere = 0usize;
    let mut torus = 0usize;
    let mut bspline = 0usize;
    let mut other = 0usize;
    for solid in scene.all_solids() {
        solids += 1;
        for face in solid.faces() {
            faces += 1;
            let kind = format!("{:?}", face.surface().kind());
            if kind.contains("Plane") { plane += 1; }
            else if kind.contains("Cylind") { cylinder += 1; }
            else if kind.contains("Cone") || kind.contains("Conical") { cone += 1; }
            else if kind.contains("Sphere") || kind.contains("Spherical") { sphere += 1; }
            else if kind.contains("Torus") || kind.contains("Toroidal") { torus += 1; }
            else if kind.contains("BSpline") || kind.contains("B-spline") { bspline += 1; }
            else { other += 1; }
        }
    }
    let units = scene.units();
    let (unit_name, to_si) = match units.length {
        Some(u) => (u.name, u.to_si),
        None => (String::new(), 0.0),
    };
    let warnings = scene.warnings();
    println!(
        "{{\"schema\":\"rcs-022-stepio-probe/1.0\",\"product\":\"step-io\",\"version\":\"0.2.4\",\"status\":\"accepted\",\"file_schema\":\"{}\",\"solid_count\":{},\"face_count\":{},\"units\":{{\"length_name\":\"{}\",\"length_to_si\":{:.17},\"precision\":{}}},\"analytic_surfaces\":{{\"plane\":{},\"cylinder\":{},\"cone\":{},\"sphere\":{},\"torus\":{},\"bspline\":{},\"other\":{}}},\"warning_count\":{}}}",
        esc(&format!("{:?}", model.header().schema)), solids, faces, esc(&unit_name), to_si,
        units.precision.map(|v| format!("{v:.17}")).unwrap_or_else(|| "null".into()),
        plane, cylinder, cone, sphere, torus, bspline, other, warnings.len()
    );
}
