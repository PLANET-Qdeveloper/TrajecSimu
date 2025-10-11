use anyhow::Result;
use askama::Template;
use crate::config::config::{SimulationConfig, AerodynamicsMode};

/// Template context for pq_rocket.xml (aircraft configuration)
#[derive(Template)]
#[template(path = "aircraft/PQ_ROCKET/pq_rocket.askama", escape = "none")]
pub struct AircraftTemplate<'a> {
    // Rocket geometry
    pub body_diameter: f64,
    pub body_length: f64,
    pub projected_frontal_area: f64,
    pub fin_span: f64,

    // Mass properties
    pub dry_mass: f64,
    pub center_of_gravity_x: f64,
    pub center_of_gravity_y: f64,
    pub center_of_gravity_z: f64,
    pub center_of_pressure_x: f64,
    pub center_of_pressure_y: f64,
    pub center_of_pressure_z: f64,
    pub center_of_pressure_mach_table: &'a [(f64, f64)],

    // Propellant
    pub oxidizer_mass: f64,
    pub oxidizer_tank_position_x: f64,
    pub oxidizer_tank_position_y: f64,
    pub oxidizer_tank_position_z: f64,
    pub fuel_mass: f64,
    pub fuel_mass_after_burn: f64,
    pub fuel_tank_position_x: f64,
    pub fuel_tank_position_y: f64,
    pub fuel_tank_position_z: f64,
    pub fuel_grain_radius: f64,

    // Inertia
    pub moment_of_inertia_xx: f64,
    pub moment_of_inertia_yy: f64,
    pub moment_of_inertia_zz: f64,
    pub moment_of_inertia_xy: f64,
    pub moment_of_inertia_xz: f64,
    pub moment_of_inertia_yz: f64,

    // Aerodynamics
    pub reference_area: f64,
    pub normal_force_coefficient_mach_table: &'a [(f64, f64)],
    pub side_force_coefficient_mach_table: &'a [(f64, f64)],
    pub drag_coefficient_zero_lift_table: &'a [Vec<f64>],
    pub roll_damping_coefficient: f64,
    pub pitch_damping_coefficient: f64,
    pub yaw_damping_coefficient: f64,

    // Thrust
    pub thrust_curve: &'a [(f64, f64)],  // (time_s, thrust_lbf)
    pub fuel_mass_remaining_schedule: &'a [(f64, f64)],  // (time_s, fraction)
    pub thruster_position_x: f64,
    pub thruster_position_y: f64,
    pub thruster_position_z: f64,

    // Parachute
    pub parachute_area_schedule: &'a [(f64, f64)],  // (time_s, area_sqft)
    pub parachute_drag_coefficient: f64,
    pub parachute_deployment_duration: f64,

    // Computed values (to avoid arithmetic in templates)
    pub wingspan: f64,  // fin_span + body_diameter / 2
    pub empty_weight: f64,  // dry_mass - fuel_mass
    pub oxidizer_mass_lbs: f64,  // oxidizer_mass * kg_to_lbs
    pub fuel_consumed_lbs: f64,  // (fuel_mass - fuel_mass_after_burn) * kg_to_lbs
    pub thruster_offset_x: f64,  // thruster_position_x - center_of_gravity_x
    pub thruster_offset_y: f64,  // thruster_position_y - center_of_gravity_y
    pub thruster_offset_z: f64,  // thruster_position_z - center_of_gravity_z
    pub drag_table_rows: Vec<String>,  // Pre-formatted drag table rows
    pub side_force_negated_table: Vec<(f64, f64)>,  // side force coefficients negated
}

/// Template context for pq_simulation.xml (simulation script)
#[derive(Template)]
#[template(path = "pq_simulation.askama", escape = "none")]
pub struct SimulationTemplate<'a> {
    // Simulation settings
    pub simulation_duration: f64,
    pub integration_time_step: f64,
    pub liftoff_time: f64,
    pub terminate_at_apogee: u32,

    // Wind profile
    pub wind_profile_altitude_table: &'a [(f64, f64, f64)],  // (altitude_m, speed_fps, direction_rad)
    pub launcher_rail_exit_height: f64,

    // Computed values
    pub ignition_time: f64,  // integration_time_step * 100
}

/// Template context for liftoff.xml (initial conditions)
#[derive(Template)]
#[template(path = "aircraft/PQ_ROCKET/liftoff.askama", escape = "none")]
pub struct LiftoffTemplate {
    // Launcher orientation
    pub launcher_azimuth_angle: f64,
    pub launcher_pitch_angle: f64,
    pub launcher_roll_angle: f64,

    // Launch site
    pub launch_site_latitude: f64,
    pub launch_site_longitude: f64,
    pub launch_site_elevation_msl: f64,
}

impl<'a> AircraftTemplate<'a> {
    pub fn from_config(config: &'a SimulationConfig) -> Self {
        let aero = &config.rocket.aerodynamics.mode;

        // Extract reference area from either mode
        let reference_area = match aero {
            AerodynamicsMode::Coefficients { reference_area, .. } => *reference_area,
            AerodynamicsMode::Parameters { reference_area, .. } => *reference_area,
        };

        // Conversion constant
        const KG_TO_LBS: f64 = 2.20462;

        // Compute derived values to avoid arithmetic in templates
        let wingspan = config.rocket.fin_span + config.rocket.body_diameter / 2.0;
        let empty_weight = config.rocket.mass.dry_mass - config.rocket.mass.fuel_mass;
        let oxidizer_mass_lbs = config.rocket.mass.oxidizer_mass * KG_TO_LBS;
        let fuel_consumed_lbs = (config.rocket.mass.fuel_mass - config.rocket.mass.fuel_mass_after_burn) * KG_TO_LBS;
        let thruster_offset_x = config.rocket.thrust.thruster_position_x - config.rocket.mass.center_of_gravity_x;
        let thruster_offset_y = config.rocket.thrust.thruster_position_y - config.rocket.mass.center_of_gravity_y;
        let thruster_offset_z = config.rocket.thrust.thruster_position_z - config.rocket.mass.center_of_gravity_z;

        // Format drag table rows (Vec<Vec<f64>> -> Vec<String>)
        let drag_table_rows: Vec<String> = aero.get_drag_table()
            .iter()
            .map(|row| {
                row.iter()
                    .map(|v| v.to_string())
                    .collect::<Vec<_>>()
                    .join(" ")
            })
            .collect();

        // Create negated side force table
        let side_force_negated_table: Vec<(f64, f64)> = aero.get_side_force_table()
            .iter()
            .map(|(mach, coeff)| (*mach, -coeff))
            .collect();

        Self {
            // Rocket geometry
            body_diameter: config.rocket.body_diameter,
            body_length: config.rocket.body_length,
            projected_frontal_area: config.rocket.projected_frontal_area,
            fin_span: config.rocket.fin_span,

            // Mass properties
            dry_mass: config.rocket.mass.dry_mass,
            center_of_gravity_x: config.rocket.mass.center_of_gravity_x,
            center_of_gravity_y: config.rocket.mass.center_of_gravity_y,
            center_of_gravity_z: config.rocket.mass.center_of_gravity_z,
            center_of_pressure_x: config.rocket.mass.center_of_pressure_x,
            center_of_pressure_y: config.rocket.mass.center_of_pressure_y,
            center_of_pressure_z: config.rocket.mass.center_of_pressure_z,
            center_of_pressure_mach_table: &config.rocket.mass.center_of_pressure_mach_table,

            // Propellant
            oxidizer_mass: config.rocket.mass.oxidizer_mass,
            oxidizer_tank_position_x: config.rocket.mass.oxidizer_tank_position_x,
            oxidizer_tank_position_y: config.rocket.mass.oxidizer_tank_position_y,
            oxidizer_tank_position_z: config.rocket.mass.oxidizer_tank_position_z,
            fuel_mass: config.rocket.mass.fuel_mass,
            fuel_mass_after_burn: config.rocket.mass.fuel_mass_after_burn,
            fuel_tank_position_x: config.rocket.mass.fuel_tank_position_x,
            fuel_tank_position_y: config.rocket.mass.fuel_tank_position_y,
            fuel_tank_position_z: config.rocket.mass.fuel_tank_position_z,
            fuel_grain_radius: config.rocket.mass.fuel_grain_radius,

            // Inertia
            moment_of_inertia_xx: config.rocket.inertia.moment_of_inertia_xx,
            moment_of_inertia_yy: config.rocket.inertia.moment_of_inertia_yy,
            moment_of_inertia_zz: config.rocket.inertia.moment_of_inertia_zz,
            moment_of_inertia_xy: config.rocket.inertia.moment_of_inertia_xy,
            moment_of_inertia_xz: config.rocket.inertia.moment_of_inertia_xz,
            moment_of_inertia_yz: config.rocket.inertia.moment_of_inertia_yz,

            // Aerodynamics
            reference_area,
            normal_force_coefficient_mach_table: aero.get_normal_force_table(),
            side_force_coefficient_mach_table: aero.get_side_force_table(),
            drag_coefficient_zero_lift_table: aero.get_drag_table(),
            roll_damping_coefficient: aero.get_roll_damping(),
            pitch_damping_coefficient: aero.get_pitch_damping(),
            yaw_damping_coefficient: aero.get_yaw_damping(),

            // Thrust
            thrust_curve: &config.rocket.thrust.thrust_curve,
            fuel_mass_remaining_schedule: &config.rocket.thrust.fuel_mass_remaining_schedule,
            thruster_position_x: config.rocket.thrust.thruster_position_x,
            thruster_position_y: config.rocket.thrust.thruster_position_y,
            thruster_position_z: config.rocket.thrust.thruster_position_z,

            // Parachute
            parachute_area_schedule: &config.rocket.parachute_area_schedule,
            parachute_drag_coefficient: config.rocket.parachute_drag_coefficient,
            parachute_deployment_duration: config.rocket.parachute_deployment_duration,

            // Computed values
            wingspan,
            empty_weight,
            oxidizer_mass_lbs,
            fuel_consumed_lbs,
            thruster_offset_x,
            thruster_offset_y,
            thruster_offset_z,
            drag_table_rows,
            side_force_negated_table,
        }
    }
}

impl<'a> SimulationTemplate<'a> {
    pub fn from_config(config: &'a SimulationConfig) -> Self {
        let ignition_time = config.rocket.solver.integration_time_step * 100.0;

        Self {
            simulation_duration: config.rocket.solver.simulation_duration,
            integration_time_step: config.rocket.solver.integration_time_step,
            liftoff_time: config.rocket.thrust.liftoff_time,
            terminate_at_apogee: config.rocket.solver.terminate_at_apogee,
            wind_profile_altitude_table: config.wind.mode.get_wind_profile_table(),
            launcher_rail_exit_height: config.launcher.launcher_rail_exit_height,
            ignition_time,
        }
    }
}

impl LiftoffTemplate {
    pub fn from_config(config: &SimulationConfig) -> Self {
        Self {
            launcher_azimuth_angle: config.launcher.launcher_azimuth_angle,
            launcher_pitch_angle: config.launcher.launcher_pitch_angle,
            launcher_roll_angle: config.launcher.launcher_roll_angle,
            launch_site_latitude: config.launcher.launch_site_latitude,
            launch_site_longitude: config.launcher.launch_site_longitude,
            launch_site_elevation_msl: config.launcher.launch_site_elevation_msl,
        }
    }
}

/// Render all JSBSim XML files from a configuration
pub fn render_jsbsim_files(config: &SimulationConfig) -> Result<(String, String, String)> {
    let aircraft = AircraftTemplate::from_config(config);
    let simulation = SimulationTemplate::from_config(config);
    let liftoff = LiftoffTemplate::from_config(config);

    let aircraft_xml = aircraft.render()?;
    let simulation_xml = simulation.render()?;
    let liftoff_xml = liftoff.render()?;

    Ok((aircraft_xml, simulation_xml, liftoff_xml))
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::input::loader;
    use crate::config::processor;

    #[test]
    fn test_template_rendering() -> Result<()> {
        // Load and process config
        let raw_config = loader::load_config("data/input/landed_area.yaml")?;
        let sim_config = processor::process_config(raw_config)?;

        // Render templates
        let (aircraft_xml, simulation_xml, liftoff_xml) = render_jsbsim_files(&sim_config)?;

        // Basic validation - check that rendered output contains expected XML elements
        assert!(aircraft_xml.contains("<?xml version"));
        assert!(aircraft_xml.contains("<metrics>"));
        assert!(aircraft_xml.contains("<mass_balance>"));
        assert!(aircraft_xml.contains("<aerodynamics>"));

        assert!(simulation_xml.contains("<?xml version"));
        assert!(simulation_xml.contains("<runscript"));
        assert!(simulation_xml.contains("<event name=\"liftoff\">"));

        assert!(liftoff_xml.contains("<?xml version"));
        assert!(liftoff_xml.contains("<initialize"));
        assert!(liftoff_xml.contains("<latitude"));

        println!("✓ All templates rendered successfully");

        Ok(())
    }
}
