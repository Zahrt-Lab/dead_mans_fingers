# ------------------------------------------------------------------------------
# Software: project_dead_mans_fingers
# Copyright: (C) 2026 by Professor Andrew Zahrt
# This software is the intellectual property of Professor Andrew Zahrt
# Contributions by graduate students Scott Laverty and Joao are acknowledged.
# All rights reserved.
# ------------------------------------------------------------------------------

"""
Test cases for experimental_parameters.py
"""

import pytest
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))
from preprocessing.experimental_parameters import (
    load_experimental_parameters,
    check_required_complete_workflow_parameters,
    check_required_bo_campaign_parameters,
    check_required_production_run_parameters,
)


# --- load_experimental_parameters ---

def test_load_experimental_parameters_valid_dict():
    params = {"trials": 30, "flow_rate": [100, 300]}
    result = load_experimental_parameters(params)
    assert result == params


def test_load_experimental_parameters_empty_dict():
    result = load_experimental_parameters({})
    assert result == {}


def test_load_experimental_parameters_raises_on_non_dict():
    with pytest.raises(TypeError):
        load_experimental_parameters("not_a_dict")
    with pytest.raises(TypeError):
        load_experimental_parameters([1, 2, 3])
    with pytest.raises(TypeError):
        load_experimental_parameters(42)


# --- check_required_bo_campaign_parameters ---

# TODO: Is this the right set of valid parameters using in BO campaign?
# Need to doubl check
# Minimal dict with all required BO campaign keys
_VALID_BO_PARAMS = {
    "trials": 30,
    "total_volume_through_reactor_bed": 1000,
    "target_volume_through_reactor_bed": 800,
    "base_directory": "/some/path",
    "name_of_xylopyridine_analogs_stock_solutions": ["Analog_1"],
    "name_of_stock_solution2": "HCl",
    "name_of_co-solvent_stock_solutions": ["MeOH"],
    "name_of_stock_solution4": "HCl",
    "pump1_xylopyridine_analogs_volume_stock_solution": 50,
    "pump2_0.1M_HCl_water_volume_stock_solution": 50,
    "pump3_co-solvents_volume_stock_solutions": 50,
    "pump4_0.1M_HCl_water_volume_stock_solution": 50,
    "minimum_volume_required": 2000,
    "Fluorescent_Bayesian_Optimization_results_filename_prefix": "BO_Results",
    "flow_rate": [100, 300],
    "dilution_factor": [0.1, 1.0],
    "temperature": [20, 80],
    "cosolvents_valve_position": [1, 6],
    "co_solvent_dilution_factor": [0.0, 0.5],
    "light_intensity": [0, 100],
    "xylopyridine_analogs_concentrations_uM": 100,
    "target_absorbance_in_the_uv_detector": 0.5,
    "max_absorbance_concentration_uM_uv_detector": 200,
    "reactant_wavelength": 300,
    "product_wavelength": 400,
    "epsilon_reactant_at_lambda1_L_per_mol_cm": 1000,
    "epsilon_product_at_lambda1_L_per_mol_cm": 500,
    "epsilon_reactant_at_lambda2_L_per_mol_cm": 800,
    "epsilon_product_at_lambda2_L_per_mol_cm": 400,
    "pathlength_cm": 1.0,
    "Fluorescent_Bayesian_Optimization_results_filename": "BO_Results_Analog_1.csv",
    "name_of_xylopyridine_analogs_to_optimize": "Analog_1",
    "xylopyridine_analog_index": 0,
}


def test_check_required_bo_campaign_parameters_valid():
    check_required_bo_campaign_parameters(_VALID_BO_PARAMS)  # should not raise


def test_check_required_bo_campaign_parameters_missing_key():
    params = dict(_VALID_BO_PARAMS)
    del params["trials"]
    with pytest.raises(KeyError):
        check_required_bo_campaign_parameters(params)


def test_check_required_bo_campaign_parameters_missing_multiple_keys():
    params = dict(_VALID_BO_PARAMS)
    del params["flow_rate"]
    del params["temperature"]
    with pytest.raises(KeyError):
        check_required_bo_campaign_parameters(params)


def test_check_required_bo_campaign_parameters_empty_dict():
    with pytest.raises(KeyError):
        check_required_bo_campaign_parameters({})


# --- check_required_production_run_parameters ---

def test_check_required_production_run_parameters_is_placeholder():
    # Function is a placeholder with no checks yet; should always return None
    assert check_required_production_run_parameters({}) is None
    assert check_required_production_run_parameters({"any_key": "any_value"}) is None