# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Environment

Always use the `project_dead_mans_fingers` conda environment. `pytest` is not pre-installed, so invoke it via:

```bash
/home/scott/anaconda3/envs/project_dead_mans_fingers/bin/python -m pytest
```

If `pytest` is missing, install it first:
```bash
/home/scott/anaconda3/envs/project_dead_mans_fingers/bin/python -m pip install pytest
```

## Running Tests

Run all tests in a subdirectory:
```bash
/home/scott/anaconda3/envs/project_dead_mans_fingers/bin/python -m pytest test/test_preprocessing/ -v
```

Run a single test file:
```bash
/home/scott/anaconda3/envs/project_dead_mans_fingers/bin/python -m pytest test/test_preprocessing/test_standardize_input.py -v
```

Run a single test by name:
```bash
/home/scott/anaconda3/envs/project_dead_mans_fingers/bin/python -m pytest test/test_preprocessing/test_standardize_input.py::test_standardize_rounds_to_two_decimal_places -v
```

## Running the Application

The main entry point takes a JSON config file and an optional `--simulation` flag:

```bash
/home/scott/anaconda3/envs/project_dead_mans_fingers/bin/python main.py <path/to/config.json> --simulation
```

Example config files are in `test/test_config_ax_demo.json` and `test_config_ax_demo.json`. Simulation mode archives any existing Ax state file and runs without hardware.

## Architecture

The system controls an automated flow-chemistry platform that optimizes photochemical reactions using multi-objective Bayesian optimization (qNEHVI via Ax/BoTorch).

### State Classes (`bayesian_optimizer/experiment_state.py`)

Two dataclasses carry all state — nothing global:

- **`BoCampaignState`**: campaign-level config (`bo_parameters` dict from JSON, `simulation_mode`, `results_cache`, `noise_sem`, `bo_csv_path`). The `get_parameter_bounds()` method extracts min/max bounds for all 6 optimization parameters.
- **`IterationState`**: per-trial state (`iteration`, `trial_conditions`, `instrument_parameters`, `absorbance_at_steady_state`, `reactor_bed_concentration_uM`).

### Execution Flow

```
main.py
  └─ generate_bo_input_file()          # preprocessing/generate_bo_input.py
       Transforms master JSON → analog-specific JSON (indexes per-analog arrays)
  └─ run_bo_campaign()                 # bayesian_optimizer/run_bo_campaign.py
       Initializes BoCampaignState, loads/creates Ax experiment
       Loop:
         ax.get_next_trial() → ax_suggested_experiment()
           └─ run_bayesian_optimization_iteration()  # experimental_commands/execute_bo_iteration_commands.py
                1. constrain_to_search_space() → standardize_input()  # clip & round params
                2. Check results_cache (skip repeat experiments)
                3. prepare_experiment()   → parameters_to_commands() → save CSV files
                4. run_experiment()       → hardware or run_simulated_experiment()
                5. analyze_and_save_results() → analyze_experiment_results() → append CSV
         ax.complete_trial()
         ax.save_to_json_file()
```

### Key Design Points

**JSON config structure**: The master config (e.g., `test_config_ax_demo.json`) has per-analog arrays for concentrations, wavelengths, extinction coefficients, etc. `generate_bo_input_file()` picks the right index for each analog and writes an analog-specific JSON to `base_directory/bo_campaign/`.

**Parameter flow**: The 6 BO parameters (`flow_rate`, `dilution_factor`, `temperature`, `co_solvent_valve_position`, `co_solvent_dilution_factor`, `light_intensity`) live in `IterationState.trial_conditions`. `parameters_to_commands()` converts these to pump flow rates (F1–F4) and volumes using mass-balance dilution math, storing results in `IterationState.instrument_parameters`.

**Pump math**: F1 = F_total × D_substrate; F2 = F_total × (1 − D_substrate − D_cosolvent); F3 = F_total × D_cosolvent; F4 is a post-reactor dilution pump to bring concentration into the UV detector's linear range — set to 0 if no dilution is needed.

**Results cache**: `BoCampaignState.results_cache` is a dict keyed by a tuple of standardized `trial_conditions` values. Duplicate parameter sets return cached (percent_yield, throughput) without re-running the experiment.

**Hardware vs simulation**: Controlled by `BoCampaignState.simulation_mode`. In simulation mode, `utils/run_simulation.py` generates synthetic UV-Vis CSV data. In hardware mode, `experimental_commands/commands.py` sends commands to serial-connected instruments.

**Post-processing**: `post_processing/post_processing_results.py` reads UV-Vis CSVs, applies Beer-Lambert law at two wavelengths (reactant ~409 nm, product ~506 nm) to calculate concentrations, then computes percent yield and throughput (nmol/min).

### Module Map

| Directory | Purpose |
|-----------|---------|
| `bayesian_optimizer/` | Ax/BoTorch integration, state classes, campaign loop |
| `preprocessing/` | Parameter validation, clamping, standardization, command conversion |
| `experimental_commands/` | CSV command generation, hardware execution, simulation dispatch |
| `post_processing/` | UV-Vis analysis, yield/throughput calculation, results CSV appending |
| `production_run/` | Post-optimization scale-up run (selects best Pareto conditions) |
| `utils/` | Simulation data generation, result visualization, exception types |
| `test/test_preprocessing/` | Pytest unit tests (currently the most complete test suite) |
| `optimization_and_production_run_data/` | Output directory for all run CSVs and Ax state JSON files |
