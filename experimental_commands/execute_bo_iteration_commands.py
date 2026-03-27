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
from typing import Tuple
from pathlib import Path

from preprocessing.constrain_to_search_space import constrain_to_search_space
from preprocessing.standardize_input import standardize_input
from preprocessing.parameters_to_commands import parameters_to_commands

from experimental_commands.generate_instrument_config import save_instrument_config_csv
from experimental_commands.commands import save_commands_csv
from experimental_commands.experiment_runner import run_hardware_experiment
from post_processing.post_processing_results import analyze_experiment_results
from post_processing.append_bayesian_experimental_results import append_bayesian_experimental_results
from utils.run_simulation import run_simulated_experiment
from bayesian_optimizer.experiment_state import BoCampaignState, IterationState

# TODO : This code is considered a god function and should be refactore

def run_experiment(bo_campaign_state: BoCampaignState,
                   iteration_state: IterationState
                   ) -> str:
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


def run_bayesian_optimization_iteration(
    bo_campaign_state: BoCampaignState,
    iteration_state: IterationState
) -> Tuple[float, float]:
    """
    Execute a complete Bayesian optimization iteration.

    Orchestrates parameter constraint and cache lookup, experiment preparation,
    execution (hardware or simulation), and result analysis and storage.

    Args:
        bo_campaign_state: Current BO campaign state
        iteration_state: Current iteration state with trial conditions

    Returns:
        Tuple of (percent_yield, product_throughput_nmol_per_min)
    """
    # Constrain and standardize parameters; all values rounded to 2 decimal places
    constrained_params = constrain_to_search_space(bo_campaign_state, iteration_state)
    iteration_state = standardize_input(constrained_params)

    current_trial_conditions = tuple(value for key, value in iteration_state.trial_conditions.items())

    # Check results cache to avoid redundant experiments
    if current_trial_conditions in bo_campaign_state.results_cache:
        print("Experiment found in cache, returning previous results")
        return bo_campaign_state.results_cache[current_trial_conditions]

    # Phase 1: Prepare experiment (parameters, files, volume checks)
    # Reactor bed concentration = stock_conc × dilution_factor.
    # e.g. dilution_factor=0.13, stock=1000 uM → 130 uM in reactor bed. This is correct.
    print("Calculating reactor bed concentration in uM for this experiment")
    reactor_bed_concentration_uM = (
        iteration_state.trial_conditions["dilution_factor"]
        * bo_campaign_state.bo_parameters["xylopyridine_analogs_concentrations_uM"]
    )
    iteration_state.update_reactor_bed_concentration_uM(reactor_bed_concentration_uM)

    base_directory = Path(bo_campaign_state.bo_parameters["base_directory"])
    base_directory.mkdir(parents=True, exist_ok=True)
    instrument_config = base_directory / Path("Instrument_Config_File.csv")
    command_path_base = base_directory / Path(f"Fluorescent_Optimization_Iteration_{iteration_state.iteration}")

    print("Calculating experimental parameters for this bayesian optimization search point")
    instrument_parameters = parameters_to_commands(
        iteration_state.trial_conditions,
        bo_campaign_state.bo_parameters["total_volume_through_reactor_bed"],
        bo_campaign_state.bo_parameters["xylopyridine_analogs_concentrations_uM"],
        bo_campaign_state.bo_parameters["max_absorbance_concentration_uM_uv_detector"],
        bo_campaign_state.bo_parameters["target_absorbance_in_the_uv_detector"],
    )
    iteration_state.update_instrument_parameters(instrument_parameters)

    save_instrument_config_csv(instrument_config)
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
        iteration_state.trial_conditions["co_solvent_dilution_factor"],
        instrument_parameters["light_intensity"],
    )

    # Phase 2: Run experiment (hardware or simulation)
    csv_file_path = run_experiment(bo_campaign_state, iteration_state)

    # Phase 3: Analyze results and save to CSV
    bo_parameters = bo_campaign_state.bo_parameters
    trial_conditions = iteration_state.trial_conditions

    print(f"Bayesian Optimization results saved to {csv_file_path}")
    avg_abs_reactant, avg_abs_product, percent_yield, throughput = analyze_experiment_results(
        bo_campaign_state, iteration_state, csv_file_path
    )

    append_bayesian_experimental_results(
        {
            "iteration": iteration_state.iteration,
            "flow_rate": trial_conditions["flow_rate"],
            "dilution_factor": trial_conditions["dilution_factor"],
            "reactor_concentration_uM": round(iteration_state.reactor_bed_concentration_uM, 2),
            "temperature": trial_conditions["temperature"],
            "co_solvent": trial_conditions["co_solvent_valve_position"],
            "co_solvent_volume": trial_conditions["co_solvent_dilution_factor"],
            "light_intensity": trial_conditions["light_intensity"],
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
        bo_campaign_state,
    )

    print(f"Finished appending the results to csv file: {bo_parameters['Fluorescent_Bayesian_Optimization_results_filename']}")

    # Cache result
    iteration_state = standardize_input(iteration_state)
    cache_key = tuple(value for key, value in iteration_state.trial_conditions.items())
    bo_campaign_state.results_cache[cache_key] = (percent_yield, throughput)

    return bo_campaign_state.results_cache[cache_key]