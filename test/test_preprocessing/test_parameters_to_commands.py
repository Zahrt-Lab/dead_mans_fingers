# ------------------------------------------------------------------------------
# Software: project_dead_mans_fingers
# Copyright: (C) 2026 by Professor Andrew Zahrt
# This software is the intellectual property of Professor Andrew Zahrt
# Contributions by graduate students Scott Laverty and Joao are acknowledged.
# All rights reserved.
# ------------------------------------------------------------------------------

"""
Test cases for parameters_to_commands.py
"""

import pytest
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))
from preprocessing.parameters_to_commands import parameters_to_commands
from bayesian_optimizer.experiment_state import BoCampaignState, IterationState


def make_bo_state(
    total_volume=1000,
    xylopyridine_uM=100,
    max_abs_uM=200,
    target_abs=0.5,
):
    state = BoCampaignState()
    state.update_bo_parameters({
        "total_volume_through_reactor_bed": total_volume,
        "xylopyridine_analogs_concentrations_uM": xylopyridine_uM,
        "max_absorbance_concentration_uM_uv_detector": max_abs_uM,
        "target_absorbance_in_the_uv_detector": target_abs,
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


def test_pump_volumes_sum_to_total():
    bo_state = make_bo_state(total_volume=1000)
    iter_state = make_iter_state(200, 0.5, 50, 3, 0.2, 50)
    result = parameters_to_commands(bo_state, iter_state)
    total = result["volume_pump1"] + result["volume_pump2"] + result["volume_pump3"]
    assert abs(total - 1000.0) < 0.01


def test_pump_flow_rates_sum_to_total_flow():
    bo_state = make_bo_state()
    iter_state = make_iter_state(200, 0.5, 50, 3, 0.2, 50)
    result = parameters_to_commands(bo_state, iter_state)
    total_flow = result["flow_rate_pump1"] + result["flow_rate_pump2"] + result["flow_rate_pump3"]
    assert abs(total_flow - 200.0) < 0.01


def test_pump4_zero_when_reactor_conc_below_cuvette_target():
    # reactor_conc = 0.5 * 100 = 50 uM, cuvette_target = 200 * 0.5 = 100 uM → no dilution needed
    bo_state = make_bo_state(xylopyridine_uM=100, max_abs_uM=200, target_abs=0.5)
    iter_state = make_iter_state(200, 0.5, 50, 3, 0.2, 50)
    result = parameters_to_commands(bo_state, iter_state)
    assert result["flow_rate_pump4"] == 0.0
    assert result["volume_pump4"] == 0.0


def test_pump4_nonzero_when_reactor_conc_above_cuvette_target():
    # reactor_conc = 0.9 * 100 = 90 uM, cuvette_target = 200 * 0.2 = 40 uM → dilution needed
    bo_state = make_bo_state(xylopyridine_uM=100, max_abs_uM=200, target_abs=0.2)
    iter_state = make_iter_state(200, 0.9, 50, 3, 0.0, 50)
    result = parameters_to_commands(bo_state, iter_state)
    assert result["flow_rate_pump4"] > 0.0
    assert result["volume_pump4"] > 0.0


def test_temperature_and_light_intensity_passed_through():
    bo_state = make_bo_state()
    iter_state = make_iter_state(200, 0.5, 65, 3, 0.2, 80)
    result = parameters_to_commands(bo_state, iter_state)
    assert result["temperature"] == 65.0
    assert result["light_intensity"] == 80.0


def test_valve_position_passed_through():
    bo_state = make_bo_state()
    iter_state = make_iter_state(200, 0.5, 50, 4, 0.2, 50)
    result = parameters_to_commands(bo_state, iter_state)
    assert result["position_valve2"] == 4


def test_invalid_flow_rate_raises():
    bo_state = make_bo_state()
    iter_state = make_iter_state(0, 0.5, 50, 3, 0.2, 50)
    with pytest.raises(ValueError):
        parameters_to_commands(bo_state, iter_state)


def test_invalid_dilution_factor_raises():
    bo_state = make_bo_state()
    iter_state = make_iter_state(200, 1.5, 50, 3, 0.2, 50)
    with pytest.raises(ValueError):
        parameters_to_commands(bo_state, iter_state)


def test_invalid_valve_position_raises():
    bo_state = make_bo_state()
    iter_state = make_iter_state(200, 0.5, 50, 7, 0.2, 50)
    with pytest.raises(ValueError):
        parameters_to_commands(bo_state, iter_state)


def test_cosolvent_exceeds_remainder_raises():
    # co_solvent_dilution_factor (0.6) > (1 - dilution_factor) (0.5)
    bo_state = make_bo_state()
    iter_state = make_iter_state(200, 0.5, 50, 3, 0.6, 50)
    with pytest.raises(ValueError):
        parameters_to_commands(bo_state, iter_state)