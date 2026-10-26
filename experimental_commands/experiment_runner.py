# ------------------------------------------------------------------------------
# Software: dead_mans_fingers
# Copyright (c) 2026 Zahrt Research Group
#
# Contributions by Scott Laverty are acknowledged.
#
# Licensed under the MIT License. See the LICENSE file in the repository root.
# ------------------------------------------------------------------------------
"""
Experiment Runner Module for Hardware Control.

This module handles the execution of the hardware experiments,
to run one bayesian optimization iteration.
"""

from pathlib import Path
import time
from experimental_commands.commands import run_commands
from utils.retrieve_latest_experimental_run import get_latest_experimental_run_csv

def run_hardware_experiment(
    command_path_base: Path,
    instrument_config: Path,
    output_dir: str,
    iteration_number: int,
) -> str:
    """
    Run the physical hardware experiment with UV-VIS detection.

    Parameters:
        command_path_base: Base path for command files
        instrument_config: Path to instrument configuration CSV
        output_dir: Directory where AutoZahrt writes its timestamped experimental log folders
        iteration_number: Current BO iteration number

    Returns:
        str: Path to the UV-VIS data CSV written by AutoZahrt
    """
    iteration_start_mtime = time.time()

    try:
        
        print("Run the experimental commands to wash the UV-detector to clear it out")
        wash_command_file = f"{command_path_base}_wash.csv"
        run_commands(wash_command_file, instrument_config, output_dir=output_dir)
        

        print("Beginning setting temperature for the experiment")
        temperature_command_file = f"{command_path_base}_temperature.csv"
        run_commands(temperature_command_file, instrument_config, output_dir=output_dir)
        print("Finished setting temperature for the experiment")

        print("Set light intensity for the experiment")
        light_intensity_command_file = f"{command_path_base}_light_intensity.csv"
        run_commands(light_intensity_command_file, instrument_config, output_dir=output_dir)

        print("Beginning flowing our compound through the reactor bed recording the product")
        experiment_command_file = f"{command_path_base}_experiment.csv"
        run_commands(experiment_command_file, instrument_config, output_dir=output_dir)
    except Exception as e:
        print(
            f"[HARDWARE ERROR] Instrument failure during experiment iteration {iteration_number}: {e}\n"
            "Check all instrument COM port connections and power before retrying."
        )
        raise

    csv_file_path = get_latest_experimental_run_csv(
        Path(output_dir),
        min_mtime=max(0.0, iteration_start_mtime - 2.0),
        timeout_seconds=30.0,
    )
    print(f"Completed hardware experiment run, returning path to UV-VIS data CSV: {csv_file_path}")
    return csv_file_path
        
