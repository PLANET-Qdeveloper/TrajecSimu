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
    println!("   - Projected frontal area: {:.6} m² (from diameter {:.3} m)",
             sim_config.rocket.projected_frontal_area,
             sim_config.rocket.body_diameter);

    if !sim_config.rocket.parachutes.is_empty() {
        println!("   - Parachutes:");
        for (i, chute) in sim_config.rocket.parachutes.iter().enumerate() {
            println!("     {}. {} - Area: {:.6} m²", i + 1, chute.name, chute.area);
        }
    }

    match &sim_config.rocket.aerodynamics.mode {
        trajecsim_rs::config::config::AerodynamicsMode::Coefficients { reference_area, .. } => {
            println!("   - Aerodynamics mode: Coefficients");
            println!("   - Aero reference area: {:.6} m²", reference_area);
        }
        trajecsim_rs::config::config::AerodynamicsMode::Parameters {
            reference_area,
            normal_force_coefficient_mach_table,
            drag_coefficient_zero_lift_table,
            ..
        } => {
            println!("   - Aerodynamics mode: Parameters (computed)");
            println!("   - Reference area: {:.6} m²", reference_area);
            println!("   - Normal force table entries: {}", normal_force_coefficient_mach_table.len());
            println!("   - Drag table rows: {}", drag_coefficient_zero_lift_table.len());
        }
    }

    match &sim_config.wind.mode {
        trajecsim_rs::config::config::WindMode::PowerLaw { ground_wind_speed, wind_profile_altitude_table, .. } => {
            println!("   - Wind mode: Power Law");
            println!("   - Ground wind speed: {:.2} m/s", ground_wind_speed);
            println!("   - Generated wind profile entries: {}", wind_profile_altitude_table.len());
        }
        trajecsim_rs::config::config::WindMode::Table { wind_profile_altitude_table } => {
            println!("   - Wind mode: Table");
            println!("   - Wind profile entries: {}", wind_profile_altitude_table.len());
        }
    }

    println!("\n✓ Config processing complete!");
    println!("\nThe SimulationConfig is now ready for use in simulation.");
    println!("All derived values are pre-computed and guaranteed to be present.");
}
