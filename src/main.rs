use anyhow::Result;
use clap::Parser;
use std::path::PathBuf;

use trajecsim_rs::input::{loader, validator};
use trajecsim_rs::config::processor;
use trajecsim_rs::simulation::runner::JsbsimRunner;
use trajecsim_rs::output::{processor::OutputProcessor, analyzer::OutputAnalyzer};

#[derive(Parser, Debug)]
#[command(author, version, about, long_about = None)]
struct Args {
    /// Path to configuration YAML file
    #[arg(short, long)]
    config: PathBuf,

    /// Output directory for simulation results
    #[arg(short, long, default_value = "output")]
    output_dir: PathBuf,
}

fn main() -> Result<()> {
    let args = Args::parse();

    // Load and validate configuration
    println!("Loading configuration from: {:?}", args.config);
    let raw_config = loader::load_config(&args.config)?;
    validator::validate_config(&raw_config)?;
    println!("Configuration loaded and validated successfully");

    // Process configuration
    println!("Processing configuration...");
    let config = processor::process_config(raw_config)?;
    println!("Configuration processed successfully");

    // Create output directory if it doesn't exist
    std::fs::create_dir_all(&args.output_dir)?;

    // Setup simulation runner
    println!("Setting up simulation runner...");
    let runner = JsbsimRunner::new(&args.output_dir)?;

    // Prepare and run simulation
    println!("Preparing simulation files...");
    let sim_files = runner.prepare_simulation(&config)?;
    println!("Aircraft XML: {:?}", sim_files.aircraft);
    println!("Simulation XML: {:?}", sim_files.simulation);

    println!("Running simulation...");
    let output_file = runner.run_simulation(&sim_files)?;
    println!("Simulation completed. Output: {:?}", output_file);

    // Process results
    println!("Processing results...");
    let processor = OutputProcessor::new();
    let data = processor.read_csv(&output_file)?;

    // Analyze results
    let analyzer = OutputAnalyzer::new();
    if let Some(stats) = analyzer.analyze(&data) {
        println!("\n=== Flight Statistics ===");
        println!("Max Altitude: {:.2} m", stats.max_altitude);
        println!("Max Velocity: {:.2} m/s", stats.max_velocity);
        println!("Landing Position: ({:.6}, {:.6})",
                 stats.landing_latitude, stats.landing_longitude);
        println!("Flight Time: {:.2} s", stats.flight_time);
    }

    if let Some(apogee) = analyzer.find_apogee(&data) {
        println!("\n=== Apogee ===");
        println!("Time: {:.2} s", apogee.time);
        println!("Altitude: {:.2} m", apogee.altitude);
    }

    println!("\nSimulation complete!");
    Ok(())
}
