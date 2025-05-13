import jsbsim

fdm = jsbsim.FGFDMExec(r"./src/jsbsim/param-xml")  # Use JSBSim default aircraft data.
fdm.load_script("pq_simulation.xml")

fdm.run_ic()

while fdm.run():
    pass
