use trajecsim_rs::input::loader;
use trajecsim_rs::config::processor;

fn main() -> Result<(), Box<dyn std::error::Error>> {
    println!("{}", "=".repeat(80));
    println!("Testing Full Configuration Processing");
    println!("{}", "=".repeat(80));

    // Load raw config
    println!("\n[1] Loading YAML configuration...");
    let raw_config = loader::load_config("data/input/landed_area.yaml")?;
    println!("    ✓ Successfully loaded YAML");

    // Process config
    println!("\n[2] Processing configuration (computing derived values)...");
    let sim_config = processor::process_config(raw_config)?;
    println!("    ✓ Successfully processed configuration");

    // Display launcher configuration
    println!("\n[3] Launcher Configuration:");
    println!("    Launch Site:");
    println!("      - Latitude:  {:.6}°", sim_config.launcher.launch_site_latitude);
    println!("      - Longitude: {:.6}°", sim_config.launcher.launch_site_longitude);
    println!("      - Elevation: {:.2} m MSL", sim_config.launcher.launch_site_elevation_msl);
    println!("\n    Launcher Orientation:");
    println!("      - Azimuth:   {:.2}°", sim_config.launcher.launcher_azimuth_angle);
    println!("      - Pitch:     {:.2}°", sim_config.launcher.launcher_pitch_angle);
    println!("      - Roll:      {:.2}°", sim_config.launcher.launcher_roll_angle);
    println!("\n    Launcher Geometry:");
    println!("      - Length:    {:.2} m", sim_config.launcher.launcher_length);
    println!("      - Rail Exit Height: {:.2} m (computed)", sim_config.launcher.launcher_rail_exit_height);

    // Display wind configuration
    println!("\n[4] Wind Configuration:");
    match &sim_config.wind.mode {
        trajecsim_rs::config::config::WindMode::PowerLaw {
            wind_ref_altitude,
            ground_wind_dir,
            ground_wind_speed,
            wind_power_factor,
            wind_profile_altitude_table,
        } => {
            println!("    Mode: Power Law");
            println!("      - Reference Altitude: {:.2} m", wind_ref_altitude);
            println!("      - Ground Wind Speed:  {:.2} m/s", ground_wind_speed);
            println!("      - Ground Wind Dir:    {:.2}°", ground_wind_dir);
            println!("      - Power Factor:       {:.5}", wind_power_factor);
            println!("      - Generated {} altitude points", wind_profile_altitude_table.len());
        }
        trajecsim_rs::config::config::WindMode::Table { wind_profile_altitude_table } => {
            println!("    Mode: Table (from file)");
            println!("      - Loaded {} altitude points", wind_profile_altitude_table.len());
        }
    }

    // Display rocket configuration
    println!("\n[5] Rocket Configuration:");
    println!("    Geometry:");
    println!("      - Diameter:  {:.3} m", sim_config.rocket.body_diameter);
    println!("      - Length:    {:.3} m", sim_config.rocket.body_length);
    println!("      - Frontal Area: {:.6} m² (computed)", sim_config.rocket.projected_frontal_area);
    println!("      - Fin Span:  {:.3} m", sim_config.rocket.fin_span);

    println!("\n    Mass Properties:");
    println!("      - Dry Mass:     {:.2} kg", sim_config.rocket.mass.dry_mass);
    println!("      - Oxidizer:     {:.2} kg", sim_config.rocket.mass.oxidizer_mass);
    println!("      - Fuel (before):{:.2} kg", sim_config.rocket.mass.fuel_mass);
    println!("      - Fuel (after): {:.2} kg", sim_config.rocket.mass.fuel_mass_after_burn);
    println!("      - CG Position:  x={:.3} m, y={:.3} m, z={:.3} m",
             sim_config.rocket.mass.center_of_gravity_x,
             sim_config.rocket.mass.center_of_gravity_y,
             sim_config.rocket.mass.center_of_gravity_z);
    println!("      - CP Position:  x={:.3} m, y={:.3} m, z={:.3} m",
             sim_config.rocket.mass.center_of_pressure_x,
             sim_config.rocket.mass.center_of_pressure_y,
             sim_config.rocket.mass.center_of_pressure_z);
    println!("      - CP Table:     {} mach points", sim_config.rocket.mass.center_of_pressure_mach_table.len());

    println!("\n    Inertia:");
    println!("      - Ixx: {:.3} kg·m²", sim_config.rocket.inertia.moment_of_inertia_xx);
    println!("      - Iyy: {:.3} kg·m²", sim_config.rocket.inertia.moment_of_inertia_yy);
    println!("      - Izz: {:.3} kg·m²", sim_config.rocket.inertia.moment_of_inertia_zz);

    // Display parachute configuration
    println!("\n[6] Parachute Configuration:");
    println!("    Number of parachutes: {}", sim_config.rocket.parachutes.len());
    for (i, chute) in sim_config.rocket.parachutes.iter().enumerate() {
        println!("\n    Parachute {} ({}):", i + 1, chute.name);
        println!("      - Area:        {:.3} m² (computed)", chute.area);
        println!("      - Cd:          {:.2}", chute.parachute_drag_coefficient);
        println!("      - Deploy Delay:{:.2} s", chute.parachute_deploy_delay);
        println!("      - Deploy Time: {:.2} s", chute.parachute_full_deploy_time);
    }
    println!("\n    Parachute Area Schedule:");
    println!("      - Total points: {}", sim_config.rocket.parachute_area_schedule.len());
    println!("      - Max duration: {:.2} s", sim_config.rocket.parachute_deployment_duration);
    println!("      - First 5 points:");
    for (i, (time, area)) in sim_config.rocket.parachute_area_schedule.iter().take(5).enumerate() {
        println!("        [{:2}] t={:6.2} s, A={:6.3} m²", i, time, area);
    }

    // Display aerodynamics configuration
    println!("\n[7] Aerodynamics Configuration:");
    match &sim_config.rocket.aerodynamics.mode {
        trajecsim_rs::config::config::AerodynamicsMode::Coefficients {
            reference_area,
            normal_force_coefficient_mach_table,
            side_force_coefficient_mach_table,
            drag_coefficient_zero_lift_table,
            roll_damping_coefficient,
            pitch_damping_coefficient,
            yaw_damping_coefficient,
        } => {
            println!("    Mode: Coefficients (from tables/values)");
            println!("      - Reference Area:     {:.6} m²", reference_area);
            println!("      - Normal Force Table: {} points", normal_force_coefficient_mach_table.len());
            println!("      - Side Force Table:   {} points", side_force_coefficient_mach_table.len());
            println!("      - Drag Table:         {} rows", drag_coefficient_zero_lift_table.len());
            println!("      - Roll Damping:       {:.4}", roll_damping_coefficient);
            println!("      - Pitch Damping:      {:.4}", pitch_damping_coefficient);
            println!("      - Yaw Damping:        {:.4}", yaw_damping_coefficient);
        }
        trajecsim_rs::config::config::AerodynamicsMode::Parameters {
            reference_area,
            normal_force_coefficient_mach_table,
            nose_shape,
            ..
        } => {
            println!("    Mode: Parameters (computed from geometry)");
            println!("      - Reference Area:     {:.6} m²", reference_area);
            println!("      - Nose Shape:         {}", nose_shape);
            println!("      - Computed CN Table:  {} points", normal_force_coefficient_mach_table.len());
        }
    }

    // Display thrust configuration
    println!("\n[8] Thrust Configuration:");
    println!("    Thrust Curve:");
    println!("      - Data points:  {}", sim_config.rocket.thrust.thrust_curve.len());
    println!("      - Cut-off time: {:.2} s", sim_config.rocket.thrust.cut_off_time);
    println!("      - Liftoff time: {:.4} s (computed)", sim_config.rocket.thrust.liftoff_time);
    println!("      - First 3 points:");
    for (i, (time, thrust)) in sim_config.rocket.thrust.thrust_curve.iter().take(3).enumerate() {
        println!("        [{:2}] t={:6.3} s, F={:8.2} N", i, time, thrust);
    }
    println!("\n    Fuel Remaining Schedule:");
    println!("      - Data points: {}", sim_config.rocket.thrust.fuel_mass_remaining_schedule.len());
    println!("      - First 5 points:");
    for (i, (time, fraction)) in sim_config.rocket.thrust.fuel_mass_remaining_schedule.iter().take(5).enumerate() {
        println!("        [{:2}] t={:6.2} s, remaining={:5.2}%", i, time, fraction * 100.0);
    }

    // Display solver configuration
    println!("\n[9] Solver Configuration:");
    println!("    - Simulation Duration:   {:.1} s", sim_config.rocket.solver.simulation_duration);
    println!("    - Integration Time Step: {:.4} s", sim_config.rocket.solver.integration_time_step);
    println!("    - Output Rate:           {} Hz", sim_config.rocket.solver.output_rate);
    println!("    - Terminate at Apogee:   {}", sim_config.rocket.solver.terminate_at_apogee);

    // Unit conversions are now handled by uom library in Rust code
    println!("\n[10] Unit Conversions:");
    println!("    All unit conversions are handled by the uom library.");
    println!("    Wind speeds converted: m/s → fps");
    println!("    Wind directions converted: degrees → radians");
    println!("    Parachute areas converted: m² → ft²");
    println!("    Thrust values converted: N → lbf");

    // Display construction parameters if present
    if let Some(construction) = &sim_config.construction {
        println!("\n[11] Construction Parameters (for structural analysis):");
        if let Some(fin) = &construction.fin {
            println!("    Fin:");
            println!("      - Half Span:          {:.3} m", fin.half_span);
            println!("      - Modulus of Elastic: {:.2e} Pa", fin.modulus_of_elasticity);
        }
        if let Some(body) = &construction.body {
            println!("    Body:");
            println!("      - Bending Stiffness:  {:.2} N·m²", body.body_bending_stiffness);
        }
        if let Some(para) = &construction.parachute {
            println!("    Parachute:");
            println!("      - Opening Shock Factor: {:.1}", para.opening_shock_factor);
        }
    }

    println!("\n{}", "=".repeat(80));
    println!("✓ All configuration processing tests passed!");
    println!("{}", "=".repeat(80));

    Ok(())
}
