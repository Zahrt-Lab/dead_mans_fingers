# ------------------------------------------------------------------------------
# Software: project_dead_mans_fingers
# Copyright: (C) 2026 by Professor Andrew Zahrt
# This software is the intellectual property of Professor Andrew Zahrt
# Contributions by graduate students Scott Laverty and Joao are acknowledged.
# All rights reserved.
# ------------------------------------------------------------------------------

"""
Test cases for experimental_commands/generate_wash_commands.py
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))

from experimental_commands.generate_wash_commands import generate_wash_commands

_HEADER = ["Component", "Action", "Parameters", "Notes", "delay"]

_COMMANDS = [
    _HEADER,
    [
        "Valve6Way_2",
        "go_to_position",
        "position=3",
        "",
        "0.5",
    ],
    [
        "Tecan_pump_3",
        "dispense",
        "flow_rate=1000, volume=1000",
        "Flushing with co-solvent at flow rate of 1000 uL/min and volume of 1000 uL",
        "0.5",
    ],
    [
        "SYNC",
        "wait_for_pumps",
        "",
        "Waiting for co-solvent pump to complete",
        "0.5",
    ],
    [
        "Tecan_pump_1",
        "dispense",
        "flow_rate=100, volume=300",
        "The flow rate of our 0.1 M HCl Water is 100 uL/min and volume is 300",
        "0.5",
    ],
    [
        "Tecan_pump_3",
        "dispense",
        "flow_rate=50, volume=150",
        "The flow rate of our cosolvent is 50 uL/min and volume is 150",
        "0.5",
    ],
    [
        "Tricontinental_C24000_1",
        "dispense",
        "flow_rate=25, volume=75",
        "The flow rate of our 0.1 M HCl water pump is 25 uL/min and volume is 75",
        "0.5",
    ],
    [
        "SYNC",
        "wait_for_pumps",
        "",
        "Waiting for XYLO and WATER pumps to complete",
        "0.5",
    ],
]


def test_generate_wash_commands_returns_list_of_lists():
    commands = generate_wash_commands(100, 300, 50, 150, 25, 75, 3)
    assert isinstance(commands, list)
    assert all(isinstance(command, list) for command in commands)


def test_generate_wash_commands_header_is_correct():
    commands = generate_wash_commands(100, 300, 50, 150, 25, 75, 3)
    assert commands[0] == _HEADER


def test_generate_wash_commands_valve_position_always_present():
    commands = generate_wash_commands(0, 0, 0, 0, 0, 0, 3)
    assert commands[1][0] == "Valve6Way_2"
    assert commands[1][1] == "go_to_position"


def test_generate_wash_commands_valve_position_encoded_correctly():
    commands = generate_wash_commands(100, 300, 50, 150, 25, 75, 4)
    assert commands[1][2] == "position=4"


def test_generate_wash_commands_sync_always_last():
    commands = generate_wash_commands(100, 300, 50, 150, 25, 75, 3)
    assert commands[-1][0] == "SYNC"
    assert commands[-1][1] == "wait_for_pumps"


def test_generate_wash_commands_minimum_row_count_when_all_pumps_zero():
    # header + valve + SYNC(cosolvent) + SYNC(xylo) = 4 rows
    commands = generate_wash_commands(0, 0, 0, 0, 0, 0, 3)
    assert len(commands) == 4


def test_generate_wash_commands_maximum_row_count_when_all_pumps_nonzero():
    # header + valve + Tecan3_flush + SYNC(cosolvent) + Tecan1 + Tecan3 + Tecan2 + SYNC(xylo) = 8 rows
    commands = generate_wash_commands(100, 300, 50, 150, 25, 75, 3)
    assert len(commands) == 8


def test_generate_wash_pump2_included_when_nonzero():
    commands = generate_wash_commands(100, 300, 0, 0, 0, 0, 3)
    components = [cmd[0] for cmd in commands]
    assert "Tecan_pump_1" in components


def test_generate_wash_pump2_omitted_when_zero_flow_rate():
    commands = generate_wash_commands(0, 300, 0, 0, 0, 0, 3)
    components = [cmd[0] for cmd in commands]
    assert "Tecan_pump_1" not in components


def test_generate_wash_pump3_included_when_nonzero():
    commands = generate_wash_commands(0, 0, 50, 150, 0, 0, 3)
    components = [cmd[0] for cmd in commands]
    assert "Tecan_pump_3" in components


def test_generate_wash_pump3_omitted_when_zero_volume():
    commands = generate_wash_commands(0, 0, 50, 0, 0, 0, 3)
    components = [cmd[0] for cmd in commands]
    assert "Tecan_pump_3" not in components


def test_generate_wash_pump4_included_when_nonzero():
    commands = generate_wash_commands(0, 0, 0, 0, 25, 75, 3)
    components = [cmd[0] for cmd in commands]
    assert "Tricontinental_C24000_1" in components


def test_generate_wash_pump4_omitted_when_zero():
    commands = generate_wash_commands(0, 0, 0, 0, 0, 0, 3)
    components = [cmd[0] for cmd in commands]
    assert "Tricontinental_C24000_1" not in components


def test_generate_wash_commands_full_output_matches_expected():
    commands = generate_wash_commands(100, 300, 50, 150, 25, 75, 3)
    assert commands == _COMMANDS, f"Expected {_COMMANDS}, but got {commands}"