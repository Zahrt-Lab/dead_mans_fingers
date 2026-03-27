# ------------------------------------------------------------------------------
# Software: project_dead_mans_fingers
# Copyright: (C) 2026 by Professor Andrew Zahrt
# This software is the intellectual property of Professor Andrew Zahrt
# Contributions by graduate students Scott Laverty and Joao are acknowledged.
# All rights reserved.
# -----------------------------------------------------------------------------

"""
Test cases for post_processing/calculate_concentration_in_reactor_bed.py
"""

import pytest

from bayesian_optimizer.experiment_state import BoCampaignState, IterationState
from post_processing.calculate_concentration_in_reactor_bed import (
    calculate_concentration_in_the_reactor_bed,
)


def make_bo_state(epsilon=100.0, pathlength=1.0):
    state = BoCampaignState()
    state.update_bo_parameters({
        "epsilon_product_at_lambda2_L_per_mol_cm": epsilon,
        "pathlength_cm": pathlength,
    })
    return state


def make_iter_state(vol_pump1=500, vol_pump2=300, vol_pump3=200, vol_pump4=0):
    state = IterationState()
    state.update_instrument_parameters({
        "volume_pump1": vol_pump1,
        "volume_pump2": vol_pump2,
        "volume_pump3": vol_pump3,
        "volume_pump4": vol_pump4,
    })
    return state


def test_returns_float():
    result = calculate_concentration_in_the_reactor_bed(0.5, make_bo_state(), make_iter_state())
    assert isinstance(result, float)


def test_zero_absorbance_returns_zero():
    result = calculate_concentration_in_the_reactor_bed(0.0, make_bo_state(), make_iter_state())
    assert result == 0.0


def test_no_pump4_dilution_returns_cuvette_concentration():
    # With no pump4 dilution, c_reactor == c_cuvette
    bo = make_bo_state(epsilon=100.0, pathlength=1.0)
    it = make_iter_state(vol_pump1=500, vol_pump2=300, vol_pump3=200, vol_pump4=0)
    result = calculate_concentration_in_the_reactor_bed(0.5, bo, it)
    # epsilon_uL = 100 * 1e6 = 1e8; c_cuvette = 0.5 / (1e8 * 1.0) = 5e-9
    assert result == pytest.approx(5e-9)


def test_pump4_dilution_increases_reactor_concentration():
    # With pump4 adding volume, detector sees diluted sample → c_reactor > c_cuvette
    bo = make_bo_state(epsilon=100.0, pathlength=1.0)
    no_dilution = calculate_concentration_in_the_reactor_bed(0.5, bo, make_iter_state(vol_pump4=0))
    with_dilution = calculate_concentration_in_the_reactor_bed(0.5, bo, make_iter_state(vol_pump4=1000))
    assert with_dilution > no_dilution


def test_negative_absorbance_clamped_to_zero():
    result = calculate_concentration_in_the_reactor_bed(-0.5, make_bo_state(), make_iter_state())
    assert result == 0.0


def test_negative_volume_pump4_raises_value_error():
    it = make_iter_state(vol_pump4=-100)
    with pytest.raises(ValueError):
        calculate_concentration_in_the_reactor_bed(0.5, make_bo_state(), it)


def test_beer_lambert_formula_correct():
    # Known values: A=1.0, epsilon=1e-6 L/(mol·cm) → epsilon_uL = 1.0 µL/(mol·cm), l=1.0 cm
    # c_cuvette = 1.0 / (1.0 * 1.0) = 1.0 mol/µL
    # No pump4: c_reactor == c_cuvette = 1.0
    bo = make_bo_state(epsilon=1e-6, pathlength=1.0)
    it = make_iter_state(vol_pump4=0)
    result = calculate_concentration_in_the_reactor_bed(1.0, bo, it)
    assert result == pytest.approx(1.0)
