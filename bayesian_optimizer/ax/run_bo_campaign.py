# ------------------------------------------------------------------------------
# Software: project_dead_mans_fingers
# Copyright: (C) 2025 by Professor Andrew Zahrt
# This software is the intellectual property of Professor Andrew Zahrt
# Contributions by graduate students Scott Laverty and Joao are acknowledged.
# All rights reserved.
# ------------------------------------------------------------------------------

'''
This module contains the AxRunner class to run the Bayesian Optimization for our experiment
'''

# bayesian_optimizer/run_bo_campaign.py
from __future__ import annotations

from bayesian_optimizer import state
from bayesian_optimizer.state import EXPERIMENTAL_PARAMETERS
from bayesian_optimizer.init_or_load_ax import _init_or_load_ax
from bayesian_optimizer.evaluate_ax import evaluate_ax

from preprocessing.experimental_parameters import (
    load_experimental_parameters,
    check_required_experimental_parameters,
)

# TODO : Need to verify input files needed for the bayesian optimizer code to run properly
# TODO : Need to develop a diagram and brief readme file as a reference for future users of this code and how it works


def run_bo_campaign(
    input_experimental_parameters: str,
    trials: int,
    state_path: str,
    save_every: int,
    objA_threshold: float,
    objB_threshold: float,
    noise_sem: float,
    simulation_mode: bool = True,
) -> None:
    """
    Top-level driver that:
      1) Loads experimental parameters into global state
      2) Initializes / resumes Ax
      3) Runs the BO loop
      4) Prints Pareto front on exit
    """
    # 1) Setup global state
    params = load_experimental_parameters(input_experimental_parameters)
    check_required_experimental_parameters(params, simulation_mode=simulation_mode)
    state.set_experimental_parameters(params)
    state.set_noise_sem(noise_sem)
    state.set_simulation_mode(simulation_mode)

    mode_str = "SIMULATION" if simulation_mode else "HARDWARE"
    print(f"\n{'='*60}")
    print(f"Running in {mode_str} mode")
    print(f"{'='*60}\n")

    fr_min, fr_max = EXPERIMENTAL_PARAMETERS["flow_rate"]
    conc_min, conc_max = EXPERIMENTAL_PARAMETERS["dilution_factor"]
    temp_min, temp_max = EXPERIMENTAL_PARAMETERS["temperature"]
    co_solvent_min, co_solvent_max = EXPERIMENTAL_PARAMETERS["cosolvents_valve_position"]
    co_solvent_volume_min, co_solvent_volume_max = EXPERIMENTAL_PARAMETERS["co_solvent_dilution_factor"]
    light_intensity_min, light_intensity_max = EXPERIMENTAL_PARAMETERS["light_intensity"]

    # 2) Ax init/load
    ax = _init_or_load_ax(
        state_path,
        fr_min,
        fr_max,
        conc_min,
        conc_max,
        temp_min,
        temp_max,
        co_solvent_min,
        co_solvent_max,
        co_solvent_volume_min,
        co_solvent_volume_max,
        light_intensity_min,
        light_intensity_max,
        objA_threshold,
        objB_threshold,
    )

    # 3) Run the loop
    step = 0

    # If trial count is 0, this will run for 30 iterations
    target = "30" if trials == 0 else str(trials)
    try:
        while True if trials == 0 else (step < trials):
            experimental_parameters_dictionary, trial_index = ax.get_next_trial()
            experimental_results = evaluate_ax(experimental_parameters_dictionary)
            ax.complete_trial(trial_index=trial_index, raw_data=experimental_results)
            step += 1

            if (step % max(1, save_every)) == 0:
                ax.save_to_json_file(filepath=state_path)

            print(
                f"[Step {step}/{target}] Trial {trial_index} -> "
                f"percent_yield={experimental_results['percent_yield'][0]:.4f}, "
                f"throughput={experimental_results['throughput'][0]:.6g} "
                f"at params={experimental_parameters_dictionary}"
            )
    except KeyboardInterrupt:
        print("\nInterrupted by user; saving Ax state...")
    finally:
        ax.save_to_json_file(filepath=state_path)
        print(f"Ax state saved to: {state_path}")

        # 4) optional Pareto print (same as your original)
        try:

            def _mean(value):
                if hasattr(value, "mean"):
                    return float(value.mean)
                if isinstance(value, (tuple, list)) and value:
                    return float(value[0])
                return float(value)

            pareto_optimal_params = ax.get_pareto_optimal_parameters()
            pareto_items = pareto_optimal_params.items() if isinstance(pareto_optimal_params, dict) else pareto_optimal_params
            print("\nPareto-optimal parameter sets (approx means):")
            for experimental_parameters, experiment_objective_function_outputs in pareto_items:
                if isinstance(experiment_objective_function_outputs, dict):
                    experimental_results_summary = {metric: round(_mean(metric_value), 4) for metric, metric_value in experiment_objective_function_outputs.items()}
                else:
                    experimental_results_summary = experiment_objective_function_outputs
                print(experimental_parameters, experimental_results_summary)
        except Exception as e:
            print(f"(Pareto print skipped: {e})")
