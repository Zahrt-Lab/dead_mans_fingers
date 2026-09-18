# Dead Man's Fingers
Dead Man's Fingers is the software repository associated with the manuscript describing an autonomous continuous-flow photochemistry platform for the optimization and production of photoconverted xylopyridine-derived diazaxanthilidene fluorophores.

The repository contains the code used to manage Bayesian optimization, experimental parameter handling, analytical post-processing, and manuscript data analysis for the reported optimization campaigns. Hardware orchestration and device-level control are handled through the external Auto_Zahrt framework.

The name *Dead Man's Fingers* refers to the fungal family from which xylopyridine was originally isolated.

---

## Overview

The platform was developed to optimize the photoconversion of xylopyridine-derived diazaxanthilidene fluorophores. The optimized conditions improved both yield and throughput relative to the previously used batch protocol, which required several days of irradiation..

The automated workflow integrates:

- continuous-flow photochemistry;
- automated reagent delivery;
- temperature and irradiation control;
- inline UV-Vis spectroscopy;
- automated steady-state detection;
- calculation of product yield and throughput;
- multi-objective Bayesian optimization;
- automated selection of subsequent experiments;
- post-campaign Pareto and hypervolume analysis.

The optimization workflow uses Ax-based Bayesian optimization to identify reaction conditions that balance two competing objectives:

- **percent yield**
- **product throughput**

The final optimization space reported in the manuscript contains four experimental variables:

- **flow rate**
- **substrate concentration / dilution factor**
- **reactor temperature**
- **light intensity**

Earlier development versions of the platform included additional variables, including co-solvent identity and composition. These variables were removed from the final experimental workflow reported in the manuscript.

---

## Software Architecture

Project Dead Man's Fingers is responsible for the optimization-level logic of the autonomous workflow, including:

1. generation and validation of experimental conditions;
2. communication with the Bayesian optimizer;
3. conversion of optimization parameters into experimental commands;
4. processing of inline UV-Vis data;
5. calculation of yield and throughput;
6. updating the Bayesian optimization campaign;
7. selection and execution of subsequent experiments;
8. post-campaign analysis.

Device-level automation and orchestration are performed by **Auto_Zahrt**, an external automation framework used to communicate with pumps, valves, temperature controllers, light sources, spectrometers, and other platform hardware.

At a high level, the experimental loop is:

```text
Bayesian optimizer
        ↓
Proposed reaction conditions
        ↓
Parameter validation and conversion
        ↓
Auto_Zahrt experimental execution
        ↓
Inline UV-Vis measurement
        ↓
Steady-state detection and data processing
        ↓
Yield and throughput calculation
        ↓
Results returned to Bayesian optimizer
        ↓
Next experiment
```

The optimization proceeds iteratively until the campaign stopping criterion is reached.

---

## Repository Structure

The main directories are:

```text
bayesian_optimizer/
```

Bayesian optimization campaign initialization, Ax integration, campaign state management, checkpointing, and optimization-loop logic.

```text
preprocessing/
```

Validation and transformation of proposed optimization parameters into experimentally usable values, including flow-rate calculations and volume tracking.

```text
experimental_commands/
```

Generation of command files and instrument configuration files used by the automated experimental platform.

```text
post_processing/
```

Processing of inline UV-Vis data, steady-state extraction, Beer-Lambert-based quantification, and calculation of yield and throughput.

```text
analysis/
```

Post-campaign analysis and visualization used to generate manuscript figures, including:

- Pareto-front plots;
- hypervolume analysis;
- parallel-coordinate plots;
- cross-campaign comparisons.

```text
calibration/
```

Calibration workflows and parameters used for quantitative UV-Vis analysis.

```text
data/
```

Experimental optimization and calibration datasets associated with the manuscript.

```text
test/
```

Software tests for the final workflow. Hardware-dependent tests are separated from software-only tests.

---

## Bayesian Optimization

The optimization workflow uses the Ax platform for multi-objective Bayesian optimization.

Experimental conditions are evaluated using two objectives:

### Yield

Product yield is determined from inline UV-Vis measurements following automated steady-state detection and analytical calibration.

### Throughput

Throughput is calculated from reaction yield, substrate concentration, and flow rate and is reported in units of product amount per unit time.

Because increasing yield and increasing throughput can favor different reaction conditions, the optimization does not identify a single universally optimal condition. Instead, the campaign identifies a **Pareto front** containing reaction conditions representing different trade-offs between the two objectives.

Hypervolume is used to monitor improvement of the multi-objective optimization campaign.

---

## Experimental Platform

The software was developed for an automated continuous-flow photochemistry platform containing:

- automated reagent-delivery pumps;
- selector valves;
- a continuous-flow photoreactor;
- temperature control;
- variable LED irradiation intensity;
- inline UV-Vis spectroscopy;
- automated steady-state detection;
- post-reactor dilution;
- automated data acquisition and processing.

Detailed hardware descriptions, reactor dimensions, calibration procedures, and experimental operating procedures are provided in the manuscript and Supporting Information.

The experimental code is specific to the laboratory platform used in this work and requires the corresponding hardware and Auto_Zahrt device drivers for direct hardware execution.

---

## Inline UV-Vis Analysis

Reaction output is monitored using inline UV-Vis spectroscopy.

The post-processing workflow includes:

1. collection of absorbance spectra during continuous flow;
2. detection of the transition from the previous experiment;
3. automated identification of steady-state behavior;
4. extraction of steady-state absorbance;
5. conversion of absorbance to product concentration using calibration parameters;
6. calculation of percent yield;
7. calculation of product throughput.

The resulting yield and throughput values are returned to the optimization workflow.

---
## Detailed Explanation of Workflow

### Vriables, Notation, and Assumptions

### Flow rates

- **$F_R$**: total flow through the reactor, selected by the optimizer (`flow_rate`), in µL/min.
- **$F_1$**: Pump 1 substrate-stock flow rate, in µL/min.
- **$F_2$**: Pump 2 aqueous-diluent flow rate, in µL/min.
- **$F_4$**: post-reactor dilution flow rate before the UV–Vis detector, in µL/min.
- **$F_{UV}$**: total flow through the UV–Vis detector, in µL/min.

**$F_R = F_1 + F_2$**

**$F_{UV} = F_R + F_4$**

### Volumes

- **$V_R$**: configured total volume passed through the reactor, in µL.
- **$V_1$**: volume delivered by Pump 1, in µL.
- **$V_2$**: volume delivered by Pump 2, in µL.
- **$V_4$**: post-reactor dilution volume delivered before detection, in µL.
- **$V_{UV}$**: total volume reaching the detector, **$V_{UV}=V_R+V_4$**.

### Concentrations

- **$C_{stock}$**: selected xylopyridine stock concentration, in µM.
- **$C_{S,in}$**: initial substrate concentration in the reactor bed, in µM or mol/L as indicated.
- **$C_{target}$**: configured target concentration at the UV–Vis detector, in µM.
- **$C_{P,UV}$**: product concentration measured in the UV cell, in mol/µL.
- **$C_{P,R}$**: product concentration at the reactor outlet before detector dilution, in mol/µL.

### Other variables

- **$D$**: substrate dilution factor (`dilution_factor`), dimensionless.
- **$T$**: reactor temperature, in °C.
- **$I$**: requested light intensity, from 0 to 100%.
- **$J$**: instrument dimmer command, from 0 to 255, with 0 representing the brightest setting.
- **$A_P$**: mean product absorbance in the selected analysis window.
- **$A_{target}$**: configured target absorbance at the detector.
- **$C_{max}$**: detector concentration corresponding to absorbance 1.0, in µM.
- **$\varepsilon_P$**: product extinction coefficient at the product wavelength, in L mol⁻¹ cm⁻¹.
- **$l$**: UV–Vis path length, in cm.
- **$V_{target}$**: target reactor volume used to define the normal post-processing cutoff, in µL.

Assumptions encoded in the calculations:

1. Pumped liquids are incompressible and additive over the relevant flow range.
2. Pump 1 and Pump 2 together establish the selected reactor flow rate.
3. Post-reactor dilution changes detector concentration but not reaction yield or molar production rate leaving the reactor.
4. Product absorbance follows the Beer–Lambert relationship at the configured product wavelength.
5. Negative concentrations caused by measurement noise are clamped to zero, and calculated percent yield is restricted to 0–100%.

---

## Step-by-Step: One Optimization Iteration (with Math)

### Step 0 — Prepare and prime the platform

- Prepare the selected xylopyridine stock solution and 0.1 M HCl(aq) diluent.
- Fill reservoirs and confirm sufficient reagent and waste capacity.
- Prime the substrate line and remove bubbles from the flow path and UV cell.
- Set safe initial temperature and illumination conditions.
- Route reactor effluent through the UV–Vis analysis path.

### Step 1 — Select the xylopyridine analog

The master configuration contains analog-specific concentrations, wavelengths, extinction coefficients, and analytical settings. `generate_bo_input_file()` selects the entries for one analog and writes an analog-specific campaign configuration.

The analog index also determines which stock-solution position is tracked during the campaign.

### Step 2 — Propose an experiment

For trial **$k$**, Ax proposes the four-dimensional condition vector:

**$x_k = (F_R, D, T, I)$**

where **$F_R$** is total reactor flow, **$D$** is substrate dilution, **$T$** is reactor temperature, and **$I$** is requested light intensity. Ax proposes each value within the campaign bounds.

### Step 3 — Constrain, standardize, and check the cache

The proposed values are constrained to the configured bounds and standardized before execution. The standardized trial conditions form a cache key. If an identical condition has already been evaluated, its stored yield and throughput are returned without repeating the experiment.

### Step 4 — Calculate reactor-feed concentration

The initial substrate concentration in the reactor is:

**$C_{S,in,\mu M} = C_{stock,\mu M}D$**

For the yield calculation, it is converted from µM to mol/L:

**$C_{S,in,mol/L} = \dfrac{C_{S,in,\mu M}}{10^6}$**

### Step 5 — Calculate reactor pump settings

Pump 1 supplies fraction **$D$** of the total reactor stream:

**$F_1 = F_RD$**

Pump 2 supplies the remaining fraction:

**$F_2 = F_R(1-D)$**

Therefore:

**$F_1 + F_2 = F_R$**

The volumes follow the same relationships:

**$V_1 = V_RD$**

**$V_2 = V_R(1-D)$**

**$V_1 + V_2 = V_R$**

The implementation warns when a nonzero pump flow is at or below 25 µL/min because pump accuracy and precision may be reduced.

### Step 6 — Calculate post-reactor detector dilution

The target detector concentration is:

**$C_{target} = C_{max}A_{target}$**

Define the required dilution ratio:

**$R = \dfrac{C_{S,in}}{C_{target}}$**

If **$C_{S,in} \leq C_{target}$**, no post-reactor dilution is required:

**$F_4 = 0$** and **$V_4 = 0$**

If **$C_{S,in} > C_{target}$**:

**$F_{UV} = F_RR$**

**$F_4 = F_R(R-1)$**

**$V_4 = V_R(R-1)$**

This dilution occurs after the reactor and does not alter the reactor conditions.

### Step 7 — Convert the light-intensity request

The mirror-box controller uses an inverse integer dimmer scale. The implemented conversion is:

**$J = \operatorname{round}\left(\dfrac{100-I}{100}\times255\right)$**

Thus **$I=100\% \Rightarrow J=0$** is the brightest setting, while **$I=0\% \Rightarrow J=255$** is the dimmest setting.

### Step 8 — Generate and execute instrument commands

The software writes command CSV files for temperature control, washing, light-intensity control, and the flow experiment with UV–Vis acquisition.

The experiment sequence initializes the detector; configures reactant, product, and reference wavelengths; records blank and dark spectra; starts continuous acquisition; dispenses the calculated volumes; waits for the pumps; stops acquisition; and closes the light-source shutter.

In simulation mode, hardware execution is replaced by generation of a synthetic UV–Vis time-series CSV.

### Step 9 — Determine the UV–Vis analysis window

For a normal-duration experiment, the time required to pass the target volume is:

**$t_{target} = \dfrac{V_{target}}{F_R}\times60$**

where time is in seconds when volume is in µL and flow is in µL/min. Data at or after **$t_{target}$** are retained.

The convergence time supplied to the detector is:

**$t_{conv} = \max\left(120,\ 0.10\,t_{target}\right)$**

If the recording ends more than the configured tolerance before its expected duration, it is treated as having converged early and the final 120 seconds are used.

### Step 10 — Average product absorbance

The retained observations are averaged at the product wavelength:

**$A_P = \dfrac{1}{n}\sum_{i=1}^{n}A_{P,i}$**

The analysis rejects a wavelength column if any retained value lies outside −0.3 to 1.3. The absorbance used for concentration is clamped to a minimum of zero:

**$A_P^+ = \max(0,A_P)$**

### Step 11 — Calculate product concentration in the UV cell

Beer–Lambert law is:

**$A_P^+ = \varepsilon_PlC_{P,UV}$**

The implementation converts the extinction coefficient from L mol⁻¹ cm⁻¹ to µL mol⁻¹ cm⁻¹. Therefore:

**$C_{P,UV} = \dfrac{A_P^+}{10^6\varepsilon_Pl}$**

and **$C_{P,UV}$** is expressed in mol/µL.

### Step 12 — Recover reactor-outlet product concentration

The detector observes product after Pump 4 dilution. The reactor-outlet concentration is recovered by reversing that dilution:

**$C_{P,R} = C_{P,UV}\dfrac{V_R+V_4}{V_R}$**

Equivalently for the generated flow conditions:

**$C_{P,R} = C_{P,UV}\dfrac{F_R+F_4}{F_R}$**

When **$V_4=0$**, **$C_{P,R}=C_{P,UV}$**.

### Step 13 — Calculate percent yield and throughput

Convert product concentration from mol/µL to mol/L:

**$C_{P,R,mol/L} = 10^6C_{P,R,mol/\mu L}$**

Percent yield is:

**$Y = \dfrac{C_{P,R,mol/L}}{C_{S,in,mol/L}}\times100\%$**

The reported value is restricted to 0–100%:

**$Y_{reported}=\min(100,\max(0,Y))$**

Product throughput is:

**$Q_{mol/min}=C_{P,R,mol/\mu L}F_R$**

or, in the reported units:

**$Q_{nmol/min}=10^9C_{P,R,mol/\mu L}F_R$**

Negative throughput is clamped to zero.

### Step 14 — Return objectives to the optimizer

Each completed experiment returns two objectives to maximize:

- **$y_1(x)=Y_{reported}$**, percent yield;
- **$y_2(x)=Q_{nmol/min}$**, product throughput.

Ax receives each objective as a measured mean and configured standard error. Given the completed dataset

**$\mathcal{D}_n=\{(x_i,y_{1,i},y_{2,i})\}_{i=1}^{n}$**,

the optimizer updates its surrogate model and selects another condition:

**$x_{n+1}=\arg\max_x\alpha(x\mid\mathcal{D}_n)$**

where **$\alpha$** is the multi-objective acquisition function used by the Ax/BoTorch generation strategy. Ax state is saved after every completed trial, and campaign hypervolume is recorded when available.

---

## Optimization Objectives and Pareto Analysis

The two objectives generally compete:

- slower flow or longer residence time may favor percent yield;
- faster flow may favor throughput even when conversion is lower.

A condition **$x_a$** dominates **$x_b$** when it is no worse in either objective and better in at least one:

**$Y(x_a)\geq Y(x_b)$** and **$Q(x_a)\geq Q(x_b)$**,

with at least one strict inequality.

The Pareto front is the set of evaluated conditions not dominated by another evaluated condition. Hypervolume summarizes the objective space dominated by the current Pareto front relative to configured objective thresholds. The repository records observed and model-predicted hypervolume when available and uses these values to visualize campaign progress.
## Data Analysis

The `analysis/` directory contains scripts used for post-campaign analysis and manuscript visualization.

The main analyses include:

### Pareto Front

Identification and visualization of non-dominated experimental conditions in yield-throughput objective space.

### Hypervolume

Tracking of multi-objective optimization progress as a function of experiment number.

### Parallel Coordinate Analysis

Visualization of relationships between experimental conditions and reaction outcomes.

### Cross-Campaign Comparison

Comparison of optimization behavior and performance across the xylopyridine analog series.

The manuscript reports autonomous optimization campaigns for the parent compound and a series of related analogs.

---

## Data

The `data/` directory contains the experimental and calibration datasets used for the manuscript.

Planned organization:

```text
data/
├── optimization/
└── calibration/
```

The optimization directory contains the final campaign data used for Pareto, hypervolume, and parallel-coordinate analyses.

The calibration directory contains the analytical calibration data used for quantitative UV-Vis measurements.

Additional raw or archival data may be provided through a separate versioned data repository or DOI-backed archive.

---

## Software Environment

The experimental campaigns reported in the manuscript were executed using Python 3.9. The optimization workflow used Ax 0.3.7 with BoTorch 0.10.0 for multi-objective Bayesian optimization, together with the associated scientific Python dependencies.


The complete software environment used for the reported experiments is provided in the repository through the corresponding requirements/environment file. This file should be used when reproducing the optimization and data-analysis workflow.

Direct execution on the physical experimental platform additionally requires the external Auto_Zahrt framework, the corresponding device drivers, instrument-specific configuration files, and access to the hardware described in the manuscript and Supporting Information. Consequently, recreating the Python environment alone is sufficient for software analysis and portions of the optimization workflow, but not for execution of physical experiments.

Hardware-independent analysis and testing can be performed without connection to the experimental platform.

---

## Running the Tests

Software tests can be run with:

```bash
python -m pytest test/ -m "not hardware"
```

Hardware-dependent tests are excluded from the automated continuous-integration workflow because they require the physical experimental platform.

The repository includes GitHub Actions continuous integration to automatically run the non-hardware test suite on a clean Python environment.

---

## Simulation

The repository contains simulation utilities used during software development and testing. To run in simulation mode, simply use the --simulation flag:

```bash
python main.py path\to\experimental_parameters.json --simulation
```

Simulation functionality is intended to evaluate the optimization and software workflow without requiring connection to the physical experimental platform.

Simulation output should not be interpreted as experimental data.

---

## Hardware Execution

Direct execution of experiments requires:

- the laboratory flow platform described in the manuscript;
- the corresponding hardware configuration;
- Auto_Zahrt;
- the required instrument drivers;
- correct serial/COM-port configuration;
- calibrated analytical parameters.

Because Auto_Zahrt and some hardware-specific components are maintained separately, cloning this repository alone is not sufficient to reproduce physical experiments on arbitrary hardware.

The code and data in this repository are intended primarily to document and reproduce the optimization and analysis workflow associated with the reported manuscript.

## Manuscript

This repository accompanies a manuscript describing the development and application of an autonomous continuous-flow photochemistry platform for multi-objective optimization of xylopyridine-derived photoconvertible fluorophores.

The study demonstrates:

- closed-loop automated experimentation;
- inline UV-Vis-based reaction analysis;
- multi-objective Bayesian optimization;
- autonomous identification of yield-throughput trade-offs;
- optimization across a series of xylopyridine analogs;
- rapid production of photoconverted fluorophores compared with batch irradiation.

Manuscript citation information will be added upon publication.

---

## Reproducing Manuscript Analysis
---
The manuscript figures derived from Bayesian optimization data can be reproduced using the scripts in the `analysis/` directory together with the datasets in `data/optimization/`.

These analyses include:

- Pareto-front generation;
- hypervolume-improvement analysis;
- parallel-coordinate visualization;
- comparison of optimization campaigns.

To get the analyses figures, run:

```bash
python -m analysis.analysis "path\to\run_001" `
  --save-dir-path "path\to\run_001\publication_plots" `
  --yield-point 60 `
  --throughput-point 1.5 `
  --trade-off-yield 80 `
  --trade-off-throughput 2.0
```
Flags:
- "path\to\run_001" — directory containing BO_Results_*_results.csv. If present, hypervolume_results.csv is analyzed too.
- --save-dir-path — output directory for generated plots. Defaults to <run directory>\publication_plots.
- --yield-point — yield percentage for the batch/reference marker.
- --throughput-point — throughput in nmol/min for that reference marker.
- --trade-off-yield — yield percentage for the selected trade-off marker.
- --trade-off-throughput — throughput in nmol/min for that trade-off marker.
-
---

## Citation

If you use this repository, please cite the associated manuscript.

A `CITATION.cff` file and final citation information will be added upon publication.

---

## Authors and Contributions

This software was developed as part of a collaborative research effort involving the Chenoweth and Zahrt laboratories.

Project Dead Man's Fingers contains contributions to:

- autonomous experimentation;
- Bayesian optimization;
- reaction-control workflows;
- analytical data processing;
- photochemical flow optimization;
- software testing and validation.

Author and contributor information should follow the final manuscript and repository contribution records.

---

## License

See the `LICENSE` file for repository licensing information.

---

## Notes on Development History

The software was developed iteratively alongside the experimental platform.

Some modules retain structures originating from earlier versions of the platform. In particular, earlier implementations included co-solvent control that is not part of the final four-variable optimization workflow reported in the manuscript.

The publication version of the repository prioritizes preservation of the validated experimental workflow and reproducibility of the reported results rather than extensive software refactoring.
