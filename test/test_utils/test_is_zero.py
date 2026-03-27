# ------------------------------------------------------------------------------
# Software: project_dead_mans_fingers
# Copyright: (C) 2026 by Professor Andrew Zahrt
# This software is the intellectual property of Professor Andrew Zahrt
# Contributions by graduate students Scott Laverty and Joao are acknowledged.
# All rights reserved.
# ------------------------------------------------------------------------------

"""
Test cases for utils/is_zero.py
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))

from utils.is_zero import is_zero


def test_is_zero_true_when_flow_rate_is_zero():
    assert is_zero(0.0, 100.0) is True


def test_is_zero_true_when_volume_is_zero():
    assert is_zero(100.0, 0.0) is True


def test_is_zero_true_when_both_are_zero():
    assert is_zero(0.0, 0.0) is True


def test_is_zero_false_when_both_nonzero():
    assert is_zero(100.0, 500.0) is False


def test_is_zero_true_when_flow_rate_within_tolerance():
    assert is_zero(1e-7, 100.0) is True


def test_is_zero_true_when_volume_within_tolerance():
    assert is_zero(100.0, 1e-7) is True


def test_is_zero_false_when_values_exceed_tolerance():
    assert is_zero(1e-5, 1e-5) is False


def test_is_zero_respects_custom_tolerance():
    assert is_zero(0.01, 100.0, zero_tolerance=0.1) is True
    assert is_zero(0.01, 100.0, zero_tolerance=0.001) is False


def test_is_zero_true_for_negative_near_zero_flow():
    assert is_zero(-1e-7, 100.0) is True


def test_is_zero_false_for_small_but_meaningful_values():
    assert is_zero(0.01, 50.0) is False
