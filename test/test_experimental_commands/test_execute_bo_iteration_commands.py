# ------------------------------------------------------------------------------
# Software: project_dead_mans_fingers
# Copyright: (C) 2026 by Professor Andrew Zahrt
# This software is the intellectual property of Professor Andrew Zahrt
# Contributions by graduate students Scott Laverty and Joao are acknowledged.
# All rights reserved.
# ------------------------------------------------------------------------------

"""
Test cases for experimental_commands/execute_bo_iteration_commands.py
"""

import pytest
from unittest.mock import patch

from bayesian_optimizer.experiment_state import BoCampaignState, IterationState
from experimental_commands.execute_bo_iteration_commands import (
    run_experiment,
    run_bayesian_optimization_iteration,
)

_PATCH_BASE = "experimental_commands.execute_bo_iteration_commands"

_MOCK_INSTRUMENT_PARAMS = {
    "flow_rate_pump1": 50.0, "volume_pump1": 250.0,
    "flow_rate_pump2": 30.0, "volume_pump2": 150.0,
    "flow_rate_pump3": 20.0, "volume_pump3": 100.0,
    "flow_rate_pump4": 0.0,  "volume_pump4": 0.0,
    "position_valve2": 2,
    "temperature": 50.0,
    "light_intensity": 80.0,
}


def make_bo_state(tmp_path, simulation_mode=True):
    state = BoCampaignState()
    state.set_simulation_mode(simulation_mode)
    state.update_bo_parameters({
        "base_directory": str(tmp_path),
        "xylopyridine_analogs_concentrations_uM": 1000.0,
        "total_volume_through_reactor_bed": 500,
        "target_volume_through_reactor_bed": 500,
        "reactant_wavelength": 409,
        "product_wavelength": 506,
        "Fluorescent_Bayesian_Optimization_results_filename": "results.csv",
        "command_path_base": str(tmp_path / "cmd"),
        "instrument_config": str(tmp_path / "Instrument_Config_File.csv"),
        "max_absorbance_concentration_uM_uv_detector": 88.0,
        "target_absorbance_in_the_uv_detector": 1.0,
    })
    return state


def make_iter_state():
    state = IterationState()
    state.update_iteration(1)
    state.update_trial_conditions({
        "flow_rate": 100.0,
        "dilution_factor": 0.5,
        "temperature": 50.0,
        "co_solvent_valve_position": 2.0,
        "co_solvent_dilution_factor": 0.2,
        "light_intensity": 80.0,
    })
    return state


@pytest.fixture
def mock_all():
    with patch(f"{_PATCH_BASE}.constrain_to_search_space", side_effect=lambda bo, it: it) as m_constrain, \
         patch(f"{_PATCH_BASE}.standardize_input", side_effect=lambda it: it) as m_std, \
         patch(f"{_PATCH_BASE}.parameters_to_commands", return_value=_MOCK_INSTRUMENT_PARAMS) as m_params, \
         patch(f"{_PATCH_BASE}.save_instrument_config_csv") as m_config, \
         patch(f"{_PATCH_BASE}.save_commands_csv") as m_commands, \
         patch(f"{_PATCH_BASE}.run_simulated_experiment", return_value="path/to/uv.csv") as m_sim, \
         patch(f"{_PATCH_BASE}.run_hardware_experiment", return_value="path/to/uv.csv") as m_hw, \
         patch(f"{_PATCH_BASE}.analyze_experiment_results", return_value=(0.8, 0.4, 50.0, 12.5)) as m_analyze, \
         patch(f"{_PATCH_BASE}.append_bayesian_experimental_results") as m_append:
        yield {
            "constrain": m_constrain, "standardize": m_std, "params": m_params,
            "config": m_config, "commands": m_commands,
            "sim": m_sim, "hw": m_hw,
            "analyze": m_analyze, "append": m_append,
        }


# --- run_experiment() ---

def test_simulation_mode_calls_run_simulated_experiment(tmp_path):
    bo = make_bo_state(tmp_path, simulation_mode=True)
    it = make_iter_state()
    with patch(f"{_PATCH_BASE}.run_simulated_experiment", return_value="sim.csv") as m_sim, \
         patch(f"{_PATCH_BASE}.run_hardware_experiment") as m_hw:
        run_experiment(bo, it)
        m_sim.assert_called_once()
        m_hw.assert_not_called()


def test_hardware_mode_calls_run_hardware_experiment(tmp_path):
    bo = make_bo_state(tmp_path, simulation_mode=False)
    it = make_iter_state()
    with patch(f"{_PATCH_BASE}.run_hardware_experiment", return_value="hw.csv") as m_hw, \
         patch(f"{_PATCH_BASE}.run_simulated_experiment") as m_sim:
        run_experiment(bo, it)
        m_hw.assert_called_once()
        m_sim.assert_not_called()


def test_run_experiment_returns_csv_path(tmp_path):
    bo = make_bo_state(tmp_path, simulation_mode=True)
    it = make_iter_state()
    with patch(f"{_PATCH_BASE}.run_simulated_experiment", return_value="path/to/results.csv"):
        result = run_experiment(bo, it)
    assert result == "path/to/results.csv"


# --- Cache tests ---

def test_cache_hit_returns_cached_result(mock_all, tmp_path):
    bo = make_bo_state(tmp_path)
    it = make_iter_state()
    cache_key = (100.0, 0.5, 50.0, 2.0, 0.2, 80.0)
    bo.results_cache[cache_key] = (42.0, 7.0)
    result = run_bayesian_optimization_iteration(bo, it)
    assert result == (42.0, 7.0)


def test_cache_hit_skips_experiment(mock_all, tmp_path):
    bo = make_bo_state(tmp_path)
    it = make_iter_state()
    cache_key = (100.0, 0.5, 50.0, 2.0, 0.2, 80.0)
    bo.results_cache[cache_key] = (42.0, 7.0)
    run_bayesian_optimization_iteration(bo, it)
    mock_all["sim"].assert_not_called()


def test_cache_miss_runs_full_pipeline(mock_all, tmp_path):
    bo = make_bo_state(tmp_path)
    run_bayesian_optimization_iteration(bo, make_iter_state())
    mock_all["sim"].assert_called_once()
    mock_all["analyze"].assert_called_once()
    mock_all["append"].assert_called_once()


def test_result_stored_in_cache_after_run(mock_all, tmp_path):
    bo = make_bo_state(tmp_path)
    run_bayesian_optimization_iteration(bo, make_iter_state())
    assert len(bo.results_cache) == 1
    cached = next(iter(bo.results_cache.values()))
    assert cached == (50.0, 12.5)


# --- Preparation tests ---

def test_reactor_concentration_calculated_correctly(mock_all, tmp_path):
    # dilution_factor=0.5, stock=1000 uM → reactor_conc = 500 uM
    bo = make_bo_state(tmp_path)
    it = make_iter_state()
    run_bayesian_optimization_iteration(bo, it)
    assert it.reactor_bed_concentration_uM == pytest.approx(500.0)


def test_parameters_to_commands_called(mock_all, tmp_path):
    bo = make_bo_state(tmp_path)
    run_bayesian_optimization_iteration(bo, make_iter_state())
    mock_all["params"].assert_called_once()


def test_save_commands_csv_called(mock_all, tmp_path):
    bo = make_bo_state(tmp_path)
    run_bayesian_optimization_iteration(bo, make_iter_state())
    mock_all["commands"].assert_called_once()


# --- Analysis tests ---

def test_analyze_experiment_results_called_with_csv_path(mock_all, tmp_path):
    bo = make_bo_state(tmp_path)
    run_bayesian_optimization_iteration(bo, make_iter_state())
    csv_arg = mock_all["analyze"].call_args.args[2]
    assert csv_arg == "path/to/uv.csv"


def test_append_results_called(mock_all, tmp_path):
    bo = make_bo_state(tmp_path)
    run_bayesian_optimization_iteration(bo, make_iter_state())
    mock_all["append"].assert_called_once()


def test_returns_two_tuple_of_floats(mock_all, tmp_path):
    bo = make_bo_state(tmp_path)
    result = run_bayesian_optimization_iteration(bo, make_iter_state())
    assert len(result) == 2
    assert all(isinstance(v, float) for v in result)


def test_returned_values_match_analysis_output(mock_all, tmp_path):
    bo = make_bo_state(tmp_path)
    result = run_bayesian_optimization_iteration(bo, make_iter_state())
    assert result == (50.0, 12.5)


def test_results_dict_key_fields(mock_all, tmp_path):
    bo = make_bo_state(tmp_path)
    it = make_iter_state()
    it.update_iteration(3)
    run_bayesian_optimization_iteration(bo, it)
    results_dict = mock_all["append"].call_args.args[0]
    assert results_dict["iteration"] == 3
    assert results_dict["flow_rate"] == 100.0
    assert results_dict["percent_yield"] == 50.0
    assert results_dict["throughput_nmol_per_min"] == 12.5


def test_results_dict_includes_light_intensity(mock_all, tmp_path):
    bo = make_bo_state(tmp_path)
    it = make_iter_state()
    run_bayesian_optimization_iteration(bo, it)
    results_dict = mock_all["append"].call_args.args[0]
    assert "light_intensity" in results_dict
    assert results_dict["light_intensity"] == 80.0


# --- Hardware ---

@pytest.mark.hardware
def test_hardware_mode_runs_hardware_experiment(tmp_path):
    pytest.skip("TODO: requires physical hardware connection")
