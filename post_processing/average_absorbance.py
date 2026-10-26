# ------------------------------------------------------------------------------
# Software: dead_mans_fingers
# Copyright (c) 2026 Zahrt Research Group
#
# Contributions by Scott Laverty are acknowledged.
#
# Licensed under the MIT License. See the LICENSE file in the repository root.
# ------------------------------------------------------------------------------

"""
The purpose of this code is to take the UV-VIS absorbance data recorded over 
time after the photochemical reaction has reached steady state, 
and average the absorbance.
"""

import pandas as pd

from utils.experiment_aborted import PostProcessingError

def average_absorbance(
    uv_vis_absorbance_over_time_df: pd.DataFrame,
    wavelength: float,
) -> float:
    """
    Returns the average absorbance at a specific wavelength of light,
    meant to be performed after target volume is reached

    parameters:
     -uv_vis_absorbance_over_time_df: This is the UV_VIS data recorded in the form of a dataframe
     -wavelength: This is the measured wavelength that will be averaged over
    return:
     -average_absorbance_recorded: Absorbance at the specified wavelenght after the
     UV-VIS results level off
    """

    # Ensure we treat the wavelength as string since column headers are strings
    wavelength_column = str(wavelength)

    if wavelength_column not in uv_vis_absorbance_over_time_df.columns:
        raise PostProcessingError(
            f"Wavelength {wavelength_column} not found in CSV headers: "
            f"{list(uv_vis_absorbance_over_time_df.columns)}"
        )
    
    if (uv_vis_absorbance_over_time_df[wavelength_column] < -0.3).any() or \
       (uv_vis_absorbance_over_time_df[wavelength_column] > 1.3).any():
        raise PostProcessingError(
            f"Values in column {wavelength_column} are out of expected range (-0.3 to 1.3)."
        )

    # Calculates the average absorbance at the specified wavelength
    average_absorbance_recorded = uv_vis_absorbance_over_time_df[
        wavelength_column
    ].mean()

    return average_absorbance_recorded
