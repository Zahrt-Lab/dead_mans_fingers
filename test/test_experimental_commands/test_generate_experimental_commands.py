# ------------------------------------------------------------------------------
# Software: dead_mans_fingers
# Copyright (c) 2026 Andrew Zahrt
#
# Contributions by Scott Laverty and Joao Albuquerque are acknowledged.
#
# Licensed under the MIT License. See the LICENSE file in the repository root.
# ------------------------------------------------------------------------------

"""
Test cases for experimental_commands/generate_experimental_commands.py
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))

from experimental_commands.generate_experimental_commands import generate_experimental_commands

_HEADER = ["Component", "Action", "Parameters", "Notes", "delay"]

# Shared args for all tests: (pump flows, volumes, light, wavelengths, thresholds)
_ARGS = (100, 50, 25, 10, 1000, 500, 250, 100, 50, 506.0, 380.0, 700.0, 200.0, 600.0)
_CONVERGENCE_TIME = 450.0


def test_generate_experimental_commands_returns_list_of_lists():
    commands = generate_experimental_commands(*_ARGS, convergence_time=_CONVERGENCE_TIME)
    assert isinstance(commands, list)
    assert all(isinstance(command, list) for command in commands)


def test_generate_experimental_commands_header_is_correct():
    commands = generate_experimental_commands(*_ARGS, convergence_time=_CONVERGENCE_TIME)
    assert commands[0] == _HEADER


def test_generate_experimental_commands_uv_vis_set_params():
    commands = generate_experimental_commands(*_ARGS, convergence_time=_CONVERGENCE_TIME)
    set_params_cmd = next(cmd for cmd in commands if cmd[0] == "OceanOptics_UVVis_1" and cmd[1] == "set_params")
    assert "integration_time=30000" in set_params_cmd[2]
    assert "num_scans=10" in set_params_cmd[2]
    assert "measurement_interval=5" in set_params_cmd[2]
    assert "target_wavelengths=506.0;380.0;700.0" in set_params_cmd[2]
    assert f"convergence_time = {_CONVERGENCE_TIME}" in set_params_cmd[2]


def test_generate_experimental_commands_uv_vis_start_continuous():
    commands = generate_experimental_commands(*_ARGS, convergence_time=_CONVERGENCE_TIME)
    start_cmd = next(cmd for cmd in commands if cmd[0] == "OceanOptics_UVVis_1" and cmd[1] == "start_continuous")
    assert "stop_upon_convergence=True" in start_cmd[2]


def test_generate_experimental_commands_pump1_included_when_nonzero():
    commands = generate_experimental_commands(100, 0, 0, 0, 1000, 0, 0, 0, 50, 506.0, 380.0, 700.0, 200.0, 600.0, convergence_time=300.0)
    components = [cmd[0] for cmd in commands]
    assert "VICI_M6_Pump_1" in components


def test_generate_experimental_commands_pump1_omitted_when_zero():
    commands = generate_experimental_commands(0, 0, 0, 0, 0, 0, 0, 0, 50, 506.0, 380.0, 700.0, 200.0, 600.0, convergence_time=300.0)
    components = [cmd[0] for cmd in commands]
    assert "VICI_M6_Pump_1" not in components


def test_generate_experimental_commands_pump1_flow_volume_encoded_correctly():
    commands = generate_experimental_commands(100, 0, 0, 0, 1000, 0, 0, 0, 50, 506.0, 380.0, 700.0, 200.0, 600.0, convergence_time=300.0)
    pump1_cmd = next(cmd for cmd in commands if cmd[0] == "VICI_M6_Pump_1")
    assert "flow_rate=100" in pump1_cmd[2]
    assert "volume=1000" in pump1_cmd[2]


def test_generate_experimental_commands_pump2_included_when_nonzero():
    commands = generate_experimental_commands(100, 50, 0, 0, 1000, 500, 0, 0, 50, 506.0, 380.0, 700.0, 200.0, 600.0, convergence_time=300.0)
    components = [cmd[0] for cmd in commands]
    assert "Tecan_pump_1" in components


def test_generate_experimental_commands_pump2_omitted_when_zero():
    commands = generate_experimental_commands(100, 0, 0, 0, 1000, 0, 0, 0, 50, 506.0, 380.0, 700.0, 200.0, 600.0, convergence_time=300.0)
    components = [cmd[0] for cmd in commands]
    assert "Tecan_pump_1" not in components


def test_generate_experimental_commands_pump3_included_when_nonzero():
    commands = generate_experimental_commands(100, 0, 25, 0, 1000, 0, 250, 0, 50, 506.0, 380.0, 700.0, 200.0, 600.0, convergence_time=300.0)
    components = [cmd[0] for cmd in commands]
    assert "Tecan_pump_3" in components


def test_generate_experimental_commands_pump3_omitted_when_zero():
    commands = generate_experimental_commands(100, 0, 0, 0, 1000, 0, 0, 0, 50, 506.0, 380.0, 700.0, 200.0, 600.0, convergence_time=300.0)
    components = [cmd[0] for cmd in commands]
    assert "Tecan_pump_3" not in components


def test_generate_experimental_commands_pump4_included_when_nonzero():
    commands = generate_experimental_commands(100, 0, 0, 10, 1000, 0, 0, 100, 50, 506.0, 380.0, 700.0, 200.0, 600.0, convergence_time=300.0)
    components = [cmd[0] for cmd in commands]
    assert "Tricontinental_C24000_1" in components


def test_generate_experimental_commands_pump4_omitted_when_zero():
    commands = generate_experimental_commands(100, 0, 0, 0, 1000, 0, 0, 0, 50, 506.0, 380.0, 700.0, 200.0, 600.0, convergence_time=300.0)
    components = [cmd[0] for cmd in commands]
    assert "Tecan_pump_2" not in components


def test_generate_experimental_commands_sync_always_present():
    commands = generate_experimental_commands(*_ARGS, convergence_time=_CONVERGENCE_TIME)
    components = [cmd[0] for cmd in commands]
    assert "SYNC" in components


def test_generate_experimental_commands_stop_continuous_present():
    commands = generate_experimental_commands(*_ARGS, convergence_time=_CONVERGENCE_TIME)
    components_actions = [(cmd[0], cmd[1]) for cmd in commands]
    assert ("OceanOptics_UVVis_1", "stop_continuous") in components_actions


def test_generate_experimental_commands_shutter_close_always_last():
    commands = generate_experimental_commands(*_ARGS, convergence_time=_CONVERGENCE_TIME)
    assert commands[-1] == ["DH2000_1", "shutter_close", "", "", "3.0"]