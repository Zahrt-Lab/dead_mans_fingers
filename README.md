# Project Dead Man's Fingers

Project Dead Man's Fingers is the software repository associated with the manuscript describing an autonomous continuous-flow photochemistry platform for the optimization and production of photoconverted xylopyridine-derived diazaxanthilidene fluorophores.

The repository contains the code used to manage Bayesian optimization, experimental parameter handling, analytical post-processing, and manuscript data analysis for the reported optimization campaigns. Hardware orchestration and device-level control are handled through the external Auto_Zahrt framework.

The name *Dead Man's Fingers* refers to the fungal family from which xylopyridine was originally isolated.

---

## Overview

The platform was developed to accelerate the photoconversion of xylopyridine-derived diazaxanthilidene fluorophores, which require several days under previously used batch conditions.

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
production_run/
```

Utilities for executing selected reaction conditions for preparative production runs.

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

## Installation

The experimental campaigns were executed using Python 3.9 and a defined scientific Python environment.

A reproducible environment file will be provided in this repository.

Typical dependencies include:

- Python
- Ax
- BoTorch
- PyTorch
- NumPy
- pandas
- SciPy
- matplotlib
- pyserial

The exact environment used for the reported experiments should be recreated using the environment file provided with the repository.

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

The repository contains simulation utilities used during software development and testing.

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

The code and data in this repository are intended primarily to document and reproduce the optimization and analysis workflow associated with the reported study.

---

## Reproducing Manuscript Analysis

The manuscript figures derived from Bayesian optimization data can be reproduced using the scripts in the `analysis/` directory together with the datasets in `data/optimization/`.

These analyses include:

- Pareto-front generation;
- hypervolume-improvement analysis;
- parallel-coordinate visualization;
- comparison of optimization campaigns.

Specific data-to-figure mappings and example commands will be added with the final publication dataset.

---

## Continuous Integration

GitHub Actions is used to automatically validate the software-only test suite.

The CI workflow:

1. checks out the repository;
2. installs Python 3.9;
3. installs the required dependencies;
4. runs all non-hardware tests.

This provides an independent check that the publication version of the repository remains functional outside the development computer.

---

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
