# ------------------------------------------------------------------------------
# Software: project_dead_mans_fingers
# Copyright: (C) 2025 by Professor Andrew Zahrt
# This software is the intellectual property of Professor Andrew Zahrt
# Contributions by graduate students Scott Laverty and Joao are acknowledged.
# All rights reserved.
# ------------------------------------------------------------------------------

"""
Experiment Runner Module for Bayesian Optimization.

This module handles the execution of experimental commands, including temperature control,
washing, and UV-Vis measurement for both hardware and simulation modes.
"""

import os
from pathlib import Path
from typing import Dict, Any, Tuple, Optional
from bayesian_optimizer.deterministic_commands import state
from bayesian_optimizer.deterministic_commands.state import BO_EXPERIMENTAL_PARAMETERS
from experimental_commands.commands import save_commands_csv, run_commands
from experimental_commands.generate_instrument_config import save_instrument_config_csv
from utils.run_simulation import run_simulation
from post_processing.append_bayesian_experimental_results import append_bayesian_experimental_results

def prepare_command_files(command_path_template: Path, instrument_config: Path,
                          instrument_params: Dict[str, float], temperature: float) -> None:
    """
    Generate and save command CSV files for the experiment.
    
    Args:
        command_path_template: Base path for command files (without extension)
        instrument_config: Path to instrument configuration file
        instrument_params: Dictionary with flow rates, volumes, and valve positions
        temperature: Reaction temperature in celsius
    """
    # Create instrument config if it doesn't exist
    if not os.path.exists(instrument_config):
        save_instrument_config_csv(instrument_config)
    
    # Save command files for temperature, wash, and experiment
    save_commands_csv(
        command_path_template,
        instrument_params["flow_rate_pump1"],
        instrument_params["flow_rate_pump2"],
        instrument_params["flow_rate_pump3"],
        instrument_params["flow_rate_pump4"],
        instrument_params["volume_pump1"],
        instrument_params["volume_pump2"],
        instrument_params["volume_pump3"],
        instrument_params["volume_pump4"],
        instrument_params["position_valve1"],
        temperature,
        instrument_params.get("fraction_of_cosolvent", 0),
        instrument_params.get("light_intensity", 0),
    )


def run_experiment(command_path_template: Path, instrument_config: Path,
                   experiment_params: Dict[str, Any], iteration_num: int,
                   results_csv: Path) -> Optional[Tuple[float, float]]:
    """
    Execute the experimental workflow (temperature, wash, measurement).
    
    In hardware mode: runs physical commands and UV-Vis measurement.
    In simulation mode: generates simulated data and returns results immediately.
    
    Args:
        command_path_template: Base path for command files
        instrument_config: Path to instrument configuration file
        experiment_params: Dict containing all experiment parameters
        iteration_num: Current iteration number
        results_csv: Path to results CSV file
    
    Returns:
        In simulation mode: (percent_yield, throughput) tuple
        In hardware mode: None (post-processing happens later)
    """
    temperature = experiment_params["temperature"]
    reactant_wavelength = BO_EXPERIMENTAL_PARAMETERS["reactant_wavelength"]
    product_wavelength = BO_EXPERIMENTAL_PARAMETERS["product_wavelength"]
    
    # Set temperature
    print(f"Setting temperature to {temperature} celsius")
    if not state.SIMULATION_MODE:
        run_commands(f"{command_path_template}_temperature.csv", instrument_config)
        print("Finished setting temperature of the thermocouple")
    else:
        print("Skipping hardware temperature commands (simulation mode)")
    
    # Run wash commands
    print("Running experimental wash commands to clear out the UV-detector")
    if not state.SIMULATION_MODE:
        run_commands(f"{command_path_template}_wash.csv", instrument_config)
    else:
        print("Skipping hardware wash commands (simulation mode)")
    
    print(f"Reactant wavelength set to {reactant_wavelength}")
    print(f"Product wavelength set to {product_wavelength}")
    print(f"Beginning UV recording at reactant wavelength {reactant_wavelength} "
          f"and product wavelength {product_wavelength}")
    
    if not state.SIMULATION_MODE:
        # Hardware mode: run real experiment
        print("Running experiment on experimental hardware")
        uv_vis_detection_object = begin_uv_vis_measurement(
            experiment_params["base_directory"], 
            iteration_num, 
            target_wavelengths=(reactant_wavelength, product_wavelength)
        )
        try:
            print("Beginning flowing our compound through the reactor bed recording the product")
            run_commands(f"{command_path_template}_experiment.csv", instrument_config)
        finally:
            print(f"Experiment completing, turning off UV recordings for iteration {iteration_num}")
            end_uv_vis_measurement(uv_vis_detection_object)
        
        return None  # Post-processing happens in results_processor
    
    else:
        # Simulation mode: generate simulated data
        print("Running experiment in simulation mode")
        instrument_params = experiment_params["instrument_parameter"]
        
        percent_yield_sim, throughput_sim = run_simulation(
            flow_rate=experiment_params["reactor_bed_flow_rate"],
            concentration=experiment_params["dilution_factor"],
            temperature=temperature,
            co_solvent=experiment_params["cosolvent_valve_position"],
            co_solvent_volume=experiment_params["fraction_of_cosolvent"],
            reactor_concentration_uM=experiment_params["reactor_bed_concentration_uM"],
            iteration_num=iteration_num,
            experimental_parameters=BO_EXPERIMENTAL_PARAMETERS,
            csv_path=results_csv,
            append_results_func=append_bayesian_experimental_results,
            volume_pump1=instrument_params["volume_pump1"],
            volume_pump2=instrument_params["volume_pump2"],
            volume_pump3=instrument_params["volume_pump3"],
            flow_rate_pump1=instrument_params["flow_rate_pump1"],
        )
        print(f"Simulation complete: {percent_yield_sim:.2f}% yield, {throughput_sim:.2f} nmol/min")
        
        return percent_yield_sim, throughput_sim
