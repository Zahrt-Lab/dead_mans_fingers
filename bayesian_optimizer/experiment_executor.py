# ------------------------------------------------------------------------------
# Software: project_dead_mans_fingers
# Copyright: (C) 2025 by Professor Andrew Zahrt
# This software is the intellectual property of Professor Andrew Zahrt
# Contributions by graduate students Scott Laverty are acknowledged.
# All rights reserved.
# ------------------------------------------------------------------------------

"""
Single Experiment Executor for Bayesian Optimization.

This module orchestrates ONE iteration/experiment of the Bayesian optimization campaign.
It coordinates parameter processing, command generation, experiment execution (simulated or hardware),
UV-Vis data post-processing, and calculation of optimization objectives (yield & throughput).

Supports both simulated data and real AutoZahrt hardware with real-time monitoring.

The main function run_bayesian_optimization_iteration() delegates to specialized modules:
- experiment_setup: Parameter validation and file/directory setup
- volume_manager: Stock solution volume tracking and validation
- experiment_runner: Command execution and hardware control
- results_processor: Post-processing and result calculation
"""

from typing import Tuple, Sequence
from bayesian_optimizer import state
from bayesian_optimizer.state import EXPERIMENTAL_PARAMETERS, iteration, RESULTS_CACHE
from preprocessing.experimental_parameters import ExperimentAborted

# Import the new modular components
from bayesian_optimizer.experiment_setup import setup_experiment_parameters, setup_directories_and_paths
from bayesian_optimizer.volume_manager import initialize_stock_volumes, check_and_update_volumes
from bayesian_optimizer.experiment_runner import prepare_command_files, run_experiment
from bayesian_optimizer.results_processor import process_results, save_results_to_csv, update_cache

def run_bayesian_optimization_iteration(
    experiment: Sequence[float],
) -> Tuple[float, float]:
    """
    Execute one iteration of the Bayesian optimization campaign.
    
    This orchestrator function delegates to specialized modules:
    1. Setup: Constrain parameters, standardize, and prepare directories
    2. Volume Management: Initialize and check stock solution volumes
    3. Execution: Generate commands and run experiment (hardware or simulation)
    4. Processing: Post-process data and calculate objectives
    5. Caching: Store results for future lookups
    
    Args:
        experiment: Tuple containing (flow_rate, dilution_factor, temperature,
                    cosolvent_valve_position, fraction_of_cosolvent, light_intensity)
    
    Returns:
        Tuple of (percent_yield, throughput_nmol_per_min)
    """
    # Step 1: Setup experiment parameters
    exp_params = setup_experiment_parameters(experiment)
    
    # Check cache before running experiment
    if exp_params["experiment_check"] in RESULTS_CACHE:
        return RESULTS_CACHE[exp_params["experiment_check"]]
    
    # Increment iteration counter
    iteration["iteration #"] += 1
    k = iteration["iteration #"]
    
    print(f"Beginning experiment {k} with flow rate: {exp_params['reactor_bed_flow_rate']} uL/min; "
          f"concentration: {exp_params['reactor_bed_concentration_uM']} uM; "
          f"temperature= {exp_params['temperature']} °C;")
    
    # Step 2: Setup directories and paths
    print("Setting up directories and file paths for this experiment")
    paths = setup_directories_and_paths(k)
    
    # Step 3: Calculate and display flow rates
    instrument_params = exp_params["instrument_parameter"]
    print("Completed calculating parameters for experimental equipment")
    print(f"The flow rate of pump 1 is {instrument_params['flow_rate_pump1']}")
    print(f"The flow rate of pump 2 is {instrument_params['flow_rate_pump2']}")
    print(f"The flow rate of pump 3 is {instrument_params['flow_rate_pump3']}")
    print(f"The flow rate of pump 4 is {instrument_params['flow_rate_pump4']}")
    print(f"The flow rate in the reactor bed is "
          f"{instrument_params['flow_rate_pump1'] + instrument_params['flow_rate_pump2'] + instrument_params['flow_rate_pump3']}")
    print(f"The flow rate of the cuvette is "
          f"{instrument_params['flow_rate_pump1'] + instrument_params['flow_rate_pump2'] + instrument_params['flow_rate_pump3'] + instrument_params['flow_rate_pump4']}")
    
    # Step 4: Initialize and check volumes
    initialize_stock_volumes()
    
    try:
        check_and_update_volumes(instrument_params, exp_params["cosolvent_valve_position"])
    except ExperimentAborted as e:
        print(f"[PAUSED] {e}. Safe to resume once stock is topped up.")
        # Recursively retry after user tops up stock
        return run_bayesian_optimization_iteration(experiment)
    
    # Step 5: Prepare command files
    print("Calculating experimental parameters for this bayesian optimization search point")
    prepare_command_files(
        paths["command_path_template"],
        paths["instrument_config"],
        instrument_params,
        exp_params["temperature"]
    )
    
    # Step 6: Run experiment (hardware or simulation)
    print(f"Bayesian Optimization results will be appended to {paths['results_csv']}")
    
    # Add experiment context to exp_params for runner and processor
    exp_params["base_directory"] = paths["base_directory"]
    
    simulation_result = run_experiment(
        paths["command_path_template"],
        paths["instrument_config"],
        exp_params,
        k,
        paths["results_csv"]
    )
    
    # Step 7: Process results
    if simulation_result is not None:
        # Simulation mode returns results directly
        percent_yield, throughput = simulation_result
        print("Skipping post-processing in simulation mode (data already calculated)")
    else:
        # Hardware mode requires post-processing
        percent_yield, throughput = process_results(
            exp_params,
            k,
            paths["reactor_bed_target_volume"],
            paths["results_csv"]
        )
        
        # Save results to CSV (simulation already saved during run_simulation)
        save_results_to_csv(
            paths["results_csv"],
            exp_params,
            k,
            paths["reactor_bed_target_volume"],
            percent_yield,
            throughput
        )
    
    # Step 8: Update cache and return
    update_cache(exp_params["experiment_check"], percent_yield, throughput)
    return percent_yield, throughput

def objective_function_percent_yield(
    experiment: Tuple[float, float, float, float, float],
) -> float:
    """Objective function for percent yield."""
    percent_yield, _ = run_bayesian_optimization_iteration(experiment)
    return percent_yield


def objective_function_throughput(experiment: Tuple[float, float, float, float, float]) -> float:
    """Objective function for throughput."""
    _, throughput = run_bayesian_optimization_iteration(experiment)
    return throughput


    

    
    
    

