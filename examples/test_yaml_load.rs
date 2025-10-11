use trajecsim_rs::input::loader;

fn main() {
    println!("Testing YAML loading...\n");

    // Test landed_area.yaml
    println!("Loading config/input/landed_area.yaml...");
    match loader::load_config("data/input/landed_area.yaml") {
        Ok(config) => {
            println!("✓ landed_area.yaml loaded successfully");
            println!("  - Launcher pitch: {}", config.flight_simulator.launcher.rotation.pitch);
            println!("  - Rocket diameter: {}", config.flight_simulator.rocket.diameter);
            println!("  - Wind dir: {}", config.flight_simulator.wind.power_law.as_ref().unwrap().ground_wind_dir);
        }
        Err(e) => {
            eprintln!("✗ Error loading landed_area.yaml: {}", e);
        }
    }

    println!();

    // Test old_landed_area.yaml
    println!("Loading config/input/old_landed_area.yaml...");
    match loader::load_config("data/input/old_landed_area.yaml") {
        Ok(config) => {
            println!("✓ old_landed_area.yaml loaded successfully");
            println!("  - Launcher pitch: {}", config.flight_simulator.launcher.rotation.pitch);
            println!("  - Rocket diameter: {}", config.flight_simulator.rocket.diameter);
            println!("  - Wind dir: {}", config.flight_simulator.wind.power_law.as_ref().unwrap().ground_wind_dir);
            println!("  - Fuel position x: {}", config.flight_simulator.rocket.mass.fuel_position.x);
        }
        Err(e) => {
            eprintln!("✗ Error loading old_landed_area.yaml: {}", e);
        }
    }
}
