# ------------------------------------------------------------------------------
# Software: dead_mans_fingers
# Copyright (c) 2026 Zahrt Research Group
#
# Contributions by Scott Laverty and Joao Albuquerque are acknowledged.
#
# Licensed under the MIT License. See the LICENSE file in the repository root.
# ------------------------------------------------------------------------------

"""
Test cases for post_processing/calculate_product_throughput.py
"""

import pytest
import sys
from pathlib import Path

# Add the project root directory to sys.path to allow imports
sys.path.append(str(Path(__file__).parent.parent.parent))
from post_processing.calculate_product_throughput import calculate_product_throughput

def test_calculate_product_throughput_float():
    '''
    Test if output is a float value
    '''
    from post_processing.calculate_product_throughput import calculate_product_throughput

    throughput = calculate_product_throughput(
        concentration_product_mol_per_uL_reactor_bed=0.3,
        reactor_flow_rate_uL_per_min=80
    )
    assert isinstance(throughput, float)

def test_calculate_product_throughput_valid():
    # Test with valid inputs (Case 1)
    concentration_product_mol_per_uL_reactor_bed = 0.3
    reactor_flow_rate_uL_per_min = 80
    throughput = calculate_product_throughput(
        concentration_product_mol_per_uL_reactor_bed=0.3,
        reactor_flow_rate_uL_per_min=80
    )
    assert isinstance(throughput, float)
    assert throughput == concentration_product_mol_per_uL_reactor_bed * reactor_flow_rate_uL_per_min * 1e9

    # Test with valid inputs (Case 2)
    concentration_product_mol_per_uL_reactor_bed = 0.1
    reactor_flow_rate_uL_per_min = 50
    throughput = calculate_product_throughput(
        concentration_product_mol_per_uL_reactor_bed=0.1,
        reactor_flow_rate_uL_per_min=50
    )
    assert isinstance(throughput, float)
    assert throughput == concentration_product_mol_per_uL_reactor_bed * reactor_flow_rate_uL_per_min * 1e9

    # Test with zero concentration (should yield zero throughput)
    concentration_product_mol_per_uL_reactor_bed = 0.0
    reactor_flow_rate_uL_per_min = 100
    throughput = calculate_product_throughput(
        concentration_product_mol_per_uL_reactor_bed=0.0,
        reactor_flow_rate_uL_per_min=100
    )
    assert isinstance(throughput, float)
    assert throughput == 0.0

