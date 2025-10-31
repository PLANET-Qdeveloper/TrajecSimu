use anyhow::Result;
use trajecsim_rs::jsbsim::JSBSimExecutive;
use trajecsim_rs::output::{DataCollector, FlightTrajectory, TrajectoryMetadata};
use std::fs;

fn main() -> Result<()> {
    println!("Full Simulation with Data Collection Example\n");

    // Create JSBSim executive
    println!("1. Initializing JSBSim...");
    let mut exec = JSBSimExecutive::new()?;
    exec.set_dt(0.01); // 10ms time step
    println!("   ✓ JSBSim initialized with dt=0.01s\n");

    // Create data collector
    let collector = DataCollector::new();

    // Create trajectory to store results
    let metadata = TrajectoryMetadata {
        simulation_id: "full_sim_001".to_string(),
        time_step_s: 0.01,
        launch_latitude_deg: 35.0,
        launch_longitude_deg: 139.0,
        launch_altitude_m: 100.0,
        wind_speed_ms: 5.0,
        wind_direction_deg: 270.0,
        rocket_config: "example_rocket".to_string(),
    };

    let mut trajectory = FlightTrajectory::new("full_simulation".to_string(), metadata);
    println!("2. Trajectory initialized");
    println!("   Simulation ID: {}", trajectory.metadata.simulation_id);
    println!("   Launch site:   {:.6}°N, {:.6}°E",
             trajectory.metadata.launch_latitude_deg,
             trajectory.metadata.launch_longitude_deg);
    println!();

    // Simulate for a few seconds without a model
    // In a real simulation, you would:
    // 1. Load a rocket model: exec.load_model("my_rocket")?;
    // 2. Set initial conditions
    // 3. Call exec.run_ic()?;
    // 4. Loop with exec.run()?;

    println!("3. Running simulation loop...");
    // Note: Without a loaded model, JSBSim won't advance time with run()
    // In a real simulation, you would load a model and use exec.run()
    // For this demo, we collect a few sample frames at the initial state

    let num_samples = 10;
    println!("   Collecting {} sample frames (demonstration only)", num_samples);

    for i in 0..num_samples {
        match collector.collect_frame(&exec) {
            Ok(frame) => {
                let time = frame.time;
                trajectory.add_frame(frame);
                if i == 0 || i == num_samples - 1 {
                    println!("   ✓ Frame {} collected at t={:.2}s", i, time);
                }
            }
            Err(e) => {
                eprintln!("   Warning: Could not collect frame {}: {}", i, e);
            }
        }
    }

    // In a real simulation with a loaded model, you would do:
    // while exec.run()? {
    //     if frame_count % collect_interval == 0 {
    //         let frame = collector.collect_frame(&exec)?;
    //         trajectory.add_frame(frame);
    //     }
    //     frame_count += 1;
    // }

    println!("   ✓ Simulation completed");
    println!("   Total frames collected: {}", trajectory.frames.len());
    println!();

    // Analyze results
    println!("4. Analyzing trajectory...");

    if let Some(max_alt_frame) = trajectory.get_apogee() {
        println!("   Max Altitude: {:.2} m at t={:.2}s",
                 max_alt_frame.position.altitude_asl_m,
                 max_alt_frame.time);
    }

    if let Some(max_vel) = trajectory.get_max_velocity() {
        println!("   Max Velocity: {:.2} m/s", max_vel);
    }

    if let Some((lat, lon)) = trajectory.get_landing_position() {
        println!("   Landing Position: {:.6}°N, {:.6}°E", lat, lon);
    }

    if let Some(duration) = trajectory.get_flight_duration() {
        println!("   Flight Duration: {:.2} s", duration);
    }

    println!();

    // Save results
    println!("5. Saving results...");

    // Save full trajectory as JSON
    let output_dir = "output";
    fs::create_dir_all(output_dir)?;

    let json_path = format!("{}/trajectory_full.json", output_dir);
    let json = serde_json::to_string_pretty(&trajectory)?;
    fs::write(&json_path, json)?;
    println!("   ✓ Full trajectory saved to: {}", json_path);

    // Save summary as CSV
    let summary = trajectory.to_summary();
    let csv_path = format!("{}/trajectory_summary.csv", output_dir);
    let mut writer = csv::Writer::from_path(&csv_path)?;
    for record in summary {
        writer.serialize(record)?;
    }
    writer.flush()?;
    println!("   ✓ Summary saved to: {}", csv_path);

    println!();
    println!("=== Simulation Complete ===");
    println!("Full trajectory data: {}", json_path);
    println!("Summary CSV:          {}", csv_path);

    Ok(())
}
