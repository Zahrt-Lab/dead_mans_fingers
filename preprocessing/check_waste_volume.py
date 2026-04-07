# ------------------------------------------------------------------------------
# Software: project_dead_mans_fingers
# Copyright: (C) 2026 by Professor Andrew Zahrt
# This software is the intellectual property of Professor Andrew Zahrt
# Contributions by graduate students Scott Laverty and Joao are acknowledged.
# All rights reserved.
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
    maximum_waste_volume_uL = 4000000.0,
    *,
    interactive: bool = True,
):
    """
    The purpose of this code is to check if the waste volume will be close to overflowing
    after running the next experiment, 

    parameters:
     - current_waste_volume_uL: The current waste solution volume in uL
     - expected_waste_volume_uL: The expected waste volume generated from the next experiment in uL
     - maximum_waste_volume_uL: The maximum waste volume before the waste overflows in uL
    return:
     - None
    """

    current_waste_volume_uL = float(current_waste_volume_uL)
    expected_waste_volume_uL = float(expected_waste_volume_uL)
    maximum_waste_volume_uL = float(maximum_waste_volume_uL)

    # Need at least this much free volume in the waste container after the next experiment
    threshold_free_volume_uL = expected_waste_volume_uL + 1000000  # 1L buffer

    # Prompt only if insufficient free volume
    if (maximum_waste_volume_uL - current_waste_volume_uL) < threshold_free_volume_uL:
        print(
            f"Warning: Waste container has {current_waste_volume_uL:.2f} µL; "
            f"need ≥ {threshold_free_volume_uL:.2f} µL free after next experiment "
            f"(expected waste {expected_waste_volume_uL:.2f} + buffer 1000000 µL)."
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
