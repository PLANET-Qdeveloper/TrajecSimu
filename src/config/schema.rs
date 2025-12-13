use super::super::config::wind_param::WindTable;
/// Processed and validated configuration ready for simulation
/// All computed values are pre-calculated and guaranteed to be present
/// All values use type-safe uom units
use std::path::PathBuf;
use uom::si::f64::*;

#[derive(Debug, Clone)]
pub struct SimulationConfig {
    pub launcher: LauncherConfig,
    pub wind: WindConfig,
    pub rocket: RocketConfig,
    pub construction: Option<ConstructionConfig>,
}


#[derive(Debug, Clone)]
pub struct LauncherConfig {
    pub azimuth_angle: Angle,
    pub pitch_angle: Angle,
    pub roll_angle: Angle,
    pub latitude: Angle,
    pub longitude: Angle,
    pub elevation_msl: Length,
    pub length: Length,
    pub rail_exit_height: Length,
}

#[derive(Debug, Clone)]
pub struct WindConfig {
    pub wind_table: WindTable,
}

#[derive(Debug, Clone)]
pub struct RocketConfig {
    pub body_diameter: Length,
    pub body_length: Length,
    pub projected_frontal_area: Area,
    pub fin_span: Length,

    pub inertia: InertiaConfig,
    pub mass: MassConfig,
    pub parachutes: Vec<ParachuteConfig>,
    pub parachute_area_schedule: Vec<Time>,
    pub aerodynamics: AerodynamicsConfig,
    pub thrust: ThrustConfig,
    pub solver: SolverConfig,
}

#[derive(Debug, Clone)]
pub struct InertiaConfig {
    pub moment_of_inertia_xx: MomentOfInertia,
    pub moment_of_inertia_yy: MomentOfInertia,
    pub moment_of_inertia_zz: MomentOfInertia,
    pub moment_of_inertia_xy: MomentOfInertia,
    pub moment_of_inertia_xz: MomentOfInertia,
    pub moment_of_inertia_yz: MomentOfInertia,
}

#[derive(Debug, Clone)]
pub struct MassConfig {
    pub dry_mass: Mass,
    pub center_of_gravity_x: Length,
    pub center_of_gravity_y: Length,
    pub center_of_gravity_z: Length,
    pub center_of_pressure_x: Length,
    pub center_of_pressure_y: Length,
    pub center_of_pressure_z: Length,

    // Center of pressure mach table: (mach_number, position)
    pub center_of_pressure_mach_table: Vec<(f64, Length)>, // Mach is dimensionless

    pub oxidizer_mass: Mass,
    pub oxidizer_tank_position_x: Length,
    pub oxidizer_tank_position_y: Length,
    pub oxidizer_tank_position_z: Length,

    pub fuel_mass: Mass,
    pub fuel_mass_after_burn: Mass,
    pub fuel_tank_position_x: Length,
    pub fuel_tank_position_y: Length,
    pub fuel_tank_position_z: Length,
    pub fuel_grain_radius: Length,
}

#[derive(Debug, Clone)]
pub struct ParachuteConfig {
    pub name: String,
    pub parachute_full_deploy_time: Time,
    pub parachute_deploy_delay: Time,
    pub parachute_drag_coefficient: f64, // Dimensionless
    pub area: Area,
}

#[derive(Debug, Clone)]
pub struct AerodynamicsConfig {
    reference_area: Area,

    // Coefficient tables: (mach_number, coefficient) - both dimensionless
    normal_force_coefficient_mach_table: Vec<(f64, f64)>,
    side_force_coefficient_mach_table: Vec<(f64, f64)>,
    // 2D table: each row is [mach, alpha1, alpha2, ...] - all dimensionless
    drag_coefficient_zero_lift_table: Vec<Vec<f64>>,

    // Damping coefficients - all dimensionless
    roll_damping_coefficient: f64,
    pitch_damping_coefficient: f64,
    yaw_damping_coefficient: f64,
}

#[derive(Debug, Clone)]
pub struct ThrustConfig {
    // Thrust curve: (time, thrust)
    pub thrust_curve: Vec<(Time, Force)>,
    // Fuel mass schedule: (time, fuel_fraction) - fraction is dimensionless
    pub fuel_mass_remaining_schedule: Vec<(Time, f64)>,
    pub thruster_position_x: Length,
    pub thruster_position_y: Length,
    pub thruster_position_z: Length,
    pub cut_off_time: Time,
    pub liftoff_time: Time,
}

#[derive(Debug, Clone)]
pub struct SolverConfig {
    pub simulation_duration: Time,
    pub integration_time_step: Time,
    pub notify_interval: Time,
    pub output_rate: u32,          // Hz (frequency)
    pub terminate_at_apogee: bool, // Boolean flag
}

#[derive(Debug, Clone)]
pub struct ConstructionConfig {
    pub fin: Option<ConstructionFinConfig>,
    pub body: Option<ConstructionBodyConfig>,
    pub parachute: Option<ConstructionParachuteConfig>,
}

#[derive(Debug, Clone)]
pub struct ConstructionFinConfig {
    pub half_span: Length,
    pub root_chord: Length,
    pub tip_chord: Length,
    pub number_of_fins: u32,
    pub drag_coefficient: f64,           // Dimensionless
    pub lift_coefficient_alpha: f64,     // Dimensionless
    pub modulus_of_elasticity: Pressure, // Pa = N/m²
    pub poisson_ratio: f64,              // Dimensionless
}

#[derive(Debug, Clone)]
pub struct ConstructionBodyConfig {
    pub nose_shape: String,
    pub nose_length: Length,
    pub body_bending_stiffness: f64, // N·m² (no direct uom type, using f64)
}

#[derive(Debug, Clone)]
pub struct ConstructionParachuteConfig {
    pub opening_shock_factor: f64, // Dimensionless
}
