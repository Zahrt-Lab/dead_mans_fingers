
# ------------------------------------------------------------------------------
# Software: dead_mans_fingers
# Copyright (c) 2026 Zahrt Research Group
#
# Contributions by Scott Laverty are acknowledged.
#
# Licensed under the MIT License. See the LICENSE file in the repository root.
# ------------------------------------------------------------------------------
'''
Analyze the results of a calibration campaign and returns the extinction coefficient.
Saves the results of the analysis to a CSV file.
'''
import pandas as pd
import numpy as np
from pathlib import Path

def analyze_calibration_results(calibration_results_df: pd.DataFrame, expected_extinction_coefficient: float, light_path_length: float, analysis_directory: str)-> tuple[float, float, float]:

    # Calculate the linear fit for the calibration curve
    coefficients = np.polyfit(calibration_results_df["concentration_M"], calibration_results_df["average_absorbance_std"], 1)
    slope, intercept = coefficients
    # Calculate the extinction coefficient from the slope of the calibration curve (slope = extinction_coefficient * light_path_length)
    calculated_extinction_coefficient = slope / light_path_length

    #Save the calibration data in one file for future analysis, containing the expected and calculated extinction coefficients, the slope and intercept of the calibration curve, and the R-squared value of the linear fit
    calibration_analysis_df = pd.DataFrame({
        "Expected Extinction Coefficient": [expected_extinction_coefficient],
        "Calculated Extinction Coefficient": [calculated_extinction_coefficient],
        "Slope": [slope],
        "Intercept": [intercept]
    })
    calibration_analysis_csv_path = Path(analysis_directory) / "calibration_analysis.csv"
    calibration_analysis_df.to_csv(calibration_analysis_csv_path, index=False)
    print(f"Calibration analysis saved to {calibration_analysis_csv_path}.")

    return calculated_extinction_coefficient, slope, intercept