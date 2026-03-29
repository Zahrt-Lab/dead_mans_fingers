# ------------------------------------------------------------------------------
# Software: project_dead_mans_fingers
# Copyright: (C) 2026 by Professor Andrew Zahrt
# This software is the intellectual property of Professor Andrew Zahrt
# Contributions by graduate students Scott Laverty and Joao are acknowledged.
# All rights reserved.
# ------------------------------------------------------------------------------

"""
Unit tests for bayesian_optimizer/init_or_load_ax.py.

Covers:
- Fresh start (no existing JSON): new AxClient created without prompting.
- Existing JSON, user chooses resume [1]: existing AxClient loaded.
- Existing JSON, user chooses restart [2]: file deleted, new AxClient created.
- Invalid input is re-prompted until a valid choice is given.
"""

import sys
from pathlib import Path
from itertools import chain

import pytest

sys.path.append(str(Path(__file__).parent.parent.parent))

from ax.service.ax_client import AxClient, ObjectiveProperties

from bayesian_optimizer.init_or_load_ax import _init_or_load_ax, _prompt_resume_or_restart


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _save_minimal_ax_json(path: Path) -> None:
    """Create and save a minimal valid Ax JSON file."""
    ax = AxClient()
    ax.create_experiment(
        name="test_experiment",
        parameters=[
            {
                "name": "x",
                "type": "range",
                "bounds": [0.0, 1.0],
                "value_type": "float",
            }
        ],
        objectives={"y": ObjectiveProperties(minimize=False, threshold=0.5)},
    )
    ax.save_to_json_file(str(path))


def _call_init_or_load(json_path: Path, ask_user_fn=None) -> AxClient:
    """Call _init_or_load_ax with fixed test-space bounds."""
    experimental_bounds = {
        "flow_rate_min": 40.0,
        "flow_rate_max": 200.0,
        "dilution_factor_min": 0.05,
        "dilution_factor_max": 0.5,
        "temperature_min": 20.0,
        "temperature_max": 60.0,
        "cosolvent_valve_position_min": 1.0,
        "cosolvent_valve_position_max": 3.0,
        "cosolvent_dilution_factor_min": 0.0,
        "cosolvent_dilution_factor_max": 0.4,
        "light_intensity_min": 0.0,
        "light_intensity_max": 100.0,
    }
    return _init_or_load_ax(
        ax_previous_run_json_file_path=str(json_path),
        experimental_bounds=experimental_bounds,
        percent_yield_threshold=10.0,
        throughput_threshold=5.0,
        ask_user_fn=ask_user_fn,
    )


# ---------------------------------------------------------------------------
# Tests: no existing file
# ---------------------------------------------------------------------------


def test_no_existing_file_returns_ax_client(tmp_path):
    """When no JSON exists, a new AxClient is returned without prompting."""
    ax = _call_init_or_load(tmp_path / "ax.json")
    assert isinstance(ax, AxClient)


def test_no_existing_file_has_zero_trials(tmp_path):
    """New campaign starts with no completed trials."""
    ax = _call_init_or_load(tmp_path / "ax.json")
    assert len(ax.get_trials_data_frame()) == 0


# ---------------------------------------------------------------------------
# Tests: existing file, user chooses resume [1]
# ---------------------------------------------------------------------------


def test_resume_returns_ax_client(tmp_path):
    """Choosing resume [1] returns an AxClient."""
    json_path = tmp_path / "ax.json"
    _save_minimal_ax_json(json_path)
    ax = _call_init_or_load(json_path, ask_user_fn=lambda _: "1")
    assert isinstance(ax, AxClient)


def test_resume_keeps_file_on_disk(tmp_path):
    """Choosing resume [1] does not delete the existing file."""
    json_path = tmp_path / "ax.json"
    _save_minimal_ax_json(json_path)
    _call_init_or_load(json_path, ask_user_fn=lambda _: "1")
    assert json_path.exists()


# ---------------------------------------------------------------------------
# Tests: existing file, user chooses restart [2]
# ---------------------------------------------------------------------------


def test_restart_returns_ax_client(tmp_path):
    """Choosing restart [2] returns a new AxClient."""
    json_path = tmp_path / "ax.json"
    _save_minimal_ax_json(json_path)
    ax = _call_init_or_load(json_path, ask_user_fn=lambda _: "2")
    assert isinstance(ax, AxClient)


def test_restart_deletes_existing_file(tmp_path):
    """Choosing restart [2] deletes the old campaign file."""
    json_path = tmp_path / "ax.json"
    _save_minimal_ax_json(json_path)
    _call_init_or_load(json_path, ask_user_fn=lambda _: "2")
    assert not json_path.exists()


def test_restart_new_campaign_has_zero_trials(tmp_path):
    """After restart, the returned AxClient has no completed trials."""
    json_path = tmp_path / "ax.json"
    _save_minimal_ax_json(json_path)
    ax = _call_init_or_load(json_path, ask_user_fn=lambda _: "2")
    assert len(ax.get_trials_data_frame()) == 0


# ---------------------------------------------------------------------------
# Tests: invalid input is re-prompted
# ---------------------------------------------------------------------------


def test_invalid_input_retries_then_resumes(tmp_path):
    """Invalid inputs loop until a valid choice; eventually resumes."""
    json_path = tmp_path / "ax.json"
    _save_minimal_ax_json(json_path)
    responses = iter(["", "x", "99", "1"])
    ax = _call_init_or_load(json_path, ask_user_fn=lambda _: next(responses))
    assert isinstance(ax, AxClient)
    assert json_path.exists()


def test_invalid_input_retries_then_restarts(tmp_path):
    """Invalid inputs loop until a valid choice; eventually restarts."""
    json_path = tmp_path / "ax.json"
    _save_minimal_ax_json(json_path)
    responses = iter(["bad", "0", "3", "2"])
    ax = _call_init_or_load(json_path, ask_user_fn=lambda _: next(responses))
    assert isinstance(ax, AxClient)
    assert not json_path.exists()


# ---------------------------------------------------------------------------
# Tests: _prompt_resume_or_restart in isolation
# ---------------------------------------------------------------------------


def test_prompt_returns_true_for_choice_1():
    assert _prompt_resume_or_restart("dummy/path", ask_user_fn=lambda _: "1") is True


def test_prompt_returns_false_for_choice_2():
    assert _prompt_resume_or_restart("dummy/path", ask_user_fn=lambda _: "2") is False


def test_prompt_loops_on_invalid_then_returns_true():
    responses = iter(["nope", "1"])
    result = _prompt_resume_or_restart("dummy/path", ask_user_fn=lambda _: next(responses))
    assert result is True


def test_prompt_loops_on_invalid_then_returns_false():
    responses = iter(["", "bad", "2"])
    result = _prompt_resume_or_restart("dummy/path", ask_user_fn=lambda _: next(responses))
    assert result is False
