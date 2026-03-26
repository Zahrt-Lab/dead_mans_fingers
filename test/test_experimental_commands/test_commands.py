# ------------------------------------------------------------------------------
# Software: project_dead_mans_fingers
# Copyright: (C) 2026 by Professor Andrew Zahrt
# This software is the intellectual property of Professor Andrew Zahrt
# Contributions by graduate students Scott Laverty and Joao are acknowledged.
# All rights reserved.
# ------------------------------------------------------------------------------

"""
Test cases for experimental_commands/commands.py

Tier 1 (mock) — always runs, no hardware required.
Tier 2 (hardware) — auto-skipped when no instrument COM ports are detected.
"""

import csv
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

sys.path.append(str(Path(__file__).parent.parent.parent))

from experimental_commands.commands import save_commands_csv, run_commands

# TODO : Add more equipment tests when hardware is available

_HEADER = ["Component", "Action", "Parameters", "Notes", "delay"]


# ---------------------------------------------------------------------------
# Tier 1 — save_commands_csv tests (always run)
# ---------------------------------------------------------------------------

def test_save_commands_csv_creates_temperature_file(tmp_path):
    base = tmp_path / "iteration_1"
    save_commands_csv(str(base), 100, 50, 25, 0, 1000, 500, 250, 0, 3, 50, 0.2, 75)
    assert (tmp_path / "iteration_1_temperature.csv").exists()


def test_save_commands_csv_creates_light_intensity_file(tmp_path):
    base = tmp_path / "iteration_1"
    save_commands_csv(str(base), 100, 50, 25, 0, 1000, 500, 250, 0, 3, 50, 0.2, 75)
    assert (tmp_path / "iteration_1_light_intensity.csv").exists()

def test_save_commands_csv_creates_experiment_file(tmp_path):
    base = tmp_path / "iteration_1"
    save_commands_csv(str(base), 100, 50, 25, 0, 1000, 500, 250, 0, 3, 50, 0.2, 75)
    assert (tmp_path / "iteration_1_experiment.csv").exists()


def test_save_commands_csv_creates_wash_file(tmp_path):
    base = tmp_path / "iteration_1"
    save_commands_csv(str(base), 100, 50, 25, 0, 1000, 500, 250, 0, 3, 50, 0.2, 75)
    assert (tmp_path / "iteration_1_wash.csv").exists()


def test_save_commands_csv_temperature_file_has_correct_header(tmp_path):
    base = tmp_path / "iteration_1"
    save_commands_csv(str(base), 100, 50, 25, 0, 1000, 500, 250, 0, 3, 50, 0.2, 75)
    with open(tmp_path / "iteration_1_temperature.csv", newline="", encoding="utf-8") as f:
        header = next(csv.reader(f))
    assert header == _HEADER


def test_save_commands_csv_light_intensity_file_has_correct_header(tmp_path):
    base = tmp_path / "iteration_1"
    save_commands_csv(str(base), 100, 50, 25, 0, 1000, 500, 250, 0, 3, 50, 0.2, 75)
    with open(tmp_path / "iteration_1_light_intensity.csv", newline="", encoding="utf-8") as f:
        header = next(csv.reader(f))
    assert header == _HEADER


def test_save_commands_csv_experiment_file_has_correct_header(tmp_path):
    base = tmp_path / "iteration_1"
    save_commands_csv(str(base), 100, 50, 25, 0, 1000, 500, 250, 0, 3, 50, 0.2, 75)
    with open(tmp_path / "iteration_1_experiment.csv", newline="", encoding="utf-8") as f:
        header = next(csv.reader(f))
    assert header == _HEADER


def test_save_commands_csv_wash_file_has_correct_header(tmp_path):
    base = tmp_path / "iteration_1"
    save_commands_csv(str(base), 100, 50, 25, 0, 1000, 500, 250, 0, 3, 50, 0.2, 75)
    with open(tmp_path / "iteration_1_wash.csv", newline="", encoding="utf-8") as f:
        header = next(csv.reader(f))
    assert header == _HEADER


def test_save_commands_csv_wash_volumes_computed_from_cosolvent_fraction(tmp_path):
    """Wash pump volumes follow F2 = 2000*(1-D), F3 = 2000*D, F4 = 1000."""
    base = tmp_path / "iteration_1"
    fraction = 0.25
    save_commands_csv(str(base), 100, 50, 25, 0, 1000, 500, 250, 0, 3, 50, fraction, 75)
    with open(tmp_path / "iteration_1_wash.csv", newline="", encoding="utf-8") as f:
        rows = list(csv.reader(f))

    # Collect all parameter strings from pump rows
    param_strings = " ".join(r[2] for r in rows[1:] if r[0].startswith("VICI"))
    assert f"flow_rate={2000 * (1 - fraction)}" in param_strings


# ---------------------------------------------------------------------------
# Tier 1 — run_commands tests (mock GeneralExperimentMethod)
# ---------------------------------------------------------------------------

def test_run_commands_raises_when_hardware_unavailable():
    """run_commands raises RuntimeError when GeneralExperimentMethod is None."""
    with patch("experimental_commands.commands.GeneralExperimentMethod", None):
        with pytest.raises(RuntimeError, match="GeneralExperimentMethod not available"):
            run_commands("some_commands.csv", "Instrument_Config_File.csv")


def test_run_commands_instantiates_general_experiment_method():
    mock_gem = MagicMock()
    with patch("experimental_commands.commands.GeneralExperimentMethod", mock_gem):
        run_commands("temperature.csv", "Instrument_Config_File.csv")
    mock_gem.assert_called_once_with("temperature.csv", "Instrument_Config_File.csv")


def test_run_commands_calls_run_experiment():
    mock_gem = MagicMock()
    with patch("experimental_commands.commands.GeneralExperimentMethod", mock_gem):
        run_commands("temperature.csv", "Instrument_Config_File.csv")
    mock_gem.return_value.run_experiment.assert_called_once()


# ---------------------------------------------------------------------------
# Tier 2 — hardware tests (auto-skipped when no COM ports detected)
# ---------------------------------------------------------------------------

@pytest.mark.hardware
def test_hardware_run_commands_temperature(hardware_available, tmp_path):
    """Placeholder: verify temperature commands execute on real hardware."""
    pytest.skip("Hardware integration test — implement when instruments are connected")


@pytest.mark.hardware
def test_hardware_run_commands_wash(hardware_available, tmp_path):
    """Placeholder: verify wash commands execute on real hardware."""
    pytest.skip("Hardware integration test — implement when instruments are connected")
