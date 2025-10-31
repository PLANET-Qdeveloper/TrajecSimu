use anyhow::Result;
use trajecsim_rs::jsbsim::JSBSimExecutive;

fn main() -> Result<()> {
    println!("JSBSim Basic Integration Example\n");

    // Create a new JSBSim executive
    println!("Creating JSBSim executive...");
    let mut exec = JSBSimExecutive::new()?;
    println!("✓ JSBSim executive created successfully");

    // Get initial simulation time
    let sim_time = exec.get_sim_time();
    println!("Initial simulation time: {:.2}s", sim_time);

    // Get delta T
    let dt = exec.get_dt();
    println!("Time step (dt): {:.4}s", dt);

    // Set a custom time step
    exec.set_dt(0.01);
    println!("✓ Set time step to 0.01s");

    let new_dt = exec.get_dt();
    println!("New time step (dt): {:.4}s", new_dt);

    println!("\nJSBSim integration is working correctly!");

    Ok(())
}
