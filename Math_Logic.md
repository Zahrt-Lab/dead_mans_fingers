
# Project Dead Man's Fingers

**Automated flow-chemistry optimization platform**

Project Dead Man's Fingers is an automated flow-chemistry optimization platform. It uses multi-objective Bayesian optimization (Ax/BoTorch, qNEHVI acquisition function) to simultaneously maximize percent yield and product throughput for photochemical reactions run on custom laboratory hardware.

---

## Directory Structure

```text
project_dead_mans_fingers/
├── main.py                          # Entry point (argparse → generate_bo_input → run_bo_campaign)
├── test_config_ax_demo.json         # Example master config
├── bayesian_optimizer/              # Ax/BoTorch integration, state classes, campaign loop
│   ├── experiment_state.py          # BoCampaignState & IterationState dataclasses
│   ├── run_bo_campaign.py           # Main optimization loop (30 iterations)
│   ├── ax_suggested_experiment.py   # Bridges Ax trial → iteration executor
│   └── init_or_load_ax.py           # Ax client init / resume from JSON
├── preprocessing/                   # Parameter validation & unit conversion
│   ├── generate_bo_input.py         # Master JSON → per-analog JSON
│   ├── parameters_to_commands.py    # 6 BO params → pump flow rates (F1–F4)
│   ├── constrain_to_search_space.py # Clip params to bounds
│   └── standardize_input.py         # Round to 2 decimal places
├── experimental_commands/           # Hardware control & CSV command generation
│   ├── execute_bo_iteration_commands.py  # Full iteration orchestrator (10 steps)
│   ├── commands.py                  # Serial port CSV execution
│   └── experiment_runner.py         # Hardware vs. simulation dispatch
├── post_processing/                 # UV-Vis analysis → yield & throughput
│   ├── post_processing_results.py   # Master pipeline
│   ├── post_process_uv_recording.py # Extract steady-state region from UV CSV
│   ├── average_absorbance.py
│   ├── calculate_concentration_in_reactor_bed.py  # Beer-Lambert
│   ├── calculate_percent_yield.py
│   ├── calculate_product_throughput.py
│   └── append_bayesian_experimental_results.py
├── utils/                           # Simulation & visualization
│   ├── run_simulation.py            # Simulated experiment executor
│   └── simulated_data.py            # Synthetic UV-Vis kinetic data generator
├── production_run/                  # Post-optimization scale-up (scaffolded, not integrated)
└── test/                            # pytest suite
    ├── test_preprocessing/          # Most complete coverage
    ├── test_post_processing/
    ├── test_experimental_commands/
    ├── test_bayesian_optimizer/
    └── test_utils/
```

---

## Key Data Flow

```text
main.py
  → generate_bo_input_file()          master JSON → analog-specific JSON
  → run_bo_campaign()
      initialize BoCampaignState + AxClient
      LOOP (30 trials):
        ax.get_next_trial() → trial_conditions (6D)
        run_bayesian_optimization_iteration()
          1. constrain_to_search_space()  (clip)
          2. standardize_input()          (round to 2dp)
          3. Check results_cache          (skip duplicates)
          4. parameters_to_commands()     (F1–F4 pump flows)
          5. save CSVs (instrument config, temp, light, experiment, wash)
          6. run_experiment()             (hardware or simulation)
          7. analyze_experiment_results() (Beer-Lambert → yield & throughput)
          8. append_bayesian_experimental_results()
          9. update results_cache
          return (percent_yield, throughput_nmol_min)
        ax.complete_trial()
        ax.save_to_json_file()           (resumable checkpoint)
```

---

## Core State Classes

**Located in `bayesian_optimizer/experiment_state.py`**

- `BoCampaignState`: campaign config, simulation flag, results cache, CSV path
- `IterationState`: trial index, 6 BO parameters, derived pump parameters, absorbances, reactor concentration

---

## 6 Optimization Parameters

| Parameter                  | Range (example) | Unit            |
|----------------------------|-----------------|-----------------|
| flow_rate                  | 40–200          | µL/min          |
| dilution_factor            | 0.05–0.5        | (dimensionless) |
| temperature                | 20–60           | °C              |
| co_solvent_valve_position  | 1–3             | (valve index)   |
| co_solvent_dilution_factor | 0.0–0.4         | (dimensionless) |
| light_intensity            | 0–100           | %               |

---

## Notable Design Decisions

1. No globals — all state passed through dataclasses
2. Results cache — memoization keyed by standardized parameter tuple (avoids re-running duplicates)
3. Deterministic pump math — 4 pump flows derived analytically from BO params via mass-balance dilution
4. Simulation mode — generates synthetic UV-Vis kinetic CSVs for hardware-free testing
5. Resumable campaigns — Ax state serialized to JSON after every trial
6. Per-analog organization — master JSON indexed; separate BO campaign per analog

 ---
 No Code Changes Planned


## High Priority TODOs

**Code Quality & Safety:**
- [ ] Validate it works in experimental setting and make minimal changes to make sure it works.
- [ ] Add a production run to the code.

---

TODO: Need to figure out how to clean it up variable names to make sure it clearer to the reader 
## Module Descriptions

- **6-Way Valve 1 (Analog Selection)**  
  Selects which xylopyridine analog is routed to the system for optimization.
  The valve position (**$V_1$**) selects analog to use before the optimization begins.

- **Pump 1 (Substrate Feed)**  
  Delivers the selected xylopyridine analog dissolved in 0.1 M HCl(aq).  
  The flow rate (**$F_1$**) is a tunable optimization parameter.

- **Pump 2 (Dilution Feed)**  
  Adds 0.1 M HCl(aq) for dilution.  
  The flow rate (**$F_2$**) is a tunable optimization parameter.

- **6-Way Valve 2 + Pump 3 (Co-solvent Selection)**  
  The optimizer selects the co-solvent via valve position and controls its flow rate using Pump 3.  
  The valve position (**$V_2$**) flow rate (**$F_3$**) is a tunable optimization parameter.

- **Temperature Control (Peltier Module)**  
  Regulates the reactor temperature.  
  The setpoint temperature (**$T$**, °C) is a tunable optimization parameter.

- **Light Source (Photoreactor)**  
  Mirror-box photoreactor providing 365 nm irradiation with a tunable power output (0–400 W).  
  The Light intensity (**$I$**) is a tunable optimization parameter.

- **2-Way Valve 1 (Analysis Routing)**  
  Directs the reactor effluent either to the UV–Vis detector during optimization or to an alternative outlet when analysis is not required.
  The valve position (**$V_3$**) is selected before the optimization begins

- **Pump 4 (UV Conditioning)**  
  Performs post-reactor dilution to achieve a target absorbance range prior to UV–Vis analysis, maintaining a standardized concentration before detection.
  The flow rate (**$F_4$**) is a tunable optimization parameter.


- **UV–Vis Detector and Analysis**  
  Measures absorbance of reactants and products and converts spectra to concentrations.  
  These values are used to calculate ** percent yield** and **throughput**.

- **10-Way Valve 1 (Waste Selection)**  
  Routes the reactor output to the appropriate waste stream based on the selected xylopyridine analog.
  The valve position (**$V_4$**) is selected before the optimization begins

- **Bayesian Optimizer**  
  Aggregates all prior experimental results and proposes the next set of experimental conditions.
 

## Variables, notation, and assumptions
Flow rates (use consistent units)


Flow rates (use consistent units)

- **$F_1$**: Pump 1 flow rate (substrate feed), e.g., µL/min 

- **$F_2$**: Pump 2 flow rate (acid dilution), e.g., µL/min 

- **$F_3$**: Pump 3 flow rate (co-solvent dilution), e.g., µL/min

- **$F_4$**: Pump 4 flow rate (post-reactor dilution before UV-Vis), e.g., µL/min

- **$F_{123}$**: Total flow through the reactor (sum of Pumps 1–3): $F_{123} = F_1 + F_2 + F_3$

- **$F_{1234}$**: Total flow through the UV-detector (sum of Pumps 1–4): $F_{1234} = F_1 + F_2 + F_3 + F_4$


Concentrations

- **$C_{S}$**: xylopyridine concentration in Pump 1 feed (nmol/L)

- **$C_{S,\text{A=1.0}}$**: substrate concentration entering the reactor bed(nmol/L), assuming no reaction occurred

- **$C_{S,\text{in}}$**: substrate concentration entering the reactor bed(nmol/L)

- **$C_{S,\text{out}}$**: substrate concentration exiting the reactor bed(nmol/L)

- **$C_{P,\text{out}}$**: product concentration exiting the reactor bed(nmol/L)

- **$C_{S,UV}$**: substrate concentration in the UV cell after Pump 4 (nmol/L)

- **$C_{P,UV}$**: product concentration in the UV cell after Pump 4 (nmol/L)

Temperature

- **$T$**: Reactor temperature (°C)

Light Intensity

- **$I$**: Light intensity (W or % of maximum)

Dilution Factor

- 


## Step-by-step: one optimization iteration (with math)
### Step 0 — Prepare and prime (one-time per run)

- Prepare and fill reservoirs (xylopyridine analogs, 0.1 M HCl water, co-solvents).

- Prime lines and remove bubbles (especially the UV flow cell).

- Set safe defaults (Peltier setpoint, light off/standby).

- Set the **$V_3$** position to send results to the uv-detector.

### Step 1 - The xylopyridine analog

The xylopyridine analog is selected for bayesian optimization on the platform.

### Step 2 — Optimizer proposes an experiment

For iteration k, the optimizer proposes a condition vector **$x_k$**, typically including:

- **$dilution factor$**

- **$F_{123}$**

- **$T$**

- **$I$**

- **$V_2$**

- **$cosolvent dilution factor$**

TODO : Need a better variable name for the cosolvent dilution factor.

**Note:** The optimizer will tune these parameters and remaining parameters are set deterministically.

### Step 4 — Set temperature of the reactor bed

- The reactor bed is set to the temperature suggested by the optimizer.

- The sensors wait for the temperature to be within +/- 1C  for 60 seconds.

### Step 5 - Wash step

Wash the detector, to remove any xylopyridine analogs before calibration.

- **$F_1$** is set to 0 uL/min.

- **$F_2$** is set to **$2000 uL/min \cdot (1 - D_{\text{cosolvent}})$**.

- **$F_3$** is set to **$2000 uL/min \cdot D_{\text{cosolvent}}$**.

- **$F_{123}$** is set to 2000 uL/min.

- **$F_4$** is set to 1000 uL/min.

- **$F_{1234}$** is set to 3000 uL/min.

### Step 6 - Run calibration

- Calibration step will be performed before each iteration to improve accuracy before each iteration.

### Step 7 - Set light insenity

- The light intensity of the lamp is set **$I$**.

### Step 8 — Compute Substrate Concentration Entering the Reactor

The optimizer specifies the total reactor flow rate and dilution fractions. Individual pump
flow rates are then calculated deterministically to achieve the desired substrate concentration
in the reactor bed.

- The optimizer defines:
  - Total reactor flow rate: **$F_{123}$**
  - Substrate dilution fraction: **$D_{\text{substrate}}$**
  - Co-solvent dilution fraction: **$D_{\text{cosolvent}}$**

### Step 9 — Compute substrate concentration entering the reactor (dilution math)

- The optimizer sets:
  - Total reactor flow rate: **$F_{123}$**
  - Aqueous dilution factor: **$D_{\text{substrate}}$**
  - Co-solvent fraction (or dilution factor): **$D_{\text{cosolvent}}$**

- From these suggested values, the flow rate of the four pumps are calculated deterministically

- Substrate concentration entering the reactor is:
  - **$C_{S,\text{in}} = C_S \cdot D_{\text{substrate}}$**

- Flow rate of pump 1 are computed deterministically (mass balance; **$C_1V_1 = C_2V_2$** in flow form):

  - **Pump 1 (substrate feed):**
    - **$F_1 = \dfrac{C_{S,\text{in}} \cdot F_{123}}{C_S} = F_{123} \cdot D_{\text{substrate}}$**

- Flow rate of pump 2 and 3 are computed using the dilution factor variables and the flow rate of pump 1.

  - **Pump 2 (aqueous diluent):**
    - **$F_2 = F_{123} \cdot (1 - D_{\text{substrate}} - D_{\text{cosolvent}})$**

  - **Pump 3 (co-solvent):**
    - **$F_3 = F_{123} \cdot D_{\text{cosolvent}}$**

- Flow rate of pump 4 is calculated deterministically (mass balance; **$C_1V_1 = C_2V_2$** in flow form)

  - **$F_4 = \dfrac{C_{S,\text{in}} \cdot F_{123}}{C_{S,\text{A=1.0}}} - F_{123}$**
  
  - Where **$C_{S,\text{A=1.0}}$** is the substrate concentration when absorbance = 1.0 at the UV detector.
  
  - If **$C_{S,\text{in}} \leq C_{S,\text{A=1.0}}$**, then **$F_4 = 0$** (no additional dilution needed).

- Volume calculations follow the same proportional relationships:

  - **$V_1 = V_{\text{total}} \cdot D_{\text{substrate}}$**
  
  - **$V_2 = V_{\text{total}} \cdot (1 - D_{\text{substrate}} - D_{\text{cosolvent}})$**
  
  - **$V_3 = V_{\text{total}} \cdot D_{\text{cosolvent}}$**
  
  - **$V_4 = \left(\dfrac{C_{S,\text{in}}}{C_{S,\text{A=1.0}}} - 1\right) \cdot (V_1 + V_2 + V_3)$** if dilution is needed, else **$V_4 = 0$**.

### Step 10 — Calculate substrate and product concentrations in the UV cell

- Beer–Lambert law is used to calculate substrate and product concentrations after the reactor effluent enters the UV cell.

- Beer–Lambert law:
  - **$A_\lambda = \varepsilon \cdot l \cdot C$**

- Substrate concentration in the UV cell (measured at 409 nm):
  - **$C_{S,UV} = \dfrac{A_{409}}{\varepsilon_S \cdot l}$**

- Product concentration in the UV cell:
  - **$C_{P,UV} = \dfrac{A_{\lambda,P}}{\varepsilon_P \cdot l}$**

### Step 11 — Calculate substrate and product concentrations exiting the reactor (pre–Pump 4)

- The substrate and product concentrations exiting the reactor bed,
  **$C_{S,\text{out}}$** and **$C_{P,\text{out}}$**, are calculated deterministically using
  a mass balance (**$C_1 V_1 = C_2 V_2$** in flow form).

- Substrate concentration exiting the reactor:
  - **$C_{S,\text{out}} = \dfrac{C_{S,UV} \cdot F_{1234}}{F_{123}}$**

- Product concentration exiting the reactor:
  - **$C_{P,\text{out}} = \dfrac{C_{P,UV} \cdot F_{1234}}{F_{123}}$**

### Step 12 - Calculate Percent yield and throughput

- Percent yield and throughput are calculated from the concentrations exiting the reactor
bed prior to Pump 4 dilution.

- **Percent Yield (%)**

  Percent yield is defined as the fraction of substrate converted to product:

  **$Percent Yield = \dfrac{C_{P,\text{out}}}{C_{S,\text{in}}} \cdot 100%$**

- **Throughput**

  Throughput is defined as the molar production rate of product exiting the reactor:

  **$Throughput = C_{P,out} \cdot F_{123}$**

  Note: This code calculates throughput in nmol/min

### Step 13 — Feed results back into the Bayesian optimizer (domain + objectives)

**Search domain (inputs):**  
The optimizer proposes a new parameter set within the defined set of bounds
**$x_k = (F_{123}, D_{\mathrm{substrate}}, T, V_{\mathrm{cosolvent}}, D_{\mathrm{cosolvent}}, I)$**  

- **$x_1 = F_{123}$**: total reactor flow rate (`flow_rate`)
- **$x_2 = D_{\mathrm{substrate}}$**: aqueous dilution factor (`dilution_factor`)
- **$x_3 = T$**: reactor temperature (`temperature`)
- **$x_4 = V_{\mathrm{cosolvent}}$**: co-solvent valve position (`co_solvent`)
- **$x_5 = D_{\mathrm{cosolvent}}$**: co-solvent volume / fraction (`co_solvent_volume`)
- **$x_6 = I$**: light intensity (`light_intensity`)

**Measured objectives (outputs):**  
Each experiment returns two metrics to maximize:
- **$y_1(x) =$ percent yield**
- **$y_2(x) =$ throughput**

TODO : Need to update the section below
**Update rule (conceptual):**  
Given a dataset of prior trials **$\mathcal{D} = \{(x_i, y_{1,i}, y_{2,i})\}_{i=1}^n$**, the optimizer updates its surrogate model and selects the next experiment:

- propose **$x_{n+1} = \arg\max_x \alpha(x \mid \mathcal{D})$**  
  where **$\alpha$** is an acquisition function balancing exploration vs exploitation.

Ax records each trial as: `params -> (percent_yield, throughput)` and uses all completed trials to propose the next parameter set.

### Step 14 - Bayesian Optimization Iterations

- Repeat steps 2-12 til the optimizer reaches it's termination criteria.

### Step 15 - Production run

- Once the optimization criteria is met a pareto front is generated balancing both between percent yield and throughput.

- The user can select which experimental conditions they wish to perform the product run and the user can select the amount of grams or nmols of compound.

- For this part the UV-detector will be off and no dilutions will be performed with pump4.

- The 2-Way Valve 1 will be routed away from the UV-detector 



