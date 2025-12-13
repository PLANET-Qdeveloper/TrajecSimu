use anyhow::{anyhow, Context, Result};
use std::f64::consts::PI;
use std::fs::File;
use std::io::{BufRead, BufReader};
use std::path::Path;

// Unit conversion using uom
use uom::si::f64::*;
use uom::si::{
    angle::degree, area::square_meter, force::newton, length::meter, mass::kilogram,
    moment_of_inertia::kilogram_square_meter, pressure::pascal, time::second,
    velocity::meter_per_second,
};

use crate::config::schema::*;
use crate::input::schema::InputParameter as RawConfig;
/// Transform raw YAML config into processed simulation config
/// This function performs all necessary computations and validations
/// All unit conversions are performed here using the uom library
pub fn process_config(raw: RawConfig) -> Result<SimulationConfig> {
    let launcher = process_launcher(&raw)?;
    let wind = process_wind(&raw)?;
    let rocket = process_rocket(&raw)?;
    let construction = process_construction(&raw);

    Ok(SimulationConfig {
        launcher,
        wind,
        rocket,
        construction,
    })
}

fn process_launcher(raw: &RawConfig) -> Result<LauncherConfig> {
    let l = &raw.flight_simulator.launcher;

    // Convert to uom types
    let magnetic_declination = Angle::new::<degree>(l.rotation.magnetic_declination);
    let launcher_azimuth_angle = Angle::new::<degree>(l.rotation.azimuth);
    let launcher_pitch_angle = Angle::new::<degree>(l.rotation.pitch);
    let launcher_roll_angle = Angle::new::<degree>(l.rotation.roll);
    let launch_site_latitude = Angle::new::<degree>(l.coordinates.latitude);
    let launch_site_longitude = Angle::new::<degree>(l.coordinates.longitude);
    let launch_site_elevation_msl = Length::new::<meter>(l.coordinates.elevation);
    let launcher_length = Length::new::<meter>(l.launcher_length);

    // Compute launcher_rail_exit_height: launcher_length * sin(pitch) + elevation
    let pitch_rad = l.rotation.pitch.to_radians();
    let launcher_rail_exit_height =
        Length::new::<meter>(l.launcher_length * pitch_rad.sin() + l.coordinates.elevation);

    Ok(LauncherConfig {
        magnetic_declination,
        launcher_azimuth_angle,
        launcher_pitch_angle,
        launcher_roll_angle,
        launch_site_latitude,
        launch_site_longitude,
        launch_site_elevation_msl,
        launcher_length,
        launcher_rail_exit_height,
        range_kmz: l.range_kmz.clone(),
    })
}

fn process_wind(raw: &RawConfig) -> Result<WindConfig> {
    let wind = &raw.flight_simulator.wind;

    let mode = if wind.use_power_law {
        let pl = wind
            .power_law
            .as_ref()
            .ok_or_else(|| anyhow!("Power law parameters required"))?;

        // Generate wind profile table from power law
        let wind_profile_altitude_table = generate_wind_profile_from_power_law(
            pl.wind_ref_altitude,
            pl.ground_wind_dir,
            pl.ground_wind_speed,
            pl.wind_power_factor,
        );

        WindMode::PowerLaw {
            wind_ref_altitude: Length::new::<meter>(pl.wind_ref_altitude),
            ground_wind_dir: Angle::new::<degree>(pl.ground_wind_dir),
            ground_wind_speed: Velocity::new::<meter_per_second>(pl.ground_wind_speed),
            wind_power_factor: pl.wind_power_factor,
            wind_profile_altitude_table,
        }
    } else {
        let path = wind
            .winds_table
            .as_ref()
            .ok_or_else(|| anyhow!("Wind table path required"))?;

        // Load wind profile table from CSV
        let wind_profile_altitude_table = load_wind_table(path)?;

        WindMode::Table {
            wind_profile_altitude_table,
        }
    };

    Ok(WindConfig { mode })
}

fn process_rocket(raw: &RawConfig) -> Result<RocketConfig> {
    let rocket = &raw.flight_simulator.rocket;

    // Compute reference area from diameter
    let projected_frontal_area = compute_reference_area(rocket.diameter);

    // Determine fin_span from construction or parameters
    let fin_span = if let Some(construction) = &raw.construction {
        if let Some(fin) = &construction.rocket.fin {
            fin.half_span * 2.0
        } else {
            0.0
        }
    } else {
        0.0
    };

    // Process parachutes
    let parachutes = process_parachutes(raw, projected_frontal_area)?;

    // Generate parachute area schedule
    let parachute_area_schedule = generate_parachute_area_schedule(&parachutes);

    // Get parachute drag coefficient from first parachute
    let parachute_drag_coefficient = parachutes
        .first()
        .map(|p| p.parachute_drag_coefficient)
        .unwrap_or(1.2); // Default value

    // Compute max deployment duration
    let parachute_deployment_duration = parachute_area_schedule
        .iter()
        .map(|(t, _)| *t)
        .max_by(|a, b| a.partial_cmp(b).unwrap_or(std::cmp::Ordering::Equal))
        .unwrap_or(Time::new::<second>(10.0)); // Default 10 seconds

    Ok(RocketConfig {
        body_diameter: Length::new::<meter>(rocket.diameter),
        body_length: Length::new::<meter>(rocket.height),
        projected_frontal_area: Area::new::<square_meter>(projected_frontal_area),
        fin_span: Length::new::<meter>(fin_span),
        inertia: process_inertia(raw)?,
        mass: process_mass(raw)?,
        parachutes,
        parachute_area_schedule,
        parachute_drag_coefficient,
        parachute_deployment_duration,
        aerodynamics: process_aerodynamics(raw, projected_frontal_area)?,
        thrust: process_thrust(raw)?,
        solver: process_solver(raw)?,
    })
}

fn process_inertia(raw: &RawConfig) -> Result<InertiaConfig> {
    let i = &raw.flight_simulator.rocket.inertia;

    Ok(InertiaConfig {
        moment_of_inertia_xx: MomentOfInertia::new::<kilogram_square_meter>(i.xx),
        moment_of_inertia_yy: MomentOfInertia::new::<kilogram_square_meter>(i.yy),
        moment_of_inertia_zz: MomentOfInertia::new::<kilogram_square_meter>(i.zz),
        moment_of_inertia_xy: MomentOfInertia::new::<kilogram_square_meter>(i.xy),
        moment_of_inertia_xz: MomentOfInertia::new::<kilogram_square_meter>(i.xz),
        moment_of_inertia_yz: MomentOfInertia::new::<kilogram_square_meter>(i.yz),
    })
}

fn process_mass(raw: &RawConfig) -> Result<MassConfig> {
    let m = &raw.flight_simulator.rocket.mass;

    // Load center of pressure mach table if provided
    let center_of_pressure_mach_table = if let Some(cp_x_table_path) = &m.cp.x_mach_table {
        let raw_table = load_1d_table(cp_x_table_path)?;
        // Convert f64 to Length
        raw_table
            .into_iter()
            .map(|(mach, pos)| (mach, Length::new::<meter>(pos)))
            .collect()
    } else {
        // Fallback to single-row table
        vec![(0.0, Length::new::<meter>(m.cp.x))]
    };

    // Compute fuel grain radius (simplified: assume cylindrical fuel grain)
    let fuel_grain_radius = raw.flight_simulator.rocket.diameter / 4.0; // Simplified assumption

    Ok(MassConfig {
        dry_mass: Mass::new::<kilogram>(m.dry_weight),
        center_of_gravity_x: Length::new::<meter>(m.cg.x),
        center_of_gravity_y: Length::new::<meter>(m.cg.y),
        center_of_gravity_z: Length::new::<meter>(m.cg.z),
        center_of_pressure_x: Length::new::<meter>(m.cp.x),
        center_of_pressure_y: Length::new::<meter>(m.cp.y),
        center_of_pressure_z: Length::new::<meter>(m.cp.z),
        center_of_pressure_mach_table,
        oxidizer_mass: Mass::new::<kilogram>(m.oxidizer_mass),
        oxidizer_tank_position_x: Length::new::<meter>(m.tank_position.x),
        oxidizer_tank_position_y: Length::new::<meter>(m.tank_position.y),
        oxidizer_tank_position_z: Length::new::<meter>(m.tank_position.z),
        fuel_mass: Mass::new::<kilogram>(m.fuel_mass_before_burn),
        fuel_mass_after_burn: Mass::new::<kilogram>(m.fuel_mass_after_burn),
        fuel_tank_position_x: Length::new::<meter>(m.fuel_position.x),
        fuel_tank_position_y: Length::new::<meter>(m.fuel_position.y),
        fuel_tank_position_z: Length::new::<meter>(m.fuel_position.z),
        fuel_grain_radius: Length::new::<meter>(fuel_grain_radius),
    })
}

fn process_parachutes(raw: &RawConfig, _reference_area: f64) -> Result<Vec<ParachuteConfig>> {
    let parachutes_map = &raw.flight_simulator.rocket.parachute;

    if parachutes_map.is_empty() {
        return Err(anyhow!("At least one parachute required"));
    }

    // Sort parachutes by name for consistent ordering
    let mut parachutes: Vec<_> = parachutes_map.iter().collect();
    parachutes.sort_by_key(|(name, _)| *name);

    let total_mass = raw.flight_simulator.rocket.mass.dry_weight;

    let mut parachute_configs = Vec::new();

    for (name, parachute) in parachutes {
        // Compute parachute area
        let area = if parachute.use_auto_parachute_area {
            let terminal_velocity = parachute
                .terminal_velocity
                .ok_or_else(|| anyhow!("Terminal velocity required for auto parachute area"))?;

            compute_parachute_area(
                terminal_velocity,
                parachute.parachute_drag_coefficient,
                total_mass,
            )
        } else {
            parachute
                .parachute_area
                .ok_or_else(|| anyhow!("Parachute area must be specified for parachute {}", name))?
        };

        parachute_configs.push(ParachuteConfig {
            name: name.clone(),
            parachute_full_deploy_time: Time::new::<second>(parachute.parachute_full_deploy_time),
            parachute_deploy_delay: Time::new::<second>(parachute.parachute_deploy_delay),
            parachute_drag_coefficient: parachute.parachute_drag_coefficient,
            area: Area::new::<square_meter>(area),
        });
    }

    Ok(parachute_configs)
}

/// Generate parachute area schedule from multi-stage parachute configs
/// Returns Vec<(Time, Area)>
///
/// The schedule accounts for:
/// - parachute_deploy_delay: time after apogee (or previous chute) when deployment starts
/// - parachute_full_deploy_time: time for linear deployment from 0 to full area
pub fn generate_parachute_area_schedule(parachutes: &[ParachuteConfig]) -> Vec<(Time, Area)> {
    let mut schedule = Vec::new();

    // Start with zero area at time 0
    schedule.push((Time::new::<second>(0.0), Area::new::<square_meter>(0.0)));

    let mut cumulative_time = 0.0;
    let mut total_area = Area::new::<square_meter>(0.0);

    for parachute in parachutes.iter() {
        // Deployment starts at cumulative_time + deploy_delay
        let deploy_delay_s = parachute.parachute_deploy_delay.get::<second>();
        let deploy_start = cumulative_time + deploy_delay_s;

        // Add point just before deployment starts (maintain current area)
        if deploy_start > cumulative_time {
            schedule.push((Time::new::<second>(deploy_start), total_area));
        }

        // Deployment ends at deploy_start + full_deploy_time
        let full_deploy_time_s = parachute.parachute_full_deploy_time.get::<second>();
        let deploy_end = deploy_start + full_deploy_time_s;

        // Add intermediate points for linear deployment
        let num_steps = 10; // Number of intermediate points
        let parachute_area_m2 = parachute.area.get::<square_meter>();

        for i in 1..=num_steps {
            let t = deploy_start + (deploy_end - deploy_start) * (i as f64 / num_steps as f64);
            let total_area_m2 = total_area.get::<square_meter>();
            let area_m2 = total_area_m2 + parachute_area_m2 * (i as f64 / num_steps as f64);
            schedule.push((Time::new::<second>(t), Area::new::<square_meter>(area_m2)));
        }

        // Update total area and cumulative time
        total_area =
            Area::new::<square_meter>(total_area.get::<square_meter>() + parachute_area_m2);
        cumulative_time = deploy_start; // Next parachute's delay is relative to this one's start

        // Add point at full deployment
        schedule.push((Time::new::<second>(deploy_end), total_area));
    }

    // Sort by time and remove duplicates
    schedule.sort_by(|a, b| {
        a.0.get::<second>()
            .partial_cmp(&b.0.get::<second>())
            .unwrap_or(std::cmp::Ordering::Equal)
    });
    schedule.dedup_by(|a, b| a.0.get::<second>() == b.0.get::<second>());

    schedule
}

fn process_aerodynamics(raw: &RawConfig, reference_area: f64) -> Result<AerodynamicsConfig> {
    let aero = &raw.flight_simulator.rocket.aerodynamics;

    let coeffs = &aero.coefficients;

    let ref_area = reference_area; // Use calculated reference area as base

    // Load or create fallback tables
    let normal_force_coefficient_mach_table =
        if let Some(table_path) = &coeffs.lift_coefficient_table {
            load_1d_table(table_path)?
        } else {
            vec![(0.0, coeffs.lift_coefficient_alpha)]
        };

    let side_force_coefficient_mach_table = if let Some(table_path) = &coeffs.side_coefficient_table
    {
        load_1d_table(table_path)?
    } else {
        vec![(0.0, coeffs.side_coefficient_beta)]
    };

    let drag_coefficient_zero_lift_table = if let Some(table_path) = &coeffs.drag_coefficient_table
    {
        load_2d_table(table_path)?
    } else {
        // Fallback to single-row table: [mach, alpha, cd]
        vec![vec![0.0, 0.0, coeffs.drag_coefficient]]
    };

    let mode = AerodynamicsMode::Coefficients {
        reference_area: Area::new::<square_meter>(ref_area),
        normal_force_coefficient_mach_table,
        side_force_coefficient_mach_table,
        drag_coefficient_zero_lift_table,
        roll_damping_coefficient: coeffs.roll_damping_coefficient,
        pitch_damping_coefficient: coeffs.pitch_damping_coefficient,
        yaw_damping_coefficient: coeffs.yaw_damping_coefficient,
    };

    Ok(AerodynamicsConfig { mode })
}

fn process_thrust(raw: &RawConfig) -> Result<ThrustConfig> {
    let t = &raw.flight_simulator.rocket.thrust;

    // Load thrust curve from CSV (time_s, thrust_N)
    let thrust_curve_n = load_1d_table(&t.thrust_curve).context("Failed to load thrust curve")?;

    // Convert to uom types
    let thrust_curve: Vec<(Time, Force)> = thrust_curve_n
        .iter()
        .map(|(time, thrust_n)| (Time::new::<second>(*time), Force::new::<newton>(*thrust_n)))
        .collect();

    // Compute fuel mass remaining schedule from thrust curve
    let fuel_mass_remaining_schedule = compute_fuel_remaining_schedule(
        &thrust_curve,
        raw.flight_simulator.rocket.mass.oxidizer_mass,
        t.cut_off_time,
    );

    // Compute liftoff time (when thrust > weight)
    let liftoff_time =
        compute_liftoff_time(&thrust_curve, raw.flight_simulator.rocket.mass.dry_weight);

    // Thruster position (assumed at CG for now, can be customized)
    let thruster_position_x = raw.flight_simulator.rocket.mass.cg.x;
    let thruster_position_y = raw.flight_simulator.rocket.mass.cg.y;
    let thruster_position_z = raw.flight_simulator.rocket.mass.cg.z;

    Ok(ThrustConfig {
        thrust_curve,
        fuel_mass_remaining_schedule,
        thruster_position_x: Length::new::<meter>(thruster_position_x),
        thruster_position_y: Length::new::<meter>(thruster_position_y),
        thruster_position_z: Length::new::<meter>(thruster_position_z),
        cut_off_time: Time::new::<second>(t.cut_off_time),
        liftoff_time,
    })
}

fn process_solver(raw: &RawConfig) -> Result<SolverConfig> {
    let s = &raw.flight_simulator.rocket.solver;

    Ok(SolverConfig {
        simulation_duration: Time::new::<second>(s.flight_duration),
        integration_time_step: Time::new::<second>(s.time_step),
        notify_interval: Time::new::<second>(s.notify_interval),
        output_rate: s.output_rate,
        terminate_at_apogee: s.apogee_mode != 0, // Convert u32 to bool
    })
}

fn process_construction(raw: &RawConfig) -> Option<ConstructionConfig> {
    raw.construction.as_ref().map(|c| ConstructionConfig {
        fin: c.rocket.fin.as_ref().map(|f| ConstructionFinConfig {
            half_span: Length::new::<meter>(f.half_span),
            root_chord: Length::new::<meter>(f.root_chord),
            tip_chord: Length::new::<meter>(f.tip_chord),
            drag_coefficient: f.drag_coefficient,
            lift_coefficient_alpha: f.lift_coefficient_alpha,
            modulus_of_elasticity: Pressure::new::<pascal>(f.modulus_of_elasticity),
            poisson_ratio: f.poisson_ratio,
        }),
        body: c.rocket.body.as_ref().map(|b| ConstructionBodyConfig {
            nose_shape: b.nose_shape.clone(),
            nose_length: Length::new::<meter>(b.nose_length),
            body_length: Length::new::<meter>(b.body_length),
            body_bending_stiffness: b.body_bending_stiffness,
        }),
        parachute: c
            .rocket
            .parachute
            .as_ref()
            .map(|p| ConstructionParachuteConfig {
                opening_shock_factor: p.opening_shock_factor,
            }),
    })
}

// ============================================================================
// Computation Functions
// ============================================================================

/// Compute reference area from diameter: A = π * (d/2)²
pub fn compute_reference_area(diameter: f64) -> f64 {
    PI * (diameter / 2.0).powi(2)
}

/// Compute parachute area from terminal velocity
/// Formula: A = (2 * m * g) / (ρ * Cd * v_t²)
/// Assuming standard atmosphere at sea level: ρ = 1.225 kg/m³, g = 9.81 m/s²
pub fn compute_parachute_area(terminal_velocity: f64, drag_coefficient: f64, mass: f64) -> f64 {
    const G: f64 = 9.81; // m/s²
    const RHO: f64 = 1.225; // kg/m³ (sea level)

    (2.0 * mass * G) / (RHO * drag_coefficient * terminal_velocity.powi(2))
}

/// Generate wind profile from power law
/// Returns Vec<(Length, Velocity, Angle)>
pub fn generate_wind_profile_from_power_law(
    wind_ref_altitude: f64,
    ground_wind_dir: f64,
    ground_wind_speed: f64,
    wind_power_factor: f64,
) -> Vec<(Length, Velocity, Angle)> {
    let mut profile = Vec::new();

    // Convert ground wind direction to Angle
    let ground_wind_dir_angle = Angle::new::<degree>(ground_wind_dir);

    // Generate profile from 0 to 10000m in 100m increments
    for altitude in (0..=10000).step_by(100) {
        let altitude_m = altitude as f64;
        let speed_m_s = if altitude_m <= wind_ref_altitude {
            ground_wind_speed
        } else {
            ground_wind_speed * (altitude_m / wind_ref_altitude).powf(wind_power_factor)
        };

        profile.push((
            Length::new::<meter>(altitude_m),
            Velocity::new::<meter_per_second>(speed_m_s),
            ground_wind_dir_angle,
        ));
    }

    profile
}

/// Compute fuel remaining schedule from thrust curve
/// Returns Vec<(Time, fuel_fraction)> where fuel_fraction is 0.0 to 1.0
pub fn compute_fuel_remaining_schedule(
    thrust_curve: &[(Time, Force)],
    oxidizer_mass: f64,
    cut_off_time: f64,
) -> Vec<(Time, f64)> {
    if thrust_curve.is_empty() {
        return vec![
            (Time::new::<second>(0.0), 1.0),
            (Time::new::<second>(cut_off_time), 0.0),
        ];
    }

    // Calculate total impulse to determine burn rate
    let total_impulse: f64 = thrust_curve
        .windows(2)
        .map(|w| {
            let dt = w[1].0.get::<second>() - w[0].0.get::<second>();
            let avg_thrust = (w[0].1.get::<newton>() + w[1].1.get::<newton>()) / 2.0;
            avg_thrust * dt
        })
        .sum();

    // Approximate specific impulse (simplified)
    let isp = 200.0; // seconds (typical hybrid rocket)
    let g0 = 9.81; // m/s²

    let total_propellant_consumed = total_impulse / (isp * g0);
    let burn_rate = total_propellant_consumed / oxidizer_mass;

    let mut schedule = Vec::new();
    let mut consumed_fraction = 0.0;

    for &(time, thrust) in thrust_curve.iter() {
        let time_s = time.get::<second>();
        let thrust_n = thrust.get::<newton>();

        if time_s >= cut_off_time {
            break;
        }

        schedule.push((time, 1.0 - consumed_fraction));

        // Update consumed fraction based on thrust
        if thrust_n > 0.0 {
            consumed_fraction += burn_rate * 0.01; // Simplified increment
            consumed_fraction = consumed_fraction.min(1.0);
        }
    }

    // Add final point
    schedule.push((Time::new::<second>(cut_off_time), 0.0));

    schedule
}

/// Compute liftoff time (when thrust exceeds weight)
/// thrust_curve is in (Time, Force)
/// mass is in kg
pub fn compute_liftoff_time(thrust_curve: &[(Time, Force)], mass_kg: f64) -> Time {
    const G: f64 = 9.81; // m/s²
    let weight_n = mass_kg * G;

    for &(time, thrust) in thrust_curve.iter() {
        let thrust_n = thrust.get::<newton>();
        if thrust_n > weight_n {
            return time;
        }
    }

    // Default to first time in curve
    thrust_curve
        .first()
        .map(|&(t, _)| t)
        .unwrap_or(Time::new::<second>(0.0))
}

// ============================================================================
// Table Loading Functions
// ============================================================================

/// Load 1D table from CSV file
/// Expected format: two columns (x, y)
/// Automatically skips header row if first column cannot be parsed as float
pub fn load_1d_table<P: AsRef<Path>>(path: P) -> Result<Vec<(f64, f64)>> {
    let file = File::open(path.as_ref())
        .with_context(|| format!("Failed to open file: {:?}", path.as_ref()))?;
    let reader = BufReader::new(file);

    let mut table = Vec::new();
    let mut is_first_line = true;

    for (line_num, line_result) in reader.lines().enumerate() {
        let line = line_result?;
        let line = line.trim();

        // Skip empty lines and comments
        if line.is_empty() || line.starts_with('#') {
            continue;
        }

        let parts: Vec<&str> = line.split(',').map(|s| s.trim()).collect();

        if parts.len() < 2 {
            return Err(anyhow!(
                "Invalid 1D table format at line {}: expected 2 columns, got {}",
                line_num + 1,
                parts.len()
            ));
        }

        // Try to parse first column - if it fails on first data line, skip as header
        let x_result: Result<f64, _> = parts[0].parse();
        let y_result: Result<f64, _> = parts[1].parse();

        if is_first_line && (x_result.is_err() || y_result.is_err()) {
            // Skip header row
            is_first_line = false;
            continue;
        }

        is_first_line = false;

        let x: f64 = x_result
            .with_context(|| format!("Failed to parse first column at line {}", line_num + 1))?;
        let y: f64 = y_result
            .with_context(|| format!("Failed to parse second column at line {}", line_num + 1))?;

        table.push((x, y));
    }

    // Sort by first column and remove duplicates
    table.sort_by(|a, b| a.0.partial_cmp(&b.0).unwrap_or(std::cmp::Ordering::Equal));
    table.dedup_by(|a, b| a.0 == b.0);

    Ok(table)
}

/// Load 2D table from CSV file
/// Expected format: CSV with optional header row, data rows with [row_index, col1, col2, ...]
/// Returns: Vec<Vec<f64>> where each inner vec is a row [mach, alpha1, alpha2, ...]
/// Automatically skips header row and empty cells
pub fn load_2d_table<P: AsRef<Path>>(path: P) -> Result<Vec<Vec<f64>>> {
    let file = File::open(path.as_ref())
        .with_context(|| format!("Failed to open file: {:?}", path.as_ref()))?;
    let reader = BufReader::new(file);

    let mut table = Vec::new();
    let mut is_first_line = true;

    for (_line_num, line_result) in reader.lines().enumerate() {
        let line = line_result?;
        let line = line.trim();

        // Skip empty lines and comments
        if line.is_empty() || line.starts_with('#') {
            continue;
        }

        let parts: Vec<&str> = line.split(',').map(|s| s.trim()).collect();
        let mut row = Vec::new();
        let mut all_empty_or_non_numeric = true;

        for part in parts.iter() {
            if part.is_empty() {
                continue; // Skip empty cells
            }

            match part.parse::<f64>() {
                Ok(value) => {
                    row.push(value);
                    all_empty_or_non_numeric = false;
                }
                Err(_) => {
                    // Non-numeric value, likely header
                    if !is_first_line {
                        // Only allow non-numeric in first line (header)
                        continue;
                    }
                }
            }
        }

        if is_first_line && all_empty_or_non_numeric {
            // Skip header row
            is_first_line = false;
            continue;
        }

        is_first_line = false;

        if !row.is_empty() {
            table.push(row);
        }
    }

    // Sort by first column (mach number) and remove duplicates
    if !table.is_empty() && !table[0].is_empty() {
        table.sort_by(|a, b| a[0].partial_cmp(&b[0]).unwrap_or(std::cmp::Ordering::Equal));
        table.dedup_by(|a, b| a[0] == b[0]);
    }

    Ok(table)
}

/// Load wind table from CSV file
/// Expected format: three columns (altitude_m, speed_m/s, direction_deg)
/// Returns: Vec<(Length, Velocity, Angle)>
/// Automatically skips header row
pub fn load_wind_table<P: AsRef<Path>>(path: P) -> Result<Vec<(Length, Velocity, Angle)>> {
    let file = File::open(path.as_ref())
        .with_context(|| format!("Failed to open file: {:?}", path.as_ref()))?;
    let reader = BufReader::new(file);

    let mut table = Vec::new();
    let mut is_first_line = true;

    for (line_num, line_result) in reader.lines().enumerate() {
        let line = line_result?;
        let line = line.trim();

        // Skip empty lines and comments
        if line.is_empty() || line.starts_with('#') {
            continue;
        }

        let parts: Vec<&str> = line.split(',').map(|s| s.trim()).collect();

        if parts.len() < 3 {
            return Err(anyhow!(
                "Invalid wind table format at line {}: expected 3 columns, got {}",
                line_num + 1,
                parts.len()
            ));
        }

        // Try to parse - if it fails on first data line, skip as header
        let altitude_result: Result<f64, _> = parts[0].parse();
        let speed_result: Result<f64, _> = parts[1].parse();
        let direction_result: Result<f64, _> = parts[2].parse();

        if is_first_line
            && (altitude_result.is_err() || speed_result.is_err() || direction_result.is_err())
        {
            // Skip header row
            is_first_line = false;
            continue;
        }

        is_first_line = false;

        let altitude_m: f64 = altitude_result
            .with_context(|| format!("Failed to parse altitude at line {}", line_num + 1))?;
        let speed_m_s: f64 = speed_result
            .with_context(|| format!("Failed to parse speed at line {}", line_num + 1))?;
        let direction_deg: f64 = direction_result
            .with_context(|| format!("Failed to parse direction at line {}", line_num + 1))?;

        // Create uom types
        table.push((
            Length::new::<meter>(altitude_m),
            Velocity::new::<meter_per_second>(speed_m_s),
            Angle::new::<degree>(direction_deg),
        ));
    }

    // Sort by altitude and remove duplicates
    table.sort_by(|a, b| {
        a.0.get::<meter>()
            .partial_cmp(&b.0.get::<meter>())
            .unwrap_or(std::cmp::Ordering::Equal)
    });
    table.dedup_by(|a, b| a.0.get::<meter>() == b.0.get::<meter>());

    Ok(table)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_compute_reference_area() {
        let diameter = 0.145;
        let area = compute_reference_area(diameter);
        let expected = PI * (0.145_f64 / 2.0_f64).powi(2);
        assert!((area - expected).abs() < 1e-10);
    }

    #[test]
    fn test_compute_parachute_area() {
        let terminal_velocity = 20.0;
        let drag_coefficient = 1.2;
        let mass = 20.0;

        let area = compute_parachute_area(terminal_velocity, drag_coefficient, mass);

        assert!(area > 0.0);
        assert!(area < 100.0);
    }

    #[test]
    fn test_generate_wind_profile_from_power_law() {
        let profile = generate_wind_profile_from_power_law(2.0, 45.0, 5.0, 0.16666);

        assert!(!profile.is_empty());
        // Check first entry has correct values
        assert_eq!(profile[0].0.get::<meter>(), 0.0);
        assert_eq!(profile[0].1.get::<meter_per_second>(), 5.0);
        assert_eq!(profile[0].2.get::<degree>(), 45.0);
    }
}
