# ------------------------------------------------------------------------------
# Software: dead_mans_fingers
# Copyright (c) 2026 Andrew Zahrt
#
# Contributions by Scott Laverty and Joao Albuquerque are acknowledged.
#
# Licensed under the MIT License. See the LICENSE file in the repository root.
# ------------------------------------------------------------------------------

'''This code is the point of entry for the calibration process
'''

import argparse
from bayesian_optimizer.experiment_state import CalibrationState
from calibration.run_calibration_campaign import run_calibration_campaign
from calibration.load_json import load_experimental_parameters

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Calibration script for the fluorescent project controlling our automated platform (qNEHVI)")
    parser.add_argument("input_experimental_parameters", help="Path to experiment JSON")
    # Add simulation flag
    parser.add_argument(
        "--simulation",
        action="store_true",
        help="If set, the script will run in simulation mode without communicating with hardware.",
    )
    return parser.parse_args()

def main():
    args = parse_args()
    input_experimental_parameters = args.input_experimental_parameters
    simulate = args.simulation

    # Load experimental parameters from the JSON file
    print(f"Loading experimental parameters from {input_experimental_parameters}")
    params = load_experimental_parameters(input_experimental_parameters)
    calibration_state = CalibrationState()
    calibration_state.update_calibration_parameters(params)
    calibration_state.set_simulation_mode(simulate)

    print("Starting calibration campaign")
    # Run the calibration process
    run_calibration_campaign(calibration_state)

    print("Calibration campaign completed")

if __name__ == "__main__":
    main()
