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
    '''
    Test if output is a float value
    '''
    percent_yield = calculate_percent_yield(
        reactant_absorbance=0.5,
        epsilon_reactant_at_lambda1_L_per_mol_cm=100,
        product_absorbance=0.5,
        epsilon_product_at_lambda2_L_per_mol_cm=100,
        pathlength_cm=1,
        initial_concentration_mol_per_L=0.01
    )
    assert isinstance(percent_yield, float)

def test_calculate_percent_yield_valid():
    # Test with valid inputs at 50% yield
    percent_yield = calculate_percent_yield(
        reactant_absorbance=0.5,
        epsilon_reactant_at_lambda1_L_per_mol_cm=100,
        product_absorbance=0.5,
        epsilon_product_at_lambda2_L_per_mol_cm=100,
        pathlength_cm=1,
        initial_concentration_mol_per_L=0.01,
    )
    assert 0 <= percent_yield <= 100 
    assert percent_yield == 50

    # Test with valid inputs at 25% yield
    percent_yield = calculate_percent_yield(
        reactant_absorbance=0.75,
        epsilon_reactant_at_lambda1_L_per_mol_cm=100,
        product_absorbance=0.25,
        epsilon_product_at_lambda2_L_per_mol_cm=100,
        pathlength_cm=1,
        initial_concentration_mol_per_L=0.01,
    )
    assert 0 <= percent_yield <= 100 
    assert percent_yield == 25

    # Test with valid inputs at 100% yield
    percent_yield = calculate_percent_yield(
        reactant_absorbance=0.0,
        epsilon_reactant_at_lambda1_L_per_mol_cm=100,
        product_absorbance=1.0,     
        epsilon_product_at_lambda2_L_per_mol_cm=100,
        pathlength_cm=1,
        initial_concentration_mol_per_L=0.01,
    )
    assert 0 <= percent_yield <= 100 
    assert percent_yield == 100

def test_calculate_percent_yield_invalid_reactant_absorbance():
    # Test with invalid inputs

    with pytest.raises(ValueError):
        percent_yield = calculate_percent_yield(
            reactant_absorbance=-0.1,  # Invalid
            epsilon_reactant_at_lambda1_L_per_mol_cm=100,
            product_absorbance=0.3,
            epsilon_product_at_lambda2_L_per_mol_cm=150,
            pathlength_cm=1,    
            initial_concentration_mol_per_L=0.01,   
        )
def test_calculate_percent_yield_invalid_product_absorbance():
    with pytest.raises(ValueError):
        percent_yield = calculate_percent_yield(
            reactant_absorbance=0.3,  
            epsilon_reactant_at_lambda1_L_per_mol_cm=100,
            product_absorbance=-0.3,
            epsilon_product_at_lambda2_L_per_mol_cm=150,
            pathlength_cm=1,    
            initial_concentration_mol_per_L=0.01,   
        )

def test_calculate_percent_yield_zero_pathlength():
    with pytest.raises(ValueError):
        calculate_percent_yield(
            reactant_absorbance=0.5,
            epsilon_reactant_at_lambda1_L_per_mol_cm=100,
            product_absorbance=0.3,
            epsilon_product_at_lambda2_L_per_mol_cm=150,
            pathlength_cm=0,  # Invalid
            initial_concentration_mol_per_L=0.01,
        )

def test_calculate_percent_yield_negative_absorbance():
    with pytest.raises(ValueError):
        calculate_percent_yield(
            reactant_absorbance=-0.1,  # Invalid
            epsilon_reactant_at_lambda1_L_per_mol_cm=100,
            product_absorbance=0.3,
            epsilon_product_at_lambda2_L_per_mol_cm=150,
            pathlength_cm=1,
            initial_concentration_mol_per_L=0.01,
        )

def test_calculate_percent_yield_negative_initial_concentration():
    with pytest.raises(ValueError):
        calculate_percent_yield(
            reactant_absorbance=0.5,
            epsilon_reactant_at_lambda1_L_per_mol_cm=100,
            product_absorbance=0.3,
            epsilon_product_at_lambda2_L_per_mol_cm=150,
            pathlength_cm=1,
            initial_concentration_mol_per_L=-0.01,  # Invalid
        )

def test_calculate_percent_yield_zero_initial_concentration():
    with pytest.raises(ValueError):
        calculate_percent_yield(
            reactant_absorbance=0.5,
            epsilon_reactant_at_lambda1_L_per_mol_cm=100,
            product_absorbance=0.3,
            epsilon_product_at_lambda2_L_per_mol_cm=150,
            pathlength_cm=1,
            initial_concentration_mol_per_L=0,  # Invalid
        )