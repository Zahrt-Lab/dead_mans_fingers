# ------------------------------------------------------------------------------
# Software: project_dead_mans_fingers
# Copyright: (C) 2025 by Professor Andrew Zahrt
# This software is the intellectual property of Professor Andrew Zahrt
# Contributions by graduate students Scott Laverty and Joao are acknowledged.
# All rights reserved.
# ------------------------------------------------------------------------------

'''
This script takes the recommend experimental parameters from the Bayesian optimizer 
and converts them into the instrument commands to be sent to the equipment for 
experiment to be performed.
'''

from typing import Dict

# TODO : Since we put multiple xylopyrdine analogs in the same stock solution, 
# TODO : Need to modify this function so it specificies which xylopyridine analogs 
# to be used for this calculation since currently it recieves the concentration of all the 
# xylopyridine analogs in the stock solution and returns a list.
def parameters_to_commands(
    flow_rate_uL_per_min: float,
    dilution_factor: float,
    cosolvent_valve_position: int,
    cosolvent_fraction: float,
    light_intensity: float,
    xylopyridine_analogs_concentrations_uM: list,
    target_absorbance_in_the_uv_detector: float,
    max_absorbance_concentration_uM_uv_detector: float,
    volume_uL: int,
) -> Dict[str, int]:
    '''

    parameters:
        - flow_rate_uL_per_min: The total flow rate in uL/min in the reactor bed
        - dilution_factor: The fraction of the total flow rate that is the 
          original stock solution (e.g. XYLO compound), the remaining will be 
          diluted by pump 2 (0.1 M HCl water) and pump 3 (co-solvent, e.g. acetonitrile)
          before reaching the reactor bed
        - cosolvent_valve_position: The position of the valve that controls which 
          co-solvent is added to the reactor bed (1-6)
        - cosolvent_fraction: The fraction of the total flow rate that is the 
           co-solvent (e.g. acetonitrile)
        - light_intensity: The intensity of the light in the reactor bed,
          max intensity is 400W and percentage of light being shown ranges
          from 0% to 100%
        - xylopyridine_analogs_concentrations_uM: A list of concentrations of the xylopyridine analogs in uM
        - target_absorbance_in_the_uv_detector: The target absorbance in the 
          UV detector for the optimization to calculate conversion and throughput
        - max_absorbance_concentration_uM_uv_detector: The concentration in uM that 
          corresponds to the maximum absorbance in the UV detector (used for calculating 
          dilution to the UV detector)
        - volume_uL: The total volume in uL to be sent through the reactor bed for the experiment       
    return:
        A dictionary with the flow rates and volumes for each pump, and the valve position 
        for the co-solvent    
    
    '''
    # Validation
    if flow_rate_uL_per_min <= 0:
        raise ValueError("flow_rate must be > 0 µL/min.")
    if volume_uL <= 0:
        raise ValueError("volume must be > 0 µL.")
    if not (0.0 <= dilution_factor <= 1.0):
        raise ValueError("dilution_factor must be in [0, 1].")
    if not (1 <= cosolvent_valve_position <= 6):
        raise ValueError(f"cosolvent valve position must be in [1, 6],"
                         f"got {cosolvent_valve_position}.")
    if not (0.0 <= cosolvent_fraction <= 1.0):
        raise ValueError("cosolvent_fraction must be in [0, 1].")
    if cosolvent_fraction > (1.0 - dilution_factor):
        raise ValueError(
            "cosolvent_fraction cannot exceed (1 - dilution_factor) " \
            "because pump2 would go negative."
        )
    if not (0.0 <= light_intensity <= 100.0):
        raise ValueError("light_intensity must be in [0, 100].")
    
    for xylopyridine_analog_concentration in xylopyridine_analogs_concentrations_uM:
        if xylopyridine_analog_concentration <= 0:
            raise ValueError("xylopyridine_analog_concentration_uM must be > 0.")
    
    if max_absorbance_concentration_uM_uv_detector <= 0:
        raise ValueError("max_absorbance_concentration_uM_uv_detector must be > 0.")
    if target_absorbance_in_the_uv_detector <= 0:
        raise ValueError("target_absorbance_in_the_uv_detector must be > 0.")

    # Pump 1 (reactant): compute TOTAL, then per-syringe command
    pump1_total_flow = flow_rate_uL_per_min * dilution_factor
    pump1_total_volume = volume_uL * dilution_factor
    flow_rate_pump1_uL_per_min = pump1_total_flow
    volume_pump1_uL = pump1_total_volume

    # Pump 2: 0.1 M HCl water for reactor bed (remainder after pump1 + cosolvent)
    pump2_dilution_fraction = (1.0 - dilution_factor) - cosolvent_fraction
    flow_rate_pump2_uL_per_min = flow_rate_uL_per_min * pump2_dilution_fraction
    volume_pump2_uL = volume_uL * pump2_dilution_fraction

    # Pump 3: co-solvent
    flow_rate_pump3_uL_per_min = flow_rate_uL_per_min * cosolvent_fraction
    volume_pump3_uL = volume_uL * cosolvent_fraction

    # Reactor-bed totals for UV dilution calculations
    reactor_bed_flow_rate_uL_per_min = \
        (pump1_total_flow + flow_rate_pump2_uL_per_min + flow_rate_pump3_uL_per_min)
    
    reactor_bed_volume_uL = \
        (pump1_total_volume + volume_pump2_uL + volume_pump3_uL)

    # Pump 4: dilution to UV detector
    reactor_bed_concentration_uM = dilution_factor * xylopyridine_analogs_concentrations_uM
    cuvette_concentration_uM = max_absorbance_concentration_uM_uv_detector * target_absorbance_in_the_uv_detector

    # If reactor is already <= target, no extra dilution needed
    if reactor_bed_concentration_uM <= cuvette_concentration_uM:
        flow_rate_pump4_uL_per_min = 0.0
        volume_pump4_uL = 0.0
    else:
        ratio = reactor_bed_concentration_uM / cuvette_concentration_uM  # > 1
        cuvette_flow_rate_uL_per_min = reactor_bed_flow_rate_uL_per_min * ratio
        flow_rate_pump4_uL_per_min = max(0.0, cuvette_flow_rate_uL_per_min - reactor_bed_flow_rate_uL_per_min)
        volume_pump4_uL = max(0.0, (ratio - 1.0) * reactor_bed_volume_uL)

    return {
        "flow_rate_pump1": int(round(max(0.0, flow_rate_pump1_uL_per_min))),
        "volume_pump1": int(round(max(0.0, volume_pump1_uL))),
        "flow_rate_pump2": int(round(max(0.0, flow_rate_pump2_uL_per_min))),
        "volume_pump2": int(round(max(0.0, volume_pump2_uL))),
        "flow_rate_pump3": int(round(max(0.0, flow_rate_pump3_uL_per_min))),
        "volume_pump3": int(round(max(0.0, volume_pump3_uL))),
        "position_valve1": int(cosolvent_valve_position),
        "flow_rate_pump4": int(round(max(0.0, flow_rate_pump4_uL_per_min))),
        "volume_pump4": int(round(max(0.0, volume_pump4_uL))),
    }
