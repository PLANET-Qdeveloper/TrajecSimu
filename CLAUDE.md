# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

TrajecSimu is a rocket trajectory simulation tool built on JSBSim (6-DOF flight simulator). It simulates rocket flight paths with various parameters including wind conditions, rocket characteristics, and parachute deployment.

## Development Commands

### Package Management
- **Install dependencies**: `uv sync`
- **Run main simulation**: `uv run src/main.py --config_file_path data/input/landed_area.yaml --output_dir data/result`
- **Run with chart output**: `uv run src/main.py --chart_output True`

### Code Quality
- **Lint code**: `uv run ruff check`
- **Format code**: `uv run ruff format`
- **Type checking**: `uv run mypy src/`

### Documentation
- **Build docs**: `uv run mkdocs build`
- **Serve docs locally**: `uv run mkdocs serve`

## Architecture Overview

### Core Structure
- `src/main.py`: Entry point that orchestrates the entire simulation workflow
- `src/trajecsim/jsbsim_support/`: JSBSim integration and parameter generation
- `src/trajecsim/util/`: Utility functions for logging, charting, KML generation, and result analysis

### Key Workflow
1. **Parameter Loading**: YAML configuration loaded via `yaml_loader.py`
2. **Parameter Generation**: Cartesian product of all parameter combinations via `parameter_product.py`
3. **XML Generation**: JSBSim XML files generated from Jinja2 templates in `param-xml-template/`
4. **Simulation Execution**: Parallel JSBSim runs via `jsb_runner.py`
5. **Result Processing**: Data aggregation, extrema analysis, and output generation

### Schema System
The project uses Pydantic for configuration validation:
- `schemas/launch.py`: Launch site parameters (coordinates, wind, launcher specs)
- `schemas/rocket.py`: Rocket physical properties, aerodynamics, fuel/oxidizer
- `schemas/simulation.py`: Simulation settings (duration, timestep, output rate)
- `schemas/validator.py`: Custom validation helpers for list conversion

### Data Flow
- Input: YAML config + CSV tables (thrust, drag coefficients)
- Processing: Generate parameter combinations → XML templates → JSBSim execution
- Output: CSV summaries, KML files, optional time-series charts

## Key Configuration

### Main Parameters
- **Wind conditions**: Direction and speed arrays for parametric sweeps
- **Rocket specs**: Mass properties, aerodynamic coefficients, parachute settings
- **Launch site**: Coordinates, elevation, launcher geometry
- **Simulation**: Time step, duration, output rates

### Result Grouping
- `kml_group_by`: Parameters to group KML output by (e.g., wind conditions)
- `result_each`: Parameters to create separate result directories for

## Development Notes

### Parallel Processing
The simulation leverages `joblib` for parallel execution across CPU cores. Each parameter combination runs as an independent JSBSim process.

### Template System
XML generation uses Jinja2 templates in `param-xml-template/` to create JSBSim aircraft and simulation configuration files dynamically.

### Data Output
Results include:
- Raw CSV data per simulation run
- Summary statistics (max altitude, speed, landing coordinates)
- Extrema analysis for key flight phases
- Optional time-series plots
- KML files for geographic visualization