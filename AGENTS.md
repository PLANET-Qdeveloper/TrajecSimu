# Repository Guidelines

## Project Structure & Module Organization
TrajecSimu orchestrates multi-run simulations around JSBSim. Core orchestration lives in `src/main.py`, which loads YAML launch scenarios and fan-outs parameter sweeps. Domain logic sits inside `src/trajecsim`: `jsbsim_support/` generates XML parameter packs and invokes the bundled `jsbsim/` simulator, `util/` handles logging, chart generation, and KML export, while `landing_range/` captures landing-range analytics per site. Scenario assets belong under `data/input/` (`landed_area.yaml`, tables/) and raw results are written to `data/result*/`. Keep illustrative screenshots in `images/`; large third-party JSBSim sources stay under `jsbsim/`.

## Build, Test, and Development Commands
- `uv sync`: resolve dependencies into the local `.venv` targeting Python 3.12.
- `uv run python src/main.py --config_file_path data/input/landed_area.yaml --output_dir data/result`: run a baseline trajectory batch; adjust `--template_dir` or output toggles as needed.
- `uv run pytest`: execute the test suite.
- `uv run ruff check src tests`: lint formatting and quality gates.
- `uv run mypy src`: enforce typing across the packages.

## Coding Style & Naming Conventions
Follow RuffÅfs defaults (line length 120, Google-style docstrings) and keep modules formatted via `ruff format`. Name modules and functions in `snake_case`, classes in `PascalCase`, and constants in `UPPER_SNAKE_CASE`. YAML configuration keys should mirror the `Params` dataclasses: lowercase with underscores. Always add type hints and prefer dataclasses or Pydantic models when exchanging structured data.

## Testing Guidelines
Place tests under `tests/`, mirroring `src/trajecsim` folders (e.g., `tests/jsbsim_support/test_generate_param_xml.py`). Use `pytest` parametrization to cover multiple launch profiles using fixtures that load sample YAML from `data/input`. When simulations produce heavy artifacts, direct them to a disposable temporary directory and assert on summaries (CSV columns, KML metadata) rather than raw binaries. Target at least smoke coverage for new CLI options and any numerical utilities; document gaps in the PR when precision tolerances prevent assertions.

## Commit & Pull Request Guidelines
Git history favors short imperative messages (`fix table rotation`, `fix conf`). Follow the same format: lowercase, lead with a verb, and keep to 50 characters where possible. Each PR should describe the scenario, include reproduction steps, reference the relevant issue, and attach plots or tables from `data/result*/` when behaviour changes. Run `uv run pytest` and `uv run ruff check` before opening; note skipped tests or outstanding data dependencies explicitly.
