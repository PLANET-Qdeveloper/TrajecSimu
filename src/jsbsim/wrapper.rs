use anyhow::{Context, Result};
use std::path::Path;
use std::ffi::{CString, c_void};

use super::ffi;

/// High-level Rust wrapper for JSBSim FDM Executive
pub struct JSBSimExecutive {
    ptr: *mut c_void,
}

impl JSBSimExecutive {
    /// Create a new JSBSim executive instance
    pub fn new() -> Result<Self> {
        let ptr = unsafe { ffi::jsbsim_create() };
        if ptr.is_null() {
            anyhow::bail!("Failed to create JSBSim FDMExec");
        }
        Ok(Self { ptr })
    }

    /// Load an aircraft model
    pub fn load_model(&mut self, model_name: &str) -> Result<()> {
        let c_model_name = CString::new(model_name)
            .context("Invalid model name")?;

        let result = unsafe {
            ffi::jsbsim_load_model(self.ptr, c_model_name.as_ptr())
        };

        if !result {
            anyhow::bail!("Failed to load model: {}", model_name);
        }

        Ok(())
    }

    /// Load a script file
    pub fn load_script<P: AsRef<Path>>(
        &mut self,
        script_path: P,
        delta_t: f64,
    ) -> Result<()> {
        let path_str = script_path.as_ref().to_str()
            .context("Invalid script path")?;
        let c_path = CString::new(path_str)
            .context("Invalid script path")?;

        let result = unsafe {
            ffi::jsbsim_load_script(self.ptr, c_path.as_ptr(), delta_t)
        };

        if !result {
            anyhow::bail!("Failed to load script: {:?}", script_path.as_ref());
        }

        Ok(())
    }

    /// Run one simulation step
    pub fn run(&mut self) -> Result<bool> {
        let result = unsafe { ffi::jsbsim_run(self.ptr) };
        Ok(result)
    }

    /// Initialize the simulation from initial conditions
    pub fn run_ic(&mut self) -> Result<bool> {
        let result = unsafe { ffi::jsbsim_run_ic(self.ptr) };
        Ok(result)
    }

    /// Get a property value
    pub fn get_property(&self, property: &str) -> Result<f64> {
        let c_property = CString::new(property)
            .context("Invalid property name")?;

        let value = unsafe {
            ffi::jsbsim_get_property_value(self.ptr, c_property.as_ptr())
        };

        Ok(value)
    }

    /// Set a property value
    pub fn set_property(&mut self, property: &str, value: f64) -> Result<()> {
        let c_property = CString::new(property)
            .context("Invalid property name")?;

        unsafe {
            ffi::jsbsim_set_property_value(self.ptr, c_property.as_ptr(), value);
        }

        Ok(())
    }

    /// Get the simulation time in seconds
    pub fn get_sim_time(&self) -> f64 {
        unsafe { ffi::jsbsim_get_sim_time(self.ptr) }
    }

    /// Set the integration time step
    pub fn set_dt(&mut self, dt: f64) {
        unsafe { ffi::jsbsim_set_dt(self.ptr, dt); }
    }

    /// Get the delta T (time step)
    pub fn get_dt(&self) -> f64 {
        unsafe { ffi::jsbsim_get_delta_t(self.ptr) }
    }

    /// Set the root directory
    pub fn set_root_dir<P: AsRef<Path>>(&mut self, root_dir: P) -> Result<()> {
        let path_str = root_dir.as_ref().to_str()
            .context("Invalid root directory")?;
        let c_path = CString::new(path_str)
            .context("Invalid root directory")?;

        let result = unsafe {
            ffi::jsbsim_set_root_dir(self.ptr, c_path.as_ptr())
        };

        if !result {
            anyhow::bail!("Failed to set root directory");
        }

        Ok(())
    }

    /// Set the aircraft path
    pub fn set_aircraft_path<P: AsRef<Path>>(&mut self, path: P) -> Result<()> {
        let path_str = path.as_ref().to_str()
            .context("Invalid aircraft path")?;
        let c_path = CString::new(path_str)
            .context("Invalid aircraft path")?;

        let result = unsafe {
            ffi::jsbsim_set_aircraft_path(self.ptr, c_path.as_ptr())
        };

        if !result {
            anyhow::bail!("Failed to set aircraft path");
        }

        Ok(())
    }

    /// Set the engine path
    pub fn set_engine_path<P: AsRef<Path>>(&mut self, path: P) -> Result<()> {
        let path_str = path.as_ref().to_str()
            .context("Invalid engine path")?;
        let c_path = CString::new(path_str)
            .context("Invalid engine path")?;

        let result = unsafe {
            ffi::jsbsim_set_engine_path(self.ptr, c_path.as_ptr())
        };

        if !result {
            anyhow::bail!("Failed to set engine path");
        }

        Ok(())
    }

    /// Set the systems path
    pub fn set_systems_path<P: AsRef<Path>>(&mut self, path: P) -> Result<()> {
        let path_str = path.as_ref().to_str()
            .context("Invalid systems path")?;
        let c_path = CString::new(path_str)
            .context("Invalid systems path")?;

        let result = unsafe {
            ffi::jsbsim_set_systems_path(self.ptr, c_path.as_ptr())
        };

        if !result {
            anyhow::bail!("Failed to set systems path");
        }

        Ok(())
    }

    /// Set the output path
    pub fn set_output_path<P: AsRef<Path>>(&mut self, path: P) -> Result<()> {
        let path_str = path.as_ref().to_str()
            .context("Invalid output path")?;
        let c_path = CString::new(path_str)
            .context("Invalid output path")?;

        let result = unsafe {
            ffi::jsbsim_set_output_path(self.ptr, c_path.as_ptr())
        };

        if !result {
            anyhow::bail!("Failed to set output path");
        }

        Ok(())
    }

    /// Disable output
    pub fn disable_output(&mut self) {
        unsafe { ffi::jsbsim_disable_output(self.ptr); }
    }

    /// Enable output
    pub fn enable_output(&mut self) {
        unsafe { ffi::jsbsim_enable_output(self.ptr); }
    }

    /// Hold (pause) the simulation
    pub fn hold(&mut self) {
        unsafe { ffi::jsbsim_hold(self.ptr); }
    }

    /// Resume the simulation
    pub fn resume(&mut self) {
        unsafe { ffi::jsbsim_resume(self.ptr); }
    }

    /// Check if simulation is holding
    pub fn is_holding(&self) -> bool {
        unsafe { ffi::jsbsim_holding(self.ptr) }
    }
}

impl Default for JSBSimExecutive {
    fn default() -> Self {
        Self::new().expect("Failed to create JSBSim executive")
    }
}

// Drop implementation to clean up C++ resources
impl Drop for JSBSimExecutive {
    fn drop(&mut self) {
        unsafe {
            ffi::jsbsim_destroy(self.ptr);
        }
    }
}

// Implement Send for JSBSimExecutive (single-threaded use only)
unsafe impl Send for JSBSimExecutive {}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_create_executive() {
        let exec = JSBSimExecutive::new();
        assert!(exec.is_ok());
    }

    #[test]
    fn test_time_functions() {
        let exec = JSBSimExecutive::new().unwrap();
        let sim_time = exec.get_sim_time();
        assert_eq!(sim_time, 0.0);
    }
}
