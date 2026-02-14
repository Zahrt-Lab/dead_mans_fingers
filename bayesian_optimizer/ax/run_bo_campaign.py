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

from bayesian_optimizer.deterministic_commands import state
from bayesian_optimizer.deterministic_commands.state import EXPERIMENTAL_PARAMETERS
from bayesian_optimizer.ax.init_or_load_ax import _init_or_load_ax
from bayesian_optimizer.ax.ax_suggested_experiment import ax_suggested_experiment

from preprocessing.experimental_parameters import (
    load_experimental_parameters,
    check_required_experimental_parameters,
)


def run_bo_campaign(
    input_experimental_parameters: str,
    trials: int,
    ax_previous_run_json_file_path: str,
    percent_yield_threshold: float,
    throughput_threshold: float,
    noise_sem: float,
    simulation_mode: bool = True,
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
     - input_experimental_parameters: Path to JSON file containing experimental
       parameters (flow rate bounds, temperature bounds, etc.)
     - ax_previous_run_json_file_path: File path to save Ax state JSON file
       (and load from if resuming)
     - percent_yield_threshold: Percent-yield threshold for Ax hypervolume calculation
     - throughput_threshold: Throughput threshold for Ax hypervolume calculation
     - noise_sem: SEM value to report to Ax for each metric (helps keep GP stable)
     - simulation_mode: If True, runs in simulation mode (does not check volumes or
       run actual hardware)

    Returns:
        None
    """
    print(
        f"Starting Bayesian Optimization Campaign with parameters "
        f"from: {input_experimental_parameters}"
    )

    # 1) Setup global state
    print(
        "Loading Bayesian Optimization experimental parameters for optimization campaign..."
    )
    parameters_for_experiment = load_experimental_parameters(
        input_experimental_parameters
    )
    check_required_experimental_parameters(
        parameters_for_experiment, simulation_mode=simulation_mode
    )
    state.set_experimental_parameters(parameters_for_experiment)
    state.set_noise_sem(noise_sem)
    state.set_simulation_mode(simulation_mode)

    experimental_mode = "SIMULATION" if simulation_mode else "HARDWARE"
    print(f"Running in {experimental_mode} mode")

    print(
        "Setting up parameter bounds for Bayesian Optimization of xylopyridine analogs..."
    )
    flow_rate_min, flow_rate_max = EXPERIMENTAL_PARAMETERS["flow_rate"]
    dilution_factor_min, dilution_factor_max = EXPERIMENTAL_PARAMETERS[
        "dilution_factor"
    ]
    temperature_min, temperature_max = EXPERIMENTAL_PARAMETERS["temperature"]
    co_solvent_min, co_solvent_max = EXPERIMENTAL_PARAMETERS[
        "cosolvents_valve_position"
    ]
    co_solvent_volume_min, co_solvent_volume_max = EXPERIMENTAL_PARAMETERS[
        "co_solvent_dilution_factor"
    ]
    light_intensity_min, light_intensity_max = EXPERIMENTAL_PARAMETERS[
        "light_intensity"
    ]

    print(f"Flow rate bounds: {flow_rate_min} - {flow_rate_max} uL/min")
    print(f"Dilution factor bounds: {dilution_factor_min} - {dilution_factor_max}")
    print(f"Temperature bounds: {temperature_min} - {temperature_max} °C")
    print(f"Co-solvent valve position bounds: {co_solvent_min} - {co_solvent_max}")
    print(
        f"Co-solvent dilution factor bounds: {co_solvent_volume_min} - {co_solvent_volume_max}"
    )
    print(f"Light intensity bounds: {light_intensity_min} - {light_intensity_max}")

    # 2) Generating ax object for optimization of xylopyridine analogs
    ax = _init_or_load_ax(
        ax_previous_run_json_file_path,
        flow_rate_min,
        flow_rate_max,
        dilution_factor_min,
        dilution_factor_max,
        temperature_min,
        temperature_max,
        co_solvent_min,
        co_solvent_max,
        co_solvent_volume_min,
        co_solvent_volume_max,
        light_intensity_min,
        light_intensity_max,
        percent_yield_threshold,
        throughput_threshold,
    )

    # 3) This is the main optimization loop,
    # which will run until we hit the trial count or the user interrupts with ctrl+c.
    step = 0

    # If trial count is 0, this will run for 30 iterations
    target = "30" if trials == 0 else str(trials)
    try:
        while True if trials == 0 else (step < trials):
            experiment_trial_conditions, trial_index = ax.get_next_trial()
            experimental_results = ax_suggested_experiment(experiment_trial_conditions)
            ax.complete_trial(trial_index=trial_index, raw_data=experimental_results)
            step += 1

            # This was done to save the results after every trial as a backup in case
            # of an unexpected issue
            ax.save_to_json_file(filepath=ax_previous_run_json_file_path)

            print(
                f"[Step {step}/{target}] Trial {trial_index} -> "
                f"percent_yield={experimental_results['percent_yield'][0]:.4f}, "
                f"throughput={experimental_results['throughput'][0]:.6g} "
                f"at experimental parameters={experiment_trial_conditions}"
            )

    except KeyboardInterrupt:
        print("\nInterrupted by user; saving Ax state...")

    finally:
        ax.save_to_json_file(filepath=ax_previous_run_json_file_path)
        print(f"Ax state saved to: {ax_previous_run_json_file_path}")

        # TODO : It would be cool to maybe include a visualization plot
        # here at the end of each iteration to get these working in real time.
