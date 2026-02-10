# ------------------------------------------------------------------------------
# Software: project_dead_mans_fingers
# Copyright: (C) 2025 by Professor Andrew Zahrt
# This software is the intellectual property of Professor Andrew Zahrt
# Contributions by graduate students Scott Laverty are acknowledged.
# All rights reserved.
# ------------------------------------------------------------------------------

"""
Volume Management Module for Bayesian Optimization.

This module handles stock solution volume initialization, checking, and updating
throughout the Bayesian optimization campaign.
"""

from typing import Dict, Any, Union, List
from bayesian_optimizer import state
from bayesian_optimizer.state import iteration, EXPERIMENTAL_PARAMETERS
from preprocessing.check_volume import check_volume
from preprocessing.experimental_parameters import ExperimentAborted


def initialize_stock_volumes() -> None:
    """
    Initialize stock solution volumes on the first iteration.
    
    Sets up volume tracking for all four pumps in the iteration state dictionary.
    """
    if iteration["iteration #"] == 1:
        pump1_vol = EXPERIMENTAL_PARAMETERS["pump1_xylopyridine_analogs_volume_stock_solution"]
        # Handle both single value and list formats
        iteration["volume_stock_solution1"] = pump1_vol[0] if isinstance(pump1_vol, list) else pump1_vol
        
        iteration["volume_stock_solution2"] = EXPERIMENTAL_PARAMETERS[
            "pump2_0.1M_HCl_water_volume_stock_solution"
        ]
        iteration["volume_stock_solution3"] = EXPERIMENTAL_PARAMETERS[
            "pump3_co-solvents_volume_stock_solutions"
        ]
        iteration["volume_stock_solution4"] = EXPERIMENTAL_PARAMETERS[
            "pump4_0.1M_HCl_water_volume_stock_solution"
        ]


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
    
    print(f"There is {iteration['volume_stock_solution1']} in stock solution 1 before the experiment")
    print(f"There is {iteration['volume_stock_solution2']} in stock solution 2 before the experiment")
    print(f"There is {iteration['volume_stock_solution3']} in stock solution 3 before the experiment")
    print(f"There is {iteration['volume_stock_solution4']} in stock solution 4 before the experiment")
    
    if not state.SIMULATION_MODE:
        # Hardware mode: check volumes and raise exception if insufficient
        iteration["volume_stock_solution1"] = check_volume(
            iteration["volume_stock_solution1"],
            volume_pump1,
            EXPERIMENTAL_PARAMETERS["minimum_volume_required"],
            EXPERIMENTAL_PARAMETERS.get("name_of_stock_solution1", "Reactant"),
        )
        iteration["volume_stock_solution2"] = check_volume(
            iteration["volume_stock_solution2"],
            volume_pump2,
            EXPERIMENTAL_PARAMETERS["minimum_volume_required"],
            EXPERIMENTAL_PARAMETERS.get("name_of_stock_solution2", "Buffer"),
        )
        
        # Handle co-solvent volume - could be single value or list
        cosolvent_vol = iteration["volume_stock_solution3"]
        if isinstance(cosolvent_vol, list):
            # For multiple co-solvents, update the specific valve position
            valve_idx = int(cosolvent_valve_position) - 1  # 1-indexed to 0-indexed
            cosolvent_vol[valve_idx] = check_volume(
                cosolvent_vol[valve_idx],
                volume_pump3,
                EXPERIMENTAL_PARAMETERS["minimum_volume_required"],
                EXPERIMENTAL_PARAMETERS.get("name_of_co-solvent_stock_solutions", ["Co-solvent"])[valve_idx],
            )
            iteration["volume_stock_solution3"] = cosolvent_vol
        else:
            iteration["volume_stock_solution3"] = check_volume(
                cosolvent_vol,
                volume_pump3,
                EXPERIMENTAL_PARAMETERS["minimum_volume_required"],
                EXPERIMENTAL_PARAMETERS.get("name_of_stock_solution3", "Co-solvent"),
            )
        
        iteration["volume_stock_solution4"] = check_volume(
            iteration["volume_stock_solution4"],
            volume_pump4,
            EXPERIMENTAL_PARAMETERS["minimum_volume_required"],
            EXPERIMENTAL_PARAMETERS.get("name_of_stock_solution4", "Dilution Water"),
        )
    else:
        # Simulation mode: just subtract volumes
        iteration["volume_stock_solution1"] -= volume_pump1
        iteration["volume_stock_solution2"] -= volume_pump2
        
        # Handle co-solvent volume - could be single value or list
        cosolvent_vol = iteration["volume_stock_solution3"]
        if isinstance(cosolvent_vol, list):
            valve_idx = int(cosolvent_valve_position) - 1
            cosolvent_vol[valve_idx] -= volume_pump3
            iteration["volume_stock_solution3"] = cosolvent_vol
        else:
            iteration["volume_stock_solution3"] -= volume_pump3
        
        # Handle dilution pump volume
        pump4_vol = iteration["volume_stock_solution4"]
        if isinstance(pump4_vol, list):
            total_volume = sum(pump4_vol) - volume_pump4
            iteration["volume_stock_solution4"] = total_volume
        else:
            iteration["volume_stock_solution4"] -= volume_pump4
    
    print(f"There is {iteration['volume_stock_solution1']} in stock solution 1 after the experiment")
    print(f"There is {iteration['volume_stock_solution2']} in stock solution 2 after the experiment")
    print(f"There is {iteration['volume_stock_solution3']} in stock solution 3 after the experiment")
    print(f"There is {iteration['volume_stock_solution4']} in stock solution 4 after the experiment")
