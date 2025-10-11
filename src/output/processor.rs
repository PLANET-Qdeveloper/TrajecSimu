use anyhow::Result;
use csv::ReaderBuilder;
use serde::{Deserialize, Serialize};
use std::path::Path;

#[derive(Debug, Deserialize, Serialize, Clone)]
pub struct SimulationOutput {
    pub time: f64,
    pub altitude: f64,
    pub velocity: f64,
    pub latitude: f64,
    pub longitude: f64,
    // Add more fields as needed based on JSBSim output
}

pub struct OutputProcessor;

impl OutputProcessor {
    pub fn new() -> Self {
        Self
    }

    pub fn read_csv<P: AsRef<Path>>(&self, path: P) -> Result<Vec<SimulationOutput>> {
        let mut reader = ReaderBuilder::new()
            .has_headers(true)
            .from_path(path)?;

        let mut records = Vec::new();
        for result in reader.deserialize() {
            let record: SimulationOutput = result?;
            records.push(record);
        }

        Ok(records)
    }

    pub fn write_csv<P: AsRef<Path>>(&self, path: P, data: &[SimulationOutput]) -> Result<()> {
        let mut writer = csv::Writer::from_path(path)?;

        for record in data {
            writer.serialize(record)?;
        }

        writer.flush()?;
        Ok(())
    }
}

impl Default for OutputProcessor {
    fn default() -> Self {
        Self::new()
    }
}
