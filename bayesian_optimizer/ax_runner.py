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

# bayesian_optimizer/ax_runner.py
from __future__ import annotations

import os
import time
from typing import Dict

from ax.service.ax_client import AxClient, ObjectiveProperties

from bayesian_optimizer import state
from bayesian_optimizer.state import (
    EXPERIMENTAL_PARAMETERS,
    iteration,
    bayesian_optimization_results_csv_path,
    SIMULATION_MODE,
)
from bayesian_optimizer.bayesian_optimization_run import (
    run_bayesian_optimization_iteration,
    objective_function_percent_yield,
    objective_function_throughput,
)
from post_processing.append_bayesian_experimental_results import (
    append_bayesian_experimental_results,
)
from preprocessing.experimental_parameters import (
    load_experimental_parameters,
    check_required_experimental_parameters,
)


def _init_or_load_ax(
    state_path: str,
    flow_rate_min: float,
    flow_rate_max: float,
    dilution_factor_min: float,
    dilution_factor_max: float,
    temperature_min: float,
    temperature_max: float,
    cosolvents_valve_position_min: float,
    cosolvents_valve_position_max: float,
    co_solvent_volume_min: float,
    co_solvent_volume_max: float,
    light_intensity_min: float,
    light_intensity_max: float,
    percent_yield_threshold: float,
    throughput_threshold: float,
) -> AxClient:
    """
    Initialize a new AxClient or resume from a JSON state file to begin a bayesian optimization campaign.
    """
    if os.path.exists(state_path):
        ax = AxClient.load_from_json_file(state_path)
        print(f"Resumed Ax experiment with {len(ax.get_trials_data_frame())} trials.")
        return ax

    ax = AxClient()
    ax.create_experiment(
        name="project_dead_mans_fingers_moo_ax",
        parameters=[
            {
                "name": "flow_rate",
                "type": "range",
                "bounds": [flow_rate_min, flow_rate_max],
                "value_type": "int",
            },
            {
                "name": "dilution_factor",
                "type": "range",
                "bounds": [dilution_factor_min, dilution_factor_max],
                "value_type": "float",
            },
            {
                "name": "temperature",
                "type": "range",
                "bounds": [temperature_min, temperature_max],
                "value_type": "float",
            },
            {
                "name": "co_solvent",
                "type": "range",
                "bounds": [cosolvents_valve_position_min, cosolvents_valve_position_max],
                "value_type": "int",
            },
            {
                "name": "co_solvent_volume",
                "type": "range",
                "bounds": [co_solvent_volume_min, co_solvent_volume_max],
                "value_type": "float",
            },
            {
                "name": "light_intensity",
                "type": "range",
                "bounds": [light_intensity_min, light_intensity_max],
                "value_type": "float",
            },
        ],
        # This will set the objective functions and their thresholds to maximize both percent yield and throughput
        objectives={
            "percent_yield": ObjectiveProperties(
                minimize=False, threshold=float(percent_yield_threshold)
            ),
            "throughput": ObjectiveProperties(
                minimize=False, threshold=float(throughput_threshold)
            ),
        },
    )
    
    print("Started new Ax experiment.")
    return ax


def evaluate_ax(params: Dict[str, float]) -> Dict[str, tuple[float, float]]:
    """
    Runs ONE lab experiment using your existing pipeline.
    Returns the two objective metrics with (mean, sem) for Ax.
    """

    # This first checks experimental cache to avoid redundant experiments
    flow_rate = float(params["flow_rate"])
    dilution_factor = float(params["dilution_factor"])
    temperature = float(params["temperature"])
    co_solvent = float(params["co_solvent"])
    co_solvent_volume = float(params["co_solvent_volume"])
    light_intensity = float(params["light_intensity"])
    # It then tries to run the experiment using the run_bayesian_optimization_iteration function, catching errors
    try:
        percent_yield, throughput = run_bayesian_optimization_iteration(
            (flow_rate, dilution_factor, temperature, co_solvent, co_solvent_volume, light_intensity)
        )

        return {
            "percent_yield": (float(percent_yield), state.NOISE_SEM),
            "throughput": (float(throughput), state.NOISE_SEM),
        }

    except Exception as e:
        err_msg = str(e)
        now = time.strftime("%Y-%m-%d %H:%M:%S")

        reactant_concentration_uM = float(
            dilution_factor * EXPERIMENTAL_PARAMETERS.get("stock_concentration_uM", 0.0)
        )

        reactant_wavelength = EXPERIMENTAL_PARAMETERS.get("reactant_wavelength", "")
        product_wavelength = EXPERIMENTAL_PARAMETERS.get("product_wavelength", "")

        append_bayesian_experimental_results(
            bayesian_optimization_results_csv_path(),
            {
                "iteration": iteration["iteration #"],
                "flow_rate": flow_rate,
                "concentration": dilution_factor,
                "reactor_concentration_uM": reactant_concentration_uM,
                "temperature": temperature,
                "co_solvent": co_solvent,
                "co_solvent_volume": co_solvent_volume,
                "light_intensity": light_intensity,
                "target_volume": "",
                "reactant_wavelength": reactant_wavelength,
                "product_wavelength": product_wavelength,
                "average_absorbance_reactant": "",
                "average_absorbance_product": "",
                "percent_yield": 0.0,
                "throughput_nmol_per_min": 0.0,
                "timestamp": now,
                "status": "error",
                "error_message": (
                    (err_msg[:240] + "…") if len(err_msg) > 240 else err_msg
                ),
            },
        )

        # A value of 0 for both percent yield and throughput indicates a failed experiment to Ax and will not be considered
        # within future optimization steps and it shouldn't crash the optimization loop
        return {
            "percent_yield": (0.0, state.NOISE_SEM),
            "throughput": (0.0, state.NOISE_SEM),
        }


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
