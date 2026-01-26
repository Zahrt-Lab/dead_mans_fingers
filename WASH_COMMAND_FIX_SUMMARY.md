# Wash Command Verification and Fix Summary

## Issue Identified

The wash commands generated in `*_wash.csv` files were **incorrectly using experiment flow rates and volumes** instead of the fixed wash parameters specified in README Step 5.

## Requirements (from README Step 5)

The wash step should use **fixed parameters** based on the co-solvent dilution fraction (`D_cosolvent`):

- **F₂** = 2000 × (1 - D_cosolvent) µL/min
- **F₃** = 2000 × D_cosolvent µL/min  
- **F₄** = 1000 µL/min
- **V₂** = 6000 × (1 - D_cosolvent) µL
- **V₃** = 6000 × D_cosolvent µL
- **V₄** = 3000 µL

**Totals:**
- V₂ + V₃ should equal **6000 µL**
- F₁₂₃₄ (total flow rate) should equal **3000 µL/min**

## Problem Found

### Before Fix:
- Wash commands were using experiment pump parameters (from the reaction)
- Example from Iteration 1 (D_cosolvent = 0.1775):
  - Expected F₂ = 1645 µL/min, **Actual = 23 µL/min** ❌
  - Expected V₂ = 4935 µL, **Actual = 998 µL** ❌
  - Total volume = 1381 µL instead of 6000 µL ❌
  - Total flow rate = 57 µL/min instead of 3000 µL/min ❌

All 5 tested iterations had the same issue - **100% failure rate**.

## Root Cause

In `experimental_commands/commands.py`, the `save_commands_csv()` function was passing **experiment parameters** directly to `generate_wash_commands()`:

```python
# WRONG - using experiment values
generate_wash_commands(
    flow_rate_pump2,     # ❌ from experiment
    volume_pump2,        # ❌ from experiment
    flow_rate_pump3,     # ❌ from experiment
    volume_pump3,        # ❌ from experiment
    flow_rate_pump4,     # ❌ from experiment
    volume_pump4,        # ❌ from experiment
    valve_position_pump3,
)
```

## Fix Applied

Modified `experimental_commands/commands.py` to **calculate wash-specific parameters** according to README Step 5:

```python
# CORRECT - calculate wash values from Step 5
wash_flow_rate_pump2 = 2000 * (1 - fraction_of_cosolvent)
wash_flow_rate_pump3 = 2000 * fraction_of_cosolvent
wash_flow_rate_pump4 = 1000
wash_volume_pump2 = 6000 * (1 - fraction_of_cosolvent)
wash_volume_pump3 = 6000 * fraction_of_cosolvent
wash_volume_pump4 = 3000

generate_wash_commands(
    wash_flow_rate_pump2,  # ✓ calculated per README
    wash_volume_pump2,     # ✓ calculated per README
    wash_flow_rate_pump3,  # ✓ calculated per README
    wash_volume_pump3,     # ✓ calculated per README
    wash_flow_rate_pump4,  # ✓ calculated per README
    wash_volume_pump4,     # ✓ calculated per README
    valve_position_pump3,
)
```

## Verification Results

### After Fix:
Tested 2 iterations with the corrected code:

**Iteration 1** (D_cosolvent = 0.0837):
- F₂: Expected 1832.59, Actual 1832.59 ✓
- F₃: Expected 167.41, Actual 167.41 ✓
- F₄: Expected 1000.00, Actual 1000.00 ✓
- V₂: Expected 5497.78, Actual 5497.78 ✓
- V₃: Expected 502.22, Actual 502.22 ✓
- V₄: Expected 3000.00, Actual 3000.00 ✓
- **V₂ + V₃ = 6000.00 ✓**
- **F₁₂₃₄ = 3000.00 ✓**

**Iteration 2** (D_cosolvent = 0.0321):
- F₂: Expected 1935.86, Actual 1935.86 ✓
- F₃: Expected 64.14, Actual 64.14 ✓
- F₄: Expected 1000.00, Actual 1000.00 ✓
- V₂: Expected 5807.58, Actual 5807.58 ✓
- V₃: Expected 192.42, Actual 192.42 ✓
- V₄: Expected 3000.00, Actual 3000.00 ✓
- **V₂ + V₃ = 6000.00 ✓**
- **F₁₂₃₄ = 3000.00 ✓**

**Result: 100% pass rate** - All wash commands now match README Step 5 specifications exactly.

## Files Modified

- **`experimental_commands/commands.py`**: Updated `save_commands_csv()` function to calculate wash parameters per README Step 5

## Impact

- ✓ Wash commands now correctly clean the system with appropriate volumes
- ✓ Total wash volume is consistently 6000 µL (V₂ + V₃)
- ✓ Total flow rate is consistently 3000 µL/min (F₂ + F₃ + F₄)
- ✓ Wash parameters are independent of experiment parameters
- ✓ Co-solvent ratio in wash matches experiment co-solvent dilution fraction

## Example Generated Wash Command (Iteration 1)

```csv
Component,Action,Parameters,Notes,delay
Valve6Way_2,go_to_position,position=4,,0.5
VICI_M6_Pump_1,dispense,"flow_rate=1832.59, volume=5497.78",The flow rate of our 0.1 M HCl Water is 1832.59 uL/min and volume is 5497.78,0.5
VICI_M6_Pump_2,dispense,"flow_rate=167.41, volume=502.22",The flow rate of our cosolvent is 167.41 uL/min and volume is 502.22,0.5
Tricontinental_Pump_C24000_2,aspirate,"flow_rate=1000, volume=3000",The flow rate of our 0.1 M HCl water pump is 1000 uL/min and volume is 3000,0.5
SYNC,wait_for_pumps,,Waiting for XYLO and WATER pumps to complete,0.5
```

This correctly washes with:
- 6000 µL total volume (5497.78 + 502.22)
- 3000 µL/min total flow rate (1832.59 + 167.41 + 1000)
- Proper co-solvent ratio matching the experiment

