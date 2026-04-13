# ------------------------------------------------------------------------------
# Software: AUTO_ZAHRT
# Copyright: (C) 2026 by Professor Andrew Zahrt
# This software is the intellectual property of Professor Andrew Zahrt
# Contributions by graduate students Scott Laverty and Joao are acknowledged.
# All rights reserved.
# ------------------------------------------------------------------------------

"""
Tests for production_run/calculate_production_run_parameters.py

Verifies reaction-time/volume math and that calculate_production_run_parameters
returns the correct dict structure with pump 4 zeroed out (production_run=True).
"""

import sys
from pathlib import Path

import pytest

sys.path.append(str(Path(__file__).parent.parent.parent))
from production_run.calculate_production_run_parameters import (
    calculate_production_run_parameters,
    calculate_production_run_reaction_time,
    calculate_production_run_volume,
)


# ---------------------------------------------------------------------------
# calculate_production_run_reaction_time
# ---------------------------------------------------------------------------

def test_reaction_time_basic():
    """1000 nmol / 100 nmol·min⁻¹ = 10 min."""
    result = calculate_production_run_reaction_time(
        desired_nmols=1000.0, throughput_nmol_per_min=100.0
    )
    assert result == pytest.approx(10.0)


def test_reaction_time_fractional():
    result = calculate_production_run_reaction_time(
        desired_nmols=500.0, throughput_nmol_per_min=200.0
    )
    assert result == pytest.approx(2.5)


# ---------------------------------------------------------------------------
# calculate_production_run_volume
# ---------------------------------------------------------------------------

def test_production_volume_basic():
    """200 (flow) × 10 (time) = 2000."""
    result = calculate_production_run_volume(
        reactor_bed_flow_rate=200.0, reaction_time_min=10.0
    )
    assert result == pytest.approx(2000.0)


def test_production_volume_small():
    result = calculate_production_run_volume(
        reactor_bed_flow_rate=50.0, reaction_time_min=4.0
    )
    assert result == pytest.approx(200.0)


# ---------------------------------------------------------------------------
# calculate_production_run_parameters — integration with parameters_to_commands
# ---------------------------------------------------------------------------

_EXPECTED_KEYS = {
    "flow_rate_pump1",
    "volume_pump1",
    "flow_rate_pump2",
    "volume_pump2",
    "flow_rate_pump3",
    "volume_pump3",
    "position_valve2",
    "flow_rate_pump4",
    "volume_pump4",
    "temperature",
    "light_intensity",
}


def _call_calculate(
    reactor_bed_flow_rate=200.0,
    dilution_factor=0.3,
    temperature=40.0,
    cosolvent_valve_position=3,
    fraction_of_cosolvent=0.1,
    light_intensity=75.0,
    throughput_nmol_per_min=20.0,
    desired_mols=1000.0,
    xylopyridine_analogs_concentrations_uM=1000.0,
) -> dict:
    return calculate_production_run_parameters(
        reactor_bed_flow_rate,
        dilution_factor,
        temperature,
        cosolvent_valve_position,
        fraction_of_cosolvent,
        light_intensity,
        throughput_nmol_per_min,
        desired_mols,
        xylopyridine_analogs_concentrations_uM,
    )


def test_returns_all_expected_keys():
    result = _call_calculate()
    assert _EXPECTED_KEYS == set(result.keys())


def test_pump4_is_zero_in_production_run():
    """production_run=True is passed to parameters_to_commands, so pump 4
    must always be 0 (no inline UV detection in a production run)."""
    result = _call_calculate()
    assert result["flow_rate_pump4"] == pytest.approx(0.0)
    assert result["volume_pump4"] == pytest.approx(0.0)


def test_pump_flow_rates_are_positive():
    """Pumps 1–3 must have positive flow rates for valid conditions."""
    result = _call_calculate()
    assert result["flow_rate_pump1"] > 0.0
    assert result["flow_rate_pump2"] > 0.0
    assert result["flow_rate_pump3"] > 0.0


def test_temperature_preserved():
    """Temperature should be passed through unchanged."""
    result = _call_calculate(temperature=55.0)
    assert result["temperature"] == pytest.approx(55.0)
