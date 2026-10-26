# ------------------------------------------------------------------------------
# Software: dead_mans_fingers
# Copyright (c) 2026 Zahrt Research Group
#
# Contributions by Scott Laverty are acknowledged.
#
# Licensed under the MIT License. See the LICENSE file in the repository root.
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
