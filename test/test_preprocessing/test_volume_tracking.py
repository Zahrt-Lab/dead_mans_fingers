# ------------------------------------------------------------------------------
# Software: dead_mans_fingers
# Copyright (c) 2026 Zahrt Research Group
#
# Contributions by Scott Laverty and Joao Albuquerque are acknowledged.
#
# Licensed under the MIT License. See the LICENSE file in the repository root.
# ------------------------------------------------------------------------------

"""
Tests for preprocessing/volume_tracking.py

Pump 1 and Pump 3 use 6-way selector valves — each position is a separate
reservoir with its own volume.  Only the active position is decremented each
iteration.
"""

import csv
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from bayesian_optimizer.experiment_state import BoCampaignState
from preprocessing.volume_tracking import (
    calculate_volumes_used,
    check_and_update_all_volumes,
    initialize_volume_state,
    load_volume_state_json,
    save_volume_log_csv,
    save_volume_state_json,
)
from utils.experiment_aborted import ExperimentAborted


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

_ANALOG_NAMES = [
    "Xylopyridine_Analog_1",
    "Xylopyridine_Analog_2",
    "Xylopyridine_Analog_3",
    "Xylopyridine_Analog_4",
    "Xylopyridine_Analog_5",
]
_COSOLVENT_NAMES = ["Ethanol", "Acetonitrile", "THF", "Isopropanol", "DMF", "DMSO"]


def _make_instrument_parameters(
    pump1=390.0,
    pump2=2100.0,
    pump3=510.0,
    pump4=0.0,
):
    return {
        "volume_pump1": pump1,
        "volume_pump2": pump2,
        "volume_pump3": pump3,
        "volume_pump4": pump4,
        "flow_rate_pump1": 26.0,
        "flow_rate_pump2": 140.0,
        "flow_rate_pump3": 34.0,
        "flow_rate_pump4": 0.0,
        "position_valve2": 1,
        "temperature": 40.0,
        "light_intensity": 50.0,
    }


def _make_bo_campaign_state(
    pump1_vols=None,
    pump2_vol=200000.0,
    pump3_vols=None,
    pump4_vol=200000.0,
    waste_vol=0.0,
    waste_max=4_000_000.0,
    waste_buffer=1_000_000.0,
    minimum_reserve=2000.0,
    analog_index=0,
) -> BoCampaignState:
    if pump1_vols is None:
        pump1_vols = [18000.0] * 5
    if pump3_vols is None:
        pump3_vols = [18000.0] * 6

    state = BoCampaignState()
    state.update_bo_parameters(
        {
            "minimum_volume_required": minimum_reserve,
            "waste_max_volume_uL": waste_max,
            "waste_buffer_volume_uL": waste_buffer,
            "xylopyridine_analog_index": analog_index,
            "name_of_xylopyridine_analogs_stock_solutions": _ANALOG_NAMES,
        }
    )
    state.update_volume_stock_solutions(
        {
            "pump1_volumes_uL": list(pump1_vols),
            "pump2_volume_uL": pump2_vol,
            "pump3_volumes_uL": list(pump3_vols),
            "pump4_volume_uL": pump4_vol,
        }
    )
    state.update_waste_volume(waste_vol)
    return state


# ---------------------------------------------------------------------------
# calculate_volumes_used
# ---------------------------------------------------------------------------

def test_calculate_volumes_used():
    """With D_cosolvent=0 all wash goes to pump2, pump3 wash=0."""
    params = _make_instrument_parameters(pump1=390, pump2=2610, pump3=0, pump4=0)
    result = calculate_volumes_used(params)

    assert result["pump1"] == pytest.approx(390.0)
    assert result["pump2"] == pytest.approx(2610.0 + 6000.0)   # wash = 6000*(1-0)
    assert result["pump3"] == pytest.approx(0.0)                # wash = 6000*0
    assert result["pump4"] == pytest.approx(3000.0)             # 0 + 3000 wash

def test_calculate_volumes_used_waste_is_sum():
    """Waste equals the sum of all four pump volumes consumed."""
    params = _make_instrument_parameters(pump1=390, pump2=2100, pump3=510, pump4=0)
    result = calculate_volumes_used(params)

    expected_waste = result["pump1"] + result["pump2"] + result["pump3"] + result["pump4"]
    assert result["waste"] == pytest.approx(expected_waste)


# ---------------------------------------------------------------------------
# check_and_update_all_volumes — selector valve behaviour
# ---------------------------------------------------------------------------

def test_only_active_analog_position_decremented():
    """Pump 1: only the analog at xylopyridine_analog_index is decremented."""
    state = _make_bo_campaign_state(analog_index=2)
    params = _make_instrument_parameters(pump1=500)
    volumes_used = calculate_volumes_used(params)

    check_and_update_all_volumes(
        state, volumes_used, iteration=1, interactive=False
    )

    vols = state.volume_stock_solutions["pump1_volumes_uL"]
    assert vols[2] == pytest.approx(18000.0 - volumes_used["pump1"])  # active
    assert vols[0] == pytest.approx(18000.0)  # untouched
    assert vols[1] == pytest.approx(18000.0)  # untouched
    assert vols[3] == pytest.approx(18000.0)  # untouched
    assert vols[4] == pytest.approx(18000.0)  # untouched

# ---------------------------------------------------------------------------
# check_and_update_all_volumes — error conditions
# ---------------------------------------------------------------------------

def test_check_and_update_all_volumes_sufficient():
    """Volumes update correctly and waste accumulates when all stocks are ample."""
    state = _make_bo_campaign_state()
    params = _make_instrument_parameters()
    volumes_used = calculate_volumes_used(params)

    check_and_update_all_volumes(
        state, volumes_used, iteration=1, interactive=False
    )

    assert state.volume_stock_solutions["pump1_volumes_uL"][0] == pytest.approx(
        18000.0 - volumes_used["pump1"]
    )
    assert state.waste_volume_uL == pytest.approx(volumes_used["waste"])


def test_insufficient_active_pump1_raises():
    """ExperimentAborted raised when the active pump1 reservoir is too low."""
    low_vols = [18000.0] * 5
    low_vols[0] = 100.0  # active analog has almost nothing
    state = _make_bo_campaign_state(pump1_vols=low_vols, analog_index=0)
    params = _make_instrument_parameters(pump1=390)
    volumes_used = calculate_volumes_used(params)

    with pytest.raises(ExperimentAborted):
        check_and_update_all_volumes(
            state, volumes_used, iteration=1, interactive=False
        )


def test_sufficient_inactive_pump1_does_not_raise():
    """No error when inactive reservoirs are low — only the active one matters."""
    low_vols = [100.0] * 5
    low_vols[2] = 18000.0  # only position 2 (index 2) is full
    state = _make_bo_campaign_state(pump1_vols=low_vols, analog_index=2)
    params = _make_instrument_parameters(pump1=390)
    volumes_used = calculate_volumes_used(params)

    # Should not raise — active position has plenty
    check_and_update_all_volumes(
        state, volumes_used, iteration=1, interactive=False
    )

def test_check_and_update_all_volumes_waste_full():
    """ExperimentAborted raised when waste container is nearly full."""
    state = _make_bo_campaign_state(waste_vol=3_500_000.0)
    params = _make_instrument_parameters()
    volumes_used = calculate_volumes_used(params)

    with pytest.raises(ExperimentAborted):
        check_and_update_all_volumes(
            state, volumes_used, iteration=1, interactive=False
        )


# ---------------------------------------------------------------------------
# Volume log
# ---------------------------------------------------------------------------

def test_volume_log_entry_appended():
    """One log entry added per call, recording active analog and co-solvent names."""
    state = _make_bo_campaign_state(analog_index=1)
    params = _make_instrument_parameters()
    volumes_used = calculate_volumes_used(params)

    assert len(state.volume_log) == 0
    check_and_update_all_volumes(
        state, volumes_used, iteration=3, interactive=False
    )
    assert len(state.volume_log) == 1
    entry = state.volume_log[0]
    assert entry["iteration"] == 3
    assert entry["pump1_active_analog"] == "Xylopyridine_Analog_2"   # index 1        # position 2
    assert "pump1_remaining_uL" in entry
    assert "waste_total_uL" in entry


# ---------------------------------------------------------------------------
# save / load volume_state.json
# ---------------------------------------------------------------------------

def test_save_and_load_volume_state_json(tmp_path):
    """Round-trip save → load preserves lists for pump1/pump3 and scalars for pump2/pump4."""
    state = _make_bo_campaign_state(
        pump1_vols=[12000.0, 11000.0, 10000.0, 9000.0, 8000.0],
        pump2_vol=80000.0,
        pump3_vols=[7000.0, 6000.0, 5000.0, 4000.0, 3000.0, 2000.0],
        pump4_vol=90000.0,
        waste_vol=500000.0,
    )
    out = str(tmp_path / "volume_state.json")
    save_volume_state_json(state, out)

    loaded = load_volume_state_json(out)
    assert loaded is not None
    assert loaded["pump1_volumes_uL"] == pytest.approx([12000, 11000, 10000, 9000, 8000])
    assert loaded["pump2_volume_uL"] == pytest.approx(80000.0)
    assert loaded["pump3_volumes_uL"] == pytest.approx([7000, 6000, 5000, 4000, 3000, 2000])
    assert loaded["pump4_volume_uL"] == pytest.approx(90000.0)
    assert loaded["waste_volume_uL"] == pytest.approx(500000.0)


def test_load_volume_state_json_missing_file(tmp_path):
    """Returns None when the file does not exist."""
    result = load_volume_state_json(str(tmp_path / "nonexistent.json"))
    assert result is None


# ---------------------------------------------------------------------------
# initialize_volume_state
# ---------------------------------------------------------------------------

_BASE_BO_PARAMS = {
    "pump1_xylopyridine_analogs_volume_stock_solution": [18000, 18000, 18000, 18000, 18000],
    "pump2_0.1M_HCl_water_volume_stock_solution": [200000],
    "pump3_co-solvents_volume_stock_solutions": [18000, 18000, 18000, 18000, 18000, 18000],
    "pump4_0.1M_HCl_water_volume_stock_solution": [200000],
    "waste_volume_current_uL": 0,
}


def test_initialize_volume_state_from_config(tmp_path):
    """Reads full lists from bo_parameters when no JSON file exists."""
    path = str(tmp_path / "volume_state.json")
    result = initialize_volume_state(_BASE_BO_PARAMS, path)

    assert result["pump1_volumes_uL"] == pytest.approx([18000.0] * 5)
    assert result["pump2_volume_uL"] == pytest.approx(200000.0)
    assert result["pump3_volumes_uL"] == pytest.approx([18000.0] * 6)
    assert result["pump4_volume_uL"] == pytest.approx(200000.0)
    assert result["waste_volume_uL"] == pytest.approx(0.0)


def test_initialize_volume_state_from_json(tmp_path):
    """Loads from existing volume_state.json (ignores config values)."""
    path = str(tmp_path / "volume_state.json")
    prior = {
        "pump1_volumes_uL": [5000.0, 4000.0, 3000.0, 2000.0, 1000.0],
        "pump2_volume_uL": 80000.0,
        "pump3_volumes_uL": [7000.0, 6000.0, 5000.0, 4000.0, 3000.0, 2000.0],
        "pump4_volume_uL": 90000.0,
        "waste_volume_uL": 1200000.0,
    }
    with open(path, "w") as f:
        json.dump(prior, f)

    result = initialize_volume_state(_BASE_BO_PARAMS, path)

    assert result["pump1_volumes_uL"] == pytest.approx([5000, 4000, 3000, 2000, 1000])
    assert result["pump3_volumes_uL"] == pytest.approx([7000, 6000, 5000, 4000, 3000, 2000])
    assert result["waste_volume_uL"] == pytest.approx(1200000.0)


# ---------------------------------------------------------------------------
# save_volume_log_csv
# ---------------------------------------------------------------------------

def test_save_volume_log_csv_columns(tmp_path):
    """CSV has the expected columns including analog/cosolvent name columns."""
    state = _make_bo_campaign_state(analog_index=0)
    params = _make_instrument_parameters()
    volumes_used = calculate_volumes_used(params)
    check_and_update_all_volumes(
        state, volumes_used, iteration=1, interactive=False
    )
    check_and_update_all_volumes(
        state, volumes_used, iteration=2, interactive=False
    )

    out = str(tmp_path / "volume_log.csv")
    save_volume_log_csv(state.volume_log, out)

    with open(out, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    assert len(rows) == 2
    expected_cols = {
        "iteration", "timestamp",
        "pump1_active_analog", "pump1_consumed_uL", "pump1_remaining_uL",
        "pump2_consumed_uL", "pump2_remaining_uL",
        "pump3_active_cosolvent", "pump3_consumed_uL", "pump3_remaining_uL",
        "pump4_consumed_uL", "pump4_remaining_uL",
        "waste_generated_uL", "waste_total_uL",
    }
    assert expected_cols.issubset(set(rows[0].keys()))
    assert rows[0]["pump1_active_analog"] == "Xylopyridine_Analog_1"


def test_save_volume_log_csv_empty(tmp_path):
    """save_volume_log_csv is a no-op for an empty log (no file created)."""
    out = str(tmp_path / "volume_log.csv")
    save_volume_log_csv([], out)
    assert not Path(out).exists()
