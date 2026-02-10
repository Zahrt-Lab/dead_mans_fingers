# ------------------------------------------------------------------------------
# Software: project_dead_mans_fingers
# Copyright: (C) 2025 by Professor Andrew Zahrt
# This software is the intellectual property of Professor Andrew Zahrt
# Contributions by graduate students Scott Laverty and Joao are acknowledged.
# All rights reserved.
# ------------------------------------------------------------------------------

'''
This module initializes or loads an Ax client for Bayesian Optimization campaigns
'''

# bayesian_optimizer/init_or_load_ax.py
from __future__ import annotations

import os

from ax.service.ax_client import AxClient, ObjectiveProperties

# TODO : Need to verify input files needed for the bayesian optimizer code to run properly
# TODO : Need to develop a diagram and brief readme file as a reference for future users of this code and how it works
def _init_or_load_ax(
    state_path: str,
    flow_rate_min: float,
    flow_rate_max: float,
    dilution_factor_min: float,
    dilution_factor_max: float,
    temperature_min: float,
    temperature_max: float,
    cosolvents_valve_position_min: float,
    cosolvents_valve_position_max: float,
    co_solvent_volume_min: float,
    co_solvent_volume_max: float,
    light_intensity_min: float,
    light_intensity_max: float,
    percent_yield_threshold: float,
    throughput_threshold: float,
) -> AxClient:
    """
    Initialize a new AxClient or resume from a JSON state file to begin a bayesian optimization campaign.
    """
    if os.path.exists(state_path):
        ax = AxClient.load_from_json_file(state_path)
        print(f"Resumed Ax experiment with {len(ax.get_trials_data_frame())} trials.")
        return ax

    ax = AxClient()
    ax.create_experiment(
        name="project_dead_mans_fingers_moo_ax",
        parameters=[
            {
                "name": "flow_rate",
                "type": "range",
                "bounds": [flow_rate_min, flow_rate_max],
                "value_type": "int",
            },
            {
                "name": "dilution_factor",
                "type": "range",
                "bounds": [dilution_factor_min, dilution_factor_max],
                "value_type": "float",
            },
            {
                "name": "temperature",
                "type": "range",
                "bounds": [temperature_min, temperature_max],
                "value_type": "float",
            },
            {
                "name": "co_solvent",
                "type": "range",
                "bounds": [cosolvents_valve_position_min, cosolvents_valve_position_max],
                "value_type": "int",
            },
            {
                "name": "co_solvent_volume",
                "type": "range",
                "bounds": [co_solvent_volume_min, co_solvent_volume_max],
                "value_type": "float",
            },
            {
                "name": "light_intensity",
                "type": "range",
                "bounds": [light_intensity_min, light_intensity_max],
                "value_type": "float",
            },
        ],
        # This will set the objective functions and their thresholds to maximize both percent yield and throughput
        objectives={
            "percent_yield": ObjectiveProperties(
                minimize=False, threshold=float(percent_yield_threshold)
            ),
            "throughput": ObjectiveProperties(
                minimize=False, threshold=float(throughput_threshold)
            ),
        },
    )
    
    print("Started new Ax experiment.")
    return ax
