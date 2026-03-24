# ------------------------------------------------------------------------------
# Software: project_dead_mans_fingers
# Copyright: (C) 2025 by Professor Andrew Zahrt
# This software is the intellectual property of Professor Andrew Zahrt
# Contributions by graduate students Scott Laverty  and Joao are acknowledged.
# All rights reserved.
# ------------------------------------------------------------------------------

'''
This is the main script used to run and control the bayesian optimizater and experimental commands
'''

# main.py
import argparse
import json

from bayesian_optimizer.run_bo_campaign import run_bo_campaign
from preprocessing.generate_bo_input import generate_bo_input_file

# Conditional import for production_run (may not be available in all environments)
try:
    from production_run.production_run import production_run
except (ImportError, ModuleNotFoundError):
    production_run = None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Bayesian Optimizer for the fluorescent project controlling our automated platform (qNEHVI)")
    parser.add_argument("input_experimental_parameters", help="Path to experiment JSON")

    parser.add_argument(
        "--state-path",
        default="ax_state.json",
        help="Where the ax_state locaton of all our bayesian optimizations our stored (default: ax_state.json)",
    )
    parser.add_argument(
        "--objA-threshold",
        type=float,
        default=1.0,
        help="Percent-yield threshold (for Bayesian Optimization hypervolume)",
    )
    parser.add_argument(
        "--objB-threshold",
        type=float,
        default=1e-9,
        help="Throughput threshold (for Bayesian Optimization reference hypervolume)",
    )
    parser.add_argument(
        "--noise-sem",
        type=float,
        default=1e-3,
        help="Per-metric Structure Equation Modeling reported to Ax (keeps GP stable)",
    )
    parser.add_argument(
        "--production-run-percent-yield-threshold",
        type=float,
        default=80.0,
        help="Percent-yield threshold for production run, if greater than this value."
        "and has highest throughput it is selected for the production run (default: 80.0).",
    )
    parser.add_argument(
        "--simulation",
        action="store_true",
        help="Use simulated data instead of running AutoZahrt hardware",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    # Load the experimental parameters JSON to get the list of xylopyridine analogs
    with open(args.input_experimental_parameters, 'r') as f:
        experiment_config = json.load(f)

    for xylopyridine_analog in experiment_config["name_of_xylopyridine_analogs_stock_solutions"]:
        print(f"Running Bayesian Optimization Campaign for xylopyridine analog: {xylopyridine_analog}")
        bo_input, bo_input_file_path = generate_bo_input_file(args.input_experimental_parameters, xylopyridine_analog)
        print(f"Generated BO input file: {bo_input_file_path}")

        # Construct ax state file path in the analog's output directory
        ax_state_file_path = f"{bo_input['base_directory']}/ax_state_{xylopyridine_analog}_ax_state.json"
        print(f"Using Ax state file: {ax_state_file_path}")

        # Before every campaign, we will run a quick test to make sure
        # we run unit test of our code,
        # run simulations of code,
        # then test the hardware
        # this will ensure everything is working before we run a campaign
        #test_set_up()

        run_bo_campaign(
            input_experimental_parameters=bo_input,
            ax_previous_run_json_file_path=ax_state_file_path,
            percent_yield_threshold=args.objA_threshold,
            throughput_threshold=args.objB_threshold,
            noise_sem=args.noise_sem,
            simulation_mode=args.simulation,
            xylopyridine_analog=xylopyridine_analog,
        )
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
