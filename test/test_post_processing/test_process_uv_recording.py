# ------------------------------------------------------------------------------
# Software: dead_mans_fingers
# Copyright (c) 2026 Zahrt Research Group
#
# Contributions by Scott Laverty and Joao Albuquerque are acknowledged.
#
# Licensed under the MIT License. See the LICENSE file in the repository root.
# ------------------------------------------------------------------------------

"""
Test cases for post_processing/post_process_uv_recording.py
"""

import pandas as pd
import pytest

from post_processing.post_process_uv_recording import post_process_uv_recording


def write_uv_csv(tmp_path, rows):
    """Write a UV-Vis CSV with Time(s), 409, 506 columns."""
    csv_path = tmp_path / "uv_recording.csv"
    df = pd.DataFrame(rows, columns=["Time(s)", "409", "506"])
    df.to_csv(csv_path, index=False)
    return str(csv_path)


def test_returns_dataframe(tmp_path):
    rows = [(t, 0.1, 0.2) for t in range(0, 600, 60)]
    csv_path = write_uv_csv(tmp_path, rows)
    result = post_process_uv_recording(flow_rate=100, target_volume=100, uv_vis_absorbance_results_csv=csv_path)
    assert isinstance(result, pd.DataFrame)


def test_filters_rows_before_target_time(tmp_path):
    # flow_rate=100 µL/min, target_volume=100 µL → threshold = 60 s
    rows = [(t, 0.1, 0.2) for t in [0, 30, 60, 90, 120]]
    csv_path = write_uv_csv(tmp_path, rows)
    result = post_process_uv_recording(flow_rate=100, target_volume=100, uv_vis_absorbance_results_csv=csv_path)
    assert all(result["Time(s)"] >= 60)


def test_all_rows_at_or_after_target_time_included(tmp_path):
    rows = [(t, 0.1, 0.2) for t in [60, 90, 120]]
    csv_path = write_uv_csv(tmp_path, rows)
    result = post_process_uv_recording(flow_rate=100, target_volume=100, uv_vis_absorbance_results_csv=csv_path)
    assert len(result) == 3


def test_saves_post_processed_csv_to_disk(tmp_path):
    rows = [(t, 0.1, 0.2) for t in range(0, 600, 60)]
    csv_path = write_uv_csv(tmp_path, rows)
    post_process_uv_recording(flow_rate=100, target_volume=100, uv_vis_absorbance_results_csv=csv_path)
    expected = str(tmp_path / "uv_recording_post_processed.csv")
    assert (tmp_path / "uv_recording_post_processed.csv").exists()


def test_missing_time_column_raises(tmp_path):
    csv_path = tmp_path / "bad.csv"
    pd.DataFrame({"A": [1, 2], "B": [3, 4]}).to_csv(csv_path, index=False)
    with pytest.raises(KeyError):
        post_process_uv_recording(flow_rate=100, target_volume=100, uv_vis_absorbance_results_csv=str(csv_path))


def test_early_convergence_uses_last_120_seconds(tmp_path):
    # max time = 600 s → keep rows >= 480 s
    rows = [(t, 0.1, 0.2) for t in range(0, 660, 60)]
    csv_path = write_uv_csv(tmp_path, rows)
    result = post_process_uv_recording(
        flow_rate=100, target_volume=100,
        uv_vis_absorbance_results_csv=csv_path,
        experiment_converged_early=True,
    )
    assert all(result["Time(s)"] >= 480)


def test_early_convergence_returns_dataframe(tmp_path):
    rows = [(t, 0.1, 0.2) for t in range(0, 660, 60)]
    csv_path = write_uv_csv(tmp_path, rows)
    result = post_process_uv_recording(
        flow_rate=100, target_volume=100,
        uv_vis_absorbance_results_csv=csv_path,
        experiment_converged_early=True,
    )
    assert isinstance(result, pd.DataFrame)


def test_early_convergence_saves_post_processed_csv(tmp_path):
    rows = [(t, 0.1, 0.2) for t in range(0, 660, 60)]
    csv_path = write_uv_csv(tmp_path, rows)
    post_process_uv_recording(
        flow_rate=100, target_volume=100,
        uv_vis_absorbance_results_csv=str(csv_path),
        experiment_converged_early=True,
    )
    assert (tmp_path / "uv_recording_post_processed.csv").exists()


def test_early_convergence_insufficient_data_returns_available_rows(tmp_path):
    # Only 60 s of data — less than 2 minutes; current logic returns all available rows
    rows = [(t, 0.1, 0.2) for t in range(0, 61, 60)]
    csv_path = write_uv_csv(tmp_path, rows)
    result = post_process_uv_recording(
        flow_rate=100, target_volume=100,
        uv_vis_absorbance_results_csv=str(csv_path),
        experiment_converged_early=True,
    )
    assert isinstance(result, pd.DataFrame)
    assert len(result) > 0


def test_empty_dataframe_after_cutoff_raises_value_error(tmp_path):
    # flow_rate=100, target_volume=600 → cutoff = 360 s; all rows are before cutoff
    rows = [(t, 0.1, 0.2) for t in [0, 30, 60]]
    csv_path = write_uv_csv(tmp_path, rows)
    with pytest.raises(ValueError):
        post_process_uv_recording(
            flow_rate=100, target_volume=600,
            uv_vis_absorbance_results_csv=csv_path,
            experiment_converged_early=False,
        )
