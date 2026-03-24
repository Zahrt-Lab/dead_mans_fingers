# ------------------------------------------------------------------------------
# Software: project_dead_mans_fingers
# Copyright: (C) 2026 by Professor Andrew Zahrt
# This software is the intellectual property of Professor Andrew Zahrt
# Contributions by graduate students Scott Laverty and Joao are acknowledged.
# All rights reserved.
# ------------------------------------------------------------------------------

"""
Bayesian Optimization Iteration Execution Module.

This module orchestrates a complete BO iteration by:
1. Preparing the experiment (parameters, files, volume checks)
2. Running the experiment (hardware or simulation)
3. Analyzing results (UV-VIS processing, yield, throughput)
"""

import time
from typing import Tuple, Dict, Any
from pathlib import Path

from preprocessing.constrain_to_search_space import constrain_to_search_space
from preprocessing.standardize_input import standardize_input
from preprocessing.parameters_to_commands import parameters_to_commands
from utils.experiment_aborted import ExperimentAborted

from experimental_commands.generate_instrument_config import save_instrument_config_csv
from experimental_commands.commands import save_commands_csv, run_commands
from experimental_commands.experiment_runner import run_hardware_experiment
from post_processing.post_processing_results import analyze_experiment_results
from post_processing.append_bayesian_experimental_results import append_bayesian_experimental_results
from utils.run_simulation import run_simulated_experiment
from bayesian_optimizer.experiment_state import BoCampaignState, IterationState

def prepare_experiment(
    bo_campaign_state: BoCampaignState,
    iteration_state: IterationState
) -> Tuple[BoCampaignState, IterationState]:
    
    """
    Phase 1: Prepare the experiment by setting up parameters, files, and checking volumes.
    
    Args:
        bo_campaign_state: The current state of the BO campaign parameters
        iteration_state: The current state of the iteration parameters

    Returns:
        Tuple containing the updated BO campaign state and iteration state
    """
    
    # TODO : Need to evaluate this function, it should return 1000 but is set to 130, something is wring here
    print("Calculating reactor bed concentration in uM for this experiment")
    reactor_bed_concentration_uM = iteration_state.trial_conditions["dilution_factor"] \
        * bo_campaign_state.bo_parameters["xylopyridine_analogs_concentrations_uM"]
    
    iteration_state.update_reactor_bed_concentration_uM(reactor_bed_concentration_uM)

    
    # Set up directories and file paths for this BO campaign if it doesn't exist already
    base_directory = Path(bo_campaign_state.bo_parameters["base_directory"])
    base_directory.mkdir(parents=True, exist_ok=True)
    instrument_config = base_directory / Path("Instrument_Config_File.csv")
    command_path_base = base_directory / Path(f"Fluorescent_Optimization_Iteration_{iteration_state.iteration}")
        
    # Convert BO parameters to instrument parameters for the automated platform to perform 
    print("Calculating experimental parameters for this bayesian optimization search point")
    instrument_parameters = parameters_to_commands(
        bo_campaign_state,
        iteration_state
    )

    iteration_state.update_instrument_parameters(instrument_parameters)
    

    # TODO: This is supposed to check and update the volumes in the experimental state
    # Currently this is just a placeholder and commented out and needs to be developed
    '''
    try:
        # TODO: Need to evaluate the quality of this code here, likely not working
        bo_campaign_state.check_and_update_volumes(instrument_parameters, cosolvent_valve_position)
    except ExperimentAborted as e:
        print(f"[PAUSED] {e}. Safe to resume once stock is topped up.")
        # Recursively retry after user intervention
        return prepare_experiment(bo_campaign_state, iteration_state)
    
    # Create instrument config file if it doesn't exist
    if not instrument_config.exists():
        save_instrument_config_csv(instrument_config)
    '''
    # Generates the instrument config file for this experiment
    save_instrument_config_csv(instrument_config)

    # Save command CSVs for this iteration
    save_commands_csv(
        command_path_base,
        instrument_parameters["flow_rate_pump1"],
        instrument_parameters["flow_rate_pump2"],
        instrument_parameters["flow_rate_pump3"],
        instrument_parameters["flow_rate_pump4"],
        instrument_parameters["volume_pump1"],
        instrument_parameters["volume_pump2"],
        instrument_parameters["volume_pump3"],
        instrument_parameters["volume_pump4"],
        instrument_parameters["position_valve2"],
        instrument_parameters["temperature"],
        iteration_state.trial_conditions['co_solvent_dilution_factor'],
        instrument_parameters["light_intensity"],
    )

    # TODO : We should probably just set these in the state.py file instead of passing them as a dictionary
    #  around in the code,need to evaluate this
    # Return all prepared parameters
    return bo_campaign_state, iteration_state


def run_experiment(bo_campaign_state: BoCampaignState,
                   iteration_state: IterationState
                   ) -> Tuple[BoCampaignState, IterationState]:
    """
    Phase 2: Run the experiment (hardware or simulation mode).
    
    Parameters:
        bo_campaign_state: BO campaign state
        iteration_state: Current iteration state
    
    Returns:
        Tuple of updated bo campaign state and iteration state
    """
    bo_parameters = bo_campaign_state.bo_parameters
    trial_conditions = iteration_state.trial_conditions

    # Set temperature
    print(f"Setting temperature to {trial_conditions['temperature']} celsius")
 
    if not bo_campaign_state.simulation_mode:
        temperature_command_file = f"{bo_parameters['command_path_base']}_temperature.csv"
        run_commands(temperature_command_file, bo_parameters["instrument_config"])
        print("Finished setting temperature of the thermocouple")
    
    else:
        print("[SIMULATION] Skipping temperature commands - would run: _temperature.csv")

    # Set Light Intensity
    print(f"Setting light intensity to {trial_conditions['light_intensity']} %")
    
    if not bo_campaign_state.simulation_mode:
        light_intensity_command_file = f"{bo_parameters['command_path_base']}_light_intensity.csv"
        run_commands(light_intensity_command_file, bo_parameters["instrument_config"])
        print("Finished setting light intensity")
    
    else:
        print("[SIMULATION] Skipping light intensity commands - would run: _light_intensity.csv")   


    # Run experiment (hardware or simulation)
    if not bo_campaign_state.simulation_mode:
        csv_file_path = run_hardware_experiment(
            bo_parameters["command_path_base"],
            bo_parameters["instrument_config"],
            iteration_state.iteration,
        )

    # TODO : We should reevaluate this simulated experiment code, not urgent
    else:
        csv_file_path = run_simulated_experiment(
            trial_conditions["flow_rate"],
            trial_conditions["temperature"],
            trial_conditions["dilution_factor"],
            bo_parameters["total_volume_through_reactor_bed"],
            iteration_state.iteration,
            bo_parameters["reactant_wavelength"],
            bo_parameters["product_wavelength"],
            bo_parameters["base_directory"],
        )
    
    return csv_file_path


def analyze_and_save_results(bo_campaign_state: BoCampaignState,
                            iteration_state: IterationState, 
                             csv_file_path: str
                             ) -> Tuple[float, float]:
    """
    Phase 3: Analyze experiment results and save to CSV.
    
    Args:
        bo_experimental_parameters: Dictionary of prepared experiment parameters
        csv_file_path: Path to UV-VIS data CSV
    
    Returns:
        Tuple of (percent_yield, throughput_nmol_per_min)
    """
    bo_parameters = bo_campaign_state.bo_parameters
    trial_conditions = iteration_state.trial_conditions
    instrument_parameters = iteration_state.instrument_parameters
    
    print(f"Bayesian Optimization results saved to {csv_file_path}")
    
    # Analyze results
    (
        avg_abs_reactant,
        avg_abs_product,
        percent_yield,
        throughput,
    ) = analyze_experiment_results(
        bo_campaign_state,
        iteration_state,
        csv_file_path
    )
    
    # Save results to CSV
    append_bayesian_experimental_results(
        {
            "iteration": iteration_state.iteration,
            "flow_rate": trial_conditions["flow_rate"],
            "dilution_factor": trial_conditions["dilution_factor"],
            "reactor_concentration_uM": round(iteration_state.reactor_bed_concentration_uM, 2),
            "temperature": trial_conditions["temperature"],
            "co_solvent": trial_conditions["co_solvent_valve_position"],
            "co_solvent_volume": trial_conditions["co_solvent_dilution_factor"],
            "target_volume": bo_parameters["target_volume_through_reactor_bed"],
            "reactant_wavelength": bo_parameters["reactant_wavelength"],
            "product_wavelength": bo_parameters["product_wavelength"],
            "average_absorbance_reactant": avg_abs_reactant,
            "average_absorbance_product": avg_abs_product,
            "percent_yield": percent_yield,
            "throughput_nmol_per_min": throughput,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "status": "ok",
            "error_message": "",
        },
        bo_campaign_state
    )
    
    print(f"Finished appending the results to csv file: {bo_parameters['Fluorescent_Bayesian_Optimization_results_filename']}")
    
    return percent_yield, throughput


def run_bayesian_optimization_iteration(
    bo_campaign_state: BoCampaignState,
    iteration_state: IterationState
) -> Tuple[float, float]:
    """
    Execute a complete Bayesian optimization iteration.
    
    This is the main entry point that orchestrates:
    1. Parameter constraint and cache lookup
    2. Experiment preparation (Phase 1)
    3. Experiment execution (Phase 2) 
    4. Result analysis and storage (Phase 3)
    
    Args:
        experiment: Tuple of (flow_rate, dilution_factor, temperature,
                    cosolvent_position, cosolvent_fraction, light_intensity)
    
    Returns:
        Tuple of (percent_yield, product_throughput_nmol_per_min)
    """
    # Constrain and standardize parameters for cache lookup, all values should be float
    # and rounded to the 2nd decimal place
    constrained_params = constrain_to_search_space(bo_campaign_state, iteration_state)
    iteration_state = standardize_input(constrained_params)

    current_trial_conditions = tuple(value for key, value in iteration_state.trial_conditions.items())

    # Check results cache to avoid redundant experiments
    if current_trial_conditions in bo_campaign_state.results_cache:
        print(f"Experiment found in cache, returning previous results")
        return bo_campaign_state.results_cache[current_trial_conditions]

    # Phase 1: Prepare experiment (parameters, files, volume checks)
    bo_campaign_state, iteration_state = prepare_experiment(bo_campaign_state, iteration_state)
    
    # Phase 2: Run experiment (hardware or simulation)
    csv_file_path = run_experiment(bo_campaign_state, iteration_state)
    
    # Phase 3: Analyze results and save to CSV
    percent_yield, throughput = analyze_and_save_results(bo_campaign_state, iteration_state, csv_file_path)
    
    # Update cache with results - create cache key from standardized trial conditions
    iteration_state = standardize_input(iteration_state)
    cache_key = tuple(value for key, value in iteration_state.trial_conditions.items())
    bo_campaign_state.results_cache[cache_key] = (percent_yield, throughput)
    
    return bo_campaign_state.results_cache[cache_key]