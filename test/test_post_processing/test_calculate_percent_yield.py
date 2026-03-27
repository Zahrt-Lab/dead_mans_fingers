# ------------------------------------------------------------------------------
# Software: project_dead_mans_fingers
# Copyright: (C) 2026 by Professor Andrew Zahrt
# This software is the intellectual property of Professor Andrew Zahrt
# Contributions by graduate students Scott Laverty and Joao are acknowledged.
# All rights reserved.
# -----------------------------------------------------------------------------

"""
Test cases for post_processing/calculate_percent_yield.py
"""

import pytest
import sys
from pathlib import Path

# Add the project root directory to sys.path to allow imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from post_processing.calculate_percent_yield import calculate_percent_yield


def test_calculate_percent_yield_float():
    percent_yield = calculate_percent_yield(
        concentration_product_mol_per_L=0.005,
        initial_concentration_mol_per_L=0.01,
    )
    assert isinstance(percent_yield, float)


def test_calculate_percent_yield_valid():
    # 50% yield
    percent_yield = calculate_percent_yield(
        concentration_product_mol_per_L=0.005,
        initial_concentration_mol_per_L=0.01,
    )
    assert percent_yield == 50.0

    # 25% yield
    percent_yield = calculate_percent_yield(
        concentration_product_mol_per_L=0.0025,
        initial_concentration_mol_per_L=0.01,
    )
    assert percent_yield == 25.0

    # 100% yield
    percent_yield = calculate_percent_yield(
        concentration_product_mol_per_L=0.01,
        initial_concentration_mol_per_L=0.01,
    )
    assert percent_yield == 100.0

    # 0% yield
    percent_yield = calculate_percent_yield(
        concentration_product_mol_per_L=0.0,
        initial_concentration_mol_per_L=0.01,
    )
    assert percent_yield == 0.0


def test_calculate_percent_yield_clamped_above_100():
    # Noise can push product above initial; should clamp to 100
    percent_yield = calculate_percent_yield(
        concentration_product_mol_per_L=0.02,
        initial_concentration_mol_per_L=0.01,
    )
    assert percent_yield == 100.0


def test_calculate_percent_yield_negative_product_concentration():
    with pytest.raises(ValueError):
        calculate_percent_yield(
            concentration_product_mol_per_L=-0.001,
            initial_concentration_mol_per_L=0.01,
        )


def test_calculate_percent_yield_zero_initial_concentration():
    with pytest.raises(ValueError):
        calculate_percent_yield(
            concentration_product_mol_per_L=0.005,
            initial_concentration_mol_per_L=0.0,
        )


def test_calculate_percent_yield_negative_initial_concentration():
    with pytest.raises(ValueError):
        calculate_percent_yield(
            concentration_product_mol_per_L=0.005,
            initial_concentration_mol_per_L=-0.01,
        )
