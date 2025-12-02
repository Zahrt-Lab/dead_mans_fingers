# main.py
import argparse

from auto_zahrt.ax_runner import run_bo_campaign


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="AUTO_ZAHRT with Ax (qNEHVI)")
    parser.add_argument("input_experimental_parameters", help="Path to experiment JSON")
    parser.add_argument(
        "--trials",
        type=int,
        default=0,
        help="How many BO steps to run (0 = run forever)",
    )
    parser.add_argument(
        "--state-path",
        default="ax_state.json",
        help="Where to persist Ax experiment state (default: ax_state.json)",
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
        help="Percent-yield threshold (for HV reference point)",
    )
    parser.add_argument(
        "--objB-threshold",
        type=float,
        default=1e-9,
        help="Throughput threshold (for HV reference point)",
    )
    parser.add_argument(
        "--noise-sem",
        type=float,
        default=1e-3,
        help="Per-metric SEM reported to Ax (keeps GP stable)",
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
    )


if __name__ == "__main__":
    main()

