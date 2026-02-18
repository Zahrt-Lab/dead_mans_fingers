# ------------------------------------------------------------------------------
# Software: project_dead_mans_fingers
# Copyright: (C) 2025 by Professor Andrew Zahrt
# This software is the intellectual property of Professor Andrew Zahrt
# Contributions by graduate students Scott Laverty and Joao are acknowledged.
# All rights reserved.
# ------------------------------------------------------------------------------

"""
Volume Management Module for Bayesian Optimization.

This module handles stock solution volume initialization, checking, and updating
throughout the Bayesian optimization campaign.
"""

# TODO : Need to evaluate the quality of this code to make sure it is robust and 
# handles all edge cases. 

from typing import Dict, Any, Union, List
from bayesian_optimizer.deterministic_commands import state
from bayesian_optimizer.deterministic_commands.state import ITERATION, BO_EXPERIMENTAL_PARAMETERS
from preprocessing.check_volume import check_volume
from utils.experiment_aborted import ExperimentAborted


def initialize_stock_volumes() -> None:
    """
    Initialize stock solution volumes on the first iteration.
    
    Sets up volume tracking for all four pumps in the iteration state dictionary.
    """
    if ITERATION["iteration #"] == 1:
        pump1_vol = BO_EXPERIMENTAL_PARAMETERS["pump1_xylopyridine_analogs_volume_stock_solution"]
        # Handle both single value and list formats
        ITERATION["volume_stock_solution1"] = pump1_vol[0] if isinstance(pump1_vol, list) else pump1_vol
        
        pump2_vol = BO_EXPERIMENTAL_PARAMETERS["pump2_0.1M_HCl_water_volume_stock_solution"]
        ITERATION["volume_stock_solution2"] = pump2_vol[0] if isinstance(pump2_vol, list) else pump2_vol
        
        ITERATION["volume_stock_solution3"] = BO_EXPERIMENTAL_PARAMETERS[
            "pump3_co-solvents_volume_stock_solutions"
        ]
        
        pump4_vol = BO_EXPERIMENTAL_PARAMETERS["pump4_0.1M_HCl_water_volume_stock_solution"]
        ITERATION["volume_stock_solution4"] = pump4_vol[0] if isinstance(pump4_vol, list) else pump4_vol


def check_and_update_volumes(instrument_params: Dict[str, float], 
                              cosolvent_valve_position: int) -> None:
    """
    Check stock solution volumes and update after consumption.
    
    In non-simulation mode, validates that sufficient volume exists before the experiment.
    If insufficient, raises ExperimentAborted. In simulation mode, simply subtracts volumes.
    
    Args:
        instrument_params: Dictionary containing volume_pump1, volume_pump2, etc.
        cosolvent_valve_position: Which co-solvent valve position is being used (1-indexed)
    
    Raises:
        ExperimentAborted: If any stock solution has insufficient volume (non-simulation only)
    """
    volume_pump1 = instrument_params["volume_pump1"]
    volume_pump2 = instrument_params["volume_pump2"]
    volume_pump3 = instrument_params["volume_pump3"]
    volume_pump4 = instrument_params["volume_pump4"]
    
    print(f"There is {ITERATION['volume_stock_solution1']} in stock solution 1 before the experiment")
    print(f"There is {ITERATION['volume_stock_solution2']} in stock solution 2 before the experiment")
    print(f"There is {ITERATION['volume_stock_solution3']} in stock solution 3 before the experiment")
    print(f"There is {ITERATION['volume_stock_solution4']} in stock solution 4 before the experiment")
    
    if not state.SIMULATION_MODE:
        # Hardware mode: check volumes and raise exception if insufficient
        ITERATION["volume_stock_solution1"] = check_volume(
            ITERATION["volume_stock_solution1"],
            volume_pump1,
            BO_EXPERIMENTAL_PARAMETERS["minimum_volume_required"],
            BO_EXPERIMENTAL_PARAMETERS.get("name_of_stock_solution1", "Reactant"),
        )
        ITERATION["volume_stock_solution2"] = check_volume(
            ITERATION["volume_stock_solution2"],
            volume_pump2,
            BO_EXPERIMENTAL_PARAMETERS["minimum_volume_required"],
            BO_EXPERIMENTAL_PARAMETERS.get("name_of_stock_solution2", "Buffer"),
        )
        
        # Handle co-solvent volume - could be single value or list
        cosolvent_vol = ITERATION["volume_stock_solution3"]
        if isinstance(cosolvent_vol, list):
            # For multiple co-solvents, update the specific valve position
            valve_idx = int(cosolvent_valve_position) - 1  # 1-indexed to 0-indexed
            cosolvent_vol[valve_idx] = check_volume(
                cosolvent_vol[valve_idx],
                volume_pump3,
                BO_EXPERIMENTAL_PARAMETERS["minimum_volume_required"],
                BO_EXPERIMENTAL_PARAMETERS.get("name_of_co-solvent_stock_solutions", ["Co-solvent"])[valve_idx],
            )
            ITERATION["volume_stock_solution3"] = cosolvent_vol
        else:
            ITERATION["volume_stock_solution3"] = check_volume(
                cosolvent_vol,
                volume_pump3,
                BO_EXPERIMENTAL_PARAMETERS["minimum_volume_required"],
                BO_EXPERIMENTAL_PARAMETERS.get("name_of_stock_solution3", "Co-solvent"),
            )
        
        ITERATION["volume_stock_solution4"] = check_volume(
            ITERATION["volume_stock_solution4"],
            volume_pump4,
            BO_EXPERIMENTAL_PARAMETERS["minimum_volume_required"],
            BO_EXPERIMENTAL_PARAMETERS.get("name_of_stock_solution4", "Dilution Water"),
        )
    else:
        # Simulation mode: just subtract volumes
        ITERATION["volume_stock_solution1"] -= volume_pump1
        ITERATION["volume_stock_solution2"] -= volume_pump2
        
        # Handle co-solvent volume - could be single value or list
        cosolvent_vol = ITERATION["volume_stock_solution3"]
        if isinstance(cosolvent_vol, list):
            valve_idx = int(cosolvent_valve_position) - 1
            cosolvent_vol[valve_idx] -= volume_pump3
            ITERATION["volume_stock_solution3"] = cosolvent_vol
        else:
            ITERATION["volume_stock_solution3"] -= volume_pump3
        
        # Handle dilution pump volume
        pump4_vol = ITERATION["volume_stock_solution4"]
        if isinstance(pump4_vol, list):
            total_volume = sum(pump4_vol) - volume_pump4
            ITERATION["volume_stock_solution4"] = total_volume
        else:
            ITERATION["volume_stock_solution4"] -= volume_pump4
    
    print(f"There is {ITERATION['volume_stock_solution1']} in stock solution 1 after the experiment")
    print(f"There is {ITERATION['volume_stock_solution2']} in stock solution 2 after the experiment")
    print(f"There is {ITERATION['volume_stock_solution3']} in stock solution 3 after the experiment")
    print(f"There is {ITERATION['volume_stock_solution4']} in stock solution 4 after the experiment")
