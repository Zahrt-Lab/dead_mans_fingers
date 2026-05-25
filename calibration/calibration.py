'''This script is responsible for running a calibration experiment. It will communicate to auto-zahrt via General Experiments and run the experiments sequence.
0) Read json file with the experimental parameters for the calibration experiment
1) Wash the platform with the solvent of the sample (usually water)
2) Run the calibration sequance
    - Run at certain concentration so the absorbance is 1
    - Dilute accordingly to get absorbances oof 0.8, 0.6, 0.4, 0.2 (5 points in total)
3) Determine de absorbance value from each run
4) Plot the calibration curve
5) Compare the extinction coefficient obtained with the expected one for the compound

Try to use as mmuch as possible from dead_mans_finger, especially the parsing and methods creation functions.


'''

# Imports
import json
from pathlib import Path
import pandas as pd
from typing import List

from bayesian_optimizer.experiment_state import CalibrationState
from experimental_commands.commands import save_commands_csv
from experimental_commands.experiment_runner import run_hardware_experiment
from experimental_commands.generate_instrument_config import save_instrument_config_csv
from post_processing.average_absorbance import average_absorbance
import matplotlib.pyplot as plt
import numpy as np



# Parse parameters and put it into a dictionary.
# Resolve relative to this file so it works regardless of the current working directory.
json_file_path = Path(__file__).resolve().with_name("params.json")

try:
    with open(json_file_path, "r", encoding="utf-8") as f:
        params = json.load(f)
except FileNotFoundError as exc:
    raise FileNotFoundError(
        f"Could not find params.json at: {json_file_path}. "
        "Expected it to live next to calibration/calibration.py."
    ) from exc

# Set experimental parameters (flow rate, concentration, etc)
total_flow_rate = params["total_flow_rate"]
volume = params["volume"]
initial_concentration_uM = params["initial_concentration"]
expected_extinction_coefficient = params["expected_extinction_coefficient"]
light_path_length = params["light_path_length"]
# Calculate the concentration for absorbance = 1
concentration_for_absorbance_1_M = 1 / (expected_extinction_coefficient * light_path_length)
concentration_for_absorbance_1_uM = concentration_for_absorbance_1_M * 1e6  # Convert M to uM
initial_dilution_factor = concentration_for_absorbance_1_uM / initial_concentration_uM
factors = [1, 0.8, 0.6, 0.4, 0.2]
dilution_factors = [initial_dilution_factor * factor for factor in factors]
std_wavelength = params["std_wavelength"]
product_wavelength = params["product_wavelength"]
reference_wavelength = params["reference_wavelength"]
blank_light_intensity_threshold = params["blank_light_intensity_threshold"]
wavelength_for_blank_light_intensity_check = params["wavelength_for_blank_light_intensity_check"]
base_directory = Path(params["base_directory"])
temperature = params["temperature"]
light_intensity = params["light_intensity"]
time_stamp = pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")
base_directory = base_directory / f"calibration_{time_stamp}"
base_directory.mkdir(parents=True, exist_ok=True)



#Create the instrument configuration file for the experiment
instrument_config_path = base_directory / "instrument_config.csv"
save_instrument_config_csv(instrument_config_path)


output_dir = base_directory / "output"

# Dataframe to keep all the results of the calibration experiment
calibration_results_df = pd.DataFrame(columns=[
    "concentration_M",
    "average_absorbance_std"
])
calibration_results_csv_path = base_directory / "calibration_results.csv"

#Start a for loop to go over the concentrations and generate the commands for each one of them
for i, dilution_factor in enumerate(dilution_factors, start=1):
    # The total flow rate will be the sum of flow_rat_pump_1 and flow_rate_pump_3
    concentration_M = initial_concentration_uM * dilution_factor * 1e-6 # Convert uM to M
    flow_rate_pump1 = total_flow_rate * (dilution_factor)
    volume_pump1 = volume * dilution_factor
    flow_rate_pump2 = total_flow_rate * (1 - dilution_factor)
    volume_pump2 = volume * (1 - dilution_factor)
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
    uv_data_dir_path = run_hardware_experiment(commands_path, instrument_config_path, output_dir, i)

    #PostProcess UV data. Create my own processing of the UV data
    # Put the UV data into a dataframe
    uv_vis_recording_df = pd.read_csv(uv_data_dir_path)
    #Select only the last minute of the recording for post-processing
    max_time = uv_vis_recording_df["Time(s)"].max()
    uv_vis_recording_post_processing_df = uv_vis_recording_df[
        uv_vis_recording_df["Time(s)"] >= max_time - 60
    ]  
        
    #Calculate the average absorbance for the standard wavelength
    average_absorbance_std = average_absorbance(
        uv_vis_recording_post_processing_df,
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
    
    calibration_results_df.to_csv(calibration_results_csv_path, index=False)
    print(f"Calibration results saved to {calibration_results_csv_path}.")

    #Run hardware returns the UV data file dir path. The next step is to read this file and extract the important data

    print(f"Experiment for dilution factor {dilution_factor} completed. Commands saved at {commands_path}.")
print("All experiments completed. Proceed to analyze the results and plot the calibration curve.")

#Save the calibration results to a CSV file


# Calculate the linear fit for the calibration curve
coefficients = np.polyfit(calibration_results_df["concentration_M"], calibration_results_df["average_absorbance_std"], 1)
slope, intercept = coefficients
# Calculate the extinction coefficient from the slope of the calibration curve (slope = extinction_coefficient * light_path_length)
calculated_extinction_coefficient = slope / light_path_length


# Plot the calibration curve
plt.figure(figsize=(8, 6))
plt.plot(calibration_results_df["concentration_M"], calibration_results_df["average_absorbance_std"], marker="o")
# Plto the linear fit
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
calibration_curve_plot_path = base_directory / "calibration_curve.png"
plt.savefig(calibration_curve_plot_path)
print(f"Calibration curve plot saved to {calibration_curve_plot_path}.")

#Save the calibration data in one file for future analysis, containing the expected and calculated extinction coefficients, the slope and intercept of the calibration curve, and the R-squared value of the linear fit
calibration_analysis_df = pd.DataFrame({
    "Expected Extinction Coefficient": [expected_extinction_coefficient],
    "Calculated Extinction Coefficient": [calculated_extinction_coefficient],
    "Slope": [slope],
    "Intercept": [intercept]
})
calibration_analysis_csv_path = base_directory / "calibration_analysis.csv"
calibration_analysis_df.to_csv(calibration_analysis_csv_path, index=False)
print(f"Calibration analysis saved to {calibration_analysis_csv_path}.")