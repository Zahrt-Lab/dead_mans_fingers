# Variable Mapping Reference

## README.md Mathematical Notation → Code Variable Names

This document maps the mathematical notation used in README.md to the corresponding variable names in the Python code.

### Flow Rates (µL/min)

| README Symbol | Code Variable Name            | Description                                    | Location |
|---------------|-------------------------------|------------------------------------------------|----------|
| $F_1$         | `flow_rate_pump1`             | Pump 1 flow rate (substrate feed)              | `parameters_to_commands.py` |
| $F_2$         | `flow_rate_pump2`             | Pump 2 flow rate (aqueous diluent)             | `parameters_to_commands.py` |
| $F_3$         | `flow_rate_pump3`             | Pump 3 flow rate (co-solvent)                  | `parameters_to_commands.py` |
| $F_4$         | `flow_rate_pump4`             | Pump 4 flow rate (post-reactor UV dilution)    | `parameters_to_commands.py` |
| $F_{123}$     | `reactor_bed_flow_rate`       | Total reactor flow ($F_1 + F_2 + F_3$)         | `bayesian_optimization_run.py` |
|               | `flow_rate` (optimizer param) | Same as $F_{123}$ (optimizer input)            | `ax_runner.py` |
| $F_{1234}$    | `cuvette_flow_rate`           | Total UV detector flow ($F_{123} + F_4$)       | `parameters_to_commands.py` |

### Concentrations (nmol/L or µM)

| README Symbol       | Code Variable Name                       | Description                                    | Location |
|---------------------|------------------------------------------|------------------------------------------------|----------|
| $C_S$               | `stock_concentration_uM`                 | Stock xylopyridine concentration               | config file / `experimental_parameters.py` |
| $C_{S,\text{in}}$   | `reactor_bed_concentration_uM`           | Substrate concentration entering reactor       | `bayesian_optimization_run.py` |
| $C_{S,\text{A=1.0}}$| `max_absorbance_concentration_uM_uv_detector` | Max absorbance concentration              | config file |
| $C_{S,\text{out}}$  | `concentration_substrate_reactor_out`    | Substrate concentration exiting reactor        | (not directly stored) |
| $C_{P,\text{out}}$  | `concentration_product_mol_per_uL_reactor_bed` × 10^9 | Product concentration exiting reactor | `calculate_concentration_in_reactor_bed.py` |
| $C_{S,UV}$          | `concentration_substrate_uv`             | Substrate concentration in UV cell             | (calculated from absorbance) |
| $C_{P,UV}$          | `concentration_product_mol_per_uL_cuvette` × 10^9 | Product concentration in UV cell      | `calculate_concentration_in_reactor_bed.py` |

### Dilution Factors (dimensionless, 0-1)

| README Symbol         | Code Variable Name         | Description                                    | Location |
|-----------------------|----------------------------|------------------------------------------------|----------|
| $D_{\text{substrate}}$ | `dilution_factor`          | Substrate dilution factor ($F_1 / F_{123}$)    | optimizer parameter |
| $D_{\text{cosolvent}}$ | `cosolvent_fraction`       | Co-solvent fraction ($F_3 / F_{123}$)          | optimizer parameter |
|                       | `fraction_of_cosolvent`    | Same as $D_{\text{cosolvent}}$                 | `bayesian_optimization_run.py` |
| $D_4$                 | (implicit)                 | Pump 4 dilution factor ($F_{1234} / F_{123}$)  | calculated in formulas |

### Optical Properties

| README Symbol             | Code Variable Name                              | Description                                    | Location |
|---------------------------|-------------------------------------------------|------------------------------------------------|----------|
| $\varepsilon_S$           | `epsilon_reactant_at_lambda1_L_per_mol_cm`      | Molar absorptivity of substrate (L/(mol·cm))   | config file |
| $\varepsilon_P$           | `epsilon_product_at_lambda2_L_per_mol_cm`       | Molar absorptivity of product (L/(mol·cm))     | config file |
| $l$                       | `pathlength_cm`                                 | UV detector pathlength (cm)                    | config file |
| $A_\lambda$ or $A_{409}$  | `average_absorbance_reactant`                   | Measured substrate absorbance                  | `average_absorbance.py` |
| $A_{\lambda,P}$ or $A_{506}$ | `average_absorbance_product`                 | Measured product absorbance                    | `average_absorbance.py` |
| $\lambda_S$               | `reactant_wavelength`                           | Substrate measurement wavelength (nm)          | config file |
| $\lambda_P$               | `product_wavelength`                            | Product measurement wavelength (nm)            | config file |

### Operating Conditions

| README Symbol | Code Variable Name         | Description                                    | Location |
|---------------|----------------------------|------------------------------------------------|----------|
| $T$           | `temperature`              | Reactor temperature (°C)                       | optimizer parameter |
| $I$           | `light_intensity`          | Light intensity (W or % of maximum)            | optimizer parameter |
| $V_2$         | `cosolvent_valve_position` | Co-solvent valve position (1-6)                | optimizer parameter |
|               | `co_solvent` (optimizer)   | Same as $V_2$ (optimizer input)                | `ax_runner.py` |
| $V_1$         | (analog selection)         | Analog selection valve (pre-optimization)      | not in current code |
| $V_3$         | (routing valve)            | Post-reactor routing valve (pre-optimization)  | not in current code |
| $V_4$         | (waste valve)              | Waste routing valve (pre-optimization)         | not in current code |

### Objectives

| README Symbol      | Code Variable Name                  | Description                                    | Location |
|--------------------|-------------------------------------|------------------------------------------------|----------|
| Percent Yield (%)  | `product_percent_yield`             | Product yield percentage (0-100%)              | `calculate_percent_yield.py` |
| Throughput         | `product_throughput_nmol_per_min`   | Product throughput (nmol/min)                  | `calculate_product_throughput.py` |

### Volumes (µL)

| README Symbol | Code Variable Name         | Description                                    | Location |
|---------------|----------------------------|------------------------------------------------|----------|
| $V_1$         | `volume_pump1`             | Volume dispensed by Pump 1                     | `parameters_to_commands.py` |
| $V_2$         | `volume_pump2`             | Volume dispensed by Pump 2                     | `parameters_to_commands.py` |
| $V_3$         | `volume_pump3`             | Volume dispensed by Pump 3                     | `parameters_to_commands.py` |
| $V_4$         | `volume_pump4`             | Volume dispensed by Pump 4                     | `parameters_to_commands.py` |
| $V_{123}$     | `reactor_bed_volume_uL`    | Total volume through reactor                   | `parameters_to_commands.py` |
| $V_{1234}$    | `volume_to_detector_uL`    | Total volume to UV detector                    | `calculate_concentration_in_reactor_bed.py` |

## Key Formula Mappings

### From README Step 8: Compute substrate concentration entering the reactor

| README Formula | Code Implementation | File |
|----------------|---------------------|------|
| $C_{S,\text{in}} = C_S \cdot D_{\text{substrate}}$ | `reactor_bed_concentration_uM = dilution_factor * stock_concentration_uM` | `bayesian_optimization_run.py` |
| $F_1 = \frac{C_{S,\text{in}} \cdot F_{123}}{C_S}$ | `pump1_total_flow = flow_rate_uL_per_min * dilution_factor` | `parameters_to_commands.py` |
| $F_2 = F_{123} \cdot (1 - D_{\text{substrate}} - D_{\text{cosolvent}})$ | `flow_rate_pump2 = flow_rate * (1 - dilution_factor - cosolvent_fraction)` | `parameters_to_commands.py` |
| $F_3 = F_{123} \cdot D_{\text{cosolvent}}$ | `flow_rate_pump3 = flow_rate * cosolvent_fraction` | `parameters_to_commands.py` |
| $F_4 = \frac{C_{S,\text{in}} \cdot F_{123}}{C_{S,\text{A=1.0}}} - F_{123}$ | Complex calculation in `parameters_to_commands.py` | `parameters_to_commands.py` |

### From README Step 9: Calculate substrate and product concentrations in UV cell

| README Formula | Code Implementation | File |
|----------------|---------------------|------|
| $C_{S,UV} = \frac{A_{409}}{\varepsilon_S \cdot l}$ | Implicit in Beer-Lambert calculation | `calculate_percent_yield.py` |
| $C_{P,UV} = \frac{A_{\lambda,P}}{\varepsilon_P \cdot l}$ | `concentration = absorbance / (epsilon * pathlength)` | `calculate_concentration_in_reactor_bed.py` |

### From README Step 10: Calculate concentrations exiting reactor

| README Formula | Code Implementation | File |
|----------------|---------------------|------|
| $C_{S,\text{out}} = \frac{C_{S,UV} \cdot F_{1234}}{F_{123}}$ | Not directly calculated (inverse of dilution) | - |
| $C_{P,\text{out}} = \frac{C_{P,UV} \cdot F_{1234}}{F_{123}}$ | `C_reactor = C_cuvette * (V_cuvette / V_reactor)` | `calculate_concentration_in_reactor_bed.py` |

### From README Step 11: Calculate percent yield and throughput

| README Formula | Code Implementation | File |
|----------------|---------------------|------|
| $\text{Percent Yield} = \frac{C_{P,\text{out}}}{C_{S,\text{in}}} \times 100\%$ | `percent_yield = (C_product / C_initial) * 100` | `calculate_percent_yield.py` |
| $\text{Throughput} = C_{P,\text{out}} \cdot F_{123}$ | `throughput = concentration * flow_rate * 1e9` | `calculate_product_throughput.py` |

## Unit Conversions

### Concentration Units
- **µM (micromolar)** = nmol/L (nanomoles per liter) = 10^-6 mol/L
- **mol/L** = 10^9 nmol/L = 10^6 µM
- **mol/µL** = 10^3 mol/mL = 10^6 mol/L = 10^15 nmol/L

### Flow Rate Units
- **µL/min** (microliters per minute)
- **mL/min** = 10^3 µL/min

### Throughput Units
- **nmol/min** (nanomoles per minute)
- **mol/min** = 10^9 nmol/min
- Calculation: `nmol/L × µL/min = nmol/min` (the L and µL cancel to give 10^-6, which when multiplied by nmol (10^-9 mol) gives correct units)

## Common Pitfalls

1. **Concentration unit confusion**: The code often uses µM (micromolar) which equals nmol/L, but Beer-Lambert law calculations use mol/L, requiring conversion factors.

2. **Flow vs Volume**: README uses $F$ for flow rates (µL/min) and $V$ for volumes (µL), but both can appear in similar contexts.

3. **Dilution factor vs fraction**: The README uses $D_{\text{substrate}}$ and $D_{\text{cosolvent}}$ as fractions (0-1), corresponding to the fraction of total flow from each pump.

4. **Pump 4 calculation**: The README formula for $F_4$ accounts for achieving target absorbance, which is implemented differently in the code using a ratio-based approach.

## Verification Checklist

When verifying calculations, check:

- [ ] $F_1 + F_2 + F_3 = F_{123}$ (flow rates sum correctly)
- [ ] $F_1 / F_{123} = D_{\text{substrate}}$ (dilution factor consistency)
- [ ] $F_3 / F_{123} = D_{\text{cosolvent}}$ (co-solvent fraction consistency)
- [ ] $C_{S,\text{in}} = C_S \times D_{\text{substrate}}$ (concentration dilution)
- [ ] Beer-Lambert law: $A = \varepsilon \cdot l \cdot C$ (absorbance calculations)
- [ ] Throughput units: nmol/min = (nmol/L) × (µL/min) × 10^-6
