# Output Data Collection System

This document describes the output data collection system for TrajecSimu rocket simulations.

## Overview

The output system collects comprehensive simulation data from JSBSim at each time step, converting from JSBSim's internal units (imperial) to SI units (metric) and organizing data into structured types.

## Architecture

```
┌─────────────────┐
│  JSBSimExecutive │  ← Simulation engine
└────────┬────────┘
         │ get_property()
         ↓
┌─────────────────┐
│  DataCollector  │  ← Collects & converts data
└────────┬────────┘
         │ collect_frame()
         ↓
┌─────────────────┐
│ SimulationFrame │  ← Single time step data
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│FlightTrajectory │  ← Complete trajectory
└────────┬────────┘
         │
         ├─→ JSON (detailed)
         └─→ CSV (summary)
```

## Data Structures

### SimulationFrame

A complete snapshot of the simulation state at a single time step. Contains:

#### PositionData
- Altitude (ASL and AGL) [m]
- Latitude/Longitude [deg]
- ECEF position [m]
- Terrain elevation [m]

#### AttitudeData
- Euler angles (φ, θ, ψ) [deg]
- Quaternions
- Aerodynamic angles (α, β) [deg]

#### VelocityData
- Total and inertial velocity [m/s]
- Body frame velocities (u, v, w) [m/s]
- NED frame velocities [m/s]
- ECEF velocities [m/s]
- Dynamic pressure [Pa]
- Reynolds number

#### AngularRates
- Body rates (P, Q, R) [deg/s]
- Angular accelerations [deg/s²]
- Inertial rates [deg/s]

#### Forces
- Aerodynamic forces (drag, side, lift) [N]
- Forces in body frame [N]
- Propulsion forces [N]
- Weight forces [N]
- Total forces [N]
- L/D ratio

#### Moments
- Aerodynamic moments [N⋅m]
- Propulsion moments [N⋅m]
- Total moments [N⋅m]

#### AtmosphereData
- Density [kg/m³]
- Temperature [K]
- Pressure [Pa]
- Viscosity [Pa⋅s, m²/s]
- Wind (NED frame) [m/s]
- Turbulence magnitude and direction

#### MassProperties
- Mass [kg]
- Weight [N]
- Center of gravity [m]
- Moments of inertia [kg⋅m²]

#### PropulsionData
- Thrust magnitude and components [N]
- Propellant mass [kg]
- Engine status

#### CustomProperties
- Parachute area [m²]
- Parachute deployment status
- Flight stage
- Flight phase (boost/coast/descent/landed)

## Unit Conversions

All data is automatically converted from JSBSim's imperial units to SI units:

| Quantity | JSBSim Unit | Output Unit | Conversion Factor |
|----------|-------------|-------------|-------------------|
| Length | ft | m | 0.3048 |
| Area | ft² | m² | 0.09290304 |
| Velocity | ft/s | m/s | 0.3048 |
| Force | lbf | N | 4.4482216152605 |
| Moment | lbf⋅ft | N⋅m | 1.3558179483314 |
| Pressure | psf | Pa | 47.880258888889 |
| Mass | slug | kg | 14.5939029372 |
| Density | slug/ft³ | kg/m³ | 515.3788184 |
| Temperature | °R | K | ×(5/9) |
| Angle | rad | deg | 57.29577951308232 |

## Usage

### Basic Data Collection

```rust
use trajecsim_rs::jsbsim::JSBSimExecutive;
use trajecsim_rs::output::DataCollector;

// Create JSBSim executive and collector
let exec = JSBSimExecutive::new()?;
let collector = DataCollector::new();

// Collect a single frame
let frame = collector.collect_frame(&exec)?;

// Access data
println!("Altitude: {:.2} m", frame.position.altitude_asl_m);
println!("Velocity: {:.2} m/s", frame.velocity.v_total_ms);
println!("Thrust: {:.2} N", frame.propulsion.thrust_n);
```

### Full Trajectory Collection

```rust
use trajecsim_rs::output::{FlightTrajectory, TrajectoryMetadata};

// Setup metadata
let metadata = TrajectoryMetadata {
    simulation_id: "sim_001".to_string(),
    time_step_s: 0.01,
    launch_latitude_deg: 35.0,
    launch_longitude_deg: 139.0,
    launch_altitude_m: 100.0,
    wind_speed_ms: 5.0,
    wind_direction_deg: 270.0,
    rocket_config: "my_rocket".to_string(),
};

let mut trajectory = FlightTrajectory::new("sim".to_string(), metadata);

// Simulation loop
while exec.run()? {
    let frame = collector.collect_frame(&exec)?;
    trajectory.add_frame(frame);
}

// Analyze
if let Some(apogee) = trajectory.get_apogee() {
    println!("Max altitude: {:.2} m", apogee.position.altitude_asl_m);
}
```

### Saving Results

#### JSON Format (Detailed)

```rust
use std::fs;

// Save complete trajectory as JSON
let json = serde_json::to_string_pretty(&trajectory)?;
fs::write("trajectory.json", json)?;
```

JSON output includes all fields from `SimulationFrame`, suitable for:
- Detailed analysis
- Post-processing
- Visualization tools
- Debugging

#### CSV Format (Summary)

```rust
use csv;

// Convert to summary and save as CSV
let summary = trajectory.to_summary();
let mut writer = csv::Writer::from_path("trajectory.csv")?;
for record in summary {
    writer.serialize(record)?;
}
writer.flush()?;
```

CSV output includes only key fields:
- Time
- Altitude
- Velocity
- Latitude/Longitude
- Thrust
- Parachute area

Suitable for:
- Quick visualization
- Spreadsheet analysis
- Plotting libraries

## Trajectory Analysis

Built-in analysis methods:

```rust
// Find apogee
let apogee_frame = trajectory.get_apogee();

// Maximum velocity
let max_vel = trajectory.get_max_velocity();

// Landing position
let (lat, lon) = trajectory.get_landing_position()?;

// Flight duration
let duration = trajectory.get_flight_duration();
```

## Custom Properties

The system supports custom rocket-specific properties:

```rust
// In JSBSim XML, define custom properties:
// <property>fcs/parachute-area-ft2</property>
// <property>simulation/flight-phase</property>
// <property>simulation/stage</property>

// They are automatically collected if available
let parachute_deployed = frame.custom.parachute_deployed;
let flight_phase = frame.custom.flight_phase;
```

## Error Handling

The collector gracefully handles missing properties:

```rust
match collector.collect_frame(&exec) {
    Ok(frame) => {
        // Process frame
    }
    Err(e) => {
        eprintln!("Could not collect frame: {}", e);
        // Properties may not exist if model isn't loaded
    }
}
```

For custom properties, default values are used if properties don't exist:
- `parachute_area_m2`: 0.0
- `flight_phase`: 0
- `stage`: 1

## Performance Considerations

### Collection Frequency

Collecting every frame generates large amounts of data. Consider:

```rust
let collect_interval = 10; // Collect every 10th frame

let mut frame_count = 0;
while exec.run()? {
    if frame_count % collect_interval == 0 {
        let frame = collector.collect_frame(&exec)?;
        trajectory.add_frame(frame);
    }
    frame_count += 1;
}
```

For a 100-second simulation at 0.01s time step with 10× decimation:
- Total frames: 10,000
- Collected frames: 1,000
- Time resolution: 0.1s

### Memory Usage

Each `SimulationFrame` is approximately:
- Memory: ~1 KB
- JSON: ~2-3 KB
- CSV (summary): ~80 bytes

For 1,000 frames:
- Memory: ~1 MB
- JSON file: ~2-3 MB
- CSV file: ~80 KB

## Examples

See the `examples/` directory:

- `data_collection.rs` - Basic data collection demo
- `full_simulation.rs` - Complete workflow with file output

Run examples:

```bash
cargo run --example data_collection
cargo run --example full_simulation
```

## Integration with Python Analysis

The JSON and CSV outputs can be easily analyzed with Python:

```python
import pandas as pd
import json

# Load CSV summary
df = pd.read_csv('trajectory_summary.csv')
print(df['altitude_m'].max())

# Load full JSON trajectory
with open('trajectory_full.json') as f:
    data = json.load(f)
    frames = data['frames']
    altitudes = [f['position']['altitude_asl_m'] for f in frames]
```

## Future Enhancements

Potential improvements:

1. **Binary output format** - More efficient storage (MessagePack, Apache Arrow)
2. **Streaming output** - Write to disk during simulation
3. **Compression** - Gzip compressed JSON/CSV
4. **HDF5 support** - Industry-standard scientific data format
5. **Real-time plotting** - Live visualization during simulation
6. **Derived quantities** - Calculate additional parameters (energy, range, etc.)

## References

- JSBSim property reference: https://jsbsim-team.github.io/jsbsim-reference-manual/
- Serde documentation: https://serde.rs/
- CSV crate: https://docs.rs/csv/
