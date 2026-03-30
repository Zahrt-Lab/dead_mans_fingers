# ------------------------------------------------------------------------------
# Software: project_dead_mans_fingers
# Copyright: (C) 2026 by Professor Andrew Zahrt
# This software is the intellectual property of Professor Andrew Zahrt
# Contributions by graduate students Scott Laverty and Joao are acknowledged.
# All rights reserved.
# ------------------------------------------------------------------------------

"""
Test cases for experimental_commands/experiment_runner.py

Tier 1 (mock) — always runs, no hardware required.
Tier 2 (hardware) — auto-skipped when no instrument COM ports are detected.
"""

import sys
from pathlib import Path
from unittest.mock import patch, call, MagicMock

import pytest

sys.path.append(str(Path(__file__).parent.parent.parent))

from experimental_commands.run_hardware_experiment import run_hardware_experiment

_INSTRUMENT_CONFIG = "Instrument_Config_File.csv"
_COMMAND_BASE = "iteration_1"

# TODO : I don't understand the unittest.mock library well enough 

# ---------------------------------------------------------------------------
# Tier 1 — mock tests (always run)
# ---------------------------------------------------------------------------

@patch("experimental_commands.experiment_runner.run_commands")
def test_temperature_command_file_path(mock_run):
    run_hardware_experiment(_COMMAND_BASE, _INSTRUMENT_CONFIG, 1)
    calls = [c.args[0] for c in mock_run.call_args_list]
    assert f"{_COMMAND_BASE}_temperature.csv" in calls


@patch("experimental_commands.experiment_runner.run_commands")
def test_light_intensity_command_file_path(mock_run):
    run_hardware_experiment(_COMMAND_BASE, _INSTRUMENT_CONFIG, 1)
    calls = [c.args[0] for c in mock_run.call_args_list]
    assert f"{_COMMAND_BASE}_light_intensity.csv" in calls


@patch("experimental_commands.experiment_runner.run_commands")
def test_experiment_command_file_path(mock_run):
    run_hardware_experiment(_COMMAND_BASE, _INSTRUMENT_CONFIG, 1)
    calls = [c.args[0] for c in mock_run.call_args_list]
    assert f"{_COMMAND_BASE}_experiment.csv" in calls


@patch("experimental_commands.experiment_runner.run_commands")
def test_wash_command_file_path(mock_run):
    run_hardware_experiment(_COMMAND_BASE, _INSTRUMENT_CONFIG, 1)
    calls = [c.args[0] for c in mock_run.call_args_list]
    assert f"{_COMMAND_BASE}_wash.csv" in calls


@patch("experimental_commands.experiment_runner.run_commands")
def test_instrument_config_passed_to_all_calls(mock_run):
    run_hardware_experiment(_COMMAND_BASE, _INSTRUMENT_CONFIG, 1)
    for c in mock_run.call_args_list:
        assert c.args[1] == _INSTRUMENT_CONFIG


@patch("experimental_commands.experiment_runner.run_commands")
def test_command_execution_order(mock_run):
    run_hardware_experiment(_COMMAND_BASE, _INSTRUMENT_CONFIG, 1)
    actual_files = [c.args[0] for c in mock_run.call_args_list]
    expected_order = [
        f"{_COMMAND_BASE}_temperature.csv",
        f"{_COMMAND_BASE}_light_intensity.csv",
        f"{_COMMAND_BASE}_experiment.csv",
        f"{_COMMAND_BASE}_wash.csv",
    ]
    assert actual_files == expected_order


@patch("experimental_commands.experiment_runner.run_commands")
def test_wash_runs_even_when_experiment_raises(mock_run):
    """Wash step must always execute — it is in the finally block."""
    def raise_on_experiment(command_file, _config):
        if "_experiment" in command_file:
            raise RuntimeError("Simulated hardware failure")

    mock_run.side_effect = raise_on_experiment
    with pytest.raises(RuntimeError):
        run_hardware_experiment(_COMMAND_BASE, _INSTRUMENT_CONFIG, 1)

    called_files = [c.args[0] for c in mock_run.call_args_list]
    assert f"{_COMMAND_BASE}_wash.csv" in called_files


@patch("experimental_commands.experiment_runner.run_commands")
def test_run_commands_called_four_times(mock_run):
    run_hardware_experiment(_COMMAND_BASE, _INSTRUMENT_CONFIG, 1)
    assert mock_run.call_count == 4


# ---------------------------------------------------------------------------
# Tier 2 — hardware tests (auto-skipped when no COM ports detected)
# ---------------------------------------------------------------------------

@pytest.mark.hardware
def test_hardware_temperature_command_executes(hardware_available):
    """Placeholder: verify temperature command reaches the instrument."""
    pytest.skip("Hardware integration test — implement when instruments are connected")


@pytest.mark.hardware
def test_hardware_light_intensity_command_executes(hardware_available):
    """Placeholder: verify light intensity command reaches the instrument."""
    pytest.skip("Hardware integration test — implement when instruments are connected")
