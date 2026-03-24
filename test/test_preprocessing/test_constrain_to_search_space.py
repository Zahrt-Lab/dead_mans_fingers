# ------------------------------------------------------------------------------
# Software: project_dead_mans_fingers
# Copyright: (C) 2026 by Professor Andrew Zahrt
# This software is the intellectual property of Professor Andrew Zahrt
# Contributions by graduate students Scott Laverty and Joao are acknowledged.
# All rights reserved.
# ------------------------------------------------------------------------------

"""
Test cases for constrain_to_search_space.py function
"""
import pytest
import sys
from pathlib import Path

# Add the parent directory to the system path to import constrain_to_search_space
sys.path.append(str(Path(__file__).parent.parent.parent))
from preprocessing.constrain_to_search_space import constraint_to_search_space


def test_constrain_to_search_space_within_bounds():
    """
    Test parameters that are within the search space bounds should remain unchanged.
    """
    assert constraint_to_search_space(
        {
            "flow_rate": 100,
            "dilution_factor": 0.5,
            "temperature": 25,
            "co_solvent_valve_position": 3,
            "co_solvent_dilution_factor": 0.2,
            "light_intensity": 70,
        }
    ) == {
        "flow_rate": 100,
        "dilution_factor": 0.5,
        "temperature": 25,
        "co_solvent_valve_position": 3,
        "co_solvent_dilution_factor": 0.2,
        "light_intensity": 70,
    }


# def test_constrain_to_search_space_below_bounds():

# def test_constrain_to_search_space_above_bounds():

# def test_constrain_to_search_space_edge_cases():
