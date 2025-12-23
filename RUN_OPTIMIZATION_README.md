# AutoZahrt Bayesian Optimization Demo

This guide explains how to run the Ax Bayesian Optimization demo for automated chemical synthesis and optimization using the AutoZahrt platform.

## Overview

The `run_ax_optimization_demo.py` script performs multi-objective Bayesian optimization to maximize:
1. **Percent Yield** - Chemical reaction yield
2. **Throughput** - Production rate (nmol/min)

The system automatically controls pumps, temperature, and monitors reactions in real-time using UV-Vis spectroscopy.

## Prerequisites

### Software Requirements

1. **Python 3.8+** with the following packages:
   ```bash
   pip install ax-platform pandas numpy matplotlib seaborn
   ```

2. **AutoZahrt v3** package (located in `Auto_Zahrt_v3/`)

3. **Project dependencies** already installed in this workspace

### Hardware Requirements

The following instruments must be connected and powered on:

- **VICI M6 Pump 1** (COM21) - Buffer/HCl pump
- **VICI M6 Pump 2** (COM22) - Cosolvent pump
- **Valve6Way** (COM7) - 6-way valve for cosolvent selection
- **TC-720 Temperature Controller** (COM12) - Reactor temperature control
- **PhD Ultra Pump** (COM19) - Harvard apparatus syringe pump for reactant
- **Isametic Pump** (COM14) - Dilution pump
- **Ocean Optics UV-Vis Spectrometer** - USB connected

### Calibration Files Required

Place these files in `ax_optimization_demo_results/` directory before running:

- `blank_spectrum.csv` - Blank reference spectrum for UV-Vis
- `dark_spectrum.csv` - Dark reference spectrum for UV-Vis

## Configuration

### 1. Experiment Configuration File

Edit `test_config_ax_demo.json` to set:
- Stock solution concentrations
- Initial volumes for each reagent
- Target wavelengths for UV-Vis monitoring
- Reactor bed volume
- Reserve volumes for each solution

Example:
```json
{
  "stock_concentration_uM": 263.9,
  "reactant_wavelength": 409.0,
  "product_wavelength": 506.0,
  "volume_stock_solution1": 20000,
  "volume_stock_solution2": 200000,
  ...
}
```

### 2. Optimization Parameters

In `run_ax_optimization_demo.py`, you can modify:

```python
trials = 10                          # Number of optimization iterations
percent_yield_threshold = 50.0       # Minimum acceptable yield (%)
throughput_threshold = 5.0           # Minimum throughput (nmol/min)
simulation_mode = False              # True = simulation, False = hardware
```

### 3. COM Port Configuration

Verify COM ports in `experimental_commands/generate_instrument_config.py`:

```python
["VICI_M6_Pump", 1, "Pump", "COM21", ""],
["VICI_M6_Pump", 2, "Pump", "COM22", ""],
["Valve6Way", 1, "VICI-6Way", "COM7", ""],
["Temperature", 1, "Temperature", "COM12", ""],
["PhdUltraPump", 1, "PhDUltraPump", "COM19", ""],
["Isametic", 1, "Isametic", "COM14", ""],
```

## Running the Optimization

### Quick Start

```bash
python run_ax_optimization_demo.py
```

### Step-by-Step Process

1. **Prepare the system:**
   - Ensure all reagent bottles are filled above reserve levels
   - Check all pumps and valves are connected
   - Verify temperature controller is responding
   - Connect UV-Vis spectrometer

2. **Create output directory:**
   ```bash
   mkdir ax_optimization_demo_results
   ```

3. **Copy calibration files:**
   ```bash
   # Place your blank and dark spectra in the output directory
   copy path\to\blank_spectrum.csv ax_optimization_demo_results\
   copy path\to\dark_spectrum.csv ax_optimization_demo_results\
   ```

4. **Run the optimization:**
   ```bash
   python run_ax_optimization_demo.py
   ```

### What Happens During Execution

For each trial (iteration), the system will:

1. **Generate Parameters** - Ax suggests optimal flow rate, concentration, temperature, and cosolvent
2. **Check Volumes** - Verify sufficient reagents remain
3. **Set Temperature** - Heat/cool reactor to target temperature and wait for convergence
4. **Run Wash Cycle** - Clean the reactor and UV-Vis detector
5. **Start UV-Vis Recording** - Begin real-time absorbance monitoring
6. **Execute Experiment** - Flow reactants through the system at specified rates
7. **Analyze Results** - Calculate yield and throughput from UV-Vis data
8. **Save Data** - Record all experimental data and plots
9. **Update Model** - Ax learns from results to suggest better parameters
10. **Repeat** - Continue to next trial

## Output Files

All results are saved to `ax_optimization_demo_results/`:

### Data Files
- `BO_results_ax_demo.csv` - Complete optimization results table
- `ax_optimization_state.json` - Ax optimization state (for resuming)
- `Instrument_Config_File.csv` - Instrument configuration used

### Per-Iteration Files
For each iteration `N`:
- `Fluorescent_Optimization_Iteration_N_experiment.csv` - Pump commands
- `Fluorescent_Optimization_Iteration_N_temperature.csv` - Temperature commands
- `Fluorescent_Optimization_Iteration_N_wash.csv` - Wash commands
- `Fluorescent_Bayesian_Optimization_iteration_N.csv` - UV-Vis time series data

### Plots
- `UV_VIS_timecourse.png` / `.pdf` - UV-Vis absorbance over time
- `bo_optimization_summary.png` - Optimization progress summary (if generated)

## Monitoring Progress

### Terminal Output

The script provides detailed progress updates:

```
[Step 1/10] Trial 0 -> percent_yield=65.23, throughput=8.45 at params={...}
[Step 2/10] Trial 1 -> percent_yield=72.18, throughput=9.12 at params={...}
...
```

### Real-Time Monitoring

- **Temperature convergence** - Monitor in terminal output
- **Pump status** - Status monitoring every 60 seconds
- **UV-Vis measurements** - Recorded every 5 seconds (configurable)

### Volume Tracking

The system tracks remaining volumes and warns when approaching reserves:

```
Proceeding: withdrawing 1943.00 µL from 'Reactant'. Remaining 18057.00 µL (reserve ≥ 2000.00 µL).
```

## Simulation Mode vs Hardware Mode

### Simulation Mode (`simulation_mode = True`)
- Runs 30x faster than real-time
- No hardware required
- Uses synthetic data based on mathematical model
- Useful for testing optimization strategy

### Hardware Mode (`simulation_mode = False`)
- Runs actual experiments with real hardware
- Real-time temperature control and pump operations
- Actual UV-Vis measurements
- Full experimental data collection

## Troubleshooting

### Common Issues

**1. ImportError: Could not import GeneralExperimentMethod**
- Solution: Ensure `Auto_Zahrt_v3` package is in the correct location
- Check: `from Auto_Zahrt_v3.methods.methods import GeneralExperimentMethod`

**2. COM Port Connection Failed**
- Solution: Check Device Manager for correct COM port assignments
- Update ports in `generate_instrument_config.py`
- Ensure instruments are powered on

**3. UV-Vis Spectrometer Not Found**
- Solution: Verify USB connection
- Install Ocean Optics drivers if needed
- Check if another program is using the spectrometer

**4. Volume Reserve Warning**
- Solution: Refill reagent bottles
- Adjust reserve volumes in config file if needed

**5. Temperature Not Converging**
- Solution: Check TC-720 connections
- Verify heating/cooling elements are functional
- Increase convergence tolerance if needed

**6. Blank/Dark Spectrum Not Found**
- Solution: Copy calibration files to output directory
- Run UV-Vis calibration to generate new spectra
- System will continue without correction (not recommended)

### Error Recovery

If the script crashes mid-optimization:
1. Check the last saved trial in `ax_optimization_state.json`
2. Resume by reloading the state (modify script to load existing state)
3. Or start fresh by deleting the state file

## Testing Individual Components

Before running the full optimization, test individual components:

```bash
# Test temperature control
python test_temperature_control.py 40

# Test wash system
python test_wash_commands.py

# Test experimental commands
python test_experimental_commands.py

# Test UV-Vis detector
python test_uv_vis_detector.py 60
```

## Advanced Configuration

### Modifying Search Space

Edit the search space in `bayesian_optimizer/ax_runner.py`:

```python
parameters=[
    {"name": "flow_rate", "type": "range", "bounds": [43.0, 200.0]},
    {"name": "dilution_factor", "type": "range", "bounds": [0.3, 0.8]},
    {"name": "temperature", "type": "range", "bounds": [20.0, 60.0]},
    {"name": "co_solvent", "type": "choice", "values": [1, 2, 3, 4, 5, 6]},
    {"name": "co_solvent_volume", "type": "range", "bounds": [0.0, 0.2]},
]
```

### Changing Number of Trials

In `run_ax_optimization_demo.py`:
```python
trials = 20  # Increase for longer optimization
```

### Adjusting Thresholds

```python
percent_yield_threshold = 60.0   # Higher yield requirement
throughput_threshold = 10.0      # Higher throughput requirement
```

## Data Analysis

After completion, analyze results using Python:

```python
import pandas as pd

# Load results
df = pd.read_csv('ax_optimization_demo_results/BO_results_ax_demo.csv')

# Find best trial
best_yield = df.loc[df['percent_yield'].idxmax()]
best_throughput = df.loc[df['throughput'].idxmax()]

print(f"Best yield: {best_yield['percent_yield']:.2f}% at trial {best_yield['iteration']}")
print(f"Best throughput: {best_throughput['throughput']:.2f} nmol/min at trial {best_throughput['iteration']}")
```

## Safety Notes

- **Always monitor the first few trials** to ensure proper operation
- **Check for leaks** in the flow system regularly
- **Ensure proper ventilation** if using volatile solvents
- **Emergency stop**: Press Ctrl+C or use the control file mechanism
- **Volume reserves** are set to prevent running dry - do not override without careful consideration

## Support

For issues or questions:
1. Check this README and troubleshooting section
2. Review individual test scripts for component-level debugging
3. Check AutoZahrt v3 documentation in `Auto_Zahrt_v3/README.md`
4. Review error messages and stack traces carefully

## Quick Reference

| Command | Purpose |
|---------|---------|
| `python run_ax_optimization_demo.py` | Run full optimization |
| `python test_temperature_control.py 40` | Test temperature to 40°C |
| `python test_wash_commands.py` | Test wash cycle |
| `python test_experimental_commands.py` | Test pump sequence |
| `python test_uv_vis_detector.py 60` | Test UV-Vis for 60s |

## License

Copyright (C) 2025 by Professor Andrew Zahrt. All rights reserved.
