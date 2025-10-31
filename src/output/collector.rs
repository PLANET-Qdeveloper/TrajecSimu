use anyhow::Result;
use crate::jsbsim::JSBSimExecutive;
use super::types::*;

/// Collects simulation data from JSBSim executive
pub struct DataCollector;

impl DataCollector {
    pub fn new() -> Self {
        Self
    }

    /// Collect a complete simulation frame from JSBSim
    pub fn collect_frame(&self, exec: &JSBSimExecutive) -> Result<SimulationFrame> {
        Ok(SimulationFrame {
            time: exec.get_sim_time(),
            position: self.collect_position(exec)?,
            attitude: self.collect_attitude(exec)?,
            velocity: self.collect_velocity(exec)?,
            rates: self.collect_rates(exec)?,
            forces: self.collect_forces(exec)?,
            moments: self.collect_moments(exec)?,
            atmosphere: self.collect_atmosphere(exec)?,
            mass_props: self.collect_mass_properties(exec)?,
            propulsion: self.collect_propulsion(exec)?,
            custom: self.collect_custom_properties(exec)?,
        })
    }

    fn collect_position(&self, exec: &JSBSimExecutive) -> Result<PositionData> {
        // JSBSim uses feet internally, convert to meters
        const FT_TO_M: f64 = 0.3048;

        Ok(PositionData {
            altitude_asl_m: exec.get_property("position/h-sl-ft")? * FT_TO_M,
            altitude_agl_m: exec.get_property("position/h-agl-ft")? * FT_TO_M,
            latitude_deg: exec.get_property("position/lat-gc-deg")?,
            latitude_geod_deg: exec.get_property("position/lat-geod-deg")?,
            longitude_deg: exec.get_property("position/long-gc-deg")?,
            terrain_elevation_m: exec.get_property("position/terrain-elevation-asl-ft")? * FT_TO_M,
            x_ecef_m: exec.get_property("position/ecef-x-ft")? * FT_TO_M,
            y_ecef_m: exec.get_property("position/ecef-y-ft")? * FT_TO_M,
            z_ecef_m: exec.get_property("position/ecef-z-ft")? * FT_TO_M,
        })
    }

    fn collect_attitude(&self, exec: &JSBSimExecutive) -> Result<AttitudeData> {
        Ok(AttitudeData {
            phi_deg: exec.get_property("attitude/phi-deg")?,
            theta_deg: exec.get_property("attitude/theta-deg")?,
            psi_deg: exec.get_property("attitude/psi-deg")?,
            alpha_deg: exec.get_property("aero/alpha-deg")?,
            beta_deg: exec.get_property("aero/beta-deg")?,
        })
    }

    fn collect_velocity(&self, exec: &JSBSimExecutive) -> Result<VelocityData> {
        const FT_TO_M: f64 = 0.3048;
        const PSF_TO_PA: f64 = 47.880258888889; // pounds per square foot to pascals

        Ok(VelocityData {
            v_total_ms: exec.get_property("velocities/vt-fps")? * FT_TO_M,
            v_inertial_ms: exec.get_property("velocities/vi-fps")? * FT_TO_M,
            u_body_ms: exec.get_property("velocities/u-fps")? * FT_TO_M,
            v_body_ms: exec.get_property("velocities/v-fps")? * FT_TO_M,
            w_body_ms: exec.get_property("velocities/w-fps")? * FT_TO_M,
            v_north_ms: exec.get_property("velocities/v-north-fps")? * FT_TO_M,
            v_east_ms: exec.get_property("velocities/v-east-fps")? * FT_TO_M,
            v_down_ms: exec.get_property("velocities/v-down-fps")? * FT_TO_M,
            vx_ecef_ms: exec.get_property("velocities/ecef-vx-fps")? * FT_TO_M,
            vy_ecef_ms: exec.get_property("velocities/ecef-vy-fps")? * FT_TO_M,
            vz_ecef_ms: exec.get_property("velocities/ecef-vz-fps")? * FT_TO_M,
            q_bar_pa: exec.get_property("aero/qbar-psf")? * PSF_TO_PA,
            reynolds_number: exec.get_property("aero/re")?,
            mach_number: exec.get_property("velocities/mach")?,
            true_velocity: exec.get_property("velocities/vt-fps")? * FT_TO_M,
            equivalent_velocity: exec.get_property("velocities/ve-fps")? * FT_TO_M,
            calibrated_velocity: exec.get_property("velocities/vc-fps")? * FT_TO_M,
            ground_velocity: exec.get_property("velocities/vg-fps")? * FT_TO_M,
        })
    }

    fn collect_rates(&self, exec: &JSBSimExecutive) -> Result<AngularRates> {
        const RAD_TO_DEG: f64 = 57.29577951308232;

        Ok(AngularRates {
            p_degs: exec.get_property("velocities/p-rad_sec")? * RAD_TO_DEG,
            q_degs: exec.get_property("velocities/q-rad_sec")? * RAD_TO_DEG,
            r_degs: exec.get_property("velocities/r-rad_sec")? * RAD_TO_DEG,
            p_dot_degs2: exec.get_property("accelerations/pdot-rad_sec2")? * RAD_TO_DEG,
            q_dot_degs2: exec.get_property("accelerations/qdot-rad_sec2")? * RAD_TO_DEG,
            r_dot_degs2: exec.get_property("accelerations/rdot-rad_sec2")? * RAD_TO_DEG,
            p_inertial_degs: exec.get_property("velocities/pi-rad_sec")? * RAD_TO_DEG,
            q_inertial_degs: exec.get_property("velocities/qi-rad_sec")? * RAD_TO_DEG,
            r_inertial_degs: exec.get_property("velocities/ri-rad_sec")? * RAD_TO_DEG,
        })
    }

    fn collect_forces(&self, exec: &JSBSimExecutive) -> Result<Forces> {
        const LBF_TO_N: f64 = 4.4482216152605; // pound-force to newtons

        Ok(Forces {
            f_drag_n: exec.get_property("forces/fbx-aero-lbs")? * LBF_TO_N,
            f_side_n: exec.get_property("forces/fby-aero-lbs")? * LBF_TO_N,
            f_lift_n: exec.get_property("forces/fbz-aero-lbs")? * LBF_TO_N,
            l_over_d: exec.get_property("aero/cl-cd")?,
            f_aero_x_n: exec.get_property("forces/fbx-aero-lbs")? * LBF_TO_N,
            f_aero_y_n: exec.get_property("forces/fby-aero-lbs")? * LBF_TO_N,
            f_aero_z_n: exec.get_property("forces/fbz-aero-lbs")? * LBF_TO_N,
            f_prop_x_n: exec.get_property("forces/fbx-prop-lbs")? * LBF_TO_N,
            f_prop_y_n: exec.get_property("forces/fby-prop-lbs")? * LBF_TO_N,
            f_prop_z_n: exec.get_property("forces/fbz-prop-lbs")? * LBF_TO_N,
            f_weight_x_n: exec.get_property("forces/fbx-weight-lbs")? * LBF_TO_N,
            f_weight_y_n: exec.get_property("forces/fby-weight-lbs")? * LBF_TO_N,
            f_weight_z_n: exec.get_property("forces/fbz-weight-lbs")? * LBF_TO_N,
            f_total_x_n: exec.get_property("forces/fbx-total-lbs")? * LBF_TO_N,
            f_total_y_n: exec.get_property("forces/fby-total-lbs")? * LBF_TO_N,
            f_total_z_n: exec.get_property("forces/fbz-total-lbs")? * LBF_TO_N,
        })
    }

    fn collect_moments(&self, exec: &JSBSimExecutive) -> Result<Moments> {
        const LBFFT_TO_NM: f64 = 1.3558179483314; // pound-force foot to newton-meter

        Ok(Moments {
            l_aero_nm: exec.get_property("moments/l-aero-lbsft")? * LBFFT_TO_NM,
            m_aero_nm: exec.get_property("moments/m-aero-lbsft")? * LBFFT_TO_NM,
            n_aero_nm: exec.get_property("moments/n-aero-lbsft")? * LBFFT_TO_NM,
            l_prop_nm: exec.get_property("moments/l-prop-lbsft")? * LBFFT_TO_NM,
            m_prop_nm: exec.get_property("moments/m-prop-lbsft")? * LBFFT_TO_NM,
            n_prop_nm: exec.get_property("moments/n-prop-lbsft")? * LBFFT_TO_NM,
            l_total_nm: exec.get_property("moments/l-total-lbsft")? * LBFFT_TO_NM,
            m_total_nm: exec.get_property("moments/m-total-lbsft")? * LBFFT_TO_NM,
            n_total_nm: exec.get_property("moments/n-total-lbsft")? * LBFFT_TO_NM,
        })
    }

    fn collect_atmosphere(&self, exec: &JSBSimExecutive) -> Result<AtmosphereData> {
        const FT_TO_M: f64 = 0.3048;
        const SLUG_FT3_TO_KG_M3: f64 = 515.3788184; // slug/ft³ to kg/m³
        const PSF_TO_PA: f64 = 47.880258888889;
        const RANKINE_TO_KELVIN: f64 = 5.0 / 9.0;

        Ok(AtmosphereData {
            rho_kgm3: exec.get_property("atmosphere/rho-slugs_ft3")? * SLUG_FT3_TO_KG_M3,
            temperature_k: exec.get_property("atmosphere/T-R")? * RANKINE_TO_KELVIN,
            pressure_sl_pa: exec.get_property("atmosphere/P-sl-psf")? * PSF_TO_PA,
            pressure_ambient_pa: exec.get_property("atmosphere/P-psf")? * PSF_TO_PA,
            absolute_viscosity: exec.get_property("atmosphere/viscosity-absolute")?,
            kinematic_viscosity: exec.get_property("atmosphere/viscosity-kinematic")?,
            wind_north_ms: exec.get_property("atmosphere/wind-north-fps")? * FT_TO_M,
            wind_east_ms: exec.get_property("atmosphere/wind-east-fps")? * FT_TO_M,
            wind_down_ms: exec.get_property("atmosphere/wind-down-fps")? * FT_TO_M,
            turbulence_magnitude_ms: exec.get_property("atmosphere/turbulence/magnitude-fps")? * FT_TO_M,
            turbulence_direction_deg: exec.get_property("atmosphere/turbulence/direction-deg")?,
        })
    }

    fn collect_mass_properties(&self, exec: &JSBSimExecutive) -> Result<MassProperties> {
        const SLUG_TO_KG: f64 = 14.5939029372; // slug to kilogram
        const LBF_TO_N: f64 = 4.4482216152605;
        const FT_TO_M: f64 = 0.3048;
        const SLUGFT2_TO_KGM2: f64 = SLUG_TO_KG * FT_TO_M * FT_TO_M;

        Ok(MassProperties {
            mass_kg: exec.get_property("inertia/mass-slugs")? * SLUG_TO_KG,
            weight_n: exec.get_property("inertia/weight-lbs")? * LBF_TO_N,
            x_cg_m: exec.get_property("inertia/cg-x-ft")? * FT_TO_M,
            y_cg_m: exec.get_property("inertia/cg-y-ft")? * FT_TO_M,
            z_cg_m: exec.get_property("inertia/cg-z-ft")? * FT_TO_M,
            ixx: exec.get_property("inertia/ixx-slugs_ft2")? * SLUGFT2_TO_KGM2,
            iyy: exec.get_property("inertia/iyy-slugs_ft2")? * SLUGFT2_TO_KGM2,
            izz: exec.get_property("inertia/izz-slugs_ft2")? * SLUGFT2_TO_KGM2,
            ixy: exec.get_property("inertia/ixy-slugs_ft2")? * SLUGFT2_TO_KGM2,
            ixz: exec.get_property("inertia/ixz-slugs_ft2")? * SLUGFT2_TO_KGM2,
            iyz: exec.get_property("inertia/iyz-slugs_ft2")? * SLUGFT2_TO_KGM2,
        })
    }

    fn collect_propulsion(&self, exec: &JSBSimExecutive) -> Result<PropulsionData> {
        const LBF_TO_N: f64 = 4.4482216152605;
        const SLUG_TO_KG: f64 = 14.5939029372;

        // Try to get engine 0 properties, default to 0 if not available
        let thrust_n = exec
            .get_property("propulsion/engine[0]/thrust-lbs")
            .unwrap_or(0.0)
            * LBF_TO_N;

        let propellant_mass = exec
            .get_property("propulsion/tank[0]/contents-lbs")
            .unwrap_or(0.0)
            * SLUG_TO_KG / 32.174; // lbs to kg

        Ok(PropulsionData {
            thrust_n,
            thrust_x_n: exec.get_property("forces/fbx-prop-lbs")? * LBF_TO_N,
            thrust_y_n: exec.get_property("forces/fby-prop-lbs")? * LBF_TO_N,
            thrust_z_n: exec.get_property("forces/fbz-prop-lbs")? * LBF_TO_N,
            propellant_mass_kg: propellant_mass,
            engine_running: thrust_n > 1.0, // Consider engine running if thrust > 1N
        })
    }

    fn collect_custom_properties(&self, exec: &JSBSimExecutive) -> Result<CustomProperties> {
        const FT2_TO_M2: f64 = 0.09290304; // square feet to square meters

        // Custom properties - may not exist in all simulations
        let parachute_area = exec
            .get_property("fcs/parachute-area-ft2")
            .unwrap_or(0.0)
            * FT2_TO_M2;

        let parachute_deployed = parachute_area > 0.01; // Consider deployed if area > 0.01 m²

        let flight_phase = exec
            .get_property("simulation/flight-phase")
            .unwrap_or(0.0) as u32;

        let stage = exec.get_property("simulation/stage").unwrap_or(1.0) as u32;

        Ok(CustomProperties {
            parachute_area_m2: parachute_area,
            parachute_deployed,
            stage,
            flight_phase,
        })
    }
}

impl Default for DataCollector {
    fn default() -> Self {
        Self::new()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_collector_creation() {
        let collector = DataCollector::new();
        assert!(std::mem::size_of_val(&collector) == 0); // Zero-sized type
    }
}
