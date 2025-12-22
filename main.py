# ------------------------------------------------------------------------------
# Software: project_dead_mans_fingers
# Copyright: (C) 2025 by Professor Andrew Zahrt
# This software is the intellectual property of Professor Andrew Zahrt
# Contributions by graduate students Scott Laverty are acknowledged.
# All rights reserved.
# ------------------------------------------------------------------------------

'''
This is the main script used to run and control the bayesian optimizater and experimental commands
'''

# main.py
import argparse

from bayesian_optimizer.ax_runner import run_bo_campaign


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Bayesian Optimizer for the fluorescent project controlling our automated platform (qNEHVI)")
    parser.add_argument("input_experimental_parameters", help="Path to experiment JSON")
    parser.add_argument(
        "--trials",
        type=int,
        default=30,
        help="How many BO steps to run (Default value: 30)",
    )
    parser.add_argument(
        "--state-path",
        default="ax_state.json",
        help="Where the ax_state locaton of all our bayesian optimizations our stored (default: ax_state.json)",
    )
    parser.add_argument(
        "--save-every",
        type=int,
        default=1,
        help="Persist state every K trials (default: 1)",
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
        "--simulation",
        action="store_true",
        help="Use simulated data instead of running AutoZahrt hardware",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    run_bo_campaign(
        input_experimental_parameters=args.input_experimental_parameters,
        trials=args.trials,
        state_path=args.state_path,
        save_every=args.save_every,
        objA_threshold=args.objA_threshold,
        objB_threshold=args.objB_threshold,
        noise_sem=args.noise_sem,
        simulation_mode=args.simulation,
    )


if __name__ == "__main__":
    main()
