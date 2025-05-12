import asyncio

import jsbsim


async def run_jsbsim():
    fdm = jsbsim.FGFDMExec(r"./src/jsbsim/param-xml")  # Use JSBSim default aircraft data.
    fdm.load_script("pq_simulation.xml")
    fdm.run_ic()

    while fdm.run():
        pass


async def main():
    await asyncio.gather(
        run_jsbsim(),
    )


if __name__ == "__main__":
    asyncio.run(main())
