# ------------------------------------------------------------------------------
# Software: dead_mans_fingers
# Copyright (c) 2026 Zahrt Research Group
#
# Contributions by Scott Laverty and Joao Albuquerque are acknowledged.
#
# Licensed under the MIT License. See the LICENSE file in the repository root.
# ------------------------------------------------------------------------------

"""
Test cases for utils/validate_state_classes.py
"""

import sys
from pathlib import Path

import pytest

sys.path.append(str(Path(__file__).parent.parent.parent))

from bayesian_optimizer.experiment_state import BoCampaignState, IterationState
from utils.validate_state_classes import validate_bo_campaign_state, validate_iteration_state

_REQUIRED_BO_PARAMS = {
    "base_directory": "./output",
    "xylopyridine_analogs_concentrations_uM": 1000.0,
    "total_volume_through_reactor_bed": 3000,
    "target_volume_through_reactor_bed": 2500,
    "reactant_wavelength": 409.0,
    "product_wavelength": 506.0,
    "reference_wavelength": 700.0,
    "blank_light_intensity_threshold": 200.0,
    "wavelength_for_blank_light_intensity_check": 600.0,
    "Fluorescent_Bayesian_Optimization_results_filename": "results.csv",
    "epsilon_reactant_at_lambda1_L_per_mol_cm": 11367.0,
    "epsilon_product_at_lambda2_L_per_mol_cm": 12994.57,
    "pathlength_cm": 1.0,
    "max_absorbance_concentration_uM_uv_detector": 88.0,
    "target_absorbance_in_the_uv_detector": 1.0,
}

_REQUIRED_TRIAL_CONDITIONS = {
    "flow_rate": 100.0,
    "dilution_factor": 0.3,
    "temperature": 40.0,
    "co_solvent_valve_position": 2,
    "co_solvent_dilution_factor": 0.1,
    "light_intensity": 50.0,
}


def make_valid_bo_state():
    state = BoCampaignState()
    state.update_bo_parameters(_REQUIRED_BO_PARAMS.copy())
    return state


def make_valid_iter_state():
    state = IterationState()
    state.update_iteration(1)
    state.update_trial_conditions(_REQUIRED_TRIAL_CONDITIONS.copy())
    return state


# --- BoCampaignState ---

def test_valid_bo_campaign_state_passes():
    validate_bo_campaign_state(make_valid_bo_state())


def test_bo_campaign_state_wrong_type_raises_type_error():
    with pytest.raises(TypeError, match="BoCampaignState"):
        validate_bo_campaign_state("not a state")


def test_bo_campaign_state_missing_key_raises():
    state = make_valid_bo_state()
    del state.bo_parameters["pathlength_cm"]
    with pytest.raises(ValueError, match="pathlength_cm"):
        validate_bo_campaign_state(state)


def test_bo_campaign_state_non_positive_noise_sem_percent_yield_raises():
    state = make_valid_bo_state()
    state.set_noise_sem(0.0, 1.0)
    with pytest.raises(ValueError, match="noise_sem_percent_yield"):
        validate_bo_campaign_state(state)


def test_bo_campaign_state_negative_noise_sem_percent_yield_raises():
    state = make_valid_bo_state()
    state.set_noise_sem(-1.0, 1.0)
    with pytest.raises(ValueError, match="noise_sem_percent_yield"):
        validate_bo_campaign_state(state)


def test_bo_campaign_state_non_positive_noise_sem_throughput_raises():
    state = make_valid_bo_state()
    state.set_noise_sem(1.0, 0.0)
    with pytest.raises(ValueError, match="noise_sem_throughput"):
        validate_bo_campaign_state(state)


def test_bo_campaign_state_negative_noise_sem_throughput_raises():
    state = make_valid_bo_state()
    state.set_noise_sem(1.0, -1.0)
    with pytest.raises(ValueError, match="noise_sem_throughput"):
        validate_bo_campaign_state(state)


def test_bo_campaign_state_invalid_simulation_mode_type_raises():
    state = make_valid_bo_state()
    state.simulation_mode = "yes"
    with pytest.raises(ValueError, match="simulation_mode"):
        validate_bo_campaign_state(state)


# --- IterationState ---

def test_valid_iteration_state_passes():
    validate_iteration_state(make_valid_iter_state())


def test_iteration_state_wrong_type_raises_type_error():
    with pytest.raises(TypeError, match="IterationState"):
        validate_iteration_state({"not": "a state"})


def test_iteration_state_negative_iteration_raises():
    state = make_valid_iter_state()
    state.update_iteration(-1)
    with pytest.raises(ValueError, match="iteration"):
        validate_iteration_state(state)


def test_iteration_state_zero_iteration_passes():
    state = make_valid_iter_state()
    state.update_iteration(0)
    validate_iteration_state(state)


def test_iteration_state_missing_trial_key_raises():
    state = make_valid_iter_state()
    trial_conditions = _REQUIRED_TRIAL_CONDITIONS.copy()
    del trial_conditions["light_intensity"]
    state.update_trial_conditions(trial_conditions)
    with pytest.raises(ValueError, match="light_intensity"):
        validate_iteration_state(state)


def test_iteration_state_negative_reactor_concentration_raises():
    state = make_valid_iter_state()
    state.update_reactor_bed_concentration_uM(-10.0)
    with pytest.raises(ValueError, match="reactor_bed_concentration_uM"):
        validate_iteration_state(state)


def test_iteration_state_zero_reactor_concentration_passes():
    state = make_valid_iter_state()
    state.update_reactor_bed_concentration_uM(0.0)
    validate_iteration_state(state)
