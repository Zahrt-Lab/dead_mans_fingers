# ------------------------------------------------------------------------------
# Software: project_dead_mans_fingers
# Copyright: (C) 2025 by Professor Andrew Zahrt
# This software is the intellectual property of Professor Andrew Zahrt
# Contributions by graduate students Scott Laverty and Joao are acknowledged.
# All rights reserved.
# ------------------------------------------------------------------------------

def compute_target_volume(
    total_reactor_volume_uL: float,
    *,
    residence_times: float = 3.0,
    volume_after_residence_times_met: float = 500.0,
) -> float:
    """
    Compute the volume that must pass through the reactor before we start
    averaging UV-Vis readings.

    Formula:  target_volume = (total_reactor_volume_uL * residence_times)
                              + volume_after_residence_times_met

    Parameters:
      - total_reactor_volume_uL: Total volume (µL) sent through the bed.
      - residence_times: How many residence times to wait before sampling.
      - volume_after_residence_times_met: Extra flush volume (µL) after the
        residence-time volume has passed ensure the signal stabilizes

    Returns:
      - target_volume (µL): Volume to pass before we start recording
    """
    if total_reactor_volume_uL <= 0:
        raise ValueError("total_reactor_volume_uL must be > 0.")
    if residence_times <= 0:
        raise ValueError("residence_times must be > 0.")
    if volume_after_residence_times_met < 0:
        raise ValueError("volume_after_residence_times_met must be ≥ 0.")

    return (
        total_reactor_volume_uL * residence_times
    ) + volume_after_residence_times_met
