# ------------------------------------------------------------------------------
# Software: project_dead_mans_fingers
# Copyright: (C) 2025 by Professor Andrew Zahrt
# This software is the intellectual property of Professor Andrew Zahrt
# Contributions by graduate students Scott Laverty and Joao are acknowledged.
# All rights reserved.
# ------------------------------------------------------------------------------

"""
This script takes the recommend experimental parameters from the Bayesian optimizer
and converts them into the instrument commands to be sent to the equipment for
experiment to be performed.
"""

from typing import Dict, Any
from bayesian_optimizer.experiment_state import BoCampaignState, IterationState

# TODO : We should go back to an older version of this code with input being
# 1) the trial conditions
# 2) the reactor bed volume 
# 3) the xylopyridine analog concentration in uM
# 4) the max absorbance concentration in uM for the UV detector
# 5) the target absorbance in the UV detector
# The reasoning is that we wish to use this in the production run as well,
# and in the production run we will not have the same BO parameters

def parameters_to_commands(
    bo_campaign_state: BoCampaignState,
    iteration_state: IterationState,
) -> Dict[str, Any]:
    """
    Parameters
    ----------
    bo_campaign_state
        Campaign-level state (constants, BO parameters).
    iteration_state
        Iteration-level state (trial conditions for this run).

    Returns
    -------
    Dict[str, int]
        Instrument command parameters (rounded to integers where needed).
    """
    trial_conditions = iteration_state.trial_conditions
    bo_parameters = bo_campaign_state.bo_parameters

    # --- Validate trial conditions ---
    flow_rate = trial_conditions["flow_rate"]
    dilution_factor = trial_conditions["dilution_factor"]
    temperature = trial_conditions["temperature"]
    cosolvent_position = trial_conditions["co_solvent_valve_position"]
    cosolvent_dilution_factor = trial_conditions["co_solvent_dilution_factor"]
    light_intensity = trial_conditions["light_intensity"]

    if flow_rate <= 0:
        raise ValueError("flow_rate must be > 0 µL/min.")
    if not (0.0 <= dilution_factor <= 1.0):
        raise ValueError("dilution_factor must be in [0, 1].")
    if not (1 <= cosolvent_position <= 6):
        raise ValueError(
            f"cosolvents_valve_position must be in [1, 6], got {cosolvent_position}."
        )
    if not (0.0 <= cosolvent_dilution_factor <= 1.0):
        raise ValueError("co_solvent_dilution_factor must be in [0, 1].")
    if cosolvent_dilution_factor > (1.0 - dilution_factor):
        raise ValueError(
            "co_solvent_dilution_factor cannot exceed (1 - dilution_factor) "
            "because pump2 would go negative."
        )
    if not (0.0 <= light_intensity <= 100.0):
        raise ValueError("light_intensity must be in [0, 100].")

    # --- Validate BO/campaign parameters ---
    total_volume = bo_parameters["total_volume_through_reactor_bed"]
    if total_volume <= 0:
        raise ValueError("total_volume_through_reactor_bed must be > 0 µL.")

    xylopyridine_uM = bo_parameters["xylopyridine_analogs_concentrations_uM"]
    max_abs_uM = bo_parameters["max_absorbance_concentration_uM_uv_detector"]
    target_abs = bo_parameters["target_absorbance_in_the_uv_detector"]

    if xylopyridine_uM <= 0:
        raise ValueError("xylopyridine_analogs_concentrations_uM must be > 0.")
    if max_abs_uM <= 0:
        raise ValueError("max_absorbance_concentration_uM_uv_detector must be > 0.")
    if target_abs <= 0:
        raise ValueError("target_absorbance_in_the_uv_detector must be > 0.")

    # --- Pump calculations ---
    # Pump 1 (reactant)
    flow_rate_pump1 = flow_rate * dilution_factor
    volume_pump1 = total_volume * dilution_factor

    # Pump 2 (acid/water remainder after pump1 + cosolvent)
    pump2_dilution_factor = (1.0 - dilution_factor) - cosolvent_dilution_factor
    flow_rate_pump2 = flow_rate * pump2_dilution_factor
    volume_pump2 = total_volume * pump2_dilution_factor

    # Pump 3 (cosolvent)
    flow_rate_pump3 = flow_rate * cosolvent_dilution_factor
    volume_pump3 = total_volume * cosolvent_dilution_factor

    # Reactor bed flow rate and volume
    flow_rate_reactor = flow_rate_pump1 + flow_rate_pump2 + flow_rate_pump3
    volume_reactor = volume_pump1 + volume_pump2 + volume_pump3

    # Pump 4 (UV dilution)
    reactor_conc_uM = dilution_factor * xylopyridine_uM
    # TODO : Is this math correct? We should double check this
    cuvette_conc_uM = max_abs_uM * target_abs

    if reactor_conc_uM <= cuvette_conc_uM:
        flow_rate_pump4 = 0.0
        volume_pump4 = 0.0
    else:
        ratio = reactor_conc_uM / cuvette_conc_uM  # > 1
        cuvette_flow = flow_rate_reactor * ratio
        flow_rate_pump4 = max(0.0, cuvette_flow - flow_rate_reactor)
        volume_pump4 = max(0.0, (ratio - 1.0) * volume_reactor)

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
