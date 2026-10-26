# ------------------------------------------------------------------------------
# Software: dead_mans_fingers
# Copyright (c) 2026 Zahrt Research Group
#
# Contributions by Scott Laverty are acknowledged.
#
# Licensed under the MIT License. See the LICENSE file in the repository root.
# ------------------------------------------------------------------------------

"""
Test cases for time_to_reach_target_volume.py
"""

import pytest
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))
from preprocessing.time_to_reach_target_volume import time_to_reach_target_volume


def test_time_basic_calculation():
    assert time_to_reach_target_volume(1, 100) == 6000.0   # 100 / 1 * 60
    assert time_to_reach_target_volume(2, 200) == 6000.0   # 200 / 2 * 60
    assert time_to_reach_target_volume(5, 500) == 6000.0   # 500 / 5 * 60


def test_time_different_rates():
    assert time_to_reach_target_volume(10, 100) == 600.0   # 100 / 10 * 60
    assert time_to_reach_target_volume(100, 100) == 60.0   # 100 / 100 * 60
    assert time_to_reach_target_volume(1, 1) == 60.0       # 1 / 1 * 60


def test_time_zero_volume():
    assert time_to_reach_target_volume(1, 0) == 0.0
    assert time_to_reach_target_volume(100, 0) == 0.0


def test_time_invalid_flow_rate_zero():
    with pytest.raises(ValueError):
        time_to_reach_target_volume(0, 100)


def test_time_invalid_flow_rate_negative():
    with pytest.raises(ValueError):
        time_to_reach_target_volume(-5, 100)
    with pytest.raises(ValueError):
        time_to_reach_target_volume(-1, 0)
