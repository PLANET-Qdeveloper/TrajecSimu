pub mod processor;
pub mod analyzer;
pub mod types;
pub mod collector;

// Re-export commonly used types
pub use types::{
    SimulationFrame, SimulationSummary, FlightTrajectory,
    PositionData, AttitudeData, VelocityData, AngularRates,
    Forces, Moments, AtmosphereData, MassProperties,
    PropulsionData, CustomProperties, TrajectoryMetadata,
};
pub use collector::DataCollector;
