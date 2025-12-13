use super::schema::InputParameter;

#[derive(Debug)]
pub struct YamlError<T> {
    pub field_name: String,
    pub severity: Severity,
    pub message: String,
    pub value: T,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Severity {
    Error,
    Warning,
}

/// Validate that a file path exists if it's specified
fn validate_path(path: &Option<std::path::PathBuf>, field_name: &str) -> Option<YamlError<String>> {
    if let Some(p) = path {
        if !p.exists() {
            return Some(YamlError {
                field_name: field_name.to_string(),
                severity: Severity::Error,
                message: format!("File not found in path: {}", p.display()),
                value: p.display().to_string(),
            });
        }
    }
    None
}

pub fn validate_config(config: &InputParameter) -> Vec<YamlError<String>> {
    let mut errors = Vec::new();

    // Path validation - check that all referenced files exist
    errors.extend(validate_paths(config));

    errors
}

fn validate_paths(config: &InputParameter) -> Vec<YamlError<String>> {
    let fs = &config.flight_simulator;

    // Launcher
    let mut errors = Vec::new();
    // Wind
    errors.extend(validate_path(&fs.wind.winds_table, "wind.winds_table"));

    // Mass - Center of Pressure tables
    errors.extend(validate_path(
        &fs.rocket.mass.cp.x_mach_table,
        "mass.cp.x_mach_table",
    ));
    errors.extend(validate_path(
        &fs.rocket.mass.cp.y_mach_table,
        "mass.cp.y_mach_table",
    ));
    errors.extend(validate_path(
        &fs.rocket.mass.cp.z_mach_table,
        "mass.cp.z_mach_table",
    ));

    // Thrust
    if !fs.rocket.thrust.thrust_curve.exists() {
        errors.push(YamlError {
            field_name: "rocket.thrust.thrust_curve".to_string(),
            severity: Severity::Error,
            message: "File not found in path: {}".to_string(),
            value: fs.rocket.thrust.thrust_curve.display().to_string(),
        });
    }

    // Aerodynamic coefficients tables
    let coeffs = &fs.rocket.aerodynamics.coefficients;
    errors.extend(validate_path(
        &coeffs.lift_coefficient_table,
        "aerodynamics.coefficients.lift_coefficient_table",
    ));
    errors.extend(validate_path(
        &coeffs.side_coefficient_table,
        "aerodynamics.coefficients.side_coefficient_table",
    ));
    errors.extend(validate_path(
        &coeffs.drag_coefficient_table,
        "aerodynamics.coefficients.drag_coefficient_table",
    ));
    errors.extend(validate_path(
        &coeffs.roll_damping_table,
        "aerodynamics.coefficients.roll_damping_table",
    ));
    errors.extend(validate_path(
        &coeffs.pitch_damping_table,
        "aerodynamics.coefficients.pitch_damping_table",
    ));
    errors.extend(validate_path(
        &coeffs.yaw_damping_table,
        "aerodynamics.coefficients.yaw_damping_table",
    ));

    errors
}
