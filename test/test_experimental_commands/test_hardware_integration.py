# ------------------------------------------------------------------------------
# Software: project_dead_mans_fingers
# Copyright: (C) 2026 by Professor Andrew Zahrt
# This software is the intellectual property of Professor Andrew Zahrt
# Contributions by graduate students Scott Laverty and Joao are acknowledged.
# All rights reserved.
# ------------------------------------------------------------------------------

"""
Hardware integration tests for experimental_commands.

All tests in this file are marked @pytest.mark.hardware and are automatically
skipped when no instrument COM ports are detected. Run these on the bench with
instruments powered and connected.

Usage:
    # Run only hardware tests:
    python -m pytest test/test_experimental_commands/test_hardware_integration.py -v

    # Skip hardware tests (default when no ports detected):
    python -m pytest test/test_experimental_commands/ -m "not hardware" -v
"""

import sys
from pathlib import Path

import pytest

sys.path.append(str(Path(__file__).parent.parent.parent))


# ---------------------------------------------------------------------------
# Temperature controller (COM12)
# ---------------------------------------------------------------------------

@pytest.mark.hardware
def test_temperature_controller_connection(detected_ports):
    """Verify temperature controller COM12 is in the detected ports."""
    assert "COM12" in detected_ports, "Temperature controller on COM12 not detected"


@pytest.mark.hardware
def test_temperature_command_executes_without_error(tmp_path, detected_ports):
    """Send a temperature set command and verify no serial error is raised."""
    pytest.skip("Implement: generate temperature CSV, call run_commands, assert no exception")


# ---------------------------------------------------------------------------
# VICI M6 Pumps (COM21, COM22)
# ---------------------------------------------------------------------------

@pytest.mark.hardware
def test_vici_pump1_connection(detected_ports):
    """Verify VICI M6 Pump 1 on COM21 is in the detected ports."""
    assert "COM21" in detected_ports, "VICI M6 Pump 1 on COM21 not detected"


@pytest.mark.hardware
def test_vici_pump2_connection(detected_ports):
    """Verify VICI M6 Pump 2 on COM22 is in the detected ports."""
    assert "COM22" in detected_ports, "VICI M6 Pump 2 on COM22 not detected"


# ---------------------------------------------------------------------------
# Valve (COM8)
# ---------------------------------------------------------------------------

@pytest.mark.hardware
def test_valve_connection(detected_ports):
    """Verify Valve6Way on COM8 is in the detected ports."""
    assert "COM8" in detected_ports, "Valve6Way on COM8 not detected"


# ---------------------------------------------------------------------------
# DH2000 Light Source (COM27)
# ---------------------------------------------------------------------------

@pytest.mark.hardware
def test_dh2000_connection(detected_ports):
    """Verify DH2000 light source on COM27 is in the detected ports."""
    assert "COM27" in detected_ports, "DH2000 on COM27 not detected"


@pytest.mark.hardware
def test_light_intensity_command_executes_without_error(tmp_path, detected_ports):
    """Send a light intensity command and verify no serial error is raised."""
    pytest.skip("Implement: generate light intensity CSV, call run_commands, assert no exception")


# ---------------------------------------------------------------------------
# OceanOptics UV-Vis (COM50)
# ---------------------------------------------------------------------------

@pytest.mark.hardware
def test_uvvis_connection(detected_ports):
    """Verify OceanOptics UV-Vis on COM50 is in the detected ports."""
    assert "COM50" in detected_ports, "OceanOptics UV-Vis on COM50 not detected"


# ---------------------------------------------------------------------------
# Full wash sequence
# ---------------------------------------------------------------------------

@pytest.mark.hardware
def test_wash_sequence_executes_without_error(tmp_path, detected_ports):
    """Run a full wash command sequence and verify no serial error is raised."""
    pytest.skip("Implement: generate wash CSV, call run_commands, assert no exception")
