# ------------------------------------------------------------------------------
# Software: project_dead_mans_fingers
# Copyright: (C) 2026 by Professor Andrew Zahrt
# This software is the intellectual property of Professor Andrew Zahrt
# Contributions by graduate students Scott Laverty and Joao are acknowledged.
# All rights reserved.
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

_HEADER = ["Component", "Action", "Parameters", "Output", "Notes", "delay"]
    
    
_COMMANDS = [
    _HEADER,
    [
        "custom_light_box_1",
        "turn_on_light_box",
        f"",
        f"Turning on the custom light box for the experiment",
        "0.5",
    ],
    [
        "custom_light_box_1",
        "set_light_intensity",
        f"intensity=75.0, " f"intensity_id=1",
        f"Setting Light Intensity to 75.0 for the experiment",
        "0.5",
    ],
]

def test_generate_light_intensity_commands():
    # Example input parameters for the function
    light_intensity = 75.00  # Desired light intensity level (0-100)
    
    # Call the function to generate commands
    commands = generate_light_intensity_commands(light_intensity)

    # Assert that the generated commands match the expected commands
    assert commands == _COMMANDS, f"Expected {_COMMANDS}, but got {commands}"