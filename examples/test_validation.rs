use trajecsim_rs::input::{loader, validator};

fn main() {
    println!("Testing YAML validation...\n");

    // Test landed_area.yaml
    println!("Validating config/input/landed_area.yaml...");
    match loader::load_config("data/input/landed_area.yaml") {
        Ok(config) => {
            match validator::validate_config(&config) {
                Ok(_) => println!("✓ landed_area.yaml validation passed"),
                Err(e) => eprintln!("✗ Validation error: {}", e),
            }
        }
        Err(e) => {
            eprintln!("✗ Error loading file: {}", e);
        }
    }

    println!();

    // Test old_landed_area.yaml
    println!("Validating config/input/old_landed_area.yaml...");
    match loader::load_config("data/input/old_landed_area.yaml") {
        Ok(config) => {
            match validator::validate_config(&config) {
                Ok(_) => println!("✓ old_landed_area.yaml validation passed"),
                Err(e) => eprintln!("✗ Validation error: {}", e),
            }
        }
        Err(e) => {
            eprintln!("✗ Error loading file: {}", e);
        }
    }
}
