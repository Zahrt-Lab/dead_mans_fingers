'''
This script runs a calibration campaign for the fluorescent project.
'''

from pathlib import Path
import numpy as np
import pandas as pd

from bayesian_optimizer.experiment_state import CalibrationState
from calibration.run_calibration_iteration import run_calibration_iteration
from experimental_commands.generate_instrument_config import save_instrument_config_csv
from calibration.analyze_calibration import analyze_calibration_results
from calibration.plot_calibration_curve import plot_calibration_curve


def run_calibration_campaign(calibration_state: CalibrationState):

    # Create folders and files
    time_stamp = pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")
    base_directory = Path(calibration_state.calibration_parameters["base_directory"])
    base_directory = base_directory / f"calibration_{time_stamp}"
    base_directory.mkdir(parents=True, exist_ok=True)
    results_dir = base_directory / "results"
    results_dir.mkdir(parents=True, exist_ok=True)
    calibration_state.update_results_dir(results_dir)
    commands_dir = base_directory / "commands"
    commands_dir.mkdir(parents=True, exist_ok=True)
    calibration_state.update_commands_dir(commands_dir)

    #Create the instrument configuration file for the experiment
    instrument_config_path = base_directory / "instrument_config.csv"
    calibration_state.update_instrument_config_path(instrument_config_path)
    save_instrument_config_csv(instrument_config_path)

    # Set experimental parameters (flow rate, concentration, etc)
    initial_concentration_uM = calibration_state.calibration_parameters["initial_concentration_uM"]
    expected_extinction_coefficient = calibration_state.calibration_parameters["expected_extinction_coefficient"]
    light_path_length_cm = calibration_state.calibration_parameters["light_path_length_cm"]
    factors = calibration_state.calibration_parameters["factors"]

    
    # Calculate the concentration for absorbance = 1
    concentration_for_absorbance_1_M = 1 / (expected_extinction_coefficient * light_path_length_cm)
    concentration_for_absorbance_1_uM = concentration_for_absorbance_1_M * 1e6  # Convert M to uM
    initial_dilution_factor = concentration_for_absorbance_1_uM / initial_concentration_uM
    dilution_factors = [initial_dilution_factor * factor for factor in factors]
    

    while calibration_state.calibration_iteration < len(dilution_factors):
        calibration_state.update_dilution_factor(dilution_factors[calibration_state.calibration_iteration])
        calibration_state.update_calibration_iteration(calibration_state.calibration_iteration + 1)
        # Run the Calibration iteration for the current dilution factor
        run_calibration_iteration(calibration_state)

    
    print("All experiments completed. Proceed to analyze the results and plot the calibration curve.")

    # Analyze the calibration results and calculate the extinction coefficient
    calculated_extinction_coefficient, slope, intercept = analyze_calibration_results(calibration_state.calibration_results_df, expected_extinction_coefficient, light_path_length_cm, base_directory)
    print(f"Calculated extinction coefficient: {calculated_extinction_coefficient:.2e} M^-1 cm^-1")


    # Plot the calibration curve
    plot_calibration_curve(calibration_state.calibration_results_df, slope, intercept, calculated_extinction_coefficient, expected_extinction_coefficient, results_dir)
    print(f"Calibration curve plot saved to {results_dir / 'calibration_curve.png'}.")


















































































































