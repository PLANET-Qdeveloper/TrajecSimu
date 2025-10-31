use serde::{Deserialize, Serialize};

/// Complete simulation output data structure matching JSBSim output format
/// Extended with custom properties for rocket simulation (thrust, parachute area)
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SimulationFrame {
    /// Simulation time in seconds
    pub time: f64,

    /// Position data
    pub position: PositionData,

    /// Attitude (orientation) data
    pub attitude: AttitudeData,

    /// Velocity data
    pub velocity: VelocityData,

    /// Angular rates
    pub rates: AngularRates,

    /// Forces acting on vehicle
    pub forces: Forces,

    /// Moments acting on vehicle
    pub moments: Moments,

    /// Atmospheric conditions
    pub atmosphere: AtmosphereData,

    /// Mass and inertia properties
    pub mass_props: MassProperties,

    /// Propulsion data
    pub propulsion: PropulsionData,

    /// Custom rocket-specific data
    pub custom: CustomProperties,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PositionData {
    /// Altitude above sea level (m)
    pub altitude_asl_m: f64,

    /// Altitude above ground level (m)
    pub altitude_agl_m: f64,

    /// Geodetic latitude (deg)
    pub latitude_deg: f64,

    /// Geodetic latitude (deg)
    pub latitude_geod_deg: f64,

    /// Longitude (deg)
    pub longitude_deg: f64,

    /// Terrain elevation (m)
    pub terrain_elevation_m: f64,

    /// ECEF position (m)
    pub x_ecef_m: f64,
    pub y_ecef_m: f64,
    pub z_ecef_m: f64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AttitudeData {
    /// Euler angles (deg)
    pub phi_deg: f64,   // Roll
    pub theta_deg: f64, // Pitch
    pub psi_deg: f64,   // Yaw

    /// Aerodynamic angles (deg)
    pub alpha_deg: f64, // Angle of attack
    pub beta_deg: f64,  // Sideslip angle

}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct VelocityData {
    /// Total velocity (m/s)
    pub v_total_ms: f64,

    /// Inertial velocity magnitude (m/s)
    pub v_inertial_ms: f64,

    /// Body frame velocities (m/s)
    pub u_body_ms: f64,
    pub v_body_ms: f64,
    pub w_body_ms: f64,

    /// NED frame velocities (m/s)
    pub v_north_ms: f64,
    pub v_east_ms: f64,
    pub v_down_ms: f64,

    /// ECEF velocities (m/s)
    pub vx_ecef_ms: f64,
    pub vy_ecef_ms: f64,
    pub vz_ecef_ms: f64,

    /// Dynamic pressure (Pa)
    pub q_bar_pa: f64,

    /// Reynolds number
    pub reynolds_number: f64,

    /// Mach number
    pub mach_number: f64,

    /// Aero velocities
    pub true_velocity: f64,
    pub equivalent_velocity: f64,
    pub calibrated_velocity: f64,
    pub ground_velocity: f64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AngularRates {
    /// Body angular rates (deg/s)
    pub p_degs: f64, // Roll rate
    pub q_degs: f64, // Pitch rate
    pub r_degs: f64, // Yaw rate

    /// Angular accelerations (deg/s²)
    pub p_dot_degs2: f64,
    pub q_dot_degs2: f64,
    pub r_dot_degs2: f64,

    /// Inertial angular rates (deg/s)
    pub p_inertial_degs: f64,
    pub q_inertial_degs: f64,
    pub r_inertial_degs: f64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Forces {
    /// Aerodynamic forces (N)
    pub f_drag_n: f64,
    pub f_side_n: f64,
    pub f_lift_n: f64,

    /// Lift-to-drag ratio
    pub l_over_d: f64,

    /// Aerodynamic forces in body frame (N)
    pub f_aero_x_n: f64,
    pub f_aero_y_n: f64,
    pub f_aero_z_n: f64,

    /// Propulsion forces in body frame (N)
    pub f_prop_x_n: f64,
    pub f_prop_y_n: f64,
    pub f_prop_z_n: f64,

    /// Weight forces in body frame (N)
    pub f_weight_x_n: f64,
    pub f_weight_y_n: f64,
    pub f_weight_z_n: f64,

    /// Total forces in body frame (N)
    pub f_total_x_n: f64,
    pub f_total_y_n: f64,
    pub f_total_z_n: f64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Moments {
    /// Aerodynamic moments (N⋅m)
    pub l_aero_nm: f64,
    pub m_aero_nm: f64,
    pub n_aero_nm: f64,

    /// Propulsion moments (N⋅m)
    pub l_prop_nm: f64,
    pub m_prop_nm: f64,
    pub n_prop_nm: f64,

    /// Total moments (N⋅m)
    pub l_total_nm: f64,
    pub m_total_nm: f64,
    pub n_total_nm: f64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AtmosphereData {
    /// Air density (kg/m³)
    pub rho_kgm3: f64,

    /// Temperature (K)
    pub temperature_k: f64,

    /// Pressure at sea level (Pa)
    pub pressure_sl_pa: f64,

    /// Ambient pressure (Pa)
    pub pressure_ambient_pa: f64,

    /// Absolute viscosity (Pa⋅s)
    pub absolute_viscosity: f64,

    /// Kinematic viscosity (m²/s)
    pub kinematic_viscosity: f64,

    /// Wind in NED frame (m/s)
    pub wind_north_ms: f64,
    pub wind_east_ms: f64,
    pub wind_down_ms: f64,

    /// Turbulence
    pub turbulence_magnitude_ms: f64,
    pub turbulence_direction_deg: f64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MassProperties {
    /// Total mass (kg)
    pub mass_kg: f64,

    /// Weight (N)
    pub weight_n: f64,

    /// Center of gravity in body frame (m)
    pub x_cg_m: f64,
    pub y_cg_m: f64,
    pub z_cg_m: f64,

    /// Moments of inertia (kg⋅m²)
    pub ixx: f64,
    pub iyy: f64,
    pub izz: f64,
    pub ixy: f64,
    pub ixz: f64,
    pub iyz: f64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PropulsionData {
    /// Engine thrust magnitude (N)
    pub thrust_n: f64,

    /// Engine thrust in body frame (N)
    pub thrust_x_n: f64,
    pub thrust_y_n: f64,
    pub thrust_z_n: f64,

    /// Propellant mass (kg)
    pub propellant_mass_kg: f64,

    /// Engine status (0 = off, 1 = on)
    pub engine_running: bool,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CustomProperties {
    /// Parachute deployed area (m²)
    pub parachute_area_m2: f64,

    /// Parachute deployment status
    pub parachute_deployed: bool,

    /// Stage number
    pub stage: u32,

    /// Flight phase (0=boost, 1=coast, 2=descent, 3=landed)
    pub flight_phase: u32,
}

/// Simplified output for quick analysis and visualization
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SimulationSummary {
    pub time: f64,
    pub altitude_m: f64,
    pub velocity_ms: f64,
    pub latitude_deg: f64,
    pub longitude_deg: f64,
    pub thrust_n: f64,
    pub parachute_area_m2: f64,
}

impl From<SimulationFrame> for SimulationSummary {
    fn from(frame: SimulationFrame) -> Self {
        Self {
            time: frame.time,
            altitude_m: frame.position.altitude_asl_m,
            velocity_ms: frame.velocity.v_total_ms,
            latitude_deg: frame.position.latitude_deg,
            longitude_deg: frame.position.longitude_deg,
            thrust_n: frame.propulsion.thrust_n,
            parachute_area_m2: frame.custom.parachute_area_m2,
        }
    }
}

/// Flight trajectory - collection of simulation frames
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct FlightTrajectory {
    /// All simulation frames
    pub frames: Vec<SimulationFrame>,

    /// Simulation parameters used
    pub metadata: TrajectoryMetadata,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TrajectoryMetadata {
    /// Simulation name/ID
    pub simulation_id: String,

    /// Time step used (s)
    pub time_step_s: f64,

    /// Launch site coordinates
    pub launch_latitude_deg: f64,
    pub launch_longitude_deg: f64,
    pub launch_altitude_m: f64,

    /// Wind conditions
    pub wind_speed_ms: f64,
    pub wind_direction_deg: f64,

    /// Rocket configuration identifier
    pub rocket_config: String,
}

impl FlightTrajectory {
    pub fn new(_simulation_id: String, metadata: TrajectoryMetadata) -> Self {
        Self {
            frames: Vec::new(),
            metadata,
        }
    }

    pub fn add_frame(&mut self, frame: SimulationFrame) {
        self.frames.push(frame);
    }

    pub fn get_apogee(&self) -> Option<&SimulationFrame> {
        self.frames
            .iter()
            .max_by(|a, b| {
                a.position
                    .altitude_asl_m
                    .partial_cmp(&b.position.altitude_asl_m)
                    .unwrap()
            })
    }

    pub fn get_max_velocity(&self) -> Option<f64> {
        self.frames
            .iter()
            .map(|f| f.velocity.v_total_ms)
            .max_by(|a, b| a.partial_cmp(b).unwrap())
    }

    pub fn get_landing_position(&self) -> Option<(f64, f64)> {
        self.frames.last().map(|f| {
            (
                f.position.latitude_deg,
                f.position.longitude_deg,
            )
        })
    }

    pub fn get_flight_duration(&self) -> Option<f64> {
        self.frames.last().map(|f| f.time)
    }

    /// Convert to simplified summary format
    pub fn to_summary(&self) -> Vec<SimulationSummary> {
        self.frames
            .iter()
            .map(|frame| frame.clone().into())
            .collect()
    }
}
