use serde::{Deserialize, Deserializer, Serialize};
use std::path::PathBuf;

/// Deserialize empty string as None, non-empty string as Some(PathBuf)
fn deserialize_optional_path<'de, D>(deserializer: D) -> Result<Option<PathBuf>, D::Error>
where
    D: Deserializer<'de>,
{
    let s: Option<String> = Option::deserialize(deserializer)?;
    Ok(s.and_then(|s| {
        if s.is_empty() {
            None
        } else {
            Some(PathBuf::from(s))
        }
    }))
}

#[derive(Debug, Deserialize, Serialize, Clone)]
pub struct InputParameter {
    pub flight_simulator: FlightSimulator,
    pub construction: Option<Construction>,
}

#[derive(Debug, Deserialize, Serialize, Clone)]
pub struct FlightSimulator {
    pub launcher: Launcher,
    pub wind: Wind,
    pub rocket: Rocket,
}

#[derive(Debug, Deserialize, Serialize, Clone)]
pub struct Launcher {
    pub rotation: LauncherRotation,
    pub coordinates: Coordinates,
    pub launcher_length: f64,
}

#[derive(Debug, Deserialize, Serialize, Clone)]
pub struct LauncherRotation {
    pub magnetic_declination: f64,
    pub azimuth: f64,
    pub pitch: f64,
    #[serde(default)]
    pub roll: f64,
}

#[derive(Debug, Deserialize, Serialize, Clone)]
pub struct Coordinates {
    pub latitude: f64,
    pub longitude: f64,
    pub elevation: f64,
}

#[derive(Debug, Deserialize, Serialize, Clone)]
pub struct Wind {
    pub use_power_law: bool,
    #[serde(default, deserialize_with = "deserialize_optional_path")]
    pub winds_table: Option<PathBuf>,
    pub power_law: Option<PowerLaw>,
}

#[derive(Debug, Deserialize, Serialize, Clone)]
pub struct PowerLaw {
    pub wind_ref_altitude: f64,
    pub ground_wind_dir: f64,
    pub ground_wind_speed: f64,
    pub wind_power_factor: f64,
}

#[derive(Debug, Deserialize, Serialize, Clone)]
pub struct Rocket {
    pub diameter: f64,
    pub height: f64,
    pub inertia: Inertia,
    pub mass: Mass,
    pub parachute: Vec<Parachute>,
    pub aerodynamics: Aerodynamics,
    pub thrust: Thrust,
    pub solver: Solver,
}

#[derive(Debug, Deserialize, Serialize, Clone)]
pub struct Inertia {
    pub xx: f64,
    pub yy: f64,
    pub zz: f64,
    #[serde(default)]
    pub xy: f64,
    #[serde(default)]
    pub xz: f64,
    #[serde(default)]
    pub yz: f64,
}

#[derive(Debug, Deserialize, Serialize, Clone)]
pub struct Mass {
    pub dry_weight: f64,
    pub cg: Position3D,
    pub cp: CenterOfPressure,
    pub oxidizer_mass: f64,
    pub tank_position: Position3D,
    pub fuel_mass_before_burn: f64,
    pub fuel_mass_after_burn: f64,
    pub fuel_position: Position3D,
}

#[derive(Debug, Deserialize, Serialize, Clone)]
pub struct Position3D {
    pub x: f64,
    #[serde(default)]
    pub y: f64,
    #[serde(default)]
    pub z: f64,
}

#[derive(Debug, Deserialize, Serialize, Clone)]
pub struct CenterOfPressure {
    pub x: f64,
    #[serde(default)]
    pub y: f64,
    #[serde(default)]
    pub z: f64,
    #[serde(default, deserialize_with = "deserialize_optional_path")]
    pub x_mach_table: Option<PathBuf>,
    #[serde(default, deserialize_with = "deserialize_optional_path")]
    pub y_mach_table: Option<PathBuf>,
    #[serde(default, deserialize_with = "deserialize_optional_path")]
    pub z_mach_table: Option<PathBuf>,
}

#[derive(Debug, Deserialize, Serialize, Clone)]
pub struct Parachute {
    pub full_deploy_time: f64,
    pub deploy_delay: f64,
    pub drag_coefficient: f64,
    pub area: f64,
}

#[derive(Debug, Deserialize, Serialize, Clone)]
pub struct Aerodynamics {
    pub coefficients: AerodynamicCoefficients,
}

#[derive(Debug, Deserialize, Serialize, Clone)]
pub struct AerodynamicCoefficients {
    pub lift_coefficient_alpha: f64,
    #[serde(default, deserialize_with = "deserialize_optional_path")]
    pub lift_coefficient_table: Option<PathBuf>,
    pub side_coefficient_beta: f64,
    #[serde(default, deserialize_with = "deserialize_optional_path")]
    pub side_coefficient_table: Option<PathBuf>,
    pub drag_coefficient: f64,
    #[serde(default, deserialize_with = "deserialize_optional_path")]
    pub drag_coefficient_table: Option<PathBuf>,
    pub roll_damping_coefficient: f64,
    #[serde(default, deserialize_with = "deserialize_optional_path")]
    pub roll_damping_table: Option<PathBuf>,
    pub pitch_damping_coefficient: f64,
    #[serde(default, deserialize_with = "deserialize_optional_path")]
    pub pitch_damping_table: Option<PathBuf>,
    pub yaw_damping_coefficient: f64,
    #[serde(default, deserialize_with = "deserialize_optional_path")]
    pub yaw_damping_table: Option<PathBuf>,
}

#[derive(Debug, Deserialize, Serialize, Clone)]
pub struct Thrust {
    pub thrust_curve: PathBuf,
    pub cut_off_time: f64,
}

#[derive(Debug, Deserialize, Serialize, Clone)]
pub struct Solver {
    pub flight_duration: f64,
    pub time_step: f64,
    pub notify_interval: f64,
    pub output_rate: u32,
    pub apogee_mode: u32,
}

#[derive(Debug, Deserialize, Serialize, Clone)]
pub struct Construction {
    pub rocket: ConstructionRocket,
}

#[derive(Debug, Deserialize, Serialize, Clone)]
pub struct ConstructionRocket {
    pub fin: Option<ConstructionFin>,
    pub body: Option<ConstructionBody>,
    pub parachute: Option<ConstructionParachute>,
}

#[derive(Debug, Deserialize, Serialize, Clone)]
pub struct ConstructionFin {
    pub root_chord: Option<f64>,
    pub tip_chord: Option<f64>,
    pub half_span: Option<f64>,
    pub number_of_fins: Option<u32>,
    pub fin_thickness: Option<f64>,
    pub modulus_of_elasticity: Option<f64>,
    pub poisson_ratio: Option<f64>,
}

#[derive(Debug, Deserialize, Serialize, Clone)]
pub struct ConstructionBody {
    pub nose_shape: Option<String>,
    pub nose_length: Option<f64>,
    pub body_bending_stiffness: Option<f64>,
}

#[derive(Debug, Deserialize, Serialize, Clone)]
pub struct ConstructionParachute {
    pub opening_shock_factor: Option<f64>,
}
