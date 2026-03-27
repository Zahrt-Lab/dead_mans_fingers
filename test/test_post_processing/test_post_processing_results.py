# ------------------------------------------------------------------------------
# Software: project_dead_mans_fingers
# Copyright: (C) 2026 by Professor Andrew Zahrt
# This software is the intellectual property of Professor Andrew Zahrt
# Contributions by graduate students Scott Laverty and Joao are acknowledged.
# All rights reserved.
# -----------------------------------------------------------------------------

"""
Test cases for post_processing/post_processing_results.py
"""

from unittest.mock import patch

import pandas as pd
import pytest

from bayesian_optimizer.experiment_state import BoCampaignState, IterationState
from post_processing.post_processing_results import analyze_experiment_results

_CSV_PATH = "dummy/path/uv_recording.csv"

_MOCK_DF = pd.DataFrame({"Time(s)": [60, 90], "409": [0.8, 0.8], "506": [0.4, 0.4]})

_PATCH_BASE = "post_processing.post_processing_results"


def make_bo_state():
    state = BoCampaignState()
    state.update_bo_parameters({
        "target_volume_through_reactor_bed": 500,
        "reactant_wavelength": 409,
        "product_wavelength": 506,
        "epsilon_reactant_at_lambda1_L_per_mol_cm": 8000.0,
        "epsilon_product_at_lambda2_L_per_mol_cm": 5000.0,
        "pathlength_cm": 1.0,
    })
    return state


def make_iter_state():
    state = IterationState()
    state.update_trial_conditions({"flow_rate": 100})
    state.update_instrument_parameters({
        "flow_rate_pump1": 50,
        "flow_rate_pump2": 30,
        "flow_rate_pump3": 20,
    })
    state.reactor_bed_concentration_uM = 200.0
    return state


@pytest.fixture
def mock_all():
    with patch(f"{_PATCH_BASE}.post_process_uv_recording", return_value=_MOCK_DF) as m_uv, \
         patch(f"{_PATCH_BASE}.average_absorbance", side_effect=[0.8, 0.4]) as m_avg, \
         patch(f"{_PATCH_BASE}.calculate_percent_yield", return_value=50.0) as m_yield, \
         patch(f"{_PATCH_BASE}.calculate_concentration_in_the_reactor_bed", return_value=1e-9) as m_conc, \
         patch(f"{_PATCH_BASE}.calculate_product_throughput", return_value=12.5) as m_throughput:
        yield {
            "uv": m_uv, "avg": m_avg, "yield": m_yield,
            "conc": m_conc, "throughput": m_throughput,
        }


def test_returns_four_tuple_of_floats(mock_all):
    result = analyze_experiment_results(make_bo_state(), make_iter_state(), _CSV_PATH)
    assert len(result) == 4
    assert all(isinstance(v, float) for v in result)


def test_returned_values_match_mocked_outputs(mock_all):
    result = analyze_experiment_results(make_bo_state(), make_iter_state(), _CSV_PATH)
    assert result == (0.8, 0.4, 50.0, 12.5)


def test_post_process_uv_recording_called_with_correct_args(mock_all):
    analyze_experiment_results(make_bo_state(), make_iter_state(), _CSV_PATH)
    mock_all["uv"].assert_called_once_with(
        flow_rate=100,
        target_volume=500,
        uv_vis_absorbance_results_csv=_CSV_PATH,
        experiment_converged_early=False,
    )


def test_average_absorbance_called_twice(mock_all):
    analyze_experiment_results(make_bo_state(), make_iter_state(), _CSV_PATH)
    assert mock_all["avg"].call_count == 2


def test_calculate_percent_yield_called(mock_all):
    analyze_experiment_results(make_bo_state(), make_iter_state(), _CSV_PATH)
    mock_all["yield"].assert_called_once()


def test_calculate_concentration_called(mock_all):
    analyze_experiment_results(make_bo_state(), make_iter_state(), _CSV_PATH)
    mock_all["conc"].assert_called_once()


def test_calculate_throughput_called(mock_all):
    analyze_experiment_results(make_bo_state(), make_iter_state(), _CSV_PATH)
    mock_all["throughput"].assert_called_once()
