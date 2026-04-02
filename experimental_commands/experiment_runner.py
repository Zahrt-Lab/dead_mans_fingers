# ------------------------------------------------------------------------------
# Software: project_dead_mans_fingers
# Copyright: (C) 2026 by Professor Andrew Zahrt
# This software is the intellectual property of Professor Andrew Zahrt
# Contributions by graduate students Scott Laverty and Joao are acknowledged.
# All rights reserved.
# ------------------------------------------------------------------------------

"""
Experiment Runner Module for Hardware Control.

This module handles the execution of the hardware experiments,
to run one bayesian optimization iteration.
"""

from pathlib import Path
from experimental_commands.commands import run_commands

def run_hardware_experiment(
    command_path_base: Path,
    instrument_config: Path,
    iteration_number: int,
) -> None:
    """
    Run the physical hardware experiment with UV-VIS detection.
    
    Parameters:
        command_path_base: Base path for command files
        instrument_config: Path to instrument configuration CSV
        iteration_number: Current BO iteration number

    Returns:
        None
    """
    
    try:
        print("Beginning setting temperature for the experiment")
        temperature_command_file = f"{command_path_base}_temperature.csv"
        run_commands(temperature_command_file, instrument_config)
        print("Finished setting temperature for the experiment")

        print("Set light intensity for the experiment")
        light_intensity_command_file = f"{command_path_base}_light_intensity.csv"
        run_commands(light_intensity_command_file, instrument_config)

        print("Beginning flowing our compound through the reactor bed recording the product")
        experiment_command_file = f"{command_path_base}_experiment.csv"
        run_commands(experiment_command_file, instrument_config)
    except Exception as e:
        print(
            f"[HARDWARE ERROR] Instrument failure during experiment iteration {iteration_number}: {e}\n"
            "Check all instrument COM port connections and power before retrying."
        )
        raise
    finally:
        print(f"Experiment completing, UV recording for {iteration_number} is turned off")
        
        print("Run the experimental commands to wash the UV-detector to clear it out")
        wash_command_file = f"{command_path_base}_wash.csv"
        run_commands(wash_command_file, instrument_config)