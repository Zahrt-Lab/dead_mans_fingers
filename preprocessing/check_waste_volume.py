# ------------------------------------------------------------------------------
# Software: dead_mans_fingers
# Copyright (c) 2026 Andrew Zahrt
#
# Contributions by Scott Laverty and Joao Albuquerque are acknowledged.
#
# Licensed under the MIT License. See the LICENSE file in the repository root.
# ------------------------------------------------------------------------------

"""
Checks if the waste volume will be close to overflowing after the next experiment,
and prompts user to empty the waste if needed.
"""

import math
from utils.experiment_aborted import ExperimentAborted

def check_waste_volume(
    current_waste_volume_uL,
    expected_waste_volume_uL,
    maximum_waste_volume_uL=4_000_000.0,
    waste_buffer_volume_uL=1_000_000.0,
    *,
    interactive: bool = True,
) -> float:
    """
    Check if the waste volume will be close to overflowing after the next experiment,
    and prompt the user to empty the waste if needed.

    parameters:
     - current_waste_volume_uL: The current waste solution volume in uL
     - expected_waste_volume_uL: The expected waste volume generated from the next experiment in uL
     - maximum_waste_volume_uL: The maximum waste volume before the waste overflows in uL
     - waste_buffer_volume_uL: Minimum free space required in the waste container as a safety buffer
    return:
     - current_waste_volume_uL: Updated waste volume after any user top-up
    """

    current_waste_volume_uL = float(current_waste_volume_uL)
    expected_waste_volume_uL = float(expected_waste_volume_uL)
    maximum_waste_volume_uL = float(maximum_waste_volume_uL)
    waste_buffer_volume_uL = float(waste_buffer_volume_uL)

    # Need at least this much free volume in the waste container after the next experiment
    threshold_free_volume_uL = expected_waste_volume_uL + waste_buffer_volume_uL

    # Prompt only if insufficient free volume
    if (maximum_waste_volume_uL - current_waste_volume_uL) < threshold_free_volume_uL:
        print(
            f"Warning: Waste container has {current_waste_volume_uL:.2f} µL; "
            f"need ≥ {threshold_free_volume_uL:.2f} µL free after next experiment "
            f"(expected waste {expected_waste_volume_uL:.2f} + buffer {waste_buffer_volume_uL:.0f} µL)."
        )

    # Loop while insufficient; ask user to input CURRENT waste volume after emptying
    while (maximum_waste_volume_uL - current_waste_volume_uL) < threshold_free_volume_uL:
        if not interactive:
            raise ExperimentAborted(
                f"Need ≥ {threshold_free_volume_uL} µL free space in waste container."
            )

        try:
            updated_current_waste_volume_uL = input(
                "Empty waste ... enter CURRENT waste µL (or 'q' to abort): "
            )
            if updated_current_waste_volume_uL.lower() == 'q':
                raise ExperimentAborted("User aborted during waste check.")
            current_waste_volume_uL = float(updated_current_waste_volume_uL)
        except ValueError:
            print("Invalid input. Please enter a numeric value for current waste volume or 'q' to abort.")

    return current_waste_volume_uL
