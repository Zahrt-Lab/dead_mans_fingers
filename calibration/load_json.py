# ------------------------------------------------------------------------------
# Software: dead_mans_fingers
# Copyright (c) 2026 Zahrt Research Group
#
# Contributions by Scott Laverty are acknowledged.
#
# Licensed under the MIT License. See the LICENSE file in the repository root.
# ------------------------------------------------------------------------------

''' This module contains functions to load experimental parameters from a JSON file.
The main function is `load_experimental_parameters`, which reads the JSON file and returns a dictionary of parameters.
'''
import json
from pathlib import Path

def load_experimental_parameters(json_file_path: Path) -> dict:
    """
    Load experimental parameters from a JSON file.

    Args:
        json_file_path (Path): The path to the JSON file containing the parameters.
    Returns:
        dict: A dictionary containing the experimental parameters.
    """
    try:

        with open(json_file_path, "r") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from {json_file_path}: {e}")
        return {}