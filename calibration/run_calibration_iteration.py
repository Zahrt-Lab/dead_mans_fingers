# ------------------------------------------------------------------------------
# Software: dead_mans_fingers
# Copyright (c) 2026 Andrew Zahrt
#
# Contributions by Scott Laverty and Joao Albuquerque are acknowledged.
#
# Licensed under the MIT License. See the LICENSE file in the repository root.
# ------------------------------------------------------------------------------

''' This script runs a single iteration of the calibration process. It is called by the main calibration loop in run_calibration.py. 
It takes as input the current iteration number, the path to the calibration configuration file, 
and the path to the output directory where the results of this iteration will be saved. 
'''
from pathlib import Path

import numpy

from bayesian_optimizer.experiment_state import CalibrationState
from experimental_commands.commands import save_commands_csv
from experimental_commands.experiment_runner import run_hardware_experiment
from calibration.post_process_uv import post_process_uv_data
from post_processing.average_absorbance import average_absorbance
import numpy as np
import pandas as pd


def run_calibration_iteration(calibration_state: CalibrationState):
    # The total flow rate will be the sum of flow_rat_pump_1 and flow_rate_pump_3
    concentration_M = calibration_state.calibration_parameters["initial_concentration_uM"] * calibration_state.dilution_factor * 1e-6 # Convert uM to M
    flow_rate_pump1 = calibration_state.calibration_parameters["total_flow_rate_uL_minute"] * (calibration_state.dilution_factor)
    volume_pump1 = calibration_state.calibration_parameters["volume_uL"] * calibration_state.dilution_factor
    flow_rate_pump2 = calibration_state.calibration_parameters["total_flow_rate_uL_minute"] * (1 - calibration_state.dilution_factor)
    volume_pump2 = calibration_state.calibration_parameters["volume_uL"] * (1 - calibration_state.dilution_factor)
    commands_path = calibration_state.commands_dir / f"commands_{calibration_state.calibration_iteration}"
    flow_rate_pump3 = 0
    volume_pump3 = 0
    flow_rate_pump4 = 0
    volume_pump4 = 0
    valve_position_pump3 = 1
    fraction_of_co_solvent = 0


    #save commands to CSV. This function already generates all commands necessary to run the experiment. 
    save_commands_csv(commands_path,
                    flow_rate_pump1,
                    flow_rate_pump2,
                    flow_rate_pump3,
                    flow_rate_pump4,
                    volume_pump1,
                    volume_pump2,
                    volume_pump3,
                    volume_pump4,
                    valve_position_pump3,
                    calibration_state.calibration_parameters["temperature"],
                    fraction_of_co_solvent,
                    calibration_state.calibration_parameters["light_intensity"],
                    calibration_state.calibration_parameters["std_wavelength"],
                    calibration_state.calibration_parameters["product_wavelength"],
                    calibration_state.calibration_parameters["reference_wavelength"],
                    calibration_state.calibration_parameters["blank_light_intensity_threshold"],
                    calibration_state.calibration_parameters["wavelength_for_blank_light_intensity_check"],
                    convergence_time=5.0
                    )

    # Run the experiment sequence
    if calibration_state.is_simulation:
        print("Running in simulation mode. Skipping hardware experiment.")
        #Simulate uv data, 0 to 300 s, abs equal to the expected extinction coefficient * concentration * light path length, plus some noise
        time = np.linspace(0, 300, 300)
        absorbance = calibration_state.calibration_parameters["expected_extinction_coefficient"] * concentration_M * calibration_state.calibration_parameters["light_path_length_cm"] + np.random.normal(0, 0.01, size=time.shape)
        uv_vis_recording_df = pd.DataFrame({
            "Time(s)": time,
            calibration_state.calibration_parameters["std_wavelength"]: absorbance
        })
        uv_data_dir_path = calibration_state.results_dir / f"simulated_uv_data_{calibration_state.calibration_iteration}.csv"
        uv_vis_recording_df.to_csv(uv_data_dir_path, index=False)
    else:
        uv_data_dir_path = run_hardware_experiment(commands_path, calibration_state.instrument_config_path, calibration_state.commands_dir, calibration_state.calibration_iteration) 
    
    #PostProcess UV data. Create my own processing of the UV data
    post_processed_uv_data_df = post_process_uv_data(uv_data_dir_path)
    
    #Calculate the average absorbance for the standard wavelength
    average_absorbance_std = average_absorbance(
        post_processed_uv_data_df,
        calibration_state.calibration_parameters["std_wavelength"]
    )
    print(f"The average absorbance for the standard wavelength {calibration_state.calibration_parameters['std_wavelength']} nm is {average_absorbance_std}")
    #Save the results in the dataframe
    calibration_state.update_calibration_results_df(concentration_M, average_absorbance_std)

    #Save the calibration results to a CSV file
    calibration_state.calibration_results_df.to_csv(calibration_state.results_dir / f"calibration_results_{calibration_state.calibration_iteration}.csv", index=False)
    print(f"Calibration results saved to {calibration_state.results_dir / f'calibration_results_{calibration_state.calibration_iteration}.csv'}.")

    #Run hardware returns the UV data file dir path. The next step is to read this file and extract the important data

    print(f"Experiment for dilution factor {calibration_state.dilution_factor} completed. Commands saved at {commands_path}.")
