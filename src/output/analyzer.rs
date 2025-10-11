use super::processor::SimulationOutput;

#[derive(Debug, Clone)]
pub struct FlightStatistics {
    pub max_altitude: f64,
    pub max_velocity: f64,
    pub landing_latitude: f64,
    pub landing_longitude: f64,
    pub flight_time: f64,
}

pub struct OutputAnalyzer;

impl OutputAnalyzer {
    pub fn new() -> Self {
        Self
    }

    pub fn analyze(&self, data: &[SimulationOutput]) -> Option<FlightStatistics> {
        if data.is_empty() {
            return None;
        }

        let max_altitude = data
            .iter()
            .map(|d| d.altitude)
            .max_by(|a, b| a.partial_cmp(b).unwrap())?;

        let max_velocity = data
            .iter()
            .map(|d| d.velocity)
            .max_by(|a, b| a.partial_cmp(b).unwrap())?;

        let last_record = data.last()?;

        Some(FlightStatistics {
            max_altitude,
            max_velocity,
            landing_latitude: last_record.latitude,
            landing_longitude: last_record.longitude,
            flight_time: last_record.time,
        })
    }

    pub fn find_apogee<'a>(&self, data: &'a [SimulationOutput]) -> Option<&'a SimulationOutput> {
        data.iter()
            .max_by(|a, b| a.altitude.partial_cmp(&b.altitude).unwrap())
    }
}

impl Default for OutputAnalyzer {
    fn default() -> Self {
        Self::new()
    }
}
