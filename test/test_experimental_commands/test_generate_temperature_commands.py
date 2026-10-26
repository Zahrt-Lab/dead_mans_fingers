# ------------------------------------------------------------------------------
# Software: dead_mans_fingers
# Copyright (c) 2026 Zahrt Research Group
#
# Contributions by Scott Laverty are acknowledged.
#
# Licensed under the MIT License. See the LICENSE file in the repository root.
# ------------------------------------------------------------------------------

"""
Test cases for experimental_commands/generate_temperature_commands.py
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))

from experimental_commands.generate_temperature_commands import generate_temperature_commands

_HEADER = ["Component", "Action", "Parameters", "Notes", "delay"]

_COMMANDS = [
    _HEADER,
    [
        "Temperature_1",
        "set_temperature",
        "temp=50, temp_id=1",
        "Setting Temperature to 50C for the experiment",
        "0.5",
    ],
    [
        "Temperature_1",
        "wait_convergence",
        "target_temp=50,tolerance=1,duration=60",
        "Waiting for temperature to converge to 50 before starting experiment",
        "0.5",
    ],
]


def test_generate_temperature_commands_returns_list_of_lists():
    commands = generate_temperature_commands(50)
    assert isinstance(commands, list)
    assert all(isinstance(command, list) for command in commands)


def test_generate_temperature_commands_header_is_correct():
    commands = generate_temperature_commands(50)
    assert commands[0] == _HEADER


def test_generate_temperature_commands_has_three_rows():
    commands = generate_temperature_commands(50)
    assert len(commands) == 3


def test_generate_temperature_commands_all_rows_have_correct_column_count():
    commands = generate_temperature_commands(50)
    for command in commands:
        assert len(command) == len(_HEADER), (
            f"Command {command} has {len(command)} columns, expected {len(_HEADER)}"
        )


def test_generate_temperature_set_temperature_command_is_correct():
    temperature = 50
    commands = generate_temperature_commands(temperature)
    assert commands[1][0] == "Temperature_1"
    assert commands[1][1] == "set_temperature"
    assert f"temp={temperature}" in commands[1][2]


def test_generate_temperature_wait_convergence_command_is_correct():
    temperature = 50
    commands = generate_temperature_commands(temperature)
    assert commands[2][0] == "Temperature_1"
    assert commands[2][1] == "wait_convergence"
    assert f"target_temp={temperature}" in commands[2][2]
    assert "tolerance=1" in commands[2][2]
    assert "duration=60" in commands[2][2]


def test_generate_temperature_commands_full_output_matches_expected():
    commands = generate_temperature_commands(50)
    assert commands == _COMMANDS, f"Expected {_COMMANDS}, but got {commands}"