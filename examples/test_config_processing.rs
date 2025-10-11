use trajecsim_rs::input::{loader, validator};
use trajecsim_rs::config::processor;

fn main() {
    println!("Testing config processing (Raw -> Processed)...\n");

    // Load raw config
    println!("1. Loading raw config from YAML...");
    let raw_config = match loader::load_config("data/input/landed_area.yaml") {
        Ok(config) => {
            println!("   ✓ Raw config loaded");
            config
        }
        Err(e) => {
            eprintln!("   ✗ Error: {}", e);
            return;
        }
    };

    // Validate raw config
    println!("\n2. Validating raw config...");
    if let Err(e) = validator::validate_config(&raw_config) {
        eprintln!("   ✗ Validation error: {}", e);
        return;
    }
    println!("   ✓ Validation passed");

    // Process config (transform + compute)
    println!("\n3. Processing config (computing derived values)...");
    let sim_config = match processor::process_config(raw_config) {
        Ok(config) => {
            println!("   ✓ Config processed successfully");
            config
        }
        Err(e) => {
            eprintln!("   ✗ Processing error: {}", e);
            return;
        }
    };

    // Display computed values
    println!("\n4. Computed values:");
    println!("   - Reference area: {:.6} m² (from diameter {:.3} m)",
             sim_config.rocket.reference_area,
             sim_config.rocket.diameter);
    println!("   - Parachute area: {:.6} m²",
             sim_config.rocket.parachute.area);

    match &sim_config.rocket.aerodynamics.mode {
        trajecsim_rs::config::config::AerodynamicsMode::Coefficients { reference_area, .. } => {
            println!("   - Aerodynamics mode: Coefficients");
            println!("   - Aero reference area: {:.6} m²", reference_area);
        }
        trajecsim_rs::config::config::AerodynamicsMode::Parameters {
            computed_lift_coefficient_alpha,
            computed_drag_coefficient,
            ..
        } => {
            println!("   - Aerodynamics mode: Parameters (computed)");
            println!("   - Computed lift coefficient: {:.6}", computed_lift_coefficient_alpha);
            println!("   - Computed drag coefficient: {:.6}", computed_drag_coefficient);
        }
    }

    match &sim_config.wind.mode {
        trajecsim_rs::config::config::WindMode::PowerLaw { ground_wind_speed, .. } => {
            println!("   - Wind mode: Power Law");
            println!("   - Ground wind speed: {:.2} m/s", ground_wind_speed);
        }
        trajecsim_rs::config::config::WindMode::Table { path } => {
            println!("   - Wind mode: Table");
            println!("   - Wind table: {:?}", path);
        }
    }

    println!("\n✓ Config processing complete!");
    println!("\nThe SimulationConfig is now ready for use in simulation.");
    println!("All derived values are pre-computed and guaranteed to be present.");
}
