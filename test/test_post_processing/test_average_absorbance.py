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
import pandas as pd
import sys
from pathlib import Path

# Add the project root directory to sys.path to allow imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from post_processing.average_absorbance import average_absorbance   

UV_VIS_DATAFRAME = pd.DataFrame()

UV_VIS_DATAFRAME["Time(s)"] = [0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60]
UV_VIS_DATAFRAME["409"] = [0.9, 0.85, 0.8, 0.75, 0.7, 0.65, 0.5, 0.45, 0.4, 0.4, 0.4, 0.4, 0.4]
UV_VIS_DATAFRAME["506"] = [0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.5, 0.55, 0.6, 0.6, 0.6, 0.6, 0.6]

def test_calculate_average_absorbance_float():
    '''
    Test if output is a float value
    '''
    average_absorbance_reactant = average_absorbance(UV_VIS_DATAFRAME, "409")
    assert isinstance(average_absorbance_reactant, float)

    average_absorbance_product = average_absorbance(UV_VIS_DATAFRAME, "506")
    assert isinstance(average_absorbance_product, float)

def test_calculate_average_absorbance_valid():
    '''
    Test with valid inputs
    '''

    processed_df = UV_VIS_DATAFRAME.copy()
    processed_df = processed_df[processed_df["Time(s)"] >= 50]

    average_absorbance_reactant = average_absorbance(processed_df, "409")
    assert round(average_absorbance_reactant, 2) == 0.4

    average_absorbance_product = average_absorbance(processed_df, "506")
    assert round(average_absorbance_product, 2) == 0.6

def test_calculate_average_absorbance_not_valid():
    '''
    Test with invalid input
    '''

    with pytest.raises(ValueError):
        average_absorbance(UV_VIS_DATAFRAME, "999")
