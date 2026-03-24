# ------------------------------------------------------------------------------
# Software: project_dead_mans_fingers
# Copyright: (C) 2026 by Professor Andrew Zahrt
# This software is the intellectual property of Professor Andrew Zahrt
# Contributions by graduate students Scott Laverty and Joao are acknowledged.
# All rights reserved.
# ------------------------------------------------------------------------------

"""
Test cases for standardize_input.py
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))
from preprocessing.standardize_input import standardize_input
from bayesian_optimizer.experiment_state import IterationState


def test_standardize_rounds_to_two_decimal_places():
    state = IterationState(trial_conditions={"flow_rate": 100.12345, "temperature": 50.6789})
    result = standardize_input(state)
    assert result.trial_conditions["flow_rate"] == 100.12
    assert result.trial_conditions["temperature"] == 50.68


def test_standardize_custom_decimal_places():
    state = IterationState(trial_conditions={"flow_rate": 100.12345, "temperature": 50.6789})
    result = standardize_input(state, ndp=3)
    assert result.trial_conditions["flow_rate"] == 100.123
    assert result.trial_conditions["temperature"] == 50.679


def test_standardize_already_rounded_values():
    state = IterationState(trial_conditions={"flow_rate": 100.0, "temperature": 50.0})
    result = standardize_input(state)
    assert result.trial_conditions["flow_rate"] == 100.0
    assert result.trial_conditions["temperature"] == 50.0


def test_standardize_returns_same_iteration_state_object():
    state = IterationState(trial_conditions={"flow_rate": 200.555})
    result = standardize_input(state)
    assert result is state  # modifies and returns the same object


def test_standardize_all_trial_conditions():
    state = IterationState(trial_conditions={
        "flow_rate": 200.999,
        "dilution_factor": 0.33333,
        "temperature": 60.5555,
        "co_solvent_valve_position": 3.0,
        "co_solvent_dilution_factor": 0.19999,
        "light_intensity": 75.125,
    })
    result = standardize_input(state)
    assert result.trial_conditions["flow_rate"] == 201.0
    assert result.trial_conditions["dilution_factor"] == 0.33
    assert result.trial_conditions["temperature"] == 60.56
    assert result.trial_conditions["co_solvent_valve_position"] == 3.0
    assert result.trial_conditions["co_solvent_dilution_factor"] == 0.2
    assert result.trial_conditions["light_intensity"] == 75.12
