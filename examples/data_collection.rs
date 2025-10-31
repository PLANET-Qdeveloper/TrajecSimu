use anyhow::Result;
use trajecsim_rs::jsbsim::JSBSimExecutive;
use trajecsim_rs::output::{DataCollector, FlightTrajectory, TrajectoryMetadata};

fn main() -> Result<()> {
    println!("JSBSim Data Collection Example\n");

    // Create JSBSim executive
    println!("Creating JSBSim executive...");
    let exec = JSBSimExecutive::new()?;
    println!("✓ JSBSim executive created\n");

    // Create data collector
    let collector = DataCollector::new();
    println!("✓ Data collector initialized\n");

    // Collect a single frame of data
    println!("Collecting simulation data frame...");
    match collector.collect_frame(&exec) {
        Ok(frame) => {
            println!("✓ Data frame collected successfully\n");

            // Display collected data
            println!("=== Simulation Frame Data ===\n");

            println!("Time: {:.2} s", frame.time);

            println!("\n--- Position ---");
            println!("  Altitude ASL: {:.2} m", frame.position.altitude_asl_m);
            println!("  Latitude:     {:.6}°", frame.position.latitude_deg);
            println!("  Longitude:    {:.6}°", frame.position.longitude_deg);

            println!("\n--- Attitude ---");
            println!("  Roll (φ):     {:.2}°", frame.attitude.phi_deg);
            println!("  Pitch (θ):    {:.2}°", frame.attitude.theta_deg);
            println!("  Yaw (ψ):      {:.2}°", frame.attitude.psi_deg);

            println!("\n--- Velocity ---");
            println!("  Total:        {:.2} m/s", frame.velocity.v_total_ms);
            println!("  North:        {:.2} m/s", frame.velocity.v_north_ms);
            println!("  East:         {:.2} m/s", frame.velocity.v_east_ms);
            println!("  Down:         {:.2} m/s", frame.velocity.v_down_ms);

            println!("\n--- Angular Rates ---");
            println!("  P (roll):     {:.2} °/s", frame.rates.p_degs);
            println!("  Q (pitch):    {:.2} °/s", frame.rates.q_degs);
            println!("  R (yaw):      {:.2} °/s", frame.rates.r_degs);

            println!("\n--- Atmosphere ---");
            println!("  Density:      {:.4} kg/m³", frame.atmosphere.rho_kgm3);
            println!("  Temperature:  {:.2} K", frame.atmosphere.temperature_k);
            println!("  Pressure:     {:.2} Pa", frame.atmosphere.pressure_ambient_pa);

            println!("\n--- Mass Properties ---");
            println!("  Mass:         {:.2} kg", frame.mass_props.mass_kg);
            println!("  Weight:       {:.2} N", frame.mass_props.weight_n);
            println!("  CG X:         {:.3} m", frame.mass_props.x_cg_m);

            println!("\n--- Propulsion ---");
            println!("  Thrust:       {:.2} N", frame.propulsion.thrust_n);
            println!("  Engine:       {}", if frame.propulsion.engine_running { "ON" } else { "OFF" });

            println!("\n--- Custom Properties ---");
            println!("  Parachute Area: {:.2} m²", frame.custom.parachute_area_m2);
            println!("  Parachute:      {}", if frame.custom.parachute_deployed { "DEPLOYED" } else { "STOWED" });
            println!("  Flight Phase:   {}", match frame.custom.flight_phase {
                0 => "Boost",
                1 => "Coast",
                2 => "Descent",
                3 => "Landed",
                _ => "Unknown",
            });
        }
        Err(e) => {
            println!("⚠ Warning: Could not collect all data properties");
            println!("  This is expected for a fresh JSBSim instance without a loaded model");
            println!("  Error: {}", e);
            println!("\n  To collect complete data, you need to:");
            println!("  1. Load an aircraft/rocket model");
            println!("  2. Set initial conditions");
            println!("  3. Run the simulation");
        }
    }

    // Demonstrate trajectory collection (conceptual)
    println!("\n\n=== Flight Trajectory Collection ===\n");

    let metadata = TrajectoryMetadata {
        simulation_id: "example_001".to_string(),
        time_step_s: 0.01,
        launch_latitude_deg: 35.0,
        launch_longitude_deg: 139.0,
        launch_altitude_m: 100.0,
        wind_speed_ms: 5.0,
        wind_direction_deg: 270.0,
        rocket_config: "test_rocket".to_string(),
    };

    let trajectory = FlightTrajectory::new("example_sim".to_string(), metadata);

    println!("✓ Trajectory metadata initialized");
    println!("  Simulation ID: {}", trajectory.metadata.simulation_id);
    println!("  Time step:     {:.3} s", trajectory.metadata.time_step_s);
    println!("  Launch site:   {:.6}°, {:.6}°",
             trajectory.metadata.launch_latitude_deg,
             trajectory.metadata.launch_longitude_deg);

    println!("\n  During simulation, frames would be collected with:");
    println!("  ```");
    println!("  let frame = collector.collect_frame(&exec)?;");
    println!("  trajectory.add_frame(frame);");
    println!("  ```");

    println!("\n✓ Data collection system ready for integration");

    Ok(())
}
