/// Processed and validated configuration ready for simulation
/// All computed values are pre-calculated and guaranteed to be present
/// All values are in JSBSim units (Imperial/US customary) unless otherwise noted
use std::path::PathBuf;

#[derive(Debug, Clone)]
pub struct SimulationConfig {
    pub launcher: LauncherConfig,
    pub wind: WindConfig,
    pub rocket: RocketConfig,
    pub construction: Option<ConstructionConfig>,
}

#[derive(Debug, Clone)]
pub struct LauncherConfig {
    pub magnetic_declination: f64,           // degrees
    pub launcher_azimuth_angle: f64,         // degrees (template variable)
    pub launcher_pitch_angle: f64,           // degrees (template variable)
    pub launcher_roll_angle: f64,            // degrees (template variable)
    pub launch_site_latitude: f64,           // degrees (template variable)
    pub launch_site_longitude: f64,          // degrees (template variable)
    pub launch_site_elevation_msl: f64,      // meters (template variable)
    pub launcher_length: f64,                // meters (template variable)
    pub launcher_rail_exit_height: f64,      // meters (template variable, computed)
    pub range_kmz: Option<PathBuf>,
}

#[derive(Debug, Clone)]
pub struct WindConfig {
    pub mode: WindMode,
}

#[derive(Debug, Clone)]
pub enum WindMode {
    PowerLaw {
        wind_ref_altitude: f64,              // meters
        ground_wind_dir: f64,                // degrees
        ground_wind_speed: f64,              // m/s
        wind_power_factor: f64,
        // Generated table for template (altitude_m, speed_fps, direction_rad)
        wind_profile_altitude_table: Vec<(f64, f64, f64)>,
    },
    Table {
        // Loaded and processed table (altitude_m, speed_fps, direction_rad)
        wind_profile_altitude_table: Vec<(f64, f64, f64)>,
    },
}

impl WindMode {
    /// Get the wind profile table regardless of mode
    pub fn get_wind_profile_table(&self) -> &[(f64, f64, f64)] {
        match self {
            WindMode::PowerLaw { wind_profile_altitude_table, .. } => wind_profile_altitude_table,
            WindMode::Table { wind_profile_altitude_table } => wind_profile_altitude_table,
        }
    }
}

#[derive(Debug, Clone)]
pub struct RocketConfig {
    pub body_diameter: f64,                  // meters (template variable)
    pub body_length: f64,                    // meters (template variable)
    pub projected_frontal_area: f64,         // m² (template variable, computed)
    pub fin_span: f64,                       // meters (template variable)

    pub inertia: InertiaConfig,
    pub mass: MassConfig,
    pub parachutes: Vec<ParachuteConfig>,
    pub parachute_area_schedule: Vec<(f64, f64)>,  // (time_s, area_sqft) - template variable
    pub parachute_drag_coefficient: f64,           // dimensionless (template variable)
    pub parachute_deployment_duration: f64,        // seconds (template variable)
    pub aerodynamics: AerodynamicsConfig,
    pub thrust: ThrustConfig,
    pub solver: SolverConfig,
}

#[derive(Debug, Clone)]
pub struct InertiaConfig {
    pub moment_of_inertia_xx: f64,           // kg·m² (template variable)
    pub moment_of_inertia_yy: f64,           // kg·m² (template variable)
    pub moment_of_inertia_zz: f64,           // kg·m² (template variable)
    pub moment_of_inertia_xy: f64,           // kg·m² (template variable)
    pub moment_of_inertia_xz: f64,           // kg·m² (template variable)
    pub moment_of_inertia_yz: f64,           // kg·m² (template variable)
}

#[derive(Debug, Clone)]
pub struct MassConfig {
    pub dry_mass: f64,                       // kg (template variable)
    pub center_of_gravity_x: f64,            // meters (template variable)
    pub center_of_gravity_y: f64,            // meters (template variable)
    pub center_of_gravity_z: f64,            // meters (template variable)
    pub center_of_pressure_x: f64,           // meters (template variable, initial value)
    pub center_of_pressure_y: f64,           // meters (template variable)
    pub center_of_pressure_z: f64,           // meters (template variable)

    // Center of pressure mach tables (mach, position_m) - template variable
    pub center_of_pressure_mach_table: Vec<(f64, f64)>,

    pub oxidizer_mass: f64,                  // kg (template variable)
    pub oxidizer_tank_position_x: f64,       // meters (template variable)
    pub oxidizer_tank_position_y: f64,       // meters (template variable)
    pub oxidizer_tank_position_z: f64,       // meters (template variable)

    pub fuel_mass: f64,                      // kg (template variable, before burn)
    pub fuel_mass_after_burn: f64,           // kg (template variable)
    pub fuel_tank_position_x: f64,           // meters (template variable)
    pub fuel_tank_position_y: f64,           // meters (template variable)
    pub fuel_tank_position_z: f64,           // meters (template variable)
    pub fuel_grain_radius: f64,              // meters (template variable, computed)
}

#[derive(Debug, Clone)]
pub struct ParachuteConfig {
    pub name: String,
    pub parachute_full_deploy_time: f64,     // seconds
    pub parachute_deploy_delay: f64,         // seconds
    pub parachute_drag_coefficient: f64,     // dimensionless
    pub area: f64,                           // m²
}

#[derive(Debug, Clone)]
pub struct AerodynamicsConfig {
    pub mode: AerodynamicsMode,
}

#[derive(Debug, Clone)]
pub enum AerodynamicsMode {
    Coefficients {
        reference_area: f64,                 // m²

        // All tables are guaranteed to exist (fallback to single-row table)
        // (mach, coefficient) - template variable
        normal_force_coefficient_mach_table: Vec<(f64, f64)>,
        side_force_coefficient_mach_table: Vec<(f64, f64)>,
        // 2D table: each row is [mach, alpha1, alpha2, ...] - template variable
        drag_coefficient_zero_lift_table: Vec<Vec<f64>>,

        // Damping coefficients (dimensionless) - template variable
        roll_damping_coefficient: f64,
        pitch_damping_coefficient: f64,
        yaw_damping_coefficient: f64,
    },
    Parameters {
        reference_area: f64,                 // m²

        // Computed aerodynamic coefficient tables
        normal_force_coefficient_mach_table: Vec<(f64, f64)>,
        side_force_coefficient_mach_table: Vec<(f64, f64)>,
        drag_coefficient_zero_lift_table: Vec<Vec<f64>>,

        roll_damping_coefficient: f64,
        pitch_damping_coefficient: f64,
        yaw_damping_coefficient: f64,

        // Original parameters
        nose_shape: String,
        nose_length: f64,                    // meters
        body_length: f64,                    // meters
        fin_root_chord: f64,                 // meters
        fin_tip_chord: f64,                  // meters
        fin_half_span: f64,                  // meters
        fin_number: u32,
        fin_thickness: f64,                  // meters
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
    // (time_s, thrust_lbf) - template variable
    pub thrust_curve: Vec<(f64, f64)>,
    // (time_s, fuel_fraction) - template variable
    pub fuel_mass_remaining_schedule: Vec<(f64, f64)>,
    pub thruster_position_x: f64,            // meters (template variable)
    pub thruster_position_y: f64,            // meters (template variable)
    pub thruster_position_z: f64,            // meters (template variable)
    pub cut_off_time: f64,                   // seconds
    pub liftoff_time: f64,                   // seconds (computed)
}

#[derive(Debug, Clone)]
pub struct SolverConfig {
    pub simulation_duration: f64,            // seconds (template variable)
    pub integration_time_step: f64,          // seconds (template variable)
    pub notify_interval: f64,                // seconds
    pub output_rate: u32,                    // Hz
    pub terminate_at_apogee: u32,            // 0 or 1 (template variable)
}

#[derive(Debug, Clone)]
pub struct ConstructionConfig {
    pub fin: Option<ConstructionFinConfig>,
    pub body: Option<ConstructionBodyConfig>,
    pub parachute: Option<ConstructionParachuteConfig>,
}

#[derive(Debug, Clone)]
pub struct ConstructionFinConfig {
    pub half_span: f64,                      // meters
    pub root_chord: f64,                     // meters
    pub tip_chord: f64,                      // meters
    pub drag_coefficient: f64,               // dimensionless
    pub lift_coefficient_alpha: f64,         // dimensionless
    pub modulus_of_elasticity: f64,          // Pa
    pub poisson_ratio: f64,                  // dimensionless
}

#[derive(Debug, Clone)]
pub struct ConstructionBodyConfig {
    pub body_bending_stiffness: f64,         // N·m²
}

#[derive(Debug, Clone)]
pub struct ConstructionParachuteConfig {
    pub opening_shock_factor: f64,           // dimensionless
}
