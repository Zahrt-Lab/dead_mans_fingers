# ------------------------------------------------------------------------------
# Software: AUTO_ZAHRT
# Copyright: (C) 2026 by Professor Andrew Zahrt
# This software is the intellectual property of Professor Andrew Zahrt
# Contributions by graduate students Scott Laverty and Joao are acknowledged.
# All rights reserved.
# ------------------------------------------------------------------------------

"""
Tests for production_run/extract_best_reaction_conditions.py

Verifies that the correct row is selected from a BO results CSV based on
a percent-yield threshold and maximum throughput.
"""

import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.append(str(Path(__file__).parent.parent.parent))
from production_run.extract_best_reaction_conditions import extract_best_reaction_conditions


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _write_bo_csv(tmp_path, rows: list[dict]) -> str:
    """Write a minimal BO results CSV to tmp_path and return its path string."""
    df = pd.DataFrame(rows)
    csv_path = str(tmp_path / "bo_results.csv")
    df.to_csv(csv_path, index=False)
    return csv_path


def _make_row(
    flow_rate=100.0,
    dilution_factor=0.5,
    temperature=25.0,
    co_solvent_valve_position=2,
    co_solvent_dilution_factor=0.1,
    light_intensity=80.0,
    percent_yield=85.0,
    throughput_nmol_per_min=20.0,
) -> dict:
    """Return a dict matching the BO results CSV column names."""
    return {
        "iteration": 1,
        "flow_rate": flow_rate,
        "dilution_factor": dilution_factor,
        "reactor_concentration_uM": 200.0,
        "temperature": temperature,
        "co_solvent_valve_position": co_solvent_valve_position,
        "co_solvent_dilution_factor": co_solvent_dilution_factor,
        "light_intensity": light_intensity,
        "target_volume": 3000,
        "reactant_wavelength": 409,
        "product_wavelength": 506,
        "average_absorbance_reactant": 0.8,
        "average_absorbance_product": 0.4,
        "percent_yield": percent_yield,
        "throughput_nmol_per_min": throughput_nmol_per_min,
        "timestamp": "2026-01-01 00:00:00",
        "status": "success",
        "error_message": "",
    }


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_returns_highest_throughput_above_threshold(tmp_path):
    """Among rows that pass the yield threshold, the one with the highest
    throughput should be returned."""
    rows = [
        _make_row(percent_yield=90.0, throughput_nmol_per_min=15.0, flow_rate=100.0),
        _make_row(percent_yield=85.0, throughput_nmol_per_min=30.0, flow_rate=200.0),  # winner
        _make_row(percent_yield=60.0, throughput_nmol_per_min=50.0, flow_rate=300.0),  # below threshold
    ]
    csv_path = _write_bo_csv(tmp_path, rows)

    (flow_rate, *_rest) = extract_best_reaction_conditions(csv_path, yield_threshold=80.0)

    assert flow_rate == pytest.approx(200.0)


def test_yield_threshold_filters_correctly(tmp_path):
    """Only the single row that passes the threshold should be returned."""
    rows = [
        _make_row(percent_yield=79.9, throughput_nmol_per_min=100.0, flow_rate=999.0),  # filtered out
        _make_row(percent_yield=80.0, throughput_nmol_per_min=10.0, flow_rate=150.0),   # passes
    ]
    csv_path = _write_bo_csv(tmp_path, rows)

    (flow_rate, *_rest) = extract_best_reaction_conditions(csv_path, yield_threshold=80.0)

    assert flow_rate == pytest.approx(150.0)


def test_all_rows_below_threshold_raises(tmp_path):
    """When no rows pass the yield threshold, idxmax() on an empty Series
    raises ValueError — verify the function propagates this clearly."""
    rows = [
        _make_row(percent_yield=50.0, throughput_nmol_per_min=20.0),
        _make_row(percent_yield=70.0, throughput_nmol_per_min=30.0),
    ]
    csv_path = _write_bo_csv(tmp_path, rows)

    with pytest.raises(ValueError):
        extract_best_reaction_conditions(csv_path, yield_threshold=80.0)


def test_return_tuple_values_match_csv_row(tmp_path):
    """All 7 returned values should match the expected row exactly."""
    rows = [
        _make_row(
            flow_rate=120.0,
            dilution_factor=0.3,
            temperature=40.0,
            co_solvent_valve_position=3,
            co_solvent_dilution_factor=0.15,
            light_intensity=75.0,
            percent_yield=90.0,
            throughput_nmol_per_min=25.0,
        )
    ]
    csv_path = _write_bo_csv(tmp_path, rows)

    (
        flow_rate,
        dilution_factor,
        temperature,
        cosolvent_valve_position,
        fraction_of_cosolvent,
        light_intensity,
        throughput,
    ) = extract_best_reaction_conditions(csv_path, yield_threshold=80.0)

    assert flow_rate == pytest.approx(120.0)
    assert dilution_factor == pytest.approx(0.3)
    assert temperature == pytest.approx(40.0)
    assert cosolvent_valve_position == pytest.approx(3.0)
    assert fraction_of_cosolvent == pytest.approx(0.15)
    assert light_intensity == pytest.approx(75.0)
    assert throughput == pytest.approx(25.0)


def test_exact_threshold_boundary_is_included(tmp_path):
    """A row at exactly the threshold value should pass the >= filter."""
    rows = [
        _make_row(percent_yield=80.0, throughput_nmol_per_min=10.0, flow_rate=150.0),
    ]
    csv_path = _write_bo_csv(tmp_path, rows)

    (flow_rate, *_rest) = extract_best_reaction_conditions(csv_path, yield_threshold=80.0)

    assert flow_rate == pytest.approx(150.0)
