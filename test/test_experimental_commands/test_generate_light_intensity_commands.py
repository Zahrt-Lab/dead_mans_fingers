# ------------------------------------------------------------------------------
# Software: dead_mans_fingers
# Copyright (c) 2026 Andrew Zahrt
#
# Contributions by Scott Laverty and Joao Albuquerque are acknowledged.
#
# Licensed under the MIT License. See the LICENSE file in the repository root.
# ------------------------------------------------------------------------------

"""
Test cases for experimental_commands/generate_set_light_intensity_commands.py
"""

import pytest
import sys
from pathlib import Path

# Add the project root directory to the Python path to allow imports
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(project_root))

from experimental_commands.generate_light_intensity_commands import generate_light_intensity_commands

_HEADER = ["Component", "Action", "Parameters", "Notes", "delay"]
    
    
_COMMANDS = [
    _HEADER,
    [
        "MirrorBox365nm_1",
        "set_dimmer",
        f"value={75.00}",
        f"Setting light intensity to {int(75.00)} for the experiment",
        0.5,
        ],
]

def test_generate_light_intensity_commands_returns_list_of_lists():
    commands = generate_light_intensity_commands(75.00)
    assert isinstance(commands, list)
    assert all(isinstance(command, list) for command in commands)

def test_generate_light_intensity_commands_header_is_correct():
    commands = generate_light_intensity_commands(75.00)
    assert commands[0] == _HEADER

def test_generate_light_intensity_commands_has_command_rows():
    commands = generate_light_intensity_commands(75.00)
    assert len(commands) == 2

def test_generate_light_intensity_commands_command_rows_have_correct_column_count():
    commands = generate_light_intensity_commands(75.00)
    for command in commands[1:]:  # Skip header
        assert len(command) == len(_HEADER), (
            f"Command {command} has {len(command)} columns, expected {len(_HEADER)}"
        )

def test_generate_light_intensity_output_is_correct():
    light_intensity = 75.00
    commands = generate_light_intensity_commands(light_intensity)
    output_light_intensity_str = commands[1][2].split(",")[0]
    output_light_intensity_float = round(float(output_light_intensity_str.replace("value=", "")), 2)
    assert output_light_intensity_float == light_intensity, (
        f"Expected output '{light_intensity}', but got '{output_light_intensity_float}'"
    )

def test_generate_light_intensity_commands():
    # Example input parameters for the function
    light_intensity = 75.00  # Desired light intensity level (0-100)
    
    # Call the function to generate commands
    commands = generate_light_intensity_commands(light_intensity)

    # Assert that the generated commands match the expected commands
    assert commands == _COMMANDS, f"Expected {_COMMANDS}, but got {commands}"
