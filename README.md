# Project Dead Man’s Fingers  
## Automated Flow Platform for Bayesian Optimization (Xylopyridine Analogs)

This repository controls an automated flow-chemistry platform that optimizes photochemical reactions of xylopyridine analogs using Bayesian optimization. In each campaign, the platform:

1) Selects a set of xylopyridine analogs.

2) Initializes a Bayesian optimization routine over experimental conditions.

3) Executes experiments based on optimizer-proposed conditions.

4) Quantifies each experiment via UV–Vis spectroscopy, calculating yield and throughput.

5) Proposes the next experiment iteratively.

6) Terminates when predefined stopping criteria are met.

7) Optionally transitions the optimized conditions to a production run to generate a target quantity (grams or moles) of the selected analog.

---

## ⚙️ System Requirements

### Software Requirements

- **Python**: 3.9 or higher
- **Operating System**: Linux (tested on Ubuntu), macOS, Windows (simulation mode only)
- **Required Python Packages**:
  - `ax-platform` >= 0.3.0 (Bayesian optimization)
  - `pandas` >= 1.3.0 (data handling)
  - `numpy` >= 1.21.0 (numerical computing)
  - `matplotlib` >= 3.4.0 (plotting)
  - `seaborn` >= 0.11.0 (visualization)
  - `pyserial` (optional, for hardware control)

### Hardware Requirements (For Non-Simulation Mode)

The following instruments must be connected and powered on:

| Instrument | Connection | Purpose |
|------------|------------|---------|
| **VICI M6 Pump 1** | COM21 | Xylopyridine analog feed (0.1 M HCl) |
| **VICI M6 Pump 2** | COM22 | Dilution feed (0.1 M HCl) |
| **6-Way Valve (Co-solvent)** | COM7 | Co-solvent selection |
| **VICI M6 Pump 3** | Connected to Valve | Co-solvent feed |
| **TC-720 Temperature Controller** | COM12 | Reactor temperature control (Peltier) |
| **PhD Ultra Syringe Pump** | COM19 | Alternative pump (if used) |
| **Ismatec Pump** | COM14 | Post-reactor dilution |
| **Ocean Optics UV-Vis** | USB | Spectroscopic detection (409 nm, 506 nm) |
| **10-Way Valve (Waste)** | COM? | Waste stream routing |
| **Light Source** | Arduino/Serial | 365 nm UV lamp (0-400 W) |

**⚠️ Safety Note**: Always verify proper ventilation, chemical compatibility, and safety interlocks before running in hardware mode.

---

## 🎯 Optimization Parameters

The Bayesian optimizer explores a 6-dimensional search space:

| Parameter | Symbol | Range | Units | Description |
|-----------|--------|-------|-------|-------------|
| **Flow Rate** | $F_{123}$ | 40 - 200 | µL/min | Total flow through reactor |
| **Dilution Factor** | $D$ | 0.05 - 0.5 | — | Fraction of stock concentration |
| **Temperature** | $T$ | 20 - 60 | °C | Reactor temperature |
| **Co-solvent Valve** | $V_2$ | 1 - 6 | position | Co-solvent selection (1=EtOH, 2=MeCN, etc.) |
| **Co-solvent Fraction** | $D_{cosol}$ | 0.0 - 0.4 | — | Fraction of co-solvent in dilution |
| **Light Intensity** | $I$ | 0 - 100 | % | UV lamp power |

### Objectives (Maximized)

1. **Percent Yield**: Fraction of xylopyridine converted to product (0-100%)
2. **Throughput**: Product generation rate (nmol/min)

The optimizer uses **qNEHVI** (quasi-Expected Noisy Hypervolume Improvement) acquisition function to propose experiments that maximize expected improvement on the Pareto front.

---

## 🐛 Known Issues & Recent Fixes

See [CODE_REVIEW.md](CODE_REVIEW.md) for comprehensive analysis.

**Recently Fixed:**
- ✅ **SIMULATION_MODE propagation** - Global state now correctly propagates through function calls
- ✅ **Undefined EXPERIMENTAL_PARAMETERS** - Fixed incorrect variable references
- ✅ **Tuple/int comparison error** - Corrected type mismatches in parameter handling

**Current Known Issues:**
- [ ] TODO comments should be converted to GitHub Issues (47 found)
- [ ] Missing hardware safety interlocks (temperature, pressure, flow limits)
- [ ] Inadequate test coverage (< 10% estimated)
- [ ] Global state management creates testing challenges
- [ ] Inconsistent error handling patterns

See [High Priority TODOs](#high-priority-todos) below.

---

## High Priority TODOs

**Code Quality & Safety:**
- [ ] Connect Arduino-controlled light intensity and integrate with experiment orchestration
- [ ] Prevent overwriting prior run outputs (iteration-stamped directories + hard fails on collisions)
- [ ] Add a live optimization GUI: progress plots + snapshot export + optional full UV-Vis spectrum export (e.g., every N runs)
- [ ] Enable per-analog Bayesian optimization (hold analog constant; optimize within each analog)
- [ ] Provide a Linux-based production runner for stable BO execution
- [ ] Refactor to production-grade code after a stable workflow is validated

## Low Priority TODOs

- [ ] Add a pre-check valve path to UV-Vis to verify concentration prior to each reaction step
- [ ] Add a GUI for setting BO parameters (run count, bounds, objectives) to avoid terminal configuration
- [ ] Add a short “Getting Started” tutorial for new users (hardware map + run procedure)

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



