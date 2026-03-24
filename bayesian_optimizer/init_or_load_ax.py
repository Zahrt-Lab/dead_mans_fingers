# ------------------------------------------------------------------------------
# Software: project_dead_mans_fingers
# Copyright: (C) 2025 by Professor Andrew Zahrt
# This software is the intellectual property of Professor Andrew Zahrt
# Contributions by graduate students Scott Laverty and Joao are acknowledged.
# All rights reserved.
# ------------------------------------------------------------------------------

'''
The purpose of this module is to initialize a new AxClient or load an existing one from a JSON file,
setting up the experiment parameters and objectives for the Bayesian optimization campaign.
'''

# bayesian_optimizer/init_or_load_ax.py
from __future__ import annotations

import os

from ax.service.ax_client import AxClient, ObjectiveProperties

def _init_or_load_ax(
    ax_previous_run_json_file_path: str,
    flow_rate_min: float,
    flow_rate_max: float,
    dilution_factor_min: float,
    dilution_factor_max: float,
    temperature_min: float,
    temperature_max: float,
    co_solvent_valve_position_min: float,
    co_solvent_valve_position_max: float,
    co_solvent_dilution_factor_min: float,
    co_solvent_dilution_factor_max: float,
    light_intensity_min: float,
    light_intensity_max: float,
    percent_yield_threshold: float,
    throughput_threshold: float,
) -> AxClient:
    """
    Initialize a new AxClient or resume from a JSON state file to begin a bayesian optimization campaign.

    Parameters:
        ax_previous_run_json_file_path: Path to JSON file to load Ax state from (if exists)
        flow_rate_min, flow_rate_max: Bounds for flow rate parameter
        dilution_factor_min, dilution_factor_max: Bounds for dilution factor parameter
        temperature_min, temperature_max: Bounds for temperature parameter
        co_solvent_valve_position_min, co_solvent_valve_position_max: Bounds for co-solvent valve position parameter
        co_solvent_dilution_factor_min, co_solvent_dilution_factor_max: Bounds for co-solvent dilution factor parameter
        light_intensity_min, light_intensity_max: Bounds for light intensity parameter
        percent_yield_threshold: Threshold for percent yield objective (for Ax)
        throughput_threshold: Threshold for throughput objective (for Ax)

    Returns:
        AxClient: AxClient instance ready for optimization campaign (with experiment created and objectives set)
    """
    if os.path.exists(ax_previous_run_json_file_path):
        ax = AxClient.load_from_json_file(ax_previous_run_json_file_path)
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
                "name": "co_solvent_valve_position",
                "type": "range",
                "bounds": [co_solvent_valve_position_min, co_solvent_valve_position_max],
                "value_type": "int",
            },
            {
                "name": "co_solvent_dilution_factor",
                "type": "range",
                "bounds": [co_solvent_dilution_factor_min, co_solvent_dilution_factor_max],
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
