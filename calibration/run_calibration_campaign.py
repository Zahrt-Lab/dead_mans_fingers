'''
This script runs a calibration campaign for the fluorescent project.
'''

from pathlib import Path
import numpy as np
import pandas as pd

from bayesian_optimizer.experiment_state import CalibrationState
from experimental_commands.generate_instrument_config import save_instrument_config_csv
from experimental_commands.commands import save_commands_csv
from experimental_commands.experiment_runner import run_hardware_experiment
from calibration.post_process_uv import post_process_uv_data
from post_processing.average_absorbance import average_absorbance
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
    commands_dir = base_directory / "commands"
    commands_dir.mkdir(parents=True, exist_ok=True)

    #Create the instrument configuration file for the experiment
    instrument_config_path = base_directory / "instrument_config.csv"
    save_instrument_config_csv(instrument_config_path)

    # Dataframe to keep all the results of the calibration experiment
    calibration_results_df = pd.DataFrame(columns=[
        "concentration_M",
        "average_absorbance_std"
    ])
    calibration_results_csv_path = results_dir / "calibration_results.csv"

    # Set experimental parameters (flow rate, concentration, etc)
    total_flow_rate_uL_minute = calibration_state.calibration_parameters["total_flow_rate_uL_minute"]
    volume_uL = calibration_state.calibration_parameters["volume_uL"]
    initial_concentration_uM = calibration_state.calibration_parameters["initial_concentration_uM"]
    expected_extinction_coefficient = calibration_state.calibration_parameters["expected_extinction_coefficient"]
    light_path_length_cm = calibration_state.calibration_parameters["light_path_length_cm"]
    std_wavelength = calibration_state.calibration_parameters["std_wavelength"]
    product_wavelength = calibration_state.calibration_parameters["product_wavelength"]
    reference_wavelength = calibration_state.calibration_parameters["reference_wavelength"]
    blank_light_intensity_threshold = calibration_state.calibration_parameters["blank_light_intensity_threshold"]
    wavelength_for_blank_light_intensity_check = calibration_state.calibration_parameters["wavelength_for_blank_light_intensity_check"]
    temperature = calibration_state.calibration_parameters["temperature"]
    light_intensity = calibration_state.calibration_parameters["light_intensity"]
    factors = calibration_state.calibration_parameters["factors"]

    
    # Calculate the concentration for absorbance = 1
    concentration_for_absorbance_1_M = 1 / (expected_extinction_coefficient * light_path_length_cm)
    concentration_for_absorbance_1_uM = concentration_for_absorbance_1_M * 1e6  # Convert M to uM
    initial_dilution_factor = concentration_for_absorbance_1_uM / initial_concentration_uM
    dilution_factors = [initial_dilution_factor * factor for factor in factors]

    for i, dilution_factor in enumerate(dilution_factors, start=1):
        # The total flow rate will be the sum of flow_rat_pump_1 and flow_rate_pump_3
        concentration_M = initial_concentration_uM * dilution_factor * 1e-6 # Convert uM to M
        flow_rate_pump1 = total_flow_rate_uL_minute * (dilution_factor)
        volume_pump1 = volume_uL * dilution_factor
        flow_rate_pump2 = total_flow_rate_uL_minute * (1 - dilution_factor)
        volume_pump2 = volume_uL * (1 - dilution_factor)
        commands_path = base_directory / f"commands_{i}"
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
                        temperature,
                        fraction_of_co_solvent,
                        light_intensity,
                        std_wavelength,
                        product_wavelength,
                        reference_wavelength,
                        blank_light_intensity_threshold,
                        wavelength_for_blank_light_intensity_check
                        )

        # Run the experiment sequence
        if calibration_state.is_simulation:
            print("Running in simulation mode. Skipping hardware experiment.")
            #Simulate uv data, 0 to 300 s, abs equal to the expected extinction coefficient * concentration * light path length, plus some noise
            time = np.linspace(0, 300, 300)
            absorbance = expected_extinction_coefficient * concentration_M * light_path_length_cm + np.random.normal(0, 0.01, size=time.shape)
            uv_vis_recording_df = pd.DataFrame({
                "Time(s)": time,
                std_wavelength: absorbance
            })
            uv_data_dir_path = base_directory / f"simulated_uv_data_{i}.csv"
            uv_vis_recording_df.to_csv(uv_data_dir_path, index=False)
        else:
            uv_data_dir_path = run_hardware_experiment(commands_path, instrument_config_path, commands_dir, i) 
        
        #PostProcess UV data. Create my own processing of the UV data
        post_processed_uv_data_df = post_process_uv_data(uv_data_dir_path)
        
        #Calculate the average absorbance for the standard wavelength
        average_absorbance_std = average_absorbance(
            post_processed_uv_data_df,
            std_wavelength
        )
        print(f"The average absorbance for the standard wavelength {std_wavelength} nm is {average_absorbance_std}")
        #Save the results in the dataframe
        calibration_results_df = pd.concat([
            calibration_results_df, 
            pd.DataFrame({
            "concentration_M": [concentration_M],
            "average_absorbance_std": [average_absorbance_std]
        })], ignore_index=True)

        #Save the calibration results to a CSV file
        calibration_results_df.to_csv(calibration_results_csv_path, index=False)
        print(f"Calibration results saved to {calibration_results_csv_path}.")

        #Run hardware returns the UV data file dir path. The next step is to read this file and extract the important data

        print(f"Experiment for dilution factor {dilution_factor} completed. Commands saved at {commands_path}.")
    print("All experiments completed. Proceed to analyze the results and plot the calibration curve.")

    # Analyze the calibration results and calculate the extinction coefficient
    calculated_extinction_coefficient, slope, intercept = analyze_calibration_results(calibration_results_df, expected_extinction_coefficient, light_path_length_cm, base_directory)
    print(f"Calculated extinction coefficient: {calculated_extinction_coefficient:.2e} M^-1 cm^-1")


    # Plot the calibration curve
    plot_calibration_curve(calibration_results_df, slope, intercept, calculated_extinction_coefficient, expected_extinction_coefficient, results_dir)
    print(f"Calibration curve plot saved to {results_dir / 'calibration_curve.png'}.")


















































































































