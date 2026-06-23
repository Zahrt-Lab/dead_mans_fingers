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

import math
from pathlib import Path

from ax.exceptions.core import OptimizationShouldStop

from bayesian_optimizer.experiment_state import BoCampaignState, IterationState
from bayesian_optimizer.init_or_load_ax import _init_or_load_ax
from experimental_commands.execute_bo_iteration_commands import run_bayesian_optimization_iteration
from utils.experiment_aborted import PostProcessingError
from utils.prime_pump import prime_pump1
from preprocessing.experimental_parameters import (
    load_experimental_parameters,
    check_required_bo_campaign_parameters,
)
from preprocessing.volume_tracking import (
    initialize_volume_state,
    save_volume_log_csv,
    save_volume_state_json,
)

def _resolve_output_directory(bo_campaign_state: BoCampaignState, ax) -> None:
    """
    Redirect to a numbered subdirectory (run_001, run_002, ...) when starting a
    fresh campaign into a base_directory that already contains output files.

    On resume, continue in the highest-numbered existing run_### directory
    under base_directory, if one exists.
    """
    base_dir = Path(bo_campaign_state.bo_parameters["base_directory"])

    if getattr(ax, "_project_dmf_resumed_from_json", False):
        run_dirs = []
        if base_dir.exists():
            for path in base_dir.iterdir():
                if path.is_dir() and path.name.startswith("run_"):
                    try:
                        run_dirs.append((int(path.name.replace("run_", "", 1)), path))
                    except ValueError:
                        continue
        if run_dirs:
            latest_run_dir = max(run_dirs, key=lambda item: item[0])[1]
            bo_campaign_state.bo_parameters["base_directory"] = str(latest_run_dir)
            print(f"Resumed campaign output directory: {latest_run_dir}")
        return  # explicit resume from an Ax JSON file - don't redirect

    if not ax.get_trials_data_frame().empty:
        return  # resuming an existing campaign — don't redirect

    if not base_dir.exists() or not any(base_dir.iterdir()):
        return  # directory is empty or does not exist — no collision

    n = 1
    while (base_dir / f"run_{n:03d}").exists():
        n += 1
    new_base = base_dir / f"run_{n:03d}"
    print(
        f"Output directory already contains files from a previous run.\n"
        f"Saving this run to: {new_base}"
    )
    bo_campaign_state.bo_parameters["base_directory"] = str(new_base)


# TODO : This python function was a good idea but I prefer it as a seperate scripts, so I want to move it to init_or_load_ax eventually.
def _rebuild_results_cache(ax, bo_campaign_state: BoCampaignState) -> None:
    """
    Reconstruct the in-memory results cache from completed Ax trials.

    Called on campaign resume so that previously-run parameter sets are not
    repeated.  The cache key format matches execute_bo_iteration_commands:
    a tuple of the 6 trial-condition values rounded to 2 decimal places,
    in dict insertion order (flow_rate, dilution_factor, temperature,
    co_solvent_valve_position, co_solvent_dilution_factor, light_intensity).
    """
    _PARAM_KEYS = [
        "flow_rate",
        "dilution_factor",
        "temperature",
        "co_solvent_valve_position",
        "co_solvent_dilution_factor",
        "light_intensity",
    ]
    trials_df = ax.get_trials_data_frame()
    if trials_df.empty:
        return
    for _, row in trials_df.iterrows():
        try:
            pct_yield = float(row["percent_yield"])
            throughput = float(row["throughput"])
            if math.isnan(pct_yield) or math.isnan(throughput):
                continue
            _PARAM_NDP = {
                "flow_rate": 2,
                "dilution_factor": 4,
                "temperature": 2,
                "co_solvent_valve_position": 0,
                "co_solvent_dilution_factor": 2,
                "light_intensity": 2,
            }
            cache_key = tuple(round(float(row[k]), _PARAM_NDP[k]) for k in _PARAM_KEYS)
            bo_campaign_state.update_results_cache(cache_key, (pct_yield, throughput))
        except (KeyError, TypeError, ValueError):
            continue
    print(f"Reconstructed results cache with {len(bo_campaign_state.results_cache)} entries from prior Ax trials.")


def run_bo_campaign(
    input_experimental_parameters: dict,
    ax_previous_run_json_file_path: str,
    percent_yield_threshold: float,
    throughput_threshold: float,
    noise_sem_percent_yield: float = 1.0,
    noise_sem_throughput: float = 1.0,
    simulation_mode: bool = True,
    xylopyridine_analog: str = "",
) -> str:
    """
    This script runs the Bayesian Optimization campaign for our experiment per
    each xylopyridine analog.
    It will
     1) Load the experimental parameters.
     2) Initialize or loads Ax state from a previous run if it exists.
     3) Prompt the user if priming the pump 1 (xylopyridine solution) is needed before starting the optimization loop.
     4) Run the optimization loop.
     5) On exit, it will print the Pareto optimal parameter sets.


    Parameters:
     - input_experimental_parameters: Dictionary containing experimental parameters
       parameters (flow rate bounds, temperature bounds, etc.)
     - ax_previous_run_json_file_path: File path to save Ax state JSON file
       (and load from if resuming)
     - percent_yield_threshold: Percent-yield threshold for Ax hypervolume calculation
     - throughput_threshold: Throughput threshold for Ax hypervolume calculation
     - noise_sem_percent_yield: SEM for percent yield reported to Ax (absolute %, default 1.0)
     - noise_sem_throughput: SEM for throughput reported to Ax (nmol/min, default 1.0)
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
    bo_campaign_state.set_noise_sem(noise_sem_percent_yield, noise_sem_throughput)
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
    print(f"Co-solvent dilution factor bounds: {experimental_bounds['co_solvent_dilution_factor_min']}"
           f" - {experimental_bounds['co_solvent_dilution_factor_max']}")
    print(f"Light intensity bounds: {experimental_bounds['light_intensity_min']}"
           f" - {experimental_bounds['light_intensity_max']}")

    # 2) Generating ax object for optimization of xylopyridine analogs
    # TODO: This stopped asking user if they want to resume or start a new campaign.
    ax = _init_or_load_ax(
        ax_previous_run_json_file_path,
        experimental_bounds,
        percent_yield_threshold,
        throughput_threshold,
    )

    # Rebuild the in-memory results cache from any completed Ax trials (resume case)
    _rebuild_results_cache(ax, bo_campaign_state)

    # Redirect to a numbered subdirectory if the output directory already has files
    _resolve_output_directory(bo_campaign_state, ax)

    # Volume state JSON lives alongside the Ax JSON (sibling file)
    volume_state_json_path = str(
        Path(ax_previous_run_json_file_path).parent / "volume_state.json"
    )

    # Initialize stock-solution and waste volumes (hardware mode only)
    if not bo_campaign_state.simulation_mode:
        initial_volumes = initialize_volume_state(
            bo_campaign_state.bo_parameters,
            volume_state_json_path,
            )
        bo_campaign_state.update_volume_stock_solutions(initial_volumes)
        bo_campaign_state.update_waste_volume(
            initial_volumes.get("waste_volume_uL", 0.0)
            )
    # 3) Prompt user to prime pump 1 if needed. Requires user input for each analog
    
    #TODO: make a priming countdown. If no user input, prime anyway (I'm not a fan of a timer implementation since it can cause significant delays in experiments")
    #set priming experimental folder
    experimental_folder = bo_campaign_state.bo_parameters["base_directory"] + "/Experimental_Log"
    to_prime = input("Prime pump 1? (y/n): ").strip().lower()
    if to_prime == "y":
        print("Priming pump 1 with xylopyridine solution...")
        
     
        prime_pump1(
            flow_rate_pump1=1000.0,
            volume_pump1=1500.0,
            valve1_position=1, #needs to cahnge to the correspondent analog
            base_directory=experimental_folder #still need to find this variable 
        )
        print("Pump 1 primed.")
    elif to_prime == "n":
        print("Skipping pump priming. Make sure pump 1 is primed before running the optimization loop if you haven't already.")
    else:
        print("Invalid input. Skipping pump priming. Make sure pump 1 is primed before running the optimization loop if you haven't already.")
    # 4) This is the main optimization loop,
    iteration = IterationState()
    step = 0

    # If configured trial count is 0, default to 30 iterations.
    if int(bo_campaign_state.bo_parameters["trials"]) == 0:
        target = 30
    else:
        target = int(bo_campaign_state.bo_parameters["trials"])

    try:
        while True if int(bo_campaign_state.bo_parameters["trials"]) == 0 else (step < int(target)):

            try:
                experiment_trial_conditions, trial_index = ax.get_next_trial()
            except OptimizationShouldStop as exc: 
                print("Optimization campaign stopped.")
                print(exc.message)
                break

            # Updates trials conditions for our experiment state
            iteration.update_iteration(trial_index + 1)
            iteration.update_trial_conditions(experiment_trial_conditions)

            try:
                percent_yield, throughput = run_bayesian_optimization_iteration(bo_campaign_state, iteration)
            except FileNotFoundError as e:
                ax.abandon_trial(trial_index=trial_index)
                print(f"[WARNING] Trial {trial_index} abandoned — UV output file not found: {e}")
                print("This likely means the UV-detector blank spectrum calibration failed before the experiment ran.")
                fixed = input("Have you recalibrated the UV-detector and resolved the issue? (y/n): ").strip().lower()
                if fixed == "y":
                    print("Continuing campaign with a new trial (the abandoned trial is not retried).")
                    continue
                else:
                    print("Stopping campaign. Please recalibrate the UV-detector and restart.")
                    break
            except PostProcessingError as e:
                ax.abandon_trial(trial_index=trial_index)
                print(f"[WARNING] Trial {trial_index} abandoned — post-processing failed: {e}")
                print("This likely means there was an issue with the UV-VIS data (e.g. out-of-range absorbance values).")
                fixed = input("Have you resolved the issue with the UV-VIS data? (y/n): ").strip().lower()
                if fixed == "y":
                    print("Continuing campaign with a new trial (the abandoned trial is not retried).")
                    continue
                else:
                    print("Stopping campaign. Please resolve the issue with the UV-VIS data and restart.")
                    break

            experimental_results = {
                "percent_yield": (float(percent_yield), bo_campaign_state.noise_sem_percent_yield),
                "throughput": (float(throughput), bo_campaign_state.noise_sem_throughput),
            }
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
        
        print("Bayesian Optimization campaign completed.")

    except KeyboardInterrupt:
        print("Keyboard interrupt received stopping Bayesian Optimization.")

    return bo_campaign_state.bo_parameters["base_directory"]

