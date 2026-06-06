# ------------------------------------------------------------------------------
# Software: AUTO_ZAHRT
# Copyright: (C) 2026 by Professor Andrew Zahrt
# This software is the intellectual property of Professor Andrew Zahrt
# Contributions by graduate students Scott Laverty and Joao are acknowledged.
# All rights reserved.
# ------------------------------------------------------------------------------

"""
Tests for production_run/production_run.py

Verifies that the orchestrator wires extract_best_reaction_conditions,
calculate_production_run_parameters, save_production_run_commands_to_csv,
save_instrument_config_csv, and run_commands together correctly.
"""

import sys
from pathlib import Path
from unittest.mock import patch, call

import pytest

sys.path.append(str(Path(__file__).parent.parent.parent))
from production_run.production_run import production_run

_PATCH_BASE = "production_run.production_run"

# ---------------------------------------------------------------------------
# Shared fixture data
# ---------------------------------------------------------------------------

_BEST_CONDITIONS = (
    200.0,   # reactor_bed_flow_rate
    0.3,     # dilution_factor
    40.0,    # temperature
    3,       # cosolvent_valve_position
    0.1,     # fraction_of_cosolvent
    75.0,    # light_intensity
    20.0,    # throughput_nmol_per_min
)

_INSTRUMENT_PARAMS = {
    "flow_rate_pump1": 60.0,
    "volume_pump1": 300.0,
    "flow_rate_pump2": 120.0,
    "volume_pump2": 600.0,
    "flow_rate_pump3": 20.0,
    "volume_pump3": 100.0,
    "position_valve2": 3,
    "flow_rate_pump4": 0.0,
    "volume_pump4": 0.0,
    "temperature": 40.0,
    "light_intensity": 64.0,
}


# ---------------------------------------------------------------------------
# Helper to run production_run() with all external calls patched out
# ---------------------------------------------------------------------------

def _run_with_mocks(tmp_path, **kwargs):
    """
    Call production_run() with all I/O patched. Returns the mock objects so
    tests can inspect call arguments.
    """
    output_dir = str(tmp_path / "output")
    bo_results = str(tmp_path / "bo_results.csv")

    defaults = dict(
        bo_results=bo_results,
        yield_threshold=80.0,
        desired_mols=1000.0,
        xylopyridine_analogs_concentrations_uM=1000.0,
        output_dir=output_dir,
    )
    defaults.update(kwargs)

    with (
        patch(f"{_PATCH_BASE}.extract_best_reaction_conditions", return_value=_BEST_CONDITIONS) as mock_extract,
        patch(f"{_PATCH_BASE}.calculate_production_run_parameters", return_value=_INSTRUMENT_PARAMS) as mock_calculate,
        patch(f"{_PATCH_BASE}.save_production_run_commands_to_csv") as mock_save_commands,
        patch(f"{_PATCH_BASE}.save_instrument_config_csv") as mock_save_config,
        patch(f"{_PATCH_BASE}.run_commands") as mock_run,
    ):
        production_run(**defaults)
        return {
            "extract": mock_extract,
            "calculate": mock_calculate,
            "save_commands": mock_save_commands,
            "save_config": mock_save_config,
            "run_commands": mock_run,
            "output_dir": output_dir,
            "bo_results": bo_results,
        }


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_output_dir_is_created(tmp_path):
    """production_run() must create output_dir before writing files."""
    output_dir = str(tmp_path / "new_dir" / "nested")
    bo_results = str(tmp_path / "bo_results.csv")

    with (
        patch(f"{_PATCH_BASE}.extract_best_reaction_conditions", return_value=_BEST_CONDITIONS),
        patch(f"{_PATCH_BASE}.calculate_production_run_parameters", return_value=_INSTRUMENT_PARAMS),
        patch(f"{_PATCH_BASE}.save_production_run_commands_to_csv"),
        patch(f"{_PATCH_BASE}.save_instrument_config_csv"),
        patch(f"{_PATCH_BASE}.run_commands"),
    ):
        production_run(
            bo_results=bo_results,
            yield_threshold=80.0,
            desired_mols=1000.0,
            xylopyridine_analogs_concentrations_uM=1000.0,
            output_dir=output_dir,
        )

    assert Path(output_dir).is_dir()


def test_extract_called_with_correct_args(tmp_path):
    """extract_best_reaction_conditions must receive bo_results path and yield_threshold."""
    mocks = _run_with_mocks(tmp_path, yield_threshold=85.0)
    mocks["extract"].assert_called_once_with(mocks["bo_results"], yield_threshold=85.0)


def test_calculate_called_with_correct_conditions(tmp_path):
    """calculate_production_run_parameters must receive the values from extract."""
    mocks = _run_with_mocks(tmp_path, desired_mols=500.0, xylopyridine_analogs_concentrations_uM=2000.0)

    args = mocks["calculate"].call_args.args
    # Positional order from production_run.py:
    # reactor_bed_flow_rate, dilution_factor, temperature, cosolvent_valve_position,
    # fraction_of_cosolvent, light_intensity, throughput_nmol_per_min,
    # desired_mols, xylopyridine_analogs_concentrations_uM
    assert args[0] == pytest.approx(200.0)   # reactor_bed_flow_rate
    assert args[1] == pytest.approx(0.3)     # dilution_factor
    assert args[2] == pytest.approx(40.0)    # temperature
    assert args[3] == 3                       # cosolvent_valve_position
    assert args[4] == pytest.approx(0.1)     # fraction_of_cosolvent
    assert args[5] == pytest.approx(75.0)    # light_intensity
    assert args[6] == pytest.approx(20.0)    # throughput_nmol_per_min
    assert args[7] == pytest.approx(500.0)   # desired_mols
    assert args[8] == pytest.approx(2000.0)  # xylopyridine_analogs_concentrations_uM


def test_save_production_run_commands_to_csv_called_with_instrument_params(tmp_path):
    """save_production_run_commands_to_csv must be called with all pump parameters from calculate."""
    mocks = _run_with_mocks(tmp_path)

    kwargs = mocks["save_commands"].call_args.kwargs
    assert kwargs["flow_rate_pump1"] == pytest.approx(60.0)
    assert kwargs["flow_rate_pump2"] == pytest.approx(120.0)
    assert kwargs["flow_rate_pump3"] == pytest.approx(20.0)
    assert kwargs["flow_rate_pump4"] == pytest.approx(0.0)
    assert kwargs["temperature"] == pytest.approx(40.0)
    assert kwargs["light_intensity"] == pytest.approx(64.0)
    assert kwargs["valve_position_pump3"] == 3


def test_save_production_run_commands_to_csv_path_is_in_output_dir(tmp_path):
    """The commands CSV must be written inside output_dir."""
    mocks = _run_with_mocks(tmp_path)

    commands_path = mocks["save_commands"].call_args.kwargs["commands_path"]
    assert commands_path.startswith(mocks["output_dir"])
    assert "production_run_commands" in commands_path


def test_save_instrument_config_path_is_in_output_dir(tmp_path):
    """The instrument config CSV must be written inside output_dir."""
    mocks = _run_with_mocks(tmp_path)

    config_path = mocks["save_config"].call_args.args[0]
    assert config_path.startswith(mocks["output_dir"])


def test_run_commands_called_four_times(tmp_path):
    """run_commands must be called four times: wash, temperature, light_intensity, production_run."""
    mocks = _run_with_mocks(tmp_path)
    assert mocks["run_commands"].call_count == 4
