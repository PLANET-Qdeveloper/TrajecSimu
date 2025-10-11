use anyhow::Result;
use std::fs::File;
use std::path::Path;

use super::schema::InputParameter;

pub fn load_config<P: AsRef<Path>>(path: P) -> Result<InputParameter> {
    let file = File::open(path)?;
    let config: InputParameter = serde_yaml::from_reader(file)?;
    Ok(config)
}
