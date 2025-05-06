import jsbsim

fdm = jsbsim.FGFDMExec(r"./src/jsbsim/param-xml")  # Use JSBSim default aircraft data.
fdm.load_script("pq_simulation.xml")
# fdm.set_output_directive("./output_file.xml")
fdm.run_ic()

while fdm.run():
    pass
