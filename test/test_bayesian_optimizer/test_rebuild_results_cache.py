# ------------------------------------------------------------------------------
# Software: dead_mans_fingers
# Copyright (c) 2026 Zahrt Research Group
#
# Contributions by Scott Laverty are acknowledged.
#
# Licensed under the MIT License. See the LICENSE file in the repository root.
# ------------------------------------------------------------------------------

"""
Unit tests for _rebuild_results_cache in bayesian_optimizer/run_bo_campaign.py.

Tests verify that the in-memory results cache is correctly populated from
the Ax trials data frame on campaign resume.
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock

import pandas as pd
import pytest

sys.path.append(str(Path(__file__).parent.parent.parent))

from bayesian_optimizer.experiment_state import BoCampaignState
from bayesian_optimizer.run_bo_campaign import _rebuild_results_cache


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_PARAM_KEYS = [
    "flow_rate",
    "dilution_factor",
    "temperature",
    "co_solvent_valve_position",
    "co_solvent_dilution_factor",
    "light_intensity",
]


def _make_trials_df(rows: list[dict]) -> pd.DataFrame:
    """Build a DataFrame mimicking ax.get_trials_data_frame() output."""
    return pd.DataFrame(rows)


def _make_ax_mock(df: pd.DataFrame) -> MagicMock:
    ax = MagicMock()
    ax.get_trials_data_frame.return_value = df
    return ax


def _make_bo_state() -> BoCampaignState:
    return BoCampaignState()


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_empty_trials_df_leaves_cache_empty():
    ax = _make_ax_mock(pd.DataFrame())
    state = _make_bo_state()
    _rebuild_results_cache(ax, state)
    assert len(state.results_cache) == 0


def test_single_trial_populates_cache():
    row = {
        "flow_rate": 100.0, "dilution_factor": 0.3, "temperature": 40.0,
        "co_solvent_valve_position": 2.0, "co_solvent_dilution_factor": 0.1,
        "light_intensity": 50.0, "percent_yield": 75.0, "throughput": 12.5,
    }
    ax = _make_ax_mock(_make_trials_df([row]))
    state = _make_bo_state()
    _rebuild_results_cache(ax, state)
    assert len(state.results_cache) == 1


def test_cache_key_matches_rounded_params():
    row = {
        "flow_rate": 100.123456, "dilution_factor": 0.299999, "temperature": 40.005,
        "co_solvent_valve_position": 2.0, "co_solvent_dilution_factor": 0.1001,
        "light_intensity": 50.004, "percent_yield": 60.0, "throughput": 8.0,
    }
    ax = _make_ax_mock(_make_trials_df([row]))
    state = _make_bo_state()
    _rebuild_results_cache(ax, state)

    expected_key = (100.12, 0.3, 40.01, 2.0, 0.1, 50.0)
    assert expected_key in state.results_cache


def test_cache_value_contains_yield_and_throughput():
    row = {
        "flow_rate": 120.0, "dilution_factor": 0.25, "temperature": 45.0,
        "co_solvent_valve_position": 1.0, "co_solvent_dilution_factor": 0.2,
        "light_intensity": 80.0, "percent_yield": 88.5, "throughput": 15.3,
    }
    ax = _make_ax_mock(_make_trials_df([row]))
    state = _make_bo_state()
    _rebuild_results_cache(ax, state)

    key = (120.0, 0.25, 45.0, 1.0, 0.2, 80.0)
    assert state.results_cache[key] == (88.5, 15.3)


def test_multiple_trials_all_cached():
    rows = [
        {
            "flow_rate": 80.0, "dilution_factor": 0.2, "temperature": 35.0,
            "co_solvent_valve_position": 1.0, "co_solvent_dilution_factor": 0.05,
            "light_intensity": 60.0, "percent_yield": 50.0, "throughput": 6.0,
        },
        {
            "flow_rate": 160.0, "dilution_factor": 0.4, "temperature": 55.0,
            "co_solvent_valve_position": 3.0, "co_solvent_dilution_factor": 0.3,
            "light_intensity": 90.0, "percent_yield": 85.0, "throughput": 22.0,
        },
    ]
    ax = _make_ax_mock(_make_trials_df(rows))
    state = _make_bo_state()
    _rebuild_results_cache(ax, state)
    assert len(state.results_cache) == 2


def test_reconstructed_cache_returns_hit_on_matching_conditions():
    row = {
        "flow_rate": 100.0, "dilution_factor": 0.3, "temperature": 40.0,
        "co_solvent_valve_position": 2.0, "co_solvent_dilution_factor": 0.1,
        "light_intensity": 50.0, "percent_yield": 75.0, "throughput": 12.5,
    }
    ax = _make_ax_mock(_make_trials_df([row]))
    state = _make_bo_state()
    _rebuild_results_cache(ax, state)

    # Simulate a cache lookup as done in execute_bo_iteration_commands
    cache_key = (100.0, 0.3, 40.0, 2.0, 0.1, 50.0)
    assert cache_key in state.results_cache
    assert state.results_cache[cache_key] == (75.0, 12.5)


def test_row_missing_metric_column_is_skipped():
    """Rows without percent_yield or throughput are silently skipped."""
    rows = [
        {
            "flow_rate": 100.0, "dilution_factor": 0.3, "temperature": 40.0,
            "co_solvent_valve_position": 2.0, "co_solvent_dilution_factor": 0.1,
            "light_intensity": 50.0,
            # missing percent_yield and throughput
        },
        {
            "flow_rate": 120.0, "dilution_factor": 0.25, "temperature": 45.0,
            "co_solvent_valve_position": 1.0, "co_solvent_dilution_factor": 0.2,
            "light_intensity": 80.0, "percent_yield": 88.5, "throughput": 15.3,
        },
    ]
    ax = _make_ax_mock(_make_trials_df(rows))
    state = _make_bo_state()
    _rebuild_results_cache(ax, state)
    # Only the complete row should be cached
    assert len(state.results_cache) == 1
