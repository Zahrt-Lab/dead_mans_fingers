# ------------------------------------------------------------------------------
# Software: dead_mans_fingers
# Copyright (c) 2026 Andrew Zahrt
#
# Contributions by Scott Laverty and Joao Albuquerque are acknowledged.
#
# Licensed under the MIT License. See the LICENSE file in the repository root.
# ------------------------------------------------------------------------------

"""
Test cases for constrain_to_search_space.py.
"""

import pytest
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))

from preprocessing.constrain_to_search_space import constrain_to_search_space
from bayesian_optimizer.experiment_state import BoCampaignState, IterationState


def make_bo_state(
    flow_rate=(100, 300),
    dilution_factor=(0.1, 1.0),
    temperature=(20, 80),
    light_intensity=(0, 100),
):
    state = BoCampaignState()
    state.update_bo_parameters({
        "flow_rate": flow_rate,
        "dilution_factor": dilution_factor,
        "temperature": temperature,
        "light_intensity": light_intensity,
    })
    return state


def make_iter_state(
    flow_rate,
    dilution_factor,
    temperature,
    light_intensity,
):
    state = IterationState()
    state.update_trial_conditions({
        "flow_rate": flow_rate,
        "dilution_factor": dilution_factor,
        "temperature": temperature,
        "light_intensity": light_intensity,
    })
    return state


def test_constrain_within_bounds_unchanged():
    bo_state = make_bo_state()
    iter_state = make_iter_state(200, 0.5, 50, 50)

    result = constrain_to_search_space(bo_state, iter_state)
    tc = result.trial_conditions

    assert tc["flow_rate"] == 200.0
    assert tc["dilution_factor"] == 0.5
    assert tc["temperature"] == 50.0
    assert tc["light_intensity"] == 50.0


def test_constrain_below_bounds_clamps_to_min():
    bo_state = make_bo_state()
    iter_state = make_iter_state(50, 0.05, 10, 0)

    result = constrain_to_search_space(bo_state, iter_state)
    tc = result.trial_conditions

    assert tc["flow_rate"] == 100.0
    assert tc["dilution_factor"] == 0.1
    assert tc["temperature"] == 20.0


def test_constrain_above_bounds_clamps_to_max():
    bo_state = make_bo_state()
    iter_state = make_iter_state(400, 1.0, 80, 100)

    result = constrain_to_search_space(bo_state, iter_state)
    tc = result.trial_conditions

    assert tc["flow_rate"] == 300.0
    assert tc["temperature"] == 80.0
    assert tc["light_intensity"] == 100.0


def test_constrain_returns_iteration_state():
    bo_state = make_bo_state()
    iter_state = make_iter_state(200, 0.5, 50, 50)

    result = constrain_to_search_space(bo_state, iter_state)

    assert isinstance(result, IterationState)


def test_constrain_wrong_number_of_parameters_raises():
    bo_state = make_bo_state()

    state = IterationState()
    state.update_trial_conditions({
        "flow_rate": 200
    })  # only 1 of 4 expected

    with pytest.raises(ValueError):
        constrain_to_search_space(bo_state, state)


def test_constrain_invalid_temperature_raises():
    bo_state = make_bo_state(temperature=(110, 120))
    iter_state = make_iter_state(200, 0.5, 115, 50)

    with pytest.raises(ValueError):
        constrain_to_search_space(bo_state, iter_state)


def test_constrain_invalid_dilution_factor_bounds_raises():
    bo_state = make_bo_state(dilution_factor=(0.1, 1.5))
    iter_state = make_iter_state(200, 1.2, 50, 50)

    with pytest.raises(ValueError):
        constrain_to_search_space(bo_state, iter_state)