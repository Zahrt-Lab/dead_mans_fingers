# ------------------------------------------------------------------------------
# Software: dead_mans_fingers
# Copyright (c) 2026 Zahrt Research Group
#
# Contributions by Scott Laverty are acknowledged.
#
# Licensed under the MIT License. See the LICENSE file in the repository root.
# ------------------------------------------------------------------------------

"""
This script takes the recommended experimental parameters from the Bayesian optimizer
and converts them into the instrument commands to be sent to the equipment for
the experiment to be performed.
"""

from typing import Dict, Any


def parameters_to_commands(
    trial_conditions: Dict[str, float],
    total_volume_through_reactor_bed: float,
    xylopyridine_analogs_concentrations_uM: float,
    max_absorbance_concentration_uM_uv_detector: float,
    target_absorbance_in_the_uv_detector: float,
    production_run: bool = False
) -> Dict[str, Any]:
    """
    Convert trial conditions and bo campaign constant values into instrument parameters.

    Parameters: 
        trial_conditions: Dict with keys: flow_rate, dilution_factor, temperature,
            co_solvent_valve_position, co_solvent_dilution_factor, light_intensity.
        total_volume_through_reactor_bed: Total volume to pump through the reactor bed in µL.
        xylopyridine_analogs_concentrations_uM: Stock solution concentration of the xylopyridine analog in µM.
        max_absorbance_concentration_uM_uv_detector: Maximum concentration (µM) the UV detector can handle linearly (we assume max absorbace = 1)
        target_absorbance_in_the_uv_detector: Given the max absorbance concentration, this is the absorbance level to target in the UV detector. (typically set to 1.0)

    Returns:
        Dict[str, Any]: Instrument command parameters (flow rates, volumes, valve, temp, light).
    """
    # --- Validate trial conditions ---
    flow_rate = trial_conditions["flow_rate"]
    dilution_factor = trial_conditions["dilution_factor"]
    temperature = trial_conditions["temperature"]
    light_intensity = trial_conditions["light_intensity"]

    if flow_rate <= 0:
        raise ValueError("flow_rate must be > 0 µL/min.")
    if not (0.0 <= dilution_factor <= 1.0):
        raise ValueError("dilution_factor must be in [0, 1].")

    if not (0.0 <= light_intensity <= 100.0):
        raise ValueError("light_intensity must be in [0, 100].")

    # --- Validate campaign constants ---
    if total_volume_through_reactor_bed <= 0:
        raise ValueError("total_volume_through_reactor_bed must be > 0 µL.")

    if xylopyridine_analogs_concentrations_uM <= 0:
        raise ValueError("xylopyridine_analogs_concentrations_uM must be > 0.")
    if not production_run:
        if max_absorbance_concentration_uM_uv_detector <= 0:
            raise ValueError("max_absorbance_concentration_uM_uv_detector must be > 0.")
        if target_absorbance_in_the_uv_detector <= 0:
            raise ValueError("target_absorbance_in_the_uv_detector must be > 0.")

    # --- Pump calculations ---
    # Pump 1 (reactant)
    flow_rate_pump1 = flow_rate * dilution_factor
    volume_pump1 = total_volume_through_reactor_bed * dilution_factor
    if flow_rate_pump1 <= 25 and flow_rate_pump1 > 0:
        print(f"WARNING: LOW FLOW RATE OF {flow_rate_pump1} µL/min FOR PUMP 1 XYLOPYRIDINE ANALOG PUMP WILL HAVE LOW ACCURACY AND PRECISION")

    # Pump 2 (acid/water remainder after pump1 + cosolvent)
    pump2_dilution_factor = (1.0 - dilution_factor)
    flow_rate_pump2 = flow_rate * pump2_dilution_factor
    volume_pump2 = total_volume_through_reactor_bed * pump2_dilution_factor
    if flow_rate_pump2 <= 25 and flow_rate_pump2 > 0:
        print(f"WARNING: LOW FLOW RATE OF {flow_rate_pump2} µL/min FOR PUMP 2 DILUTION PUMP WILL HAVE LOW ACCURACY AND PRECISION")
    
    co_solvent_dilution_factor = 0.0
    # Pump 3 (cosolvent)
    flow_rate_pump3 = flow_rate * co_solvent_dilution_factor
    volume_pump3 = total_volume_through_reactor_bed * co_solvent_dilution_factor
    if flow_rate_pump3 <= 25 and flow_rate_pump3 > 0:
        print(f"WARNING: LOW FLOW RATE OF {flow_rate_pump3} µL/min FOR PUMP 3 COSOLVENT PUMP WILL HAVE LOW ACCURACY AND PRECISION")

    # Reactor bed flow rate and volume
    flow_rate_reactor = flow_rate_pump1 + flow_rate_pump2 + flow_rate_pump3
    volume_reactor = volume_pump1 + volume_pump2 + volume_pump3

    if production_run == False:
        # Pump 4 (UV dilution): dilutes reactor output to keep detector in linear range.
        # cuvette_conc_uM is the target concentration at the detector.
        reactor_conc_uM = dilution_factor * xylopyridine_analogs_concentrations_uM
        cuvette_conc_uM = max_absorbance_concentration_uM_uv_detector * target_absorbance_in_the_uv_detector
        # If reactor concentration is already below target, no dilution needed.
        if reactor_conc_uM <= cuvette_conc_uM:
            flow_rate_pump4 = 0.0
            volume_pump4 = 0.0
        # If reactor concentration is above target, calculate dilution flow and volume.
        else:
            ratio = reactor_conc_uM / cuvette_conc_uM  # > 1
            cuvette_flow = flow_rate_reactor * ratio
            flow_rate_pump4 = max(0.0, cuvette_flow - flow_rate_reactor)
            volume_pump4 = max(0.0, (ratio - 1.0) * volume_reactor)
            if flow_rate_pump4 <= 25 and flow_rate_pump4 > 0:
                print(f"WARNING: LOW FLOW RATE OF {flow_rate_pump4} µL/min FOR PUMP 4 UV DILUTION PUMP WILL HAVE LOW ACCURACY AND PRECISION")
    else:
        # Production runs do not use the inline UV detector, so pump 4 is not needed.
        flow_rate_pump4 = 0.0
        volume_pump4 = 0.0

    # Set Light intensity as a value between 0 (brightest) and 255 (dimmest) in integer values
    light_intensity = int(round((100.0 - light_intensity) / 100.0 * 255))

    cosolvent_position = 1  # For now, we are not using a co-solvent, so the valve position is set to 1.

    return {
        "flow_rate_pump1": float(round(flow_rate_pump1, 2)),
        "volume_pump1": float(round(volume_pump1, 2)),
        "flow_rate_pump2": float(round(flow_rate_pump2, 2)),
        "volume_pump2": float(round(volume_pump2, 2)),
        "flow_rate_pump3": float(round(flow_rate_pump3, 2)),
        "volume_pump3": float(round(volume_pump3, 2)),
        "position_valve2": int(round(cosolvent_position)),
        "flow_rate_pump4": float(round(flow_rate_pump4, 2)),
        "volume_pump4": float(round(volume_pump4, 2)),
        "temperature": float(round(temperature, 2)),
        "light_intensity": float(round(light_intensity, 2)),
    }
