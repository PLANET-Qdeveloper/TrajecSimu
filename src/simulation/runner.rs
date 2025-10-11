use anyhow::{Context, Result};
use rayon::prelude::*;
use std::path::{Path, PathBuf};
use std::process::Command;

use crate::config::config::SimulationConfig;
use super::template;

pub struct JsbsimRunner {
    output_dir: PathBuf,
}

impl JsbsimRunner {
    pub fn new<P: AsRef<Path>>(output_dir: P) -> Result<Self> {
        Ok(Self {
            output_dir: output_dir.as_ref().to_path_buf(),
        })
    }

    pub fn prepare_simulation(&self, config: &SimulationConfig) -> Result<SimulationFiles> {
        // Render templates using Askama
        let (aircraft_xml, simulation_xml, liftoff_xml) = template::render_jsbsim_files(config)?;

        // Write XML files
        let aircraft_dir = self.output_dir.join("aircraft/PQ_ROCKET");
        std::fs::create_dir_all(&aircraft_dir)?;

        let aircraft_path = aircraft_dir.join("pq_rocket.xml");
        let liftoff_path = aircraft_dir.join("liftoff.xml");
        let simulation_path = self.output_dir.join("pq_simulation.xml");

        std::fs::write(&aircraft_path, aircraft_xml)?;
        std::fs::write(&liftoff_path, liftoff_xml)?;
        std::fs::write(&simulation_path, simulation_xml)?;

        Ok(SimulationFiles {
            aircraft: aircraft_path,
            liftoff: liftoff_path,
            simulation: simulation_path,
        })
    }

    pub fn run_simulation(&self, files: &SimulationFiles) -> Result<PathBuf> {
        let output = Command::new("jsbsim")
            .arg("--script")
            .arg(&files.simulation)
            .arg("--logdirectivefile")
            .arg(&self.output_dir.join("output_directives.xml"))
            .current_dir(&self.output_dir)
            .output()
            .context("Failed to execute JSBSim")?;

        if !output.status.success() {
            anyhow::bail!(
                "JSBSim failed: {}",
                String::from_utf8_lossy(&output.stderr)
            );
        }

        Ok(self.output_dir.join("pq_rocket_output.csv"))
    }

    pub fn run_parallel_simulations(&self, configs: Vec<SimulationConfig>) -> Vec<Result<PathBuf>> {
        configs
            .par_iter()
            .map(|config| {
                let files = self.prepare_simulation(config)?;
                self.run_simulation(&files)
            })
            .collect()
    }
}

#[derive(Debug)]
pub struct SimulationFiles {
    pub aircraft: PathBuf,
    pub liftoff: PathBuf,
    pub simulation: PathBuf,
}
