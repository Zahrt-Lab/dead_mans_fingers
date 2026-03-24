# ------------------------------------------------------------------------------
# Software: project_dead_mans_fingers
# Copyright: (C) 2026 by Professor Andrew Zahrt
# This software is the intellectual property of Professor Andrew Zahrt
# Contributions by graduate students Scott Laverty and Joao are acknowledged.
# All rights reserved.
# ------------------------------------------------------------------------------

"""
Test cases for constrain_to_search_space.py
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
    cosolvents_valve_position=(1, 6),
    co_solvent_dilution_factor=(0.0, 0.5),
    light_intensity=(0, 100),
):
    state = BoCampaignState()
    state.update_bo_parameters({
        "flow_rate": flow_rate,
        "dilution_factor": dilution_factor,
        "temperature": temperature,
        "cosolvents_valve_position": cosolvents_valve_position,
        "co_solvent_dilution_factor": co_solvent_dilution_factor,
        "light_intensity": light_intensity,
    })
    return state


def make_iter_state(flow_rate, dilution_factor, temperature,
                    co_solvent_valve_position, co_solvent_dilution_factor, light_intensity):
    state = IterationState()
    state.update_trial_conditions({
        "flow_rate": flow_rate,
        "dilution_factor": dilution_factor,
        "temperature": temperature,
        "co_solvent_valve_position": co_solvent_valve_position,
        "co_solvent_dilution_factor": co_solvent_dilution_factor,
        "light_intensity": light_intensity,
    })
    return state


def test_constrain_within_bounds_unchanged():
    bo_state = make_bo_state()
    iter_state = make_iter_state(200, 0.5, 50, 3, 0.2, 50)
    result = constrain_to_search_space(bo_state, iter_state)
    tc = result.trial_conditions
    assert tc["flow_rate"] == 200.0
    assert tc["dilution_factor"] == 0.5
    assert tc["temperature"] == 50.0
    assert tc["co_solvent_valve_position"] == 3.0
    assert tc["co_solvent_dilution_factor"] == 0.2
    assert tc["light_intensity"] == 50.0


def test_constrain_below_bounds_clamps_to_min():
    bo_state = make_bo_state()
    iter_state = make_iter_state(50, 0.05, 10, 1, 0.0, 0)
    result = constrain_to_search_space(bo_state, iter_state)
    tc = result.trial_conditions
    assert tc["flow_rate"] == 100.0       # clamped from 50 → min 100
    assert tc["dilution_factor"] == 0.1   # clamped from 0.05 → min 0.1
    assert tc["temperature"] == 20.0      # clamped from 10 → min 20


def test_constrain_above_bounds_clamps_to_max():
    bo_state = make_bo_state()
    iter_state = make_iter_state(400, 1.0, 80, 6, 0.5, 100)
    result = constrain_to_search_space(bo_state, iter_state)
    tc = result.trial_conditions
    assert tc["flow_rate"] == 300.0       # clamped from 400 → max 300
    assert tc["temperature"] == 80.0      # at max, unchanged
    assert tc["light_intensity"] == 100.0 # at max, unchanged


def test_constrain_returns_iteration_state():
    bo_state = make_bo_state()
    iter_state = make_iter_state(200, 0.5, 50, 3, 0.2, 50)
    result = constrain_to_search_space(bo_state, iter_state)
    assert isinstance(result, IterationState)


def test_constrain_wrong_number_of_parameters_raises():
    bo_state = make_bo_state()
    state = IterationState()
    state.update_trial_conditions({"flow_rate": 200})  # only 1 of 6 expected
    with pytest.raises(ValueError):
        constrain_to_search_space(bo_state, state)


def test_constrain_invalid_temperature_raises():
    # Use bounds that allow a value outside physical limit (0-100°C) after clamping
    # If bounds are set to (110, 120), clamping would keep the value at 110-120, which is > 100
    bo_state = make_bo_state(temperature=(110, 120))
    iter_state = make_iter_state(200, 0.5, 115, 3, 0.2, 50)
    with pytest.raises(ValueError):
        constrain_to_search_space(bo_state, iter_state)


def test_constrain_invalid_dilution_factor_bounds_raises():
    # dilution_max > 1 should raise on the physical constraint check
    bo_state = make_bo_state(dilution_factor=(0.1, 1.5))
    iter_state = make_iter_state(200, 1.2, 50, 3, 0.2, 50)
    with pytest.raises(ValueError):
        constrain_to_search_space(bo_state, iter_state)