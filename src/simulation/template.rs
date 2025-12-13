use anyhow::Result;
use askama::Template;
use crate::config::config::{SimulationConfig, AerodynamicsMode};

// Import uom units for extracting f64 values
use uom::si::{
    angle::degree,
    area::square_meter,
    force::newton,
    length::meter,
    mass::kilogram,
    moment_of_inertia::kilogram_square_meter,
    time::second,
    velocity::meter_per_second,
};

/// Template context for pq_rocket.xml (aircraft configuration)
#[derive(Template)]
#[template(path = "aircraft/PQ_ROCKET/pq_rocket.askama", escape = "none")]
pub struct AircraftTemplate {
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
    pub center_of_pressure_mach_table: Vec<(f64, f64)>,

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
    pub normal_force_coefficient_mach_table: Vec<(f64, f64)>,
    pub side_force_coefficient_mach_table: Vec<(f64, f64)>,
    pub drag_coefficient_zero_lift_table: Vec<Vec<f64>>,
    pub roll_damping_coefficient: f64,
    pub pitch_damping_coefficient: f64,
    pub yaw_damping_coefficient: f64,

    // Thrust
    pub thrust_curve: Vec<(f64, f64)>,  // (time_s, thrust_N)
    pub fuel_mass_remaining_schedule: Vec<(f64, f64)>,  // (time_s, fraction)
    pub thruster_position_x: f64,
    pub thruster_position_y: f64,
    pub thruster_position_z: f64,

    // Parachute
    pub parachute_area_schedule: Vec<(f64, f64)>,  // (time_s, area_m2)
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
pub struct SimulationTemplate {
    // Simulation settings
    pub simulation_duration: f64,
    pub integration_time_step: f64,
    pub liftoff_time: f64,
    pub terminate_at_apogee: u32,  // 0 or 1 for template compatibility

    // Wind profile
    pub wind_profile_altitude_table: Vec<(f64, f64, f64)>,  // (altitude_m, speed_m/s, direction_deg)
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

impl AircraftTemplate {
    pub fn from_config(config: &SimulationConfig) -> Self {
        let aero = &config.rocket.aerodynamics.mode;

        // Extract reference area from either mode
        let reference_area = match aero {
            AerodynamicsMode::Coefficients { reference_area, .. } => reference_area.get::<square_meter>(),

        };

        // Conversion constant
        const KG_TO_LBS: f64 = 2.20462;

        // Extract f64 values from uom types
        let body_diameter_m = config.rocket.body_diameter.get::<meter>();
        let fin_span_m = config.rocket.fin_span.get::<meter>();
        let dry_mass_kg = config.rocket.mass.dry_mass.get::<kilogram>();
        let fuel_mass_kg = config.rocket.mass.fuel_mass.get::<kilogram>();
        let fuel_mass_after_burn_kg = config.rocket.mass.fuel_mass_after_burn.get::<kilogram>();
        let oxidizer_mass_kg = config.rocket.mass.oxidizer_mass.get::<kilogram>();

        // Compute derived values to avoid arithmetic in templates
        let wingspan = fin_span_m + body_diameter_m / 2.0;
        let empty_weight = dry_mass_kg - fuel_mass_kg;
        let oxidizer_mass_lbs = oxidizer_mass_kg * KG_TO_LBS;
        let fuel_consumed_lbs = (fuel_mass_kg - fuel_mass_after_burn_kg) * KG_TO_LBS;
        let thruster_offset_x = config.rocket.thrust.thruster_position_x.get::<meter>() - config.rocket.mass.center_of_gravity_x.get::<meter>();
        let thruster_offset_y = config.rocket.thrust.thruster_position_y.get::<meter>() - config.rocket.mass.center_of_gravity_y.get::<meter>();
        let thruster_offset_z = config.rocket.thrust.thruster_position_z.get::<meter>() - config.rocket.mass.center_of_gravity_z.get::<meter>();

        // Convert center_of_pressure_mach_table from Vec<(f64, Length)> to Vec<(f64, f64)>
        let cp_mach_table_f64: Vec<(f64, f64)> = config.rocket.mass.center_of_pressure_mach_table
            .iter()
            .map(|(mach, length)| (*mach, length.get::<meter>()))
            .collect();

        // Convert thrust_curve from Vec<(Time, Force)> to Vec<(f64, f64)>
        let thrust_curve_f64: Vec<(f64, f64)> = config.rocket.thrust.thrust_curve
            .iter()
            .map(|(time, force)| (time.get::<second>(), force.get::<newton>()))
            .collect();

        // Convert fuel_mass_remaining_schedule from Vec<(Time, f64)> to Vec<(f64, f64)>
        let fuel_schedule_f64: Vec<(f64, f64)> = config.rocket.thrust.fuel_mass_remaining_schedule
            .iter()
            .map(|(time, fraction)| (time.get::<second>(), *fraction))
            .collect();

        // Convert parachute_area_schedule from Vec<(Time, Area)> to Vec<(f64, f64)>
        let parachute_schedule_f64: Vec<(f64, f64)> = config.rocket.parachute_area_schedule
            .iter()
            .map(|(time, area)| (time.get::<second>(), area.get::<square_meter>()))
            .collect();

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
            body_diameter: body_diameter_m,
            body_length: config.rocket.body_length.get::<meter>(),
            projected_frontal_area: config.rocket.projected_frontal_area.get::<square_meter>(),
            fin_span: fin_span_m,

            // Mass properties
            dry_mass: dry_mass_kg,
            center_of_gravity_x: config.rocket.mass.center_of_gravity_x.get::<meter>(),
            center_of_gravity_y: config.rocket.mass.center_of_gravity_y.get::<meter>(),
            center_of_gravity_z: config.rocket.mass.center_of_gravity_z.get::<meter>(),
            center_of_pressure_x: config.rocket.mass.center_of_pressure_x.get::<meter>(),
            center_of_pressure_y: config.rocket.mass.center_of_pressure_y.get::<meter>(),
            center_of_pressure_z: config.rocket.mass.center_of_pressure_z.get::<meter>(),
            center_of_pressure_mach_table: cp_mach_table_f64,

            // Propellant
            oxidizer_mass: oxidizer_mass_kg,
            oxidizer_tank_position_x: config.rocket.mass.oxidizer_tank_position_x.get::<meter>(),
            oxidizer_tank_position_y: config.rocket.mass.oxidizer_tank_position_y.get::<meter>(),
            oxidizer_tank_position_z: config.rocket.mass.oxidizer_tank_position_z.get::<meter>(),
            fuel_mass: fuel_mass_kg,
            fuel_mass_after_burn: fuel_mass_after_burn_kg,
            fuel_tank_position_x: config.rocket.mass.fuel_tank_position_x.get::<meter>(),
            fuel_tank_position_y: config.rocket.mass.fuel_tank_position_y.get::<meter>(),
            fuel_tank_position_z: config.rocket.mass.fuel_tank_position_z.get::<meter>(),
            fuel_grain_radius: config.rocket.mass.fuel_grain_radius.get::<meter>(),

            // Inertia
            moment_of_inertia_xx: config.rocket.inertia.moment_of_inertia_xx.get::<kilogram_square_meter>(),
            moment_of_inertia_yy: config.rocket.inertia.moment_of_inertia_yy.get::<kilogram_square_meter>(),
            moment_of_inertia_zz: config.rocket.inertia.moment_of_inertia_zz.get::<kilogram_square_meter>(),
            moment_of_inertia_xy: config.rocket.inertia.moment_of_inertia_xy.get::<kilogram_square_meter>(),
            moment_of_inertia_xz: config.rocket.inertia.moment_of_inertia_xz.get::<kilogram_square_meter>(),
            moment_of_inertia_yz: config.rocket.inertia.moment_of_inertia_yz.get::<kilogram_square_meter>(),

            // Aerodynamics
            reference_area,
            normal_force_coefficient_mach_table: aero.get_normal_force_table().to_vec(),
            side_force_coefficient_mach_table: aero.get_side_force_table().to_vec(),
            drag_coefficient_zero_lift_table: aero.get_drag_table().to_vec(),
            roll_damping_coefficient: aero.get_roll_damping(),
            pitch_damping_coefficient: aero.get_pitch_damping(),
            yaw_damping_coefficient: aero.get_yaw_damping(),

            // Thrust
            thrust_curve: thrust_curve_f64,
            fuel_mass_remaining_schedule: fuel_schedule_f64,
            thruster_position_x: config.rocket.thrust.thruster_position_x.get::<meter>(),
            thruster_position_y: config.rocket.thrust.thruster_position_y.get::<meter>(),
            thruster_position_z: config.rocket.thrust.thruster_position_z.get::<meter>(),

            // Parachute
            parachute_area_schedule: parachute_schedule_f64,
            parachute_drag_coefficient: config.rocket.parachute_drag_coefficient,
            parachute_deployment_duration: config.rocket.parachute_deployment_duration.get::<second>(),

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

impl SimulationTemplate {
    pub fn from_config(config: &SimulationConfig) -> Self {
        let integration_time_step_s = config.rocket.solver.integration_time_step.get::<second>();
        let ignition_time = integration_time_step_s * 100.0;

        // Convert wind_profile_altitude_table from Vec<(Length, Velocity, Angle)> to Vec<(f64, f64, f64)>
        let wind_table_f64: Vec<(f64, f64, f64)> = config.wind.mode.get_wind_profile_table()
            .iter()
            .map(|(alt, speed, dir)| {
                (alt.get::<meter>(), speed.get::<meter_per_second>(), dir.get::<degree>())
            })
            .collect();

        Self {
            simulation_duration: config.rocket.solver.simulation_duration.get::<second>(),
            integration_time_step: integration_time_step_s,
            liftoff_time: config.rocket.thrust.liftoff_time.get::<second>(),
            terminate_at_apogee: if config.rocket.solver.terminate_at_apogee { 1 } else { 0 },
            wind_profile_altitude_table: wind_table_f64,
            launcher_rail_exit_height: config.launcher.launcher_rail_exit_height.get::<meter>(),
            ignition_time,
        }
    }
}

impl LiftoffTemplate {
    pub fn from_config(config: &SimulationConfig) -> Self {
        Self {
            launcher_azimuth_angle: config.launcher.launcher_azimuth_angle.get::<degree>(),
            launcher_pitch_angle: config.launcher.launcher_pitch_angle.get::<degree>(),
            launcher_roll_angle: config.launcher.launcher_roll_angle.get::<degree>(),
            launch_site_latitude: config.launcher.launch_site_latitude.get::<degree>(),
            launch_site_longitude: config.launcher.launch_site_longitude.get::<degree>(),
            launch_site_elevation_msl: config.launcher.launch_site_elevation_msl.get::<meter>(),
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
