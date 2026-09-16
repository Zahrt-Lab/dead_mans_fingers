# ------------------------------------------------------------------------------
# Software: dead_mans_fingers
# Copyright (c) 2026 Andrew Zahrt
#
# Contributions by Scott Laverty and Joao Albuquerque are acknowledged.
#
# Licensed under the MIT License. See the LICENSE file in the repository root.
# ------------------------------------------------------------------------------

'''This script is responsible for plotting the calibration curve, given the calibration results and the calculated extinction coefficient.
It saves the calibration curve plot to a file.
'''

from pathlib import Path

from numpy.compat import Path
import matplotlib.pyplot as plt
import numpy as np

def plot_calibration_curve(calibration_results_df, slope, intercept, calculated_extinction_coefficient, expected_extinction_coefficient, results_directory):
    
    plt.figure(figsize=(8, 6))
    plt.plot(calibration_results_df["concentration_M"], calibration_results_df["average_absorbance_std"], marker="o")
    # Plot the linear fit
    x_fit = np.linspace(calibration_results_df["concentration_M"].min(), calibration_results_df["concentration_M"].max(), 100)
    y_fit = slope * x_fit + intercept
    plt.plot(x_fit, y_fit, color="red", linestyle="--", label=f"Linear Fit (y = {slope:.2f}x + {intercept:.2f})\nCalculated Extinction Coefficient = {calculated_extinction_coefficient:.2e} M^-1 cm^-1)")
    plt.title("Calibration Curve")
    plt.xlabel("Concentration (M)")
    plt.ylabel("Average Absorbance")
    plt.legend()
    # Compare the extinction coefficient obtained with the expected one for the compound
    plt.annotate(
        f"Expected Extinction Coefficient = {expected_extinction_coefficient:.2e} M^-1 cm^-1",
        xy=(0.05, 0.95),
        xycoords="axes fraction",
        fontsize=10,
        ha="left",
        va="top",
        bbox=dict(boxstyle="round,pad=0.5", fc="yellow", alpha=0.5)
    )
    #save the plot
    calibration_curve_plot_path = Path(results_directory) / "calibration_curve.png"
    plt.savefig(calibration_curve_plot_path)