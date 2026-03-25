# ------------------------------------------------------------------------------
# Software: project_dead_mans_fingers
# Copyright: (C) 2025 by Professor Andrew Zahrt
# This software is the intellectual property of Professor Andrew Zahrt
# Contributions by graduate students Scott Laverty and Joao are acknowledged.
# All rights reserved.
# ------------------------------------------------------------------------------

"""
This script runs the Bayesian Optimization campaign for our experiment per
each individual xylopyridine analog.
"""

# bayesian_optimizer/run_bo_campaign.py
from __future__ import annotations

from bayesian_optimizer.experiment_state import BoCampaignState, IterationState
from bayesian_optimizer.init_or_load_ax import _init_or_load_ax
from bayesian_optimizer.ax_suggested_experiment import ax_suggested_experiment

from preprocessing.experimental_parameters import (
    load_experimental_parameters,
    check_required_bo_campaign_parameters,
)


def run_bo_campaign(
    input_experimental_parameters: dict,
    ax_previous_run_json_file_path: str,
    percent_yield_threshold: float,
    throughput_threshold: float,
    noise_sem: float,
    simulation_mode: bool = True,
    xylopyridine_analog: str = "",
) -> None:
    """
    This script runs the Bayesian Optimization campaign for our experiment per
    each xylopyridine analog.
    It will
     1) Load the experimental parameters.
     2) Initialize or loads Ax state from a previous run if it exists.
     3) Run the optimization loop.
     4) On exit, it will print the Pareto optimal parameter sets.


    Parameters:
     - input_experimental_parameters: Dictionary containing experimental parameters
       parameters (flow rate bounds, temperature bounds, etc.)
     - ax_previous_run_json_file_path: File path to save Ax state JSON file
       (and load from if resuming)
     - percent_yield_threshold: Percent-yield threshold for Ax hypervolume calculation
     - throughput_threshold: Throughput threshold for Ax hypervolume calculation
     - noise_sem: SEM value to report to Ax for each metric (helps keep GP stable)
     - simulation_mode: If True, runs in simulation mode (does not check volumes or
       run actual hardware)
     - xylopyridine_analog: Name of the xylopyridine analog being optimized

    Returns:
        None
    """

    # 1) Setup global state
    print(
        f"Loading Bayesian Optimization experimental parameters for optimization \
            campaign of xylopyridine analogs : {xylopyridine_analog}."
    )

    parameters_for_experiment = load_experimental_parameters(
        input_experimental_parameters
    )
    check_required_bo_campaign_parameters(parameters_for_experiment)

    bo_campaign_state = BoCampaignState()
    bo_campaign_state.update_bo_parameters(parameters_for_experiment)
    bo_campaign_state.set_noise_sem(noise_sem)
    bo_campaign_state.set_simulation_mode(simulation_mode)

    experimental_mode = "SIMULATION" if bo_campaign_state.simulation_mode else "HARDWARE"
    print(f"Running in {experimental_mode} mode")

    print(
        "Setting up parameter bounds for Bayesian Optimization of xylopyridine analogs..."
    )

    # Get all parameter bounds from state helper function
    experimental_bounds = bo_campaign_state.get_parameter_bounds()

    print(f"Flow rate bounds: {experimental_bounds['flow_rate_min']}"
          f" - {experimental_bounds['flow_rate_max']} uL/min")
    print(f"Dilution factor bounds: {experimental_bounds['dilution_factor_min']}"
           f" - {experimental_bounds['dilution_factor_max']}")
    print(f"Temperature bounds: {experimental_bounds['temperature_min']}"
           f" - {experimental_bounds['temperature_max']} °C")
    print(f"Co-solvent valve position bounds: {experimental_bounds['cosolvent_valve_position_min']}"
           f" - {experimental_bounds['cosolvent_valve_position_max']}")
    print(f"Co-solvent dilution factor bounds: {experimental_bounds['cosolvent_dilution_factor_min']}"
           f" - {experimental_bounds['cosolvent_dilution_factor_max']}")
    print(f"Light intensity bounds: {experimental_bounds['light_intensity_min']}"
           f" - {experimental_bounds['light_intensity_max']}")

    # 2) Generating ax object for optimization of xylopyridine analogs
    ax = _init_or_load_ax(
        ax_previous_run_json_file_path,
        experimental_bounds['flow_rate_min'],
        experimental_bounds['flow_rate_max'],
        experimental_bounds['dilution_factor_min'],
        experimental_bounds['dilution_factor_max'],
        experimental_bounds['temperature_min'],
        experimental_bounds['temperature_max'],
        experimental_bounds['cosolvent_valve_position_min'],
        experimental_bounds['cosolvent_valve_position_max'],
        experimental_bounds['cosolvent_dilution_factor_min'],
        experimental_bounds['cosolvent_dilution_factor_max'],
        experimental_bounds['light_intensity_min'],
        experimental_bounds['light_intensity_max'],
        percent_yield_threshold,
        throughput_threshold,
    )

    # 3) This is the main optimization loop,
    iteration = IterationState()
    step = 0

    # If configured trial count is 0, default to 30 iterations.
    configured_trials = int(bo_campaign_state.bo_parameters["trials"])
    target = "30" if configured_trials == 0 else str(configured_trials)
    try:
        while True if int(bo_campaign_state.bo_parameters["trials"]) == 0 else (step < int(target)):
            experiment_trial_conditions, trial_index = ax.get_next_trial()

            # Updates trials conditions for our experiment state
            iteration.update_iteration(trial_index + 1)
            iteration.update_trial_conditions(experiment_trial_conditions)

            experimental_results = ax_suggested_experiment(bo_campaign_state, iteration)

            ax.complete_trial(trial_index=trial_index, raw_data=experimental_results)
            step += 1

            # At the end of each step, we save the Ax state to a JSON file
            ax.save_to_json_file(filepath=ax_previous_run_json_file_path)

            print(
                f"[Step {step}/{target}] Trial {trial_index} -> "
                f"percent_yield={experimental_results['percent_yield'][0]:.4f}, "
                f"throughput={experimental_results['throughput'][0]:.6g} "
                f"at experimental parameters={experiment_trial_conditions}"
            )


    except KeyboardInterrupt:
        print("Keyboard interrupt received stopping Bayesian Optimization.")
    

    # TODO : It would be cool to maybe include a visualization plot
