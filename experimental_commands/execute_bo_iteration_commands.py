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
from typing import Tuple, Sequence, Dict, Any
from pathlib import Path

# TODO : I learned you can just import the state variables directly
# instead you need to import the whole state module and the access
# the variables with state.VARIABLE_NAME, this is because we need to
# update the global state variables and if we import them directly
# they will not update in the global state
# Should probably update the remaining variables in this code
from bayesian_optimizer.deterministic_commands import state
from bayesian_optimizer.deterministic_commands.state import (
    BO_EXPERIMENTAL_PARAMETERS,
    ITERATION,
    RESULTS_CACHE,
)
from bayesian_optimizer.deterministic_commands.volume_manager import (
    initialize_stock_volumes,
    check_and_update_volumes,
)

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


def prepare_experiment(
    experiment: Sequence[float],
) -> Dict[str, Any]:
    """
    Phase 1: Prepare the experiment by setting up parameters, files, and checking volumes.
    
    Args:
        experiment: Tuple of (flow_rate, dilution_factor, temperature, 
                    cosolvent_position, cosolvent_fraction, light_intensity)
    
    Returns:
        Dictionary containing all prepared experiment parameters and paths
    """
    # Constrain and standardize parameters
    (
        reactor_bed_flow_rate,
        dilution_factor,
        temperature,
        cosolvent_valve_position,
        fraction_of_cosolvent,
        light_intensity,
    ) = constrain_to_search_space(experiment)
    
    experiment_check = standardize_input(
        (
            reactor_bed_flow_rate,
            dilution_factor,
            temperature,
            cosolvent_valve_position,
            fraction_of_cosolvent,
            light_intensity,
        )
    )
    
    # Updates the experimental parameter for this BO campaign in the global state
    ITERATION["iteration #"] += 1
    k = ITERATION["iteration #"]
    
    # Calculate reactor bed concentration
    # Get the stock concentration - it's a list, use first element for single analog experiments
    # TODO : Need to evaluate this function, it should return 1000 but is set to 130, something is wring here
    print("Calculating reactor bed concentration in uM for this experiment")
    print(BO_EXPERIMENTAL_PARAMETERS["xylopyridine_analogs_concentrations_uM"])
    reactor_bed_concentration_uM = dilution_factor * BO_EXPERIMENTAL_PARAMETERS["xylopyridine_analogs_concentrations_uM"]
    
    print(
        f"Beginning experiment {k} with flow rate: {reactor_bed_flow_rate} uL/min; "
        f"concentration: {reactor_bed_concentration_uM} uM; "
        f"temperature= {temperature} °C; "
        f"co-solvent valve position= {cosolvent_valve_position}; "
        f"co-solvent fraction= {fraction_of_cosolvent}; "
        f"light intensity= {light_intensity} %"
    )
    
    # Set up directories and file paths for this BO campaign if it doesn't exist already
    base_directory = Path(BO_EXPERIMENTAL_PARAMETERS["base_directory"])
    base_directory.mkdir(parents=True, exist_ok=True)
    instrument_config = base_directory / "Instrument_Config_File.csv"
    command_path_base = base_directory / f"Fluorescent_Optimization_Iteration_{k}"
    
    print(f"The base directory is {base_directory}")
    print(f"The instrument config file is {instrument_config}")
    print(f"The fluorescent reaction command template is {command_path_base}")
    print(f"The fluorescent reaction bayesian optimization results saved to " \
          f"{BO_EXPERIMENTAL_PARAMETERS['Fluorescent_Bayesian_Optimization_results_filename']}")
    
    # Volume to flow through the reactor bed
    volume = int(round(BO_EXPERIMENTAL_PARAMETERS["total_volume_through_reactor_bed"], 0))
    
    # Convert BO parameters to instrument parameters for the automated platform to perform 
    print("Calculating experimental parameters for this bayesian optimization search point")
    instrument_parameters = parameters_to_commands(
        flow_rate_uL_per_min=reactor_bed_flow_rate,
        dilution_factor=dilution_factor,
        cosolvent_valve_position=int(cosolvent_valve_position),
        cosolvent_fraction=fraction_of_cosolvent,
        light_intensity=light_intensity,
        xylopyridine_analogs_concentrations_uM=BO_EXPERIMENTAL_PARAMETERS["xylopyridine_analogs_concentrations_uM"],
        target_absorbance_in_the_uv_detector=BO_EXPERIMENTAL_PARAMETERS["target_absorbance_in_the_uv_detector"],
        max_absorbance_concentration_uM_uv_detector=BO_EXPERIMENTAL_PARAMETERS["max_absorbance_concentration_uM_uv_detector"],
        volume_uL=volume,
    )
    
    # Extract pump parameters
    flow_rate_pump1 = instrument_parameters["flow_rate_pump1"]
    volume_pump1 = instrument_parameters["volume_pump1"]
    flow_rate_pump2 = instrument_parameters["flow_rate_pump2"]
    volume_pump2 = instrument_parameters["volume_pump2"]
    flow_rate_pump3 = instrument_parameters["flow_rate_pump3"]
    volume_pump3 = instrument_parameters["volume_pump3"]
    flow_rate_pump4 = instrument_parameters["flow_rate_pump4"]
    volume_pump4 = instrument_parameters["volume_pump4"]
    cosolvent_valve_position = instrument_parameters["position_valve1"]
    
    print("Completed calculating parameters for experimental equipment")
    print(f"The flow rate of pump 1 is {flow_rate_pump1}")
    print(f"The flow rate of pump 2 is {flow_rate_pump2}")
    print(f"The flow rate of pump 3 is {flow_rate_pump3}")
    print(f"The flow rate of pump 4 is {flow_rate_pump4}")
    print(f"The flow rate in the reactor bed is {flow_rate_pump1 + flow_rate_pump2 + flow_rate_pump3}")
    print(f"The flow rate of the cuvette is {flow_rate_pump1 + flow_rate_pump2 + flow_rate_pump3 + flow_rate_pump4}")
    
    # TODO : Need to evaluate the quality of this code to make sure it is robust and handles all edge cases.'
    # Initialize volumes on first iteration
    initialize_stock_volumes()
    
    # Check and update stock solution volumes
    try:
        # TODO: Need to evaluate the quality of this code here
        check_and_update_volumes(instrument_parameters, cosolvent_valve_position)
    except ExperimentAborted as e:
        print(f"[PAUSED] {e}. Safe to resume once stock is topped up.")
        # Recursively retry after user intervention
        return prepare_experiment(experiment)
    
    # Create instrument config file if it doesn't exist
    if not instrument_config.exists():
        save_instrument_config_csv(instrument_config)
    
    # Save command CSVs for this iteration
    save_commands_csv(
        command_path_base,
        flow_rate_pump1,
        flow_rate_pump2,
        flow_rate_pump3,
        flow_rate_pump4,
        volume_pump1,
        volume_pump2,
        volume_pump3,
        volume_pump4,
        cosolvent_valve_position,
        temperature,
        fraction_of_cosolvent,
        light_intensity,
    )

    # TODO : We should probably just set these in the state.py file instead of passing them as a dictionary
    #  around in the code,need to evaluate this
    # Return all prepared parameters
    return {
        "experiment_check": experiment_check,
        "iteration_number": k,
        "reactor_bed_flow_rate": reactor_bed_flow_rate,
        "dilution_factor": dilution_factor,
        "temperature": temperature,
        "cosolvent_valve_position": cosolvent_valve_position,
        "fraction_of_cosolvent": fraction_of_cosolvent,
        "light_intensity": light_intensity,
        "reactor_bed_concentration_uM": reactor_bed_concentration_uM,
        "base_directory": base_directory,
        "instrument_config": instrument_config,
        "command_path_base": command_path_base,
        "results_csv": BO_EXPERIMENTAL_PARAMETERS["Fluorescent_Bayesian_Optimization_results_filename"],
        "volume": volume,
        "flow_rate_pump1": flow_rate_pump1,
        "flow_rate_pump2": flow_rate_pump2,
        "flow_rate_pump3": flow_rate_pump3,
        "flow_rate_pump4": flow_rate_pump4,
        "volume_pump1": volume_pump1,
        "volume_pump2": volume_pump2,
        "volume_pump3": volume_pump3,
        "volume_pump4": volume_pump4,
    }


def run_experiment(experimental_parameters: Dict[str, Any]) -> str:
    """
    Phase 2: Run the experiment (hardware or simulation mode).
    
    Args:
        experimental_parameters: Dictionary of prepared experiment parameters
    
    Returns:
        Path to the CSV file containing UV-VIS data
    """
    # Set temperature
    print(f"Setting temperature to {experimental_parameters['temperature']} celsius")
    print(experimental_parameters)
    print("Is the simulation mode on? " + str(state.SIMULATION_MODE))
    if not state.SIMULATION_MODE:
        temperature_command_file = f"{experimental_parameters['command_path_base']}_temperature.csv"
        run_commands(temperature_command_file, experimental_parameters["instrument_config"])
        print("Finished setting temperature of the thermocouple")
    else:
        print("[SIMULATION] Skipping temperature commands - would run: _temperature.csv")

    # Set Light Intensity
    print(f"Setting light intensity to {experimental_parameters['light_intensity']} %")
    if not state.SIMULATION_MODE:
        light_intensity_command_file = f"{experimental_parameters['command_path_base']}_light_intensity.csv"
        run_commands(light_intensity_command_file, experimental_parameters["instrument_config"])
        print("Finished setting light intensity")
    else:
        print("[SIMULATION] Skipping light intensity commands - would run: _light_intensity.csv")   

    # Get wavelengths from experimental parameters
    reactant_wavelength = BO_EXPERIMENTAL_PARAMETERS["reactant_wavelength"]
    product_wavelength = BO_EXPERIMENTAL_PARAMETERS["product_wavelength"]
    
    print(f"Reactant wavelength set to {reactant_wavelength}")
    print(f"Product wavelength set to {product_wavelength}")
    
    # Run experiment (hardware or simulation)
    if not state.SIMULATION_MODE:
        csv_file_path = run_hardware_experiment(
            experimental_parameters["command_path_base"],
            experimental_parameters["instrument_config"],
            experimental_parameters["iteration_number"],
        )
    else:
        csv_file_path = run_simulated_experiment(
            experimental_parameters["reactor_bed_flow_rate"],
            experimental_parameters["temperature"],
            experimental_parameters["dilution_factor"],
            experimental_parameters["volume"],
            experimental_parameters["iteration_number"],
            reactant_wavelength,
            product_wavelength,
            experimental_parameters["base_directory"],
        )
    
    return csv_file_path


def analyze_and_save_results(bo_experimental_parameters: Dict[str, Any], 
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
    # Calculate reactor bed target volume (volume before steady state recording)
    reactor_bed_target_volume = bo_experimental_parameters["volume"]
    print(f"Reactor bed target volume to reach before recording is {reactor_bed_target_volume}")
    
    # Get wavelengths
    reactant_wavelength = state.BO_EXPERIMENTAL_PARAMETERS["reactant_wavelength"]
    product_wavelength = state.BO_EXPERIMENTAL_PARAMETERS["product_wavelength"]
    
    print(f"Bayesian Optimization results saved to {csv_file_path}")
    
    # Analyze results
    (
        avg_abs_reactant,
        avg_abs_product,
        percent_yield,
        throughput,
    ) = analyze_experiment_results(
        csv_file_path,
        ITERATION["converged_early"],
        bo_experimental_parameters["reactor_bed_flow_rate"],
        reactor_bed_target_volume,
        bo_experimental_parameters["reactor_bed_concentration_uM"],
        reactant_wavelength,
        product_wavelength,
        bo_experimental_parameters["flow_rate_pump1"],
        bo_experimental_parameters["flow_rate_pump2"],
        bo_experimental_parameters["flow_rate_pump3"],
        bo_experimental_parameters["flow_rate_pump4"],
    )
    
    # Save results to CSV
    append_bayesian_experimental_results(
        bo_experimental_parameters["results_csv"],
        {
            "iteration": bo_experimental_parameters["iteration_number"],
            "flow_rate": bo_experimental_parameters["experiment_check"][0],
            "dilution_factor": bo_experimental_parameters["experiment_check"][1],
            "reactor_concentration_uM": round(bo_experimental_parameters["reactor_bed_concentration_uM"], 8),
            "temperature": bo_experimental_parameters["experiment_check"][2],
            "co_solvent": bo_experimental_parameters["experiment_check"][3],
            "co_solvent_volume": bo_experimental_parameters["experiment_check"][4],
            "target_volume": reactor_bed_target_volume,
            "reactant_wavelength": reactant_wavelength,
            "product_wavelength": product_wavelength,
            "average_absorbance_reactant": avg_abs_reactant,
            "average_absorbance_product": avg_abs_product,
            "percent_yield": percent_yield,
            "throughput_nmol_per_min": throughput,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "status": "ok",
            "error_message": "",
        },
    )
    
    print(f"Finished appending the results to csv file: {bo_experimental_parameters['results_csv']}")
    
    return percent_yield, throughput


def run_bayesian_optimization_iteration(
    experiment: Sequence[float],
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
    constrained_params = constrain_to_search_space(experiment)
    experiment_check = standardize_input(constrained_params)
    
    # Check cache first - if experiment was done previously, return cached results
    if experiment_check in RESULTS_CACHE:
        print(f"Experiment found in cache, returning previous results")
        return RESULTS_CACHE[experiment_check]
    
    # Phase 1: Prepare experiment (parameters, files, volume checks)
    prepared_params = prepare_experiment(experiment)
    
    # Phase 2: Run experiment (hardware or simulation)
    csv_file_path = run_experiment(prepared_params)
    
    # Phase 3: Analyze results and save to CSV
    percent_yield, throughput = analyze_and_save_results(prepared_params, csv_file_path)
    
    # Update cache with results
    experiment_check = prepared_params["experiment_check"]
    RESULTS_CACHE[experiment_check] = (percent_yield, throughput)
    
    return RESULTS_CACHE[experiment_check]
