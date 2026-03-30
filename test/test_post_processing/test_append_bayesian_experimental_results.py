# ------------------------------------------------------------------------------
# Software: project_dead_mans_fingers
# Copyright: (C) 2026 by Professor Andrew Zahrt
# This software is the intellectual property of Professor Andrew Zahrt
# Contributions by graduate students Scott Laverty and Joao are acknowledged.
# All rights reserved.
# -----------------------------------------------------------------------------

"""
Test cases for post_processing/append_bayesian_experimental_results.py
"""

import csv

import pytest

from bayesian_optimizer.experiment_state import BoCampaignState
from post_processing.append_bayesian_experimental_results import (
    append_bayesian_experimental_results,
)

_SAMPLE_RESULTS = {
    "iteration": 1,
    "flow_rate": 100,
    "dilution_factor": 0.5,
    "reactor_concentration_uM": 200.0,
    "temperature": 25,
    "co_solvent_valve_position": 2,
    "co_solvent_dilution_factor": 0.1,
    "light_intensity": 80,
    "target_volume": 500,
    "reactant_wavelength": 409,
    "product_wavelength": 506,
    "average_absorbance_reactant": 0.8,
    "average_absorbance_product": 0.4,
    "percent_yield": 50.0,
    "throughput_nmol_per_min": 12.5,
    "timestamp": "2026-01-01 00:00:00",
    "status": "success",
    "error_message": "",
}


def make_bo_state(tmp_path):
    state = BoCampaignState()
    state.update_bo_parameters({
        "base_directory": str(tmp_path),
        "Fluorescent_Bayesian_Optimization_results_filename": "results.csv",
    })
    return state


def test_creates_file_when_none_exists(tmp_path):
    bo = make_bo_state(tmp_path)
    append_bayesian_experimental_results(_SAMPLE_RESULTS, bo)
    assert (tmp_path / "results.csv").exists()


def test_writes_header_on_new_file(tmp_path):
    bo = make_bo_state(tmp_path)
    append_bayesian_experimental_results(_SAMPLE_RESULTS, bo)
    with open(tmp_path / "results.csv") as f:
        reader = csv.reader(f)
        header = next(reader)
    assert header[0] == "iteration"


def test_appends_row_to_existing_file(tmp_path):
    bo = make_bo_state(tmp_path)
    append_bayesian_experimental_results(_SAMPLE_RESULTS, bo)
    append_bayesian_experimental_results(_SAMPLE_RESULTS, bo)
    with open(tmp_path / "results.csv") as f:
        lines = f.readlines()
    assert len(lines) == 3  # header + 2 data rows


def test_header_not_duplicated_on_append(tmp_path):
    bo = make_bo_state(tmp_path)
    append_bayesian_experimental_results(_SAMPLE_RESULTS, bo)
    append_bayesian_experimental_results(_SAMPLE_RESULTS, bo)
    append_bayesian_experimental_results(_SAMPLE_RESULTS, bo)
    with open(tmp_path / "results.csv") as f:
        reader = csv.reader(f)
        rows = list(reader)
    header_count = sum(1 for row in rows if row and row[0] == "iteration")
    assert header_count == 1


def test_row_values_match_results_dict(tmp_path):
    bo = make_bo_state(tmp_path)
    append_bayesian_experimental_results(_SAMPLE_RESULTS, bo)
    with open(tmp_path / "results.csv") as f:
        reader = csv.DictReader(f)
        row = next(reader)
    assert float(row["percent_yield"]) == pytest.approx(50.0)
    assert float(row["throughput_nmol_per_min"]) == pytest.approx(12.5)


def test_all_18_columns_present_in_header(tmp_path):
    bo = make_bo_state(tmp_path)
    append_bayesian_experimental_results(_SAMPLE_RESULTS, bo)
    with open(tmp_path / "results.csv") as f:
        reader = csv.reader(f)
        header = next(reader)
    assert len(header) == 18
