# ------------------------------------------------------------------------------
# Software: project_dead_mans_fingers
# Copyright: (C) 2025 by Professor Andrew Zahrt
# This software is the intellectual property of Professor Andrew Zahrt
# Contributions by graduate students Scott Laverty  and Joao are acknowledged.
# All rights reserved.
# ------------------------------------------------------------------------------

'''
Non-interactive version of main.py for debugging and automated runs.
This version runs in simulation mode with pre-configured parameters.
'''

# main_v2.py
import json

from bayesian_optimizer.ax.run_bo_campaign import run_bo_campaign
from preprocessing.generate_bo_input import generate_bo_input_file

# Conditional import for production_run (may not be available in all environments)
try:
    from production_run.production_run import production_run
except (ImportError, ModuleNotFoundError):
    production_run = None


def main() -> None:
    # ========== CONFIGURATION ==========
    # Edit these values to change behavior without command-line arguments
    input_experimental_parameters = "test_config_ax_demo.json"
    ax_state_path = "ax_state"
    objA_threshold = 1.0  # Percent-yield threshold
    objB_threshold = 1e-9  # Throughput threshold
    noise_sem = 1e-3  # Per-metric SEM for Ax
    production_run_percent_yield_threshold = 80.0
    simulation_mode = True  # Always run in simulation mode (no hardware)
    # ===================================

    print("=" * 60)
    print("Running main_v2.py (Non-Interactive Simulation Mode)")
    print("=" * 60)
    print(f"Config file: {input_experimental_parameters}")
    print(f"Simulation mode: {simulation_mode}")
    print(f"Ax state path: {ax_state_path}")
    print(f"Yield threshold: {objA_threshold}")
    print(f"Throughput threshold: {objB_threshold}")
    print("=" * 60)
    print()

    # Load the experimental parameters JSON to get the list of xylopyridine analogs
    with open(input_experimental_parameters, 'r') as f:
        experiment_config = json.load(f)

    for xylopyridine_analog in experiment_config["name_of_xylopyridine_analogs_stock_solutions"]:
        print(f"\n{'='*60}")
        print(f"Running Bayesian Optimization Campaign for: {xylopyridine_analog}")
        print(f"{'='*60}\n")

        bo_input = generate_bo_input_file(input_experimental_parameters, xylopyridine_analog)

        run_bo_campaign(
            input_experimental_parameters=bo_input,
            ax_previous_run_json_file_path=ax_state_path + f"_{xylopyridine_analog}_ax_state.json",
            percent_yield_threshold=objA_threshold,
            throughput_threshold=objB_threshold,
            noise_sem=noise_sem,
            simulation_mode=simulation_mode,
            xylopyridine_analog=xylopyridine_analog,
        )

        print(f"\n{'='*60}")
        print(f"Completed campaign for: {xylopyridine_analog}")
        print(f"{'='*60}\n")

    print("\n" + "=" * 60)
    print("All Bayesian Optimization campaigns completed!")
    print("=" * 60)

    # Production run section (currently commented out in original)
    '''
    for xylopyridine_analog in experiment_config["name_of_xylopyridine_analogs_stock_solutions"]:
        print(f"Beginning production run for xylopyridine analog: {xylopyridine_analog}")
        # TODO : Will likely need to update the input parameters based on final form of code 
        if production_run is not None:
            production_run()
        else:
            print("Skipping production_run - not available in this environment")
    '''


if __name__ == "__main__":
    main()

