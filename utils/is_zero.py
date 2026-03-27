# ------------------------------------------------------------------------------
# Software: project_dead_mans_fingers
# Copyright: (C) 2026 by Professor Andrew Zahrt
# This software is the intellectual property of Professor Andrew Zahrt
# Contributions by graduate students Scott Laverty and Joao are acknowledged.
# All rights reserved.
# ------------------------------------------------------------------------------

"""
Utility for checking whether a pump should be skipped based on near-zero
flow rate or volume. Used by all command generators that conditionally
include pump dispense/aspirate rows.
"""


def is_zero(flow_rate: float, volume: float, zero_tolerance: float = 1e-6) -> bool:
    """
    Return True if the pump should be skipped because flow rate or volume
    is effectively zero.

    Parameters:
        flow_rate: Pump flow rate in µL/min.
        volume: Pump volume in µL.
        zero_tolerance: Values at or below this magnitude are treated as zero.
    Returns:
        True if either value is effectively zero, False otherwise.
    """
    return abs(flow_rate) <= zero_tolerance or abs(volume) <= zero_tolerance
