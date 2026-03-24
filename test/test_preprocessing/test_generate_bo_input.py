# ------------------------------------------------------------------------------
# Software: project_dead_mans_fingers
# Copyright: (C) 2026 by Professor Andrew Zahrt
# This software is the intellectual property of Professor Andrew Zahrt
# Contributions by graduate students Scott Laverty and Joao are acknowledged.
# All rights reserved.
# ------------------------------------------------------------------------------

"""
Test cases for generate_bo_input.py
"""

import json
import sys
from pathlib import Path

import pytest

sys.path.append(str(Path(__file__).parent.parent.parent))
from preprocessing.generate_bo_input import generate_bo_input_file


# Minimal complete-workflow JSON with two analogs for testing
_BASE_WORKFLOW = {
    "trials": 30,
    "total_volume_through_reactor_bed": 1000,
    "target_volume_through_reactor_bed": 800,
    "base_directory": "",  # filled in by tests using tmp_path
    "name_of_xylopyridine_analogs_stock_solutions": ["Analog_1", "Analog_2"],
    "name_of_stock_solution2": "HCl",
    "name_of_co-solvent_stock_solutions": ["MeOH", "EtOH"],
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
    "xylopyridine_analogs_concentrations_uM": [100, 150],
    "target_absorbance_in_the_uv_detector": [0.5, 0.4],
    "max_absorbance_concentration_uM_uv_detector": [200, 250],
    "reactant_wavelength": [300, 310],
    "product_wavelength": [400, 410],
    "epsilon_reactant_at_lambda1_L_per_mol_cm": [1000, 1100],
    "epsilon_product_at_lambda1_L_per_mol_cm": [500, 550],
    "epsilon_reactant_at_lambda2_L_per_mol_cm": [800, 850],
    "epsilon_product_at_lambda2_L_per_mol_cm": [400, 450],
    "pathlength_cm": 1.0,
    "product_run": False,
    "production_run_quantity_nmol": 0,
}


def write_workflow_json(tmp_path, overrides=None):
    workflow = dict(_BASE_WORKFLOW)
    workflow["base_directory"] = str(tmp_path)
    if overrides:
        workflow.update(overrides)
    json_path = tmp_path / "complete_workflow.json"
    json_path.write_text(json.dumps(workflow))
    return str(json_path)


def test_generate_bo_input_returns_dict_and_path(tmp_path):
    json_path = write_workflow_json(tmp_path)
    result_dict, result_path = generate_bo_input_file(str(json_path), "Analog_1")
    assert isinstance(result_dict, dict)
    assert isinstance(result_path, str)


def test_generate_bo_input_removes_production_keys(tmp_path):
    json_path = write_workflow_json(tmp_path)
    result_dict, _ = generate_bo_input_file(str(json_path), "Analog_1")
    assert "product_run" not in result_dict
    assert "production_run_quantity_nmol" not in result_dict


def test_generate_bo_input_sets_analog_specific_fields(tmp_path):
    json_path = write_workflow_json(tmp_path)
    result_dict, _ = generate_bo_input_file(str(json_path), "Analog_1")
    assert result_dict["name_of_xylopyridine_analogs_to_optimize"] == "Analog_1"
    assert result_dict["xylopyridine_analog_index"] == 0
    assert result_dict["xylopyridine_analogs_concentrations_uM"] == 100
    assert result_dict["reactant_wavelength"] == 300
    assert result_dict["product_wavelength"] == 400


def test_generate_bo_input_second_analog_uses_correct_index(tmp_path):
    json_path = write_workflow_json(tmp_path)
    result_dict, _ = generate_bo_input_file(str(json_path), "Analog_2")
    assert result_dict["xylopyridine_analog_index"] == 1
    assert result_dict["xylopyridine_analogs_concentrations_uM"] == 150
    assert result_dict["reactant_wavelength"] == 310


def test_generate_bo_input_updates_base_directory(tmp_path):
    json_path = write_workflow_json(tmp_path)
    result_dict, _ = generate_bo_input_file(str(json_path), "Analog_1")
    assert result_dict["base_directory"].endswith("Analog_1/bo_campaign")


def test_generate_bo_input_sets_results_filename(tmp_path):
    json_path = write_workflow_json(tmp_path)
    result_dict, _ = generate_bo_input_file(str(json_path), "Analog_1")
    assert result_dict["Fluorescent_Bayesian_Optimization_results_filename"] == \
        "BO_Results_Analog_1_results.csv"


def test_generate_bo_input_saves_json_file(tmp_path):
    json_path = write_workflow_json(tmp_path)
    _, result_path = generate_bo_input_file(str(json_path), "Analog_1")
    assert Path(result_path).exists()
    saved = json.loads(Path(result_path).read_text())
    assert saved["name_of_xylopyridine_analogs_to_optimize"] == "Analog_1"
