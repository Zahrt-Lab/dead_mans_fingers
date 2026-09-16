# ------------------------------------------------------------------------------
# Software: dead_mans_fingers
# Copyright (c) 2026 Andrew Zahrt
#
# Contributions by Scott Laverty and Joao Albuquerque are acknowledged.
#
# Licensed under the MIT License. See the LICENSE file in the repository root.
# ------------------------------------------------------------------------------

"""
Test cases for parameters_to_commands.py
"""

import pytest
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))
from preprocessing.parameters_to_commands import parameters_to_commands


def make_trial_conditions(
    flow_rate=200,
    dilution_factor=0.5,
    temperature=50,
    light_intensity=50,
):
    return {
        "flow_rate": flow_rate,
        "dilution_factor": dilution_factor,
        "temperature": temperature,
        "light_intensity": light_intensity,
    }


def call(
    trial_conditions=None,
    total_volume=1000,
    xylopyridine_uM=100,
    max_abs_uM=200,
    target_abs=0.5,
):
    if trial_conditions is None:
        trial_conditions = make_trial_conditions()
    return parameters_to_commands(
        trial_conditions,
        total_volume,
        xylopyridine_uM,
        max_abs_uM,
        target_abs,
    )


def test_pump_volumes_sum_to_total():
    result = call(total_volume=1000)
    total = result["volume_pump1"] + result["volume_pump2"] + result["volume_pump3"]
    assert abs(total - 1000.0) < 0.01


def test_pump_flow_rates_sum_to_total_flow():
    result = call()
    total_flow = result["flow_rate_pump1"] + result["flow_rate_pump2"] + result["flow_rate_pump3"]
    assert abs(total_flow - 200.0) < 0.01


def test_pump4_zero_when_reactor_conc_below_cuvette_target():
    # reactor_conc = 0.5 * 100 = 50 uM, cuvette_target = 200 * 0.5 = 100 uM → no dilution needed
    result = call(
        trial_conditions=make_trial_conditions(dilution_factor=0.5),
        xylopyridine_uM=100,
        max_abs_uM=200,
        target_abs=0.5,
    )
    assert result["flow_rate_pump4"] == 0.0
    assert result["volume_pump4"] == 0.0


def test_pump4_nonzero_when_reactor_conc_above_cuvette_target():
    # reactor_conc = 0.9 * 100 = 90 uM, cuvette_target = 200 * 0.2 = 40 uM → dilution needed
    result = call(
        trial_conditions=make_trial_conditions(dilution_factor=0.9),
        xylopyridine_uM=100,
        max_abs_uM=200,
        target_abs=0.2,
    )
    assert result["flow_rate_pump4"] > 0.0
    assert result["volume_pump4"] > 0.0


def test_temperature_passed_through_and_light_intensity_inverted():
    # temperature passes through unchanged; light_intensity is inverted: input 0-100 → output 0-255 (0=brightest)
    result = call(trial_conditions=make_trial_conditions(temperature=65, light_intensity=80))
    assert result["temperature"] == 65.0
    # input 80 → (100-80)/100*255 = 51
    assert result["light_intensity"] == 51.0


def test_light_intensity_inversion_boundaries():
    # 100% (brightest) → 0; 0% (dimmest) → 255; 50% → 128
    assert call(trial_conditions=make_trial_conditions(light_intensity=100))["light_intensity"] == 0.0
    assert call(trial_conditions=make_trial_conditions(light_intensity=0))["light_intensity"] == 255.0
    assert call(trial_conditions=make_trial_conditions(light_intensity=50))["light_intensity"] == 128.0


def test_invalid_flow_rate_raises():
    with pytest.raises(ValueError):
        call(trial_conditions=make_trial_conditions(flow_rate=0))


def test_invalid_dilution_factor_raises():
    with pytest.raises(ValueError):
        call(trial_conditions=make_trial_conditions(dilution_factor=1.5))



def test_accepts_individual_scalars_without_state_objects():
    # Confirm the function no longer requires BoCampaignState / IterationState
    tc = make_trial_conditions()
    result = parameters_to_commands(tc, 1000, 100, 200, 0.5)
    assert "flow_rate_pump1" in result
