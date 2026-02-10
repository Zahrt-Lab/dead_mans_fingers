# Bayesian Optimizer Workflow Documentation

## Overview

This document explains the complete workflow of the multi-objective Bayesian optimization system for the project_dead_mans_fingers automated flow chemistry platform. The optimizer uses **Ax Platform** (Meta's Adaptive Experimentation platform) with **qNEHVI** (q-Noisy Expected Hypervolume Improvement) for multi-objective optimization.

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Architecture Overview](#architecture-overview)
3. [Complete Workflow](#complete-workflow)
4. [Module Descriptions](#module-descriptions)
5. [File Structure](#file-structure)
6. [Data Flow](#data-flow)
7. [Simulation vs Hardware Mode](#simulation-vs-hardware-mode)

---

## Quick Start

### Running an Optimization Campaign

```bash
# Simulation mode (no hardware required)
python main.py test_config_ax_demo.json --simulation --trials 10

# Hardware mode (requires AutoZahrt platform)
python main.py test_config_ax_demo.json --trials 10
```

### Command Line Arguments

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `input_experimental_parameters` | str | *required* | Path to experiment JSON config file |
| `--trials` | int | 30 | Number of Bayesian optimization iterations |
| `--state-path` | str | ax_state.json | Path to save/load Ax optimization state |
| `--save-every` | int | 1 | Save state every K trials |
| `--objA-threshold` | float | 1.0 | Percent yield threshold for hypervolume |
| `--objB-threshold` | float | 1e-9 | Throughput threshold for hypervolume |
| `--noise-sem` | float | 1e-3 | Noise standard error for Gaussian Process |
| `--simulation` | flag | False | Use simulated data instead of hardware |

---

## Architecture Overview

### High-Level Components

```
┌─────────────────────────────────────────────────────────────────┐
│                         main.py                                  │
│                  Entry Point & CLI Parser                        │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                   run_bo_campaign.py                             │
│     Campaign Orchestrator (Multi-Trial Loop)                    │
│  • Loads experimental parameters                                │
│  • Initializes/resumes Ax client                                │
│  • Runs n optimization trials                                   │
│  • Saves state periodically                                     │
│  • Prints Pareto front                                          │
└────────┬────────────────────────────┬───────────────────────────┘
         │                            │
         ▼                            ▼
┌──────────────────────┐    ┌──────────────────────┐
│ init_or_load_ax.py   │    │   evaluate_ax.py     │
│  Ax Client Setup     │    │  Experiment Wrapper  │
│  • Load from state   │    │  • Extract params    │
│  • Create new        │    │  • Run experiment    │
│  • Define search     │    │  • Handle errors     │
│    space & objectives│    │  • Return results    │
└──────────────────────┘    └──────────┬───────────┘
                                       │
                                       ▼
                     ┌──────────────────────────────────┐
                     │    experiment_executor.py        │
                     │  Single Experiment Executor      │
                     │  • Constrain parameters          │
                     │  • Generate commands             │
                     │  • Run simulation OR hardware    │
                     │  • Post-process UV data          │
                     │  • Calculate yield & throughput  │
                     │  • Cache results                 │
                     └──────────────────────────────────┘
```

---

## Complete Workflow

### Phase 1: Initialization (First Run)

```
1. main.py
   └─ Parse command line arguments
   └─ Call run_bo_campaign()

2. run_bo_campaign.py
   └─ Load experimental parameters from JSON
   └─ Validate required parameters
   └─ Set global state (state.py)
      • EXPERIMENTAL_PARAMETERS
      • NOISE_SEM
      • SIMULATION_MODE
   └─ Extract parameter bounds from config

3. init_or_load_ax.py
   └─ Check if state file exists (ax_state.json)
   └─ If NEW campaign:
      ├─ Create new AxClient
      ├─ Define search space with 6 parameters:
      │  • flow_rate (int): reactor flow rate [µL/min]
      │  • dilution_factor (float): substrate dilution [0-1]
      │  • temperature (float): reactor temperature [°C]
      │  • co_solvent (int): valve position for co-solvent
      │  • co_solvent_volume (float): co-solvent fraction [0-1]
      │  • light_intensity (float): LED light intensity [%]
      ├─ Define objectives (both maximize):
      │  • percent_yield: % conversion to product
      │  • throughput: nmol/min production rate
      └─ Return new ax client
   └─ If RESUMING:
      ├─ Load AxClient from JSON
      └─ Return existing ax client with history
```

### Phase 2: Optimization Loop (Each Trial)

```
FOR trial_number = 1 to n_trials:

   1. run_bo_campaign.py
      └─ ax.get_next_trial()
         • Ax uses qNEHVI acquisition function
         • Proposes next parameter set to evaluate
      
   2. evaluate_ax.py
      └─ Extract 6 parameters from Ax proposal
      └─ Call run_bayesian_optimization_iteration()
      
   3. experiment_executor.py
      
      3a. PREPROCESSING
          ├─ constrain_to_search_space(): Ensure params within bounds
          ├─ standardize_input(): Round/normalize for cache lookup
          ├─ Check RESULTS_CACHE: Skip if experiment done before
          └─ Increment iteration counter
      
      3b. SETUP
          ├─ Create directories for this iteration
          ├─ Calculate reactor concentrations
          └─ parameters_to_commands(): Convert to instrument settings
             • Flow rates for 4 pumps
             • Valve positions
             • Volumes to dispense
      
      3c. VOLUME CHECKING (Hardware mode only)
          └─ check_volume(): Verify sufficient stock solutions
             • Raises ExperimentAborted if insufficient
      
      3d. EXPERIMENT EXECUTION
          
          IF SIMULATION_MODE:
              └─ run_simulation(): Generate synthetic UV-Vis data
                 • Realistic absorbance traces
                 • Based on input parameters
          
          IF HARDWARE_MODE:
              ├─ generate_instrument_config(): Create config CSV
              ├─ save_commands_csv(): Write command files
              ├─ run_commands(): Execute on AutoZahrt platform
              │  • Move valves
              │  • Start pumps
              │  • Heat reactor
              │  • Run UV-Vis detector
              │  • Collect real-time data
              └─ Monitor progress
      
      3e. POST-PROCESSING
          ├─ post_process_uv_recording(): Process UV spectra
          │  • Baseline correction
          │  • Steady-state detection
          ├─ average_absorbance(): Get final absorbance values
          │  • Reactant wavelength (e.g., 409 nm)
          │  • Product wavelength (e.g., 506 nm)
          ├─ calculate_concentration_in_the_reactor_bed():
          │  • Use Beer-Lambert law
          │  • Account for dilution factors
          ├─ calculate_percent_yield(): % conversion
          └─ calculate_product_throughput(): nmol/min
      
      3f. RESULTS STORAGE
          ├─ append_bayesian_experimental_results(): Save to CSV
          ├─ Update RESULTS_CACHE: Avoid duplicates
          └─ Return (percent_yield, throughput)
   
   4. evaluate_ax.py
      └─ Wrap results in Ax format:
         {
            "percent_yield": (mean, sem),
            "throughput": (mean, sem)
         }
   
   5. run_bo_campaign.py
      ├─ ax.complete_trial(): Update Ax model with results
      ├─ Refit Gaussian Process surrogate model
      ├─ Save state to JSON (every save_every trials)
      └─ Print progress

REPEAT until n_trials complete or KeyboardInterrupt
```

### Phase 3: Completion

```
1. run_bo_campaign.py
   ├─ Save final state to JSON
   ├─ ax.get_pareto_optimal_parameters()
   │  • Extract non-dominated solutions
   │  • These represent best trade-offs
   └─ Print Pareto front:
      Example:
      {'flow_rate': 120, 'dilution_factor': 0.5, ...}
      -> {'percent_yield': 85.3, 'throughput': 2.4e-7}
```

---

## Module Descriptions

### 1. `main.py`
**Purpose:** Entry point and command-line interface  
**Key Functions:**
- `parse_args()`: Parse command-line arguments
- `main()`: Call run_bo_campaign with parsed arguments

**Inputs:** Command-line arguments  
**Outputs:** None (orchestrates entire campaign)

---

### 2. `run_bo_campaign.py`
**Purpose:** High-level campaign orchestrator (multi-trial loop)  
**Key Functions:**
- `run_bo_campaign()`: Main optimization loop

**Does:**
- Loads experimental parameters from JSON
- Validates required parameters
- Initializes or resumes Ax client
- Runs n optimization trials
- Saves state periodically  
- Prints Pareto-optimal solutions

**Inputs:**
- Path to experimental config JSON
- Trial count, state path, save frequency
- Objective thresholds, noise SEM
- Simulation mode flag

**Outputs:**
- Saved optimization state (ax_state.json)
- Results CSV file
- Console output with progress

---

### 3. `init_or_load_ax.py`
**Purpose:** Ax client initialization and configuration  
**Key Functions:**
- `_init_or_load_ax()`: Create new or load existing Ax client

**Does:**
- Checks for existing state file
- Loads previous campaign if found
- Creates new AxClient with:
  - 6-parameter search space
  - 2 optimization objectives (percent_yield, throughput)
  - qNEHVI acquisition function (implicit)

**Inputs:**
- State file path
- Parameter bounds (min/max for each of 6 parameters)
- Objective thresholds

**Outputs:** Configured AxClient instance

---

### 4. `evaluate_ax.py`
**Purpose:** Wrapper between Ax and experiment execution  
**Key Functions:**
- `evaluate_ax()`: Evaluate one parameter set

**Does:**
- Extracts 6 parameters from Ax proposal dictionary
- Calls `run_bayesian_optimization_iteration()`
- Handles exceptions gracefully
- Returns results in Ax-compatible format: `{metric: (mean, sem)}`

**Inputs:** Parameter dictionary from Ax  
**Outputs:** Results dictionary with (mean, sem) tuples

**Error Handling:**
- Catches all exceptions during experiment
- Logs to results CSV with error message
- Returns (0.0, 0.0) for failed runs (Ax ignores these)

---

### 5. `experiment_executor.py` (formerly `bayesian_optimization_run.py`)
**Purpose:** Single experiment execution engine  
**Key Functions:**
- `run_bayesian_optimization_iteration()`: Execute one experiment
- `objective_function_percent_yield()`: Wrapper for yield only
- `objective_function_throughput()`: Wrapper for throughput only

**Does:**
1. **Preprocessing:**
   - Constrains parameters to valid ranges
   - Standardizes inputs for caching
   - Checks if experiment already done

2. **Setup:**
   - Creates output directories
   - Converts optimization parameters to instrument commands
   - Checks stock solution volumes (hardware mode)

3. **Execution:**
   - **Simulation:** Generates synthetic UV-Vis data
   - **Hardware:** Executes real experiment on AutoZahrt platform

4. **Post-processing:**
   - Processes UV-Vis spectra
   - Calculates concentrations (Beer-Lambert law)
   - Computes percent yield and throughput

5. **Storage:**
   - Appends results to CSV
   - Caches to avoid duplicate experiments

**Inputs:** Tuple of 6 floats (flow_rate, dilution, temp, cosolvent, cosolvent_vol, light)  
**Outputs:** Tuple of 2 floats (percent_yield, throughput)

---

### Supporting Modules

#### `state.py`
**Purpose:** Global state management  
**Contains:**
- `EXPERIMENTAL_PARAMETERS`: Config loaded from JSON
- `iteration`: Counter and stock solution volumes
- `RESULTS_CACHE`: Avoid redundant experiments
- `NOISE_SEM`: Noise level for Gaussian Process
- `SIMULATION_MODE`: Flag for simulation vs hardware

#### Preprocessing Modules
- `standardize_input.py`: Round parameters for cache lookup
- `constrain_to_search_space.py`: Enforce parameter bounds
- `parameters_to_commands.py`: Convert params to pump/valve settings
- `check_volume.py`: Verify sufficient stock solutions

#### Experimental Command Modules
- `commands.py`: Execute instrument commands
- `generate_instrument_config.py`: Create hardware config files
- `generate_experimental_commands.py`: Generate command sequences

#### Post-Processing Modules
- `post_process_uv_recording.py`: UV spectrum processing
- `average_absorbance.py`: Extract steady-state absorbance
- `calculate_percent_yield.py`: Compute % conversion
- `calculate_concentration_in_reactor_bed.py`: Beer-Lambert calculations
- `calculate_product_throughput.py`: Calculate nmol/min production
- `append_bayesian_experimental_results.py`: Save to CSV

#### Utility Modules
- `run_simulation.py`: Generate synthetic experimental data

---

## File Structure

```
project_dead_mans_fingers/
│
├── main.py                          # Entry point
│
├── bayesian_optimizer/
│   ├── run_bo_campaign.py          # Campaign orchestrator (multi-trial)
│   ├── init_or_load_ax.py          # Ax client setup
│   ├── evaluate_ax.py              # Experiment wrapper for Ax
│   ├── experiment_executor.py      # Single experiment executor
│   └── state.py                    # Global state management
│
├── preprocessing/
│   ├── experimental_parameters.py  # Load/validate config
│   ├── standardize_input.py        # Normalize parameters
│   ├── constrain_to_search_space.py # Enforce bounds
│   ├── parameters_to_commands.py   # Convert to instrument settings
│   └── check_volume.py             # Verify stock volumes
│
├── experimental_commands/
│   ├── commands.py                 # Execute hardware commands
│   ├── generate_instrument_config.py
│   ├── generate_experimental_commands.py
│   └── execute_bo_iteration_commands.py
│
├── post_processing/
│   ├── post_process_uv_recording.py
│   ├── average_absorbance.py
│   ├── calculate_percent_yield.py
│   ├── calculate_concentration_in_reactor_bed.py
│   ├── calculate_product_throughput.py
│   └── append_bayesian_experimental_results.py
│
├── utils/
│   └── run_simulation.py           # Synthetic data generator
│
├── test_config_ax_demo.json        # Example config file
├── ax_state.json                   # Optimization state (created during run)
│
└── ax_optimization_demo_results/   # Output directory
    ├── BO_results_ax_demo.csv      # All results
    ├── Fluorescent_Optimization_Iteration_N_*.csv  # Per-iteration data
    └── *.png                        # Visualization plots
```

---

## Data Flow

### Input Configuration (JSON)

Example: `test_config_ax_demo.json`

```json
{
  "flow_rate": [40, 200],              // µL/min range
  "dilution_factor": [0.3, 0.7],       // Substrate dilution
  "temperature": [25.0, 90.0],         // °C
  "cosolvents_valve_position": [1, 6], // Valve positions
  "co_solvent_dilution_factor": [0.0, 0.5], // Co-solvent fraction
  "light_intensity": [0.0, 100.0],     // % LED power
  
  "stock_concentration_uM": 1000.0,    // Substrate concentration
  "volume": 5000,                      // Target volume µL
  "base_directory": "ax_optimization_demo_results/",
  
  "reactant_wavelength": 409,          // nm
  "product_wavelength": 506,           // nm
  "epsilon_reactant_at_lambda1_L_per_mol_cm": 5000,
  "epsilon_product_at_lambda2_L_per_mol_cm": 35000,
  ...
}
```

### State File (JSON)

`ax_state.json` stores complete Ax optimization state:
- All previous trials and their results
- Gaussian Process model parameters
- Search space definition
- Objective configuration
- Can be loaded to resume optimization

### Results CSV

`BO_results_ax_demo.csv` contains all experimental results:

| Column | Description |
|--------|-------------|
| iteration | Trial number (1, 2, 3, ...) |
| flow_rate | Reactor flow rate (µL/min) |
| concentration | Dilution factor (0-1) |
| reactor_concentration_uM | Actual substrate concentration |
| temperature | Reactor temperature (°C) |
| co_solvent | Valve position |
| co_solvent_volume | Co-solvent fraction |
| light_intensity | LED power (%) |
| average_absorbance_reactant | Absorbance at λ₁ |
| average_absorbance_product | Absorbance at λ₂ |
| percent_yield | % conversion to product |
| throughput_nmol_per_min | Production rate |
| timestamp | Experiment completion time |
| status | "ok" or "error" |
| error_message | Error details (if failed) |

---

## Simulation vs Hardware Mode

### Simulation Mode (`--simulation`)

**Purpose:** Test optimizer without hardware access  

**Characteristics:**
- Fast execution (~seconds per trial)
- No hardware required
- Deterministic or stochastic synthetic data
- Perfect for:
  - Algorithm development
  - Parameter tuning
  - Testing new configurations
  - Debugging

**Data Generation:**
- `run_simulation()` in `utils/run_simulation.py`
- Generates realistic UV-Vis absorbance traces
- Can model kinetics, noise, baseline drift
- Results depend on input parameters

**Example:**
```bash
python main.py test_config_ax_demo.json --simulation --trials 10
```

---

### Hardware Mode (default)

**Purpose:** Run real experiments on AutoZahrt platform  

**Characteristics:**
- Slow execution (~5-15 min per trial)
- Requires functioning AutoZahrt hardware:
  - 4 syringe pumps
  - 2 multi-position valves
  - Temperature controller
  - UV-Vis detector with flow cell
  - Light source
- Real chemical consumption
- Real UV-Vis spectra

**Safety Features:**
- Volume checking before each experiment
- Error logging for failed runs
- State saving for crash recovery

**Example:**
```bash
python main.py test_config_ax_demo.json --trials 30
```

---

## Bayesian Optimization Details

### Multi-Objective Optimization

This system optimizes **two competing objectives simultaneously:**

1. **Percent Yield** (maximize)
   - Conversion efficiency: substrate → product
   - Calculated from UV-Vis absorbance ratio

2. **Throughput** (maximize)  
   - Production rate in nmol/min
   - Higher flow rates increase throughput but may decrease yield

**Trade-off:** High yield often requires slow flow (low throughput)

### Pareto Frontier

The optimizer finds the **Pareto front**: the set of non-dominated solutions where you can't improve one objective without worsening the other.

Example Pareto front:
```
Solution A: 95% yield, 1.2e-7 nmol/min  (slow & efficient)
Solution B: 80% yield, 3.5e-7 nmol/min  (fast & decent)
Solution C: 60% yield, 6.8e-7 nmol/min  (very fast, lower quality)
```

### qNEHVI Acquisition Function

**q-Noisy Expected Hypervolume Improvement** (qNEHVI):
- Batch acquisition function (can propose multiple experiments)
- Accounts for observation noise
- Maximizes hypervolume improvement
- Standard algorithm for multi-objective BO

### Gaussian Process Surrogate

Ax uses Gaussian Processes to model:
- `percent_yield = f₁(flow_rate, dilution, temp, ...)`
- `throughput = f₂(flow_rate, dilution, temp, ...)`

These models are updated after each experiment and used to propose the next experiment.

---

## Troubleshooting

### Common Issues

**1. Import Error: uv_vis_detector**
```
ImportError: cannot import name 'begin_uv_vis_measurement'
```
**Solution:** This is expected in simulation mode. The try/except in `experiment_executor.py` handles this.

**2. SQLAlchemy Warning**
```
WARNING: Ax currently requires a sqlalchemy version below 2.0
```
**Solution:** This is a known Ax compatibility issue. It doesn't affect functionality (SQL storage is disabled).

**3. Experiment Aborted**
```
ExperimentAborted: Insufficient volume in stock solution1
```
**Solution:** Check stock volumes in config JSON or refill physical stocks.

**4. Pareto Print Failed**
```
(Pareto print skipped: ...)
```
**Solution:** This is normal if too few trials completed. Requires 2+ trials for Pareto front.

---

## Advanced Usage

### Resume Previous Campaign

```bash
# Continues from saved state
python main.py test_config_ax_demo.json --trials 50 --state-path my_campaign.json
```

### Adjust Noise Model

Higher noise → more exploration:
```bash
python main.py config.json --noise-sem 0.01 --simulation
```

### Change Save Frequency

Save every 5 trials (reduces I/O):
```bash
python main.py config.json --save-every 5
```

### Infinite Loop Mode

Run until manual stop:
```bash
python main.py config.json --trials 0  # 0 = infinite
```

---

## References

- **Ax Platform:** https://ax.dev/
- **qNEHVI Paper:** Daulton et al. (2020) "Differentiable Expected Hypervolume Improvement for Parallel Multi-Objective Bayesian Optimization"
- **Bayesian Optimization Review:** Shahriari et al. (2016) "Taking the Human Out of the Loop: A Review of Bayesian Optimization"

---

## Contact

For questions about this codebase, contact:
- Professor Andrew Zahrt
- Graduate student: Scott Laverty

---

**Document Version:** 1.0  
**Last Updated:** February 10, 2026  
**Corresponds to Code Branch:** scott/branch-jan25
