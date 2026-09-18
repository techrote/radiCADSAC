use std::env;
use std::process::ExitCode;
use vcad_kernel::Solid;

fn run() -> Result<(), Box<dyn std::error::Error>> {
    let path = env::args().nth(1).ok_or("usage: rcs022-vcad-probe <file.step>")?;
    let breps = vcad_kernel_step::read_step(&path)?;
    if breps.is_empty() {
        return Err("STEP import produced zero solids".into());
    }

    let mut total_volume = 0.0_f64;
    let mut global_min = [f64::INFINITY; 3];
    let mut global_max = [f64::NEG_INFINITY; 3];
    let mut bodies = Vec::with_capacity(breps.len());

    for brep in breps {
        let solid = Solid::from_brep(brep);
        let volume = solid.volume().abs();
        let (min, max) = solid.bounding_box();
        for i in 0..3 {
            global_min[i] = global_min[i].min(min[i]);
            global_max[i] = global_max[i].max(max[i]);
        }
        total_volume += volume;
        bodies.push(serde_json::json!({
            "volume_mm3": volume,
            "bbox_mm": [min[0], min[1], min[2], max[0], max[1], max[2]]
        }));
    }

    println!("{}", serde_json::json!({
        "consumer": "vcad",
        "consumer_commit": "eba7a2e6a89ff06801776fbc599d5c8a64036168",
        "body_count": bodies.len(),
        "volume_mm3": total_volume,
        "bbox_mm": [global_min[0], global_min[1], global_min[2], global_max[0], global_max[1], global_max[2]],
        "bodies": bodies
    }));
    Ok(())
}

fn main() -> ExitCode {
    match run() {
        Ok(()) => ExitCode::SUCCESS,
        Err(e) => {
            eprintln!("RCS022_VCAD_IMPORT_FAILED: {e}");
            ExitCode::from(2)
        }
    }
}
