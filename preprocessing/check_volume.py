# ------------------------------------------------------------------------------
# Software: project_dead_mans_fingers
# Copyright: (C) 2025 by Professor Andrew Zahrt
# This software is the intellectual property of Professor Andrew Zahrt
# Contributions by graduate students Scott Laverty and Joao are acknowledged.
# All rights reserved.
# ------------------------------------------------------------------------------

def check_volume(
    current_volume_uL,
    required_volume_uL,
    minimum_volume_remaining_uL,
    solution_name,
    *,
    interactive: bool = True,
):
    """
    The purpose of this code is to

    parameters:
     - current_volume_uL: The current stock solution remaining
     - required_volume_uL: volume required for the next experiment
     - minimum_volume_remaining_uL: Volume remaining needed to continue experiment e.g. 2mL
     - solution_name: Name of our stock solution
    return:
     - remaining_volume_uL: Is remaining volume after the experiment is completed
    """

    current_volume_uL = float(current_volume_uL)
    required_volume_uL = float(required_volume_uL)
    minimum_volume_remaining_uL = float(minimum_volume_remaining_uL)

    # Need at least this much BEFORE withdrawing
    threshold_uL = required_volume_uL + minimum_volume_remaining_uL

    # Prompt only if insufficient
    if current_volume_uL < threshold_uL:
        print(
            f"Stock solution {solution_name} is {current_volume_uL:.2f} µL; "
            f"need ≥ {threshold_uL:.2f} µL (required {required_volume_uL:.2f} + "
            f"reserve {minimum_volume_remaining_uL:.2f})."
        )

    # Loop while insufficient; ask user to input CURRENT volume after topping up
    while current_volume_uL < threshold_uL:
        if not interactive:
            raise ExperimentAborted(f"{solution_name}: need ≥ {threshold_uL} µL.")

        try:
            updated_current_volume_uL = input(
                "Add solvent ... enter CURRENT µL (or 'q' to abort): "
            ).strip()

        except (EOFError, KeyboardInterrupt):
            raise ExperimentAborted("Input aborted")

        if updated_current_volume_uL.lower() in {"q", "quit", "exit"}:
            raise ExperimentAborted("Aborted by user")

        try:
            updated_current_volume_uL = float(updated_current_volume_uL)

        except ValueError:
            print("Please enter a number (µL).")
            continue

        if (
            not math.isfinite(updated_current_volume_uL)
        ) or updated_current_volume_uL <= 0:
            print("Please enter a positive amount (µL).")
            continue

        current_volume_uL = updated_current_volume_uL

        shortage = threshold_uL - current_volume_uL
        if shortage > 0:
            print(
                f"Still short by {shortage:.2f} µL. Keep adding to '{solution_name}'."
            )

    remaining_volume_after_experiment = current_volume_uL - required_volume_uL
    print(
        f"Proceeding: withdrawing {required_volume_uL:.2f} µL from '{solution_name}'. "
        f"Remaining {remaining_volume_after_experiment:.2f} µL "
        f"(reserve ≥ {minimum_volume_remaining_uL:.2f} µL)."
    )
    return remaining_volume_after_experiment
