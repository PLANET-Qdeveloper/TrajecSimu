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
    pub magnetic_declination: Angle,
    pub launcher_azimuth_angle: Angle,
    pub launcher_pitch_angle: Angle,
    pub launcher_roll_angle: Angle,
    pub launch_site_latitude: Angle,
    pub launch_site_longitude: Angle,
    pub launch_site_elevation_msl: Length,
    pub launcher_length: Length,
    pub launcher_rail_exit_height: Length,
    pub range_kmz: Option<PathBuf>,
}

#[derive(Debug, Clone)]
pub struct WindConfig {
    pub mode: WindMode,
}

#[derive(Debug, Clone)]
pub enum WindMode {
    PowerLaw {
        wind_ref_altitude: Length,
        ground_wind_dir: Angle,
        ground_wind_speed: Velocity,
        wind_power_factor: f64,  // Dimensionless exponent
        // Wind profile table: (altitude, speed, direction)
        wind_profile_altitude_table: Vec<(Length, Velocity, Angle)>,
    },
    Table {
        // Wind profile table: (altitude, speed, direction)
        wind_profile_altitude_table: Vec<(Length, Velocity, Angle)>,
    },
}

impl WindMode {
    /// Get the wind profile table regardless of mode
    pub fn get_wind_profile_table(&self) -> &[(Length, Velocity, Angle)] {
        match self {
            WindMode::PowerLaw { wind_profile_altitude_table, .. } => wind_profile_altitude_table,
            WindMode::Table { wind_profile_altitude_table } => wind_profile_altitude_table,
        }
    }
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
    pub parachute_area_schedule: Vec<(Time, Area)>,
    pub parachute_drag_coefficient: f64,  // Dimensionless
    pub parachute_deployment_duration: Time,
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
    pub center_of_pressure_mach_table: Vec<(f64, Length)>,  // Mach is dimensionless

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
    pub parachute_drag_coefficient: f64,  // Dimensionless
    pub area: Area,
}

#[derive(Debug, Clone)]
pub struct AerodynamicsConfig {
    pub mode: AerodynamicsMode,
}

#[derive(Debug, Clone)]
pub enum AerodynamicsMode {
    Coefficients {
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
    },
    Parameters {
        reference_area: Area,

        // Computed aerodynamic coefficient tables - all dimensionless
        normal_force_coefficient_mach_table: Vec<(f64, f64)>,
        side_force_coefficient_mach_table: Vec<(f64, f64)>,
        drag_coefficient_zero_lift_table: Vec<Vec<f64>>,

        roll_damping_coefficient: f64,
        pitch_damping_coefficient: f64,
        yaw_damping_coefficient: f64,

        // Original parameters
        nose_shape: String,
        nose_length: Length,
        body_length: Length,
        fin_root_chord: Length,
        fin_tip_chord: Length,
        fin_half_span: Length,
        fin_number: u32,  // Dimensionless count
        fin_thickness: Length,
    },
}

impl AerodynamicsMode {
    /// Get normal force coefficient table regardless of mode
    pub fn get_normal_force_table(&self) -> &[(f64, f64)] {
        match self {
            AerodynamicsMode::Coefficients { normal_force_coefficient_mach_table, .. } => normal_force_coefficient_mach_table,
            AerodynamicsMode::Parameters { normal_force_coefficient_mach_table, .. } => normal_force_coefficient_mach_table,
        }
    }

    /// Get side force coefficient table regardless of mode
    pub fn get_side_force_table(&self) -> &[(f64, f64)] {
        match self {
            AerodynamicsMode::Coefficients { side_force_coefficient_mach_table, .. } => side_force_coefficient_mach_table,
            AerodynamicsMode::Parameters { side_force_coefficient_mach_table, .. } => side_force_coefficient_mach_table,
        }
    }

    /// Get drag coefficient table regardless of mode
    pub fn get_drag_table(&self) -> &[Vec<f64>] {
        match self {
            AerodynamicsMode::Coefficients { drag_coefficient_zero_lift_table, .. } => drag_coefficient_zero_lift_table,
            AerodynamicsMode::Parameters { drag_coefficient_zero_lift_table, .. } => drag_coefficient_zero_lift_table,
        }
    }

    /// Get roll damping coefficient regardless of mode
    pub fn get_roll_damping(&self) -> f64 {
        match self {
            AerodynamicsMode::Coefficients { roll_damping_coefficient, .. } => *roll_damping_coefficient,
            AerodynamicsMode::Parameters { roll_damping_coefficient, .. } => *roll_damping_coefficient,
        }
    }

    /// Get pitch damping coefficient regardless of mode
    pub fn get_pitch_damping(&self) -> f64 {
        match self {
            AerodynamicsMode::Coefficients { pitch_damping_coefficient, .. } => *pitch_damping_coefficient,
            AerodynamicsMode::Parameters { pitch_damping_coefficient, .. } => *pitch_damping_coefficient,
        }
    }

    /// Get yaw damping coefficient regardless of mode
    pub fn get_yaw_damping(&self) -> f64 {
        match self {
            AerodynamicsMode::Coefficients { yaw_damping_coefficient, .. } => *yaw_damping_coefficient,
            AerodynamicsMode::Parameters { yaw_damping_coefficient, .. } => *yaw_damping_coefficient,
        }
    }
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
    pub output_rate: u32,  // Hz (frequency)
    pub terminate_at_apogee: bool,  // Boolean flag
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
    pub drag_coefficient: f64,  // Dimensionless
    pub lift_coefficient_alpha: f64,  // Dimensionless
    pub modulus_of_elasticity: Pressure,  // Pa = N/m²
    pub poisson_ratio: f64,  // Dimensionless
}

#[derive(Debug, Clone)]
pub struct ConstructionBodyConfig {
    pub body_bending_stiffness: f64,  // N·m² (no direct uom type, using f64)
}

#[derive(Debug, Clone)]
pub struct ConstructionParachuteConfig {
    pub opening_shock_factor: f64,  // Dimensionless
}
