# ------------------------------------------------------------------------------
# Software: dead_mans_fingers
# Copyright (c) 2026 Zahrt Research Group
#
# Contributions by Scott Laverty and Joao Albuquerque are acknowledged.
#
# Licensed under the MIT License. See the LICENSE file in the repository root.
# ------------------------------------------------------------------------------

"""
Test cases for post_processing/detect_early_convergence.py
"""

import pandas as pd
import pytest

from post_processing.detect_early_convergence import detect_early_convergence


def write_uv_csv(tmp_path, max_time_seconds, time_step=5):
    """Write a minimal UV-Vis CSV with Time(s) column up to max_time_seconds."""
    times = list(range(0, max_time_seconds + 1, time_step))
    df = pd.DataFrame({"Time(s)": times, "409": [0.5] * len(times), "506": [0.3] * len(times)})
    csv_path = tmp_path / "uv_recording.csv"
    df.to_csv(csv_path, index=False)
    return str(csv_path)


def test_returns_true_when_recording_is_significantly_short(tmp_path):
    # expected duration = 500 uL / 100 uL/min * 60 = 300 s; recorded only 100 s
    csv_path = write_uv_csv(tmp_path, max_time_seconds=100)
    assert detect_early_convergence(csv_path, flow_rate=100, total_volume=500) is True


def test_returns_false_when_recording_matches_expected_duration(tmp_path):
    # expected duration = 300 uL / 100 uL/min * 60 = 180 s; recorded 180 s (within tolerance)
    csv_path = write_uv_csv(tmp_path, max_time_seconds=180)
    assert detect_early_convergence(csv_path, flow_rate=100, total_volume=300) is False


def test_returns_false_when_within_tolerance(tmp_path):
    # expected = 300 s; recorded = 250 s → shortfall = 50 s < default tolerance of 60 s
    csv_path = write_uv_csv(tmp_path, max_time_seconds=250)
    assert detect_early_convergence(csv_path, flow_rate=100, total_volume=500) is False


def test_returns_true_when_just_outside_tolerance(tmp_path):
    # expected = 300 s; recorded = 230 s → shortfall = 70 s > default tolerance of 60 s
    csv_path = write_uv_csv(tmp_path, max_time_seconds=230)
    assert detect_early_convergence(csv_path, flow_rate=100, total_volume=500) is True


def test_custom_tolerance_respected(tmp_path):
    # expected = 300 s; recorded = 250 s → shortfall = 50 s
    # with tolerance=60: 50 < 60 → False
    csv_path = write_uv_csv(tmp_path, max_time_seconds=250)
    assert detect_early_convergence(csv_path, flow_rate=100, total_volume=500, tolerance_seconds=60) is False


def test_returns_false_when_recording_exceeds_expected(tmp_path):
    # expected = 180 s; recorded = 300 s (longer than expected) → not early
    csv_path = write_uv_csv(tmp_path, max_time_seconds=300)
    assert detect_early_convergence(csv_path, flow_rate=100, total_volume=300) is False
