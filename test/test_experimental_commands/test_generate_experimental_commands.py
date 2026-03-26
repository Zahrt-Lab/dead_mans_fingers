# ------------------------------------------------------------------------------
# Software: project_dead_mans_fingers
# Copyright: (C) 2026 by Professor Andrew Zahrt
# This software is the intellectual property of Professor Andrew Zahrt
# Contributions by graduate students Scott Laverty and Joao are acknowledged.
# All rights reserved.
# ------------------------------------------------------------------------------

"""
Test cases for experimental_commands/generate_experimental_commands.py
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))

from experimental_commands.generate_experimental_commands import generate_experimental_commands

_HEADER = ["Component", "Action", "Parameters", "Notes", "delay"]

# NOTE: set_params and start_continuous rows have 6 elements due to an extra
# empty Notes field in the source. All other rows have 5 elements.
_COMMANDS = [
    _HEADER,
    ["DH2000_1", "shutter_open", "", "", "3.0"],
    ["OceanOptics_UVVis_1", "init", "", "", "3.0"],
    ["OceanOptics_UVVis_1", "set_params",
     "integration_time=30000,num_scans=10,measurement_interval=5,target_wavelengths=409;506",
     "", "", "3.0"],
    ["OceanOptics_UVVis_1", "record_blank", "", "", "3.0"],
    ["DH2000_1", "shutter_close", "", "", "3.0"],
    ["OceanOptics_UVVis_1", "record_dark", "", "", "3.0"],
    ["DH2000_1", "shutter_open", "", "", "3.0"],
    ["OceanOptics_UVVis_1", "start_continuous", "stop_upon_convergence=True", "", "", "3.0"],
    [
        "Tricontinental_Pump_C24000_1",
        "dispense",
        "flow_rate=100,volume=1000",
        "The flow rate of our Xylo compund is 100 uL/min and volume is 1000",
        "0.5",
    ],
    [
        "VICI_M6_Pump_1",
        "dispense",
        "flow_rate=50, volume=500",
        "The flow rate of our 0.1 M HCl Water is 50 uL/min and volume is 500",
        "0.5",
    ],
    [
        "VICI_M6_Pump_2",
        "dispense",
        "flow_rate=25, volume=250",
        "The flow rate of our cosolvent is 25 uL/min and volume is 250",
        "0.5",
    ],
    [
        "Tricontinental_Pump_C24000_2",
        "aspirate",
        "flow_rate=10, volume=100",
        "The flow rate of our 0.1 M HCl water pump is 10 uL/min and volume is 100",
        "0.5",
    ],
    ["SYNC", "wait_for_pumps", "", "Waiting for XYLO and WATER pumps to complete", "0.5"],
    ["OceanOptics_UVVis_1", "stop_continuous", "", "", "3.0"],
]


def test_generate_experimental_commands_returns_list_of_lists():
    commands = generate_experimental_commands(100, 50, 25, 10, 1000, 500, 250, 100)
    assert isinstance(commands, list)
    assert all(isinstance(command, list) for command in commands)


def test_generate_experimental_commands_header_is_correct():
    commands = generate_experimental_commands(100, 50, 25, 10, 1000, 500, 250, 100)
    assert commands[0] == _HEADER


def test_generate_experimental_commands_dh2000_shutter_open_first():
    commands = generate_experimental_commands(100, 50, 25, 10, 1000, 500, 250, 100)
    assert commands[1] == ["DH2000_1", "shutter_open", "", "", "3.0"]


def test_generate_experimental_commands_uv_vis_init():
    commands = generate_experimental_commands(100, 50, 25, 10, 1000, 500, 250, 100)
    assert commands[2] == ["OceanOptics_UVVis_1", "init", "", "", "3.0"]


def test_generate_experimental_commands_uv_vis_set_params():
    commands = generate_experimental_commands(100, 50, 25, 10, 1000, 500, 250, 100)
    assert commands[3][0] == "OceanOptics_UVVis_1"
    assert commands[3][1] == "set_params"
    assert "integration_time=30000" in commands[3][2]
    assert "num_scans=10" in commands[3][2]
    assert "measurement_interval=5" in commands[3][2]
    assert "target_wavelengths=409;506" in commands[3][2]


def test_generate_experimental_commands_uv_vis_record_blank():
    commands = generate_experimental_commands(100, 50, 25, 10, 1000, 500, 250, 100)
    assert commands[4] == ["OceanOptics_UVVis_1", "record_blank", "", "", "3.0"]


def test_generate_experimental_commands_dh2000_shutter_close():
    commands = generate_experimental_commands(100, 50, 25, 10, 1000, 500, 250, 100)
    assert commands[5] == ["DH2000_1", "shutter_close", "", "", "3.0"]


def test_generate_experimental_commands_uv_vis_record_dark():
    commands = generate_experimental_commands(100, 50, 25, 10, 1000, 500, 250, 100)
    assert commands[6] == ["OceanOptics_UVVis_1", "record_dark", "", "", "3.0"]


def test_generate_experimental_commands_dh2000_shutter_reopen():
    commands = generate_experimental_commands(100, 50, 25, 10, 1000, 500, 250, 100)
    assert commands[7] == ["DH2000_1", "shutter_open", "", "", "3.0"]


def test_generate_experimental_commands_uv_vis_start_continuous():
    commands = generate_experimental_commands(100, 50, 25, 10, 1000, 500, 250, 100)
    assert commands[8][0] == "OceanOptics_UVVis_1"
    assert commands[8][1] == "start_continuous"
    assert "stop_upon_convergence=True" in commands[8][2]


def test_generate_experimental_commands_pump1_always_present():
    commands = generate_experimental_commands(100, 0, 0, 0, 1000, 0, 0, 0)
    components = [cmd[0] for cmd in commands]
    assert "Tricontinental_Pump_C24000_1" in components


def test_generate_experimental_commands_pump1_flow_volume_encoded_correctly():
    commands = generate_experimental_commands(100, 0, 0, 0, 1000, 0, 0, 0)
    pump1_cmd = next(cmd for cmd in commands if cmd[0] == "Tricontinental_Pump_C24000_1")
    assert "flow_rate=100" in pump1_cmd[2]
    assert "volume=1000" in pump1_cmd[2]


def test_generate_experimental_commands_pump2_included_when_nonzero():
    commands = generate_experimental_commands(100, 50, 0, 0, 1000, 500, 0, 0)
    components = [cmd[0] for cmd in commands]
    assert "VICI_M6_Pump_1" in components


def test_generate_experimental_commands_pump2_omitted_when_zero():
    commands = generate_experimental_commands(100, 0, 0, 0, 1000, 0, 0, 0)
    components = [cmd[0] for cmd in commands]
    assert "VICI_M6_Pump_1" not in components


def test_generate_experimental_commands_pump3_included_when_nonzero():
    commands = generate_experimental_commands(100, 0, 25, 0, 1000, 0, 250, 0)
    components = [cmd[0] for cmd in commands]
    assert "VICI_M6_Pump_2" in components


def test_generate_experimental_commands_pump3_omitted_when_zero():
    commands = generate_experimental_commands(100, 0, 0, 0, 1000, 0, 0, 0)
    components = [cmd[0] for cmd in commands]
    assert "VICI_M6_Pump_2" not in components


def test_generate_experimental_commands_pump4_included_when_nonzero():
    commands = generate_experimental_commands(100, 0, 0, 10, 1000, 0, 0, 100)
    components = [cmd[0] for cmd in commands]
    assert "Tricontinental_Pump_C24000_2" in components


def test_generate_experimental_commands_pump4_omitted_when_zero():
    commands = generate_experimental_commands(100, 0, 0, 0, 1000, 0, 0, 0)
    components = [cmd[0] for cmd in commands]
    assert "Tricontinental_Pump_C24000_2" not in components


def test_generate_experimental_commands_sync_always_present():
    commands = generate_experimental_commands(100, 0, 0, 0, 1000, 0, 0, 0)
    components = [cmd[0] for cmd in commands]
    assert "SYNC" in components


def test_generate_experimental_commands_stop_continuous_always_last():
    commands = generate_experimental_commands(100, 50, 25, 10, 1000, 500, 250, 100)
    assert commands[-1] == ["OceanOptics_UVVis_1", "stop_continuous", "", "", "3.0"]


def test_generate_experimental_commands_full_output_matches_expected():
    commands = generate_experimental_commands(100, 50, 25, 10, 1000, 500, 250, 100)
    assert commands == _COMMANDS, f"Expected {_COMMANDS}, but got {commands}"