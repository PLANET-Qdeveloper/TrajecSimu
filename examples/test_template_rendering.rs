use trajecsim_rs::input::loader;
use trajecsim_rs::config::processor;
use trajecsim_rs::simulation::template;
use std::fs;
use std::path::Path;

fn main() -> Result<(), Box<dyn std::error::Error>> {
    println!("{}", "=".repeat(80));
    println!("Testing Askama Template Rendering");
    println!("{}", "=".repeat(80));

    // Load and process config
    println!("\n[1] Loading and processing configuration...");
    let raw_config = loader::load_config("data/input/landed_area.yaml")?;
    let sim_config = processor::process_config(raw_config)?;
    println!("    ✓ Configuration loaded and processed");

    // Render templates
    println!("\n[2] Rendering Askama templates...");
    let (aircraft_xml, simulation_xml, liftoff_xml) = template::render_jsbsim_files(&sim_config)?;
    println!("    ✓ pq_rocket.xml rendered ({} bytes)", aircraft_xml.len());
    println!("    ✓ pq_simulation.xml rendered ({} bytes)", simulation_xml.len());
    println!("    ✓ liftoff.xml rendered ({} bytes)", liftoff_xml.len());

    // Create output directory
    let output_dir = Path::new("data/output/rendered_xml");
    fs::create_dir_all(output_dir)?;
    println!("\n[3] Writing XML files to {:?}...", output_dir);

    // Write aircraft XML
    let aircraft_path = output_dir.join("pq_rocket.xml");
    fs::write(&aircraft_path, &aircraft_xml)?;
    println!("    ✓ Wrote {}", aircraft_path.display());

    // Write simulation XML
    let simulation_path = output_dir.join("pq_simulation.xml");
    fs::write(&simulation_path, &simulation_xml)?;
    println!("    ✓ Wrote {}", simulation_path.display());

    // Write liftoff XML
    let liftoff_path = output_dir.join("liftoff.xml");
    fs::write(&liftoff_path, &liftoff_xml)?;
    println!("    ✓ Wrote {}", liftoff_path.display());

    // Validate XML structure
    println!("\n[4] Validating XML structure...");
    validate_xml_structure(&aircraft_xml, "pq_rocket.xml")?;
    validate_xml_structure(&simulation_xml, "pq_simulation.xml")?;
    validate_xml_structure(&liftoff_xml, "liftoff.xml")?;
    println!("    ✓ All XML files validated");

    // Display sample content
    println!("\n[5] Sample Content Preview:");
    println!("\n  pq_rocket.xml (first 20 lines):");
    for (i, line) in aircraft_xml.lines().take(20).enumerate() {
        println!("    {:3} | {}", i + 1, line);
    }
    println!("    ... ({} total lines)", aircraft_xml.lines().count());

    println!("\n  pq_simulation.xml (wind table section):");
    let sim_lines: Vec<&str> = simulation_xml.lines().collect();
    for (i, line) in sim_lines.iter().enumerate() {
        if line.contains("atmosphere/psiw-rad") {
            // Show 15 lines starting from wind direction table
            for j in 0..15 {
                if i + j < sim_lines.len() {
                    println!("    {:3} | {}", i + j + 1, sim_lines[i + j]);
                }
            }
            break;
        }
    }

    println!("\n  liftoff.xml (launcher orientation):");
    for (i, line) in liftoff_xml.lines().enumerate() {
        if line.contains("phi") || line.contains("theta") || line.contains("psi") {
            println!("    {:3} | {}", i + 1, line);
        }
    }

    println!("\n{}", "=".repeat(80));
    println!("✓ Template rendering test passed!");
    println!("{}", "=".repeat(80));

    Ok(())
}

fn validate_xml_structure(xml: &str, filename: &str) -> Result<(), Box<dyn std::error::Error>> {
    // Basic XML validation
    if !xml.starts_with("<?xml version") {
        return Err(format!("{}: Missing XML declaration", filename).into());
    }

    // Check for balanced tags (simple check)
    let open_count = xml.matches('<').count();
    let close_count = xml.matches('>').count();
    if open_count != close_count {
        return Err(format!("{}: Unbalanced angle brackets", filename).into());
    }

    // Check for specific expected elements based on filename
    match filename {
        "pq_rocket.xml" => {
            if !xml.contains("<metrics>") {
                return Err("pq_rocket.xml: Missing <metrics> section".into());
            }
            if !xml.contains("<mass_balance>") {
                return Err("pq_rocket.xml: Missing <mass_balance> section".into());
            }
            if !xml.contains("<aerodynamics>") {
                return Err("pq_rocket.xml: Missing <aerodynamics> section".into());
            }
            if !xml.contains("<propulsion>") {
                return Err("pq_rocket.xml: Missing <propulsion> section".into());
            }
        }
        "pq_simulation.xml" => {
            if !xml.contains("<runscript") {
                return Err("pq_simulation.xml: Missing <runscript> element".into());
            }
            if !xml.contains("<event name=\"liftoff\">") {
                return Err("pq_simulation.xml: Missing liftoff event".into());
            }
            if !xml.contains("atmosphere/psiw-rad") {
                return Err("pq_simulation.xml: Missing wind direction table".into());
            }
        }
        "liftoff.xml" => {
            if !xml.contains("<initialize") {
                return Err("liftoff.xml: Missing <initialize> element".into());
            }
            if !xml.contains("<latitude") {
                return Err("liftoff.xml: Missing latitude".into());
            }
        }
        _ => {}
    }

    Ok(())
}
