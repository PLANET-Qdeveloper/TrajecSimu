use anyhow::{anyhow, Result};
use super::schema::InputParameter;

/// Validate that a file path exists if it's specified
fn validate_path(path: &Option<std::path::PathBuf>, field_name: &str) -> Result<()> {
    if let Some(p) = path {
        if !p.exists() {
            return Err(anyhow!("File not found for {}: {}", field_name, p.display()));
        }
    }
    Ok(())
}

pub fn validate_config(config: &InputParameter) -> Result<()> {
    // Wind validation
    if config.flight_simulator.wind.use_power_law {
        if config.flight_simulator.wind.power_law.is_none() {
            return Err(anyhow!("Power law parameters required when use_power_law is true"));
        }
    } else {
        if config.flight_simulator.wind.winds_table.is_none() {
            return Err(anyhow!("Wind table required when use_power_law is false"));
        }
    }

    // Parachute validation
    for (id, parachute) in &config.flight_simulator.rocket.parachute {
        if parachute.use_auto_parachute_area {
            if parachute.terminal_velocity.is_none() {
                return Err(anyhow!(
                    "Terminal velocity required for parachute {} when use_auto_parachute_area is true",
                    id
                ));
            }
        } else {
            if parachute.parachute_area.is_none() {
                return Err(anyhow!(
                    "Parachute area required for parachute {} when use_auto_parachute_area is false",
                    id
                ));
            }
        }
    }

    // Aerodynamics validation - both coefficients and parameters are always present in the schema
    if config.flight_simulator.rocket.aerodynamics.use_aerodynamic_coefficients {
        if config.flight_simulator.rocket.aerodynamics.coefficients.is_none() {
            return Err(anyhow!("Aerodynamic coefficients required when use_aerodynamic_coefficients is true"));
        }
    } else {
        if config.flight_simulator.rocket.aerodynamics.parameters.is_none(){
            return Err(anyhow!("Aerodynamic parameters required when use_aerodynamic_coefficients is false"))
        }
    }

    // Path validation - check that all referenced files exist
    validate_paths(config)?;

    Ok(())
}

fn validate_paths(config: &InputParameter) -> Result<()> {
    let fs = &config.flight_simulator;

    // Launcher
    validate_path(&fs.launcher.range_kmz, "launcher.range_kmz")?;

    // Wind
    validate_path(&fs.wind.winds_table, "wind.winds_table")?;

    // Mass - Center of Pressure tables
    validate_path(&fs.rocket.mass.cp.x_mach_table, "mass.cp.x_mach_table")?;
    validate_path(&fs.rocket.mass.cp.y_mach_table, "mass.cp.y_mach_table")?;
    validate_path(&fs.rocket.mass.cp.z_mach_table, "mass.cp.z_mach_table")?;

    // Thrust
    if !fs.rocket.thrust.thrust_curve.exists() {
        return Err(anyhow!(
            "Thrust curve file not found: {}",
            fs.rocket.thrust.thrust_curve.display()
        ));
    }

    // Aerodynamic coefficients tables
    if let Some(coeffs) = &fs.rocket.aerodynamics.coefficients {
        validate_path(&coeffs.lift_coefficient_table, "aerodynamics.coefficients.lift_coefficient_table")?;
        validate_path(&coeffs.side_coefficient_table, "aerodynamics.coefficients.side_coefficient_table")?;
        validate_path(&coeffs.drag_coefficient_table, "aerodynamics.coefficients.drag_coefficient_table")?;
        validate_path(&coeffs.roll_damping_table, "aerodynamics.coefficients.roll_damping_table")?;
        validate_path(&coeffs.pitch_damping_table, "aerodynamics.coefficients.pitch_damping_table")?;
        validate_path(&coeffs.yaw_damping_table, "aerodynamics.coefficients.yaw_damping_table")?;
    }

    Ok(())
}
