# ------------------------------------------------------------------------------
# Software: AUTO_ZAHRT
# Copyright: (C) 2025 by Professor Andrew Zahrt
# This software is the intellectual property of Professor Andrew Zahrt
# Contributions by graduate students Scott Laverty are acknowledged.
# All rights reserved.
# ------------------------------------------------------------------------------

"""
Bayesian Optimization Code to optimize the throughput/yield of our Xylo compound
"""

import os
import sys
import csv
import time
from typing import Tuple, Any, Sequence, Dict, List
from pathlib import Path
import json
import math

import pandas as pd
import argparse
from ax.service.ax_client import AxClient, ObjectiveProperties

from ..Auto_Zahrt_v3.methods.methods import GeneralExperimentMethod
from ..Auto_Zahrt_v3.uv_detectors.uv_detector import Ocean_Optics_UV_vis


def load_experimental_parameters(input_json_file: str) -> Dict[str, Any]:
    """
        This script loads our json file as en experimental parameters for this bayesian optimization

        parameters:
         - input_json_file:
         return:
         - experimental_parameters_dictionary: A dictionary of all the experimental
    parameters used in our dicionary
    """

    with open(input_json_file, "r", encoding="utf-8") as f:
        experimental_parameters_dictionary = json.load(f)
    if not isinstance(experimental_parameters_dictionary, dict):
        raise ValueError(
            "Experimental parameters JSON must be an object at the top level."
        )
    return experimental_parameters_dictionary


def check_required_experimental_parameters(
        experimental_parameters: Dict[str, Any]
) -> None:
    """
    Checks to make sure all our necessary inputs our presents

    return:
     -None
    """
    required_experimental_parameters = [
        "budget",
        "volume",
        "base_directory",
        "minimum_volume_required",
        "volume_stock_solution1",
        "volume_stock_solution2",
        "volume_stock_solution3",
        "name_of_stock_solution1",
        "name_of_stock_solution2",
        "name_of_stock_solution3",
        "Fluorescent_Bayesian_Optimization_results_filename",
        "syringe_size",
        "number_of_syringes",
        "flow_rate",
        "concentration",
        "temperature",
        "stock_concentration_uM",
        "target_absorbance_in_the_uv_detector",
        "max_absorbance_concentration_uM_uv_detector",
        "reactant_wavelength",
        "product_wavelength",
        "epsilon_reactant_at_lambda1_L_per_mol_cm",
        "epsilon_product_at_lambda1_L_per_mol_cm",
        "epsilon_reactant_at_lambda2_L_per_mol_cm",
        "epsilon_product_at_lambda2_L_per_mol_cm",
        "pathlength_cm",
        "residence_times",
        "volume_after_residence_times_met",
    ]
    missing_experimental_parameter = [
        parameter
        for parameter in required_experimental_parameters
        if parameter not in experimental_parameters
    ]
    if missing_experimental_parameter:
        raise KeyError(
            f"Missing required EXPERIMENTAL_PARAMETERS keys: {missing_experimental_parameter}"
        )
    if not (
            0.0 <= experimental_parameters["concentration"][0] <= 1.0
            and 0.0 <= experimental_parameters["concentration"][1] <= 1.0
    ):
        raise ValueError("concentration bounds must be between 0 and 1.")


class ExperimentAborted(Exception):
    pass


def check_volume(
        current_volume_uL,
        required_volume_uL,
        minimum_volume_remaining_uL,
        solution_name,
        *,
        interactive: bool = True,
):
    """
    The purpose of this code is to

    parameters:
     - current_volume_uL: The current stock solution remaining
     - required_volume_uL: volume required for the next experiment
     - minimum_volume_remaining_uL: Volume remaining needed to continue experiment e.g. 2mL
     - solution_name: Name of our stock solution
    return:
     - remaining_volume_uL: Is remaining volume after the experiment is completed
    """

    current_volume_uL = float(current_volume_uL)
    required_volume_uL = float(required_volume_uL)
    minimum_volume_remaining_uL = float(minimum_volume_remaining_uL)

    # Need at least this much BEFORE withdrawing
    threshold_uL = required_volume_uL + minimum_volume_remaining_uL

    # Prompt only if insufficient
    if current_volume_uL < threshold_uL:
        print(
            f"Stock solution {solution_name} is {current_volume_uL:.2f} µL; "
            f"need ≥ {threshold_uL:.2f} µL (required {required_volume_uL:.2f} + "
            f"reserve {minimum_volume_remaining_uL:.2f})."
        )

    # Loop while insufficient; ask user to input CURRENT volume after topping up
    while current_volume_uL < threshold_uL:
        if not interactive:
            raise ExperimentAborted(f"{solution_name}: need ≥ {threshold_uL} µL.")

        try:
            updated_current_volume_uL = input(
                "Add solvent ... enter CURRENT µL (or 'q' to abort): "
            ).strip()

        except (EOFError, KeyboardInterrupt):
            raise ExperimentAborted("Input aborted")

        if updated_current_volume_uL.lower() in {"q", "quit", "exit"}:
            raise ExperimentAborted("Aborted by user")

        try:
            updated_current_volume_uL = float(updated_current_volume_uL)

        except ValueError:
            print("Please enter a number (µL).")
            continue

        if (
                not math.isfinite(updated_current_volume_uL)
        ) or updated_current_volume_uL <= 0:
            print("Please enter a positive amount (µL).")
            continue

        current_volume_uL = updated_current_volume_uL

        shortage = threshold_uL - current_volume_uL
        if shortage > 0:
            print(
                f"Still short by {shortage:.2f} µL. Keep adding to '{solution_name}'."
            )

    remaining_volume_after_experiment = current_volume_uL - required_volume_uL
    print(
        f"Proceeding: withdrawing {required_volume_uL:.2f} µL from '{solution_name}'. "
        f"Remaining {remaining_volume_after_experiment:.2f} µL "
        f"(reserve ≥ {minimum_volume_remaining_uL:.2f} µL)."
    )
    return remaining_volume_after_experiment


def parameters_to_commands(
        flow_rate_uL_per_min: float,
        concentration: float,
        stock_concentration_uM: float,
        target_absorbance_in_the_uv_detector: float,
        max_absorbance_concentration_uM_uv_detector: float,
        volume_uL: int,
        number_of_syringes: int,
) -> Tuple[int, int, int, int, int, int]:
    """
    Generates instrument commands based on the recommendations from the bayesian optimizer

    parameters:
     - flow_rate: total flow rate when going through our reaction bed
     - concentration: Concentration of our system when going through our reaction bed
     - stock_concentration_uM:
     - target_absorbance_in_the_UV_detector: Sets the target absorbance the pumps
     should dilute to using
     the UV detector
     - max_absorbance_concentration_uM_UV_detector:
     - volume: total volume to go through our reaction bed
     - number_of_syringes: Tells the code, how many syringes are currently being used within the code

    return:
     - flow_rate_pump1: Rate to flow pump containing the Xylo compound
     - flow_rate_pump2: Rate to flow pump 0.1 M HCl Water diluting Xylo compound for
     the reaction bed
     - flow_rate_pump3: Rate to flow pump 0.1 M HCl Water diluting Xylo compound for
     the UV detector
     - volume_pump1: Volume to flow of Xylo compound through the pumps
     - volume_pump2: Volume of 0.1 M HCl water diluting Xylo compound for the reaction bed
     - volume_pump3: Volume of 0.1 M HCl Water diluting Xylo compound for the UV detector
    """
    if flow_rate_uL_per_min <= 0:
        raise ValueError("flow_rate must be > 0 µL/min.")
    if volume_uL <= 0:
        raise ValueError("volume must be > 0 µL.")
    if not (0.0 <= concentration <= 1.0):
        raise ValueError("concentration must be in [0, 1].")
    if number_of_syringes <= 0:
        raise ValueError("number_of_syringes must be >= 1.")

    # We are using two different pumps to control concentration and volume and is need to
    # help us control the conc.
    flow_rate_pump1_uL_per_min = (flow_rate_uL_per_min * concentration) / number_of_syringes
    volume_pump1_uL = (volume_uL * concentration) / number_of_syringes

    flow_rate_pump2_uL_per_min = flow_rate_uL_per_min * (1 - concentration)
    volume_pump2_uL = volume_uL * (1 - concentration)

    # Concentration in reactor stream (after first dilution):
    reactor_bed_concentration_uM = concentration * stock_concentration_uM

    # Desired concentration at detector from absorbance target:
    cuvette_concentration_uM = (
            max_absorbance_concentration_uM_uv_detector * target_absorbance_in_the_uv_detector
    )

    if cuvette_concentration_uM <= 0:
        raise ValueError("Target absorbance × max detector concentration must be > 0.")

    # If reactor is already <= target, no extra dilution needed
    if reactor_bed_concentration_uM <= cuvette_concentration_uM:
        flow_rate_pump3_uL_per_min = 0
        volume_pump3_uL = 0
    else:
        # Ratio of total flow to reactor flow needed to reach target must be ratio>1
        ratio = reactor_bed_concentration_uM / cuvette_concentration_uM
        reactor_bed_flow_rate_uL_per_min = flow_rate_pump1_uL_per_min + flow_rate_pump2_uL_per_min
        # Compute pump3 flow so that Q_total = r * Q_reactor
        cuvette_flow_rate_uL_per_min = reactor_bed_flow_rate_uL_per_min * ratio
        flow_rate_pump3_uL_per_min = max(0.0, cuvette_flow_rate_uL_per_min - reactor_bed_flow_rate_uL_per_min)
        # Apply same ratio to volumes: V_total = r * V_reactor => V_pump3 = (r-1)*V_reactor
        reactor_bed_volume_uL = volume_pump1_uL + volume_pump2_uL
        volume_pump3_uL = max(0.0, (ratio - 1.0) * reactor_bed_volume_uL)

    return (
        int(round(flow_rate_pump1_uL_per_min)), int(round(volume_pump1_uL)),
        int(round(flow_rate_pump2_uL_per_min)), int(round(volume_pump2_uL)),
        int(round(flow_rate_pump3_uL_per_min)), int(round(volume_pump3_uL)),
    )


def compute_target_volume(
        total_reactor_volume_uL: float,
        *,
        residence_times: float = 3.0,
        volume_after_residence_times_met: float = 500.0,
) -> float:
    """
    Compute the volume that must pass through the reactor before we start
    averaging UV-Vis readings.

    Formula:  target_volume = (total_reactor_volume_uL * residence_times)
                              + volume_after_residence_times_met

    Parameters:
      - total_reactor_volume_uL: Total volume (µL) sent through the bed.
      - residence_times: How many residence times to wait before sampling.
      - volume_after_residence_times_met: Extra flush volume (µL) after the
        residence-time volume has passed ensure the signal stabilizes

    Returns:
      - target_volume (µL): Volume to pass before we start recording
    """
    if total_reactor_volume_uL <= 0:
        raise ValueError("total_reactor_volume_uL must be > 0.")
    if residence_times <= 0:
        raise ValueError("residence_times must be > 0.")
    if volume_after_residence_times_met < 0:
        raise ValueError("volume_after_residence_times_met must be ≥ 0.")

    return (
            total_reactor_volume_uL * residence_times
    ) + volume_after_residence_times_met


def generate_instrument_config() -> List[List[str]]:
    """
    This is the instrument configuration of all the instruments that will be used for this
    experiment UV-detector connects automatically and doesn't have an explicit com port
    and was not included

    return:
     -rows: the config file for all the instuments to use in this experiment
    """
    header = ["InstrumentType", "DeviceNumber", "Name", "COMPort", "OtherParams"]
    rows = [
        header,
        ["Temperature", "1", "Temperature", "COM12", ""],
        ["Pump", "1", "Pump", "COM21", ""],
        ["Pump", "2", "Pump", "COM22", ""],
        ["HarvardPump", "1", "HarvardPump", "COM19", ""],
    ]
    return rows


def generate_temperature_commands(
        temperature: float, previous_temperature: float
) -> List[List[str]]:
    """
    These are the experimental parameters to feed into our equipment to be performed

    parameters:
     - temperature: The temperature to set our experiment to for this experiment
     - previous_temperature: The temperature our temperature controller was
     previously set to
    return:
     - commands: The instrument commands to heat the reaction will be used
    """

    # For every 1 degree the temperature controller will take an extra 30 second to
    # heat up or cool down if it reaches minimum time of 300 seconds.
    # Ex. If previous_temperature = 54 and temperature = 26;
    # (abs(26C - 54C) * 30 = 28C * 30 seconds = 840 seconds,
    # mininum warm up time is 300 seconds
    warm_up_time = max(300, int(abs(temperature - previous_temperature) * 30))

    header = ["Component", "Action", "Parameters", "Output", "Notes", "delay"]
    commands = [
        header,
        [
            "Temperature",
            "set_temperature",
            f"temp={temperature}, " f"temp_id=1",
            f"Setting Temperature to {temperature}C with a {warm_up_time} seconds warm up time",
            "",
            warm_up_time,
        ],
    ]
    return commands


def generate_experimental_commands(
        syringe_size: int,
        number_of_syringes: int,
        flow_rate_pump1: float,
        flow_rate_pump2: float,
        flow_rate_pump3: float,
        volume_pump1: float,
        volume_pump2: float,
        volume_pump3: float,
        *,
        zero_tolerance: float = 1e-6,  # treat |x| <= zero_tol as zero
        log_skips: bool = True,
) -> List[List[str]]:
    """
    This will generate the experimental flow reaction commands for this reactor bed

    parameters:
    - syringe_size: The type of syringe being used for the harvard aparatus
    - number_of_syringes: The number of syringes loaded on the harvard aparatus syringe
    - flow_rate_pump1: Flow rate of harvard apparatus with our XYLO compound
    - flow_rate_pump2: Flow rate of 0.1 M HCl water for diluting our compound
    before it reaches the detector using the VICI M6 Pump 1
    - flow_rate_pump3: Flow rate of 0.1 M HCL water for diluting our compound
    before it reaches the UV-detector and after the reactor bed using the
    VICI M6 Pump 2
    - volume_pump1: Volume of Xylo compound to pump using harvard aparatus
    - volume_pump2: volume 0.1 M HCl water to dilute our Xylo compound before
    it reaches the reactor bed
    - volume_pump3: volume 0.1 M HCl water to dilute our Xylo compound solution
    before it reaches the UV-detector

    return:
    - commands: Experimental commands for reacting the flow reaction
    """

    def _is_zero(rate: float, vol: float) -> bool:
        return (abs(rate) <= zero_tolerance) or (abs(vol) <= zero_tolerance)

    header = ["Component", "Action", "Parameters", "Output", "Notes", "delay"]
    commands = [header]
    commands.append([
        "HarvardPump",
        "select_syringe",
        f"syringe={syringe_size},pump_id=1",
        f"The selected syringe size is {syringe_size}, loaded with {number_of_syringes} syringes",
        "",
        0.5,
    ]
    )
    commands.append([
        "HarvardPump",
        "infuse",
        f"volume={volume_pump1},rate={flow_rate_pump1},pump_id=1",
        f"The flow rate of our Xylo compund is {flow_rate_pump1} uL/min and volume is {volume_pump1}",
        "",
        0.5,
    ]
    )
    if not _is_zero(flow_rate_pump2, volume_pump2):
        commands.append(
            [
                "Pump",
                "dispensing",
                f"flow_rate={flow_rate_pump2}, " f"volume={volume_pump2}, pump_id=1",
                f"The flow rate of our Water is {flow_rate_pump2} uL/min and volume is {volume_pump2}",
                "",
                0.5,
            ]
        )

    if not _is_zero(flow_rate_pump3, volume_pump3):
        commands.append([
            "Pump",
            "dispensing",
            f"flow_rate={flow_rate_pump3}, volume={volume_pump3}, pump_id=2",
            f"The flow rate of our Water is {flow_rate_pump3} uL/min and volume is {volume_pump3}",
            "",
            0.5,
        ]
        )
    commands.append([
        "SYNC",
        "wait_for_pumps",
        "",
        "Waiting for XYLO and WATER pumps to complete",
        "",
        0.5,
    ]
    )
    commands.append([
        "HarvardPump",
        "stop",
        "pump_id=1",
        "The pump should have stopped but this is a safety check",
        "",
        0.5,
    ]
    )

    return commands


def generate_wash_commands() -> List[List[str]]:
    """
    These are the experimental parameters to feed into our equipment to wash the XYLO compound
    out of the detector before the next reaction

    return:
    - commands: The commands to wash the Xylo compound out of the detector
    """

    header = ["Component", "Action", "Parameters", "Output", "Notes", "delay"]
    commands = [
        header,
        [
            "Pump",
            "dispensing",
            "flow_rate=3000, volume=3000.0, pump_id=2",
            "The flow rate of our Water is 3000 uL/min",
            "",
            0.5,
        ],
        [
            "SYNC",
            "wait_for_pumps",
            "",
            "Waiting for flushing of water to complete",
            "",
            0.5,
        ],
    ]
    return commands


# This saves the output instrument config file to a csv file
def save_instrument_config_csv(config_file: str) -> None:
    """
    This saves the output instrument config file to a csv file

    config_file:
     - This contains the instrument configuration file of all equipment used for this project

    return:
     - None
    """

    with open(config_file, "w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerows(generate_instrument_config())


# This saves all the instrument commands to a csv file
def save_commands_csv(
        commands_path: str,
        syringe_size: int,
        number_of_syringes: int,
        flow_rate_pump1: float,
        flow_rate_pump2: float,
        flow_rate_pump3: float,
        volume_pump1: float,
        volume_pump2: float,
        volume_pump3: float,
        temperature: float,
        previous_temperature: float,
) -> None:
    """
    The role of this csv file is to generate the csv commands for each individual
    iteration of our bayesian optimization and will have three different commands
    to set temperture, flow our compound at various concentrations, and wash the
    system after the experiment is complete

    parameters:
     - commands_path: Output directory and csv prefix for all our instrument commands
     - syringe_size: The type of syringe being used for the harvard aparatus
     - flow_rate_pump1: Flow rate of harvard apparatus with our XYLO compound
     - flow_rate_pump2: Flow rate of 0.1 M HCl water for diluting our compound
     before it reaches the detector using the VICI M6 Pump 1
     - flow_rate_pump3: Flow rate of 0.1 M HCL water for diluting our compound
     before it reaches the UV-detector and after the reactor bed using the
     VICI M6 Pump 2
     - volume_pump1: Volume of Xylo compound to pump using harvard aparatus
     - volume_pump2: volume 0.1 M HCl water to dilute our Xylo compound before
     it reaches the reactor bed
     - volume_pump3: volume 0.1 M HCl water to dilute our Xylo compound solution
     before it reaches the UV-detector
     - temperature: Temperature to set the thermal couple to for the experiment
     - previous_temperature: Previous temperature the thermal couple was set for
     the previous experiment
    return:
     - None
    """

    temperature_commands_csv = f"{commands_path}_temperature.csv"
    experiment_commands_csv = f"{commands_path}_experiment.csv"
    wash_commands_csv = f"{commands_path}_wash.csv"

    with open(temperature_commands_csv, "w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerows(
            generate_temperature_commands(temperature, previous_temperature)
        )

    with open(experiment_commands_csv, "w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerows(
            generate_experimental_commands(
                syringe_size,
                number_of_syringes,
                flow_rate_pump1,
                flow_rate_pump2,
                flow_rate_pump3,
                volume_pump1,
                volume_pump2,
                volume_pump3,
            )
        )

    with open(wash_commands_csv, "w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerows(generate_wash_commands())


def run_commands(experiment_commands, instrument_config_file) -> None:
    """
    This runs all of our experimental commands given the command and instrument config files

    parameters:
     - experiment_commands: Experimental Commands in the form of a csv
     - instrument_config_file: Instrument config file to help us to determine what equipment
     is being used
    """

    fluorescent_reaction_optimization_experiment = GeneralExperimentMethod(
        experiment_commands, instrument_config_file
    )
    fluorescent_reaction_optimization_experiment.run_experiment()


# Will create UV-detector object and return UV-VIS start time
def begin_uv_vis_measurement(
        output_directory: str,
        iter_index: int,
        *,
        baseline_intensity: int = 10000,
        integration_time: int = 60000,
        num_scans: int = 10,
        target_wavelengths: Tuple[float, float] = (409.0, 506.0),
        file_name: str = "Fluorescent_Bayesian_Optimization",
        measurement_interval: int = 5,
) -> Ocean_Optics_UV_vis:
    """
    The role of this script is to begin the UV measurements which will use the default
    parameters for this experiment

    parameters:
     - output_directory: The directory UV VIS file will be outputed to
     - iteration: What iteration of the Bayesian Optimization is being performed
     - baseline_intensity: Is the intensity reference for calibration
     - integration_time: exposure time in milliseconds for the spectrometer
     - num_scans: number of scans to perform to average the measurement
     - target_wavelengths: The target wavelengths to absorb
     - file_name: UV-VIS output
     - measurement_interval:
    return:
     - UV_VIS_detector_object: UV_VIS_detector python object
    """

    print(
        f"Initiatiating UV-VIS recording for Bayesian Optimization Iteration {iter_index}"
    )
    uv_vis_detector_object = Ocean_Optics_UV_vis(
        output_directory,
        baseline_intensity,
        integration_time,
        num_scans,
        target_wavelengths,
        save_file_path=f"{file_name}_iteration_{iter_index}.csv",
        measurement_interval=measurement_interval,
    )

    uv_vis_detector_object.initialize_Ocean_Optics_UV_VIS()
    uv_vis_detector_object.set_integration_time()
    uv_vis_detector_object.set_number_of_scans(num_scans)
    uv_vis_detector_object.set_measurement_interval(measurement_interval)

    # Our Blank and Dark UV spectrum will be loaded from here
    blank_path = Path(output_directory) / "blank_spectrum.csv"
    dark_path = Path(output_directory) / "dark_spectrum.csv"

    try:
        uv_vis_detector_object.load_blank_spectrum_from_csv(blank_path)
    except (FileNotFoundError, OSError, ValueError) as e:
        print(f"Was unable to successfully load blank spectrum file: {blank_path}")
        print(f"Error: {e}")

    try:
        uv_vis_detector_object.load_dark_spectrum_from_csv(dark_path)
    except (FileNotFoundError, OSError, ValueError) as e:
        print(f"Was unable to successfully load dark spectrum file: {dark_path}")
        print(f"Error: {e}")

    # This will begin the continous UV-measurements for this iteration of the Bayesian Optimization
    uv_vis_detector_object.start_continuous()
    return uv_vis_detector_object


def end_uv_vis_measurement(uv_vis_detector_object: Any) -> None:
    """
    Ends the UV-VIS recording

    return:
     - None
    """

    uv_vis_detector_object.stop_continuous()


def time_to_reach_target_volume(
        flow_rate: int,
        target_volume: int,
) -> float:
    """
    Time to flow the target volume based on the flow rate of the pumps

    parameters:
     - flow_rate: Measures the amount of fluid that travels through the pumps tubes in a given time
     - target_volume: Target Volume for the pumps to transfer out
    return:
     - time_target_volume_is_reached - Calculates time to flow total volume for the experiment
    """
    if flow_rate <= 0:
        raise ValueError("flow_rate must be > 0 to compute residence time.")

    time_target_volume_is_reached = (target_volume / flow_rate) * 60
    return time_target_volume_is_reached


def post_process_uv_recording(
        flow_rate: int,
        target_volume: int,
        uv_vis_absorbance_over_time_csv_file: str,
        *,
        baseline_points: int = 10,
) -> pd.DataFrame:
    """
    The role of this script is to run post-processing to extract all the points
    after the target volume is reached

    parameters:
     -flow_rate: volume of fluid exiting the pumps at a given time period
     -target_volume: target volume to reach after our reactor bed has experienced
      3-5 residence times
     -uv_vis_absorbance_over_time_csv_file:
    return:
     -uv_vis_recording_after_target_volume
    """

    time_target_volume_is_reached = time_to_reach_target_volume(
        flow_rate, target_volume
    )
    uv_vis_recording = pd.read_csv(uv_vis_absorbance_over_time_csv_file)

    if "Time(s)" not in uv_vis_recording.columns:
        raise ValueError(
            f"Expected a Time(s) column in {uv_vis_absorbance_over_time_csv_file}"
        )

    absorbance_columns = [
        absorbance_column for absorbance_column in uv_vis_recording.columns if absorbance_column != "Time(s)"
    ]

    # Baseline-correct all absorbance columns (everything except Time)
    for absorbance_column in absorbance_columns:
        absorbance_pd_series = pd.to_numeric(uv_vis_recording[absorbance_column], errors="coerce")
        baseline_shift = min(len(absorbance_pd_series), baseline_points)
        if baseline_shift == 0:
            continue
        absorbance_baseline = absorbance_pd_series.iloc[:baseline_shift].mean()
        uv_vis_recording[absorbance_column] = absorbance_pd_series - absorbance_baseline

    # This performs the filtering to only keep time points after the target volume is reached
    uv_vis_recording_after_target_volume = uv_vis_recording[
        uv_vis_recording["Time(s)"] >= time_target_volume_is_reached
        ].reset_index(drop=True)

    base, ext = os.path.splitext(uv_vis_absorbance_over_time_csv_file)
    uv_vis_recording_baseline_corrected_filename = f"{base}_baseline_corrected{ext}"
    uv_vis_recording_baseline_corrected_after_target_volume_filename = f"{base}_post_processed{ext}"

    uv_vis_recording.to_csv(
        uv_vis_recording_baseline_corrected_filename, index=False
    )
    uv_vis_recording_after_target_volume.to_csv(
        uv_vis_recording_baseline_corrected_after_target_volume_filename, index=False
    )

    return uv_vis_recording_after_target_volume


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
        raise ValueError(
            f"Wavelength {wavelength_column} not found in CSV headers: "
            f"{list(uv_vis_absorbance_over_time_df.columns)}"
        )

    average_absorbance_recorded = uv_vis_absorbance_over_time_df[
        wavelength_column
    ].mean()

    return average_absorbance_recorded


def append_bayesian_experimental_results(
        bayesian_optimization_csv_path: str, results: dict
) -> None:
    """
    Append one result row to the Bayesian Optimization code; write header if file is new/empty.

    parameters:
     -bayesian_optimization_csv_path: Name of the file location path and file name
     -results: Results of the optimization which will be appended to this file
    return:
     -None
    """

    file_exists = os.path.exists(bayesian_optimization_csv_path)
    # define a stable column order
    column_names = [
        "iteration",
        "flow_rate",
        "concentration",
        "reactor_concentration_uM",
        "temperature",
        "target_volume",
        "reactant_wavelength",
        "product_wavelength",
        "average_absorbance_reactant",
        "average_absorbance_product",
        "percent_yield",
        "percent_conversion_original",
        "throughput_nmol_per_min",
        "timestamp",
        "status",
        "error_message",
    ]
    with open(
            bayesian_optimization_csv_path, "a", newline="", encoding="utf-8"
    ) as bayesian_optimization_file:
        writer = csv.DictWriter(bayesian_optimization_file, fieldnames=column_names)
        if not file_exists or os.path.getsize(bayesian_optimization_csv_path) == 0:
            writer.writeheader()
        writer.writerow(results)
        bayesian_optimization_file.flush()
        os.fsync(
            bayesian_optimization_file.fileno()
        )  # ensure it hits disk (useful on Windows)


# ---------------- Iteration counter for filenames ----------------
iteration = {
    "iteration #": 0,
    "last_temperature": None,
    "volume_stock_solution1": None,
    "volume_stock_solution2": None,
    "volume_stock_solution3": None,
}


def constrain_to_search_space(
        experiment_conditions: Sequence[float],
) -> Tuple[int, float, int]:
    """
    Keep's Dragonfly suggestions within your valid parameter types/ranges.

    parameters:
     - experiment_conditions: Experimental conditions we will be testing for a specific iteration
     for the project
    results:
     -flow_rate:
     -concentration: Concentration for the experiment
     -temperature: Set temperature for the experiment
    """
    flow_rate = int(round(experiment_conditions[0]))
    # This is a quick check to make sure the concentration is within the
    # specified bounds if not it will select either the min or max boundary
    concentration = float(
        min(
            max(experiment_conditions[1], EXPERIMENTAL_PARAMETERS["concentration"][0]),
            EXPERIMENTAL_PARAMETERS["concentration"][1],
        )
    )
    temperature = int(round(experiment_conditions[2]))

    flow_rate_minimum, flow_rate_maximum = EXPERIMENTAL_PARAMETERS["flow_rate"]
    temperature_minimum, temperature_maximum = EXPERIMENTAL_PARAMETERS["temperature"]
    flow_rate = int(min(flow_rate_maximum, max(flow_rate_minimum, flow_rate)))
    temperature = int(min(temperature_maximum, max(temperature_minimum, temperature)))

    return flow_rate, concentration, temperature


def calculate_percent_yield(
        reactant_absorbance: float,
        epsilon_reactant_at_lambda1_L_per_mol_cm: float,
        product_absorbance: float,
        epsilon_product_at_lambda2_L_per_mol_cm: float,
        pathlength_cm: float,
) -> float:
    """
    The purpose of this code is to calculate our percent yield based on the absorbance of our
    reactant and our product

    Uses Beer–Lambert: C = A / (ε * l)
      C_A = reactant_absorbance / (epsilon_reactant * pathlength_cm)
      C_B = product_absorbance  / (epsilon_product  * pathlength_cm)

    parameters:
     - reactant_absorbance: absorbance for the wavelength of our reactant
     - epsilon_reactant_at_lambda1_L_per_mol_cm: epsilon of our reactant at our
      measured reactant wavelength
     - product_absorbance: absorbance for the wavelength of our product
     - epsilon_product_at_lambda2_L_per_mol_cm: epsilon of our product at our
      measured product wavelength
     - pathlength_cm: pathlength distance to the UV detector
    return:
     - percent yield: Calculated product yield based on the UV absorbance from
      the reactants and product
    """

    if pathlength_cm <= 0:
        raise ValueError("pathlength_cm must be > 0 cm.")
    if (
            epsilon_reactant_at_lambda1_L_per_mol_cm <= 0
            or epsilon_product_at_lambda2_L_per_mol_cm <= 0
    ):
        raise ValueError("Molar absorptivities must be > 0.")

    concentration_reactant_mol_per_L = reactant_absorbance / (
            epsilon_reactant_at_lambda1_L_per_mol_cm * pathlength_cm
    )
    concentration_product_mol_per_L = product_absorbance / (
            epsilon_product_at_lambda2_L_per_mol_cm * pathlength_cm
    )

    # Prevents negative values from absorbance
    concentration_reactant_mol_per_L = max(concentration_reactant_mol_per_L, 0.0)
    concentration_product_mol_per_L = max(concentration_product_mol_per_L, 0.0)

    # We should calculate the epsilon of both the reactant and product when calculating the percent yield
    # Needs to get beer's law plot of product and reactant than calculate the epsilon value
    sum_of_reacted_and_unreacted_compound_mol_per_L = (
            concentration_reactant_mol_per_L + concentration_product_mol_per_L
    )

    if sum_of_reacted_and_unreacted_compound_mol_per_L <= 0:
        return 0.00

    percent_yield = (
                            concentration_product_mol_per_L
                            / sum_of_reacted_and_unreacted_compound_mol_per_L
                    ) * 100

    # This is meant to keep the percent yields from 0 to 100 in case of any noise affecting results
    return max(0.0, min(100.0, percent_yield))


##### CALCULATE THE TRUE YIELD, TAKEN INTO ACCOUNT THE INITIAL STARTING MATERIAL CONCENTRATION############
def calculate_true_percent_yield(
        concentration_product_mol_per_uL_reactor_bed: float,
        initial_reactor_concentration_uM: float,
) -> float:
    """
    Calculate percent yield of product with respect to the INITIAL
    starting concentration in the reactor bed.

    parameters:
     - concentration_product_mol_per_uL_reactor_bed:
         product concentration in the reactor bed (mol/µL)
     - initial_reactor_concentration_uM:
         initial total concentration of starting material in the reactor bed (µM)

    return:
     - percent_yield_true: 0–100 % yield vs initial concentration
    """

    # initial_reactor_concentration_uM is in µM = µmol/L
    # Convert µM → mol/µL:
    #   1 µM = 1e-6 mol/L
    #   1 L = 1e6 µL
    #   => 1 µM = 1e-12 mol/µL
    initial_reactor_concentration_mol_per_uL = initial_reactor_concentration_uM * 1e-12

    if initial_reactor_concentration_mol_per_uL <= 0:
        return 0.0

    # Clamp product concentration to non-negative to avoid noise issues
    concentration_product_mol_per_uL_reactor_bed = max(
        0.0, concentration_product_mol_per_uL_reactor_bed
    )
    # TODO The current initial_reactor_concentration is not measured by the UV-detector but calculated by the code in the preprocessing steps, in future we might want to use the UV detector to get this value
    percent_yield_true = (
                                 concentration_product_mol_per_uL_reactor_bed
                                 / initial_reactor_concentration_mol_per_uL
                         ) * 100.0

    # Keep in [0, 100]
    return max(0.0, min(100.0, percent_yield_true))


def calculate_concentration_in_the_reactor_bed(absorbance: float,
                                               volume_pump1_uL: float,
                                               volume_pump2_uL: float,
                                               volume_pump3_uL: float
                                               ) -> float:
    '''
    The purpose of this script is given the absorbance of the product in the cuvette,
    it will calculate the concentration of our product within the reactor bed

    parameters:
     - absorbance: Measured absorbance of our product within our UV detector
     - volume_pump1_uL: Volume of pump 1 of reactant
     - volume_pump2_uL: Volume of pump 2 diluting before reaching the reactor bed
     - volume_pump3_uL: Volume of pump 3 diluting before reaching the cuvette
    return:
     - concentration_product_mol_per_uL_reactor_bed: Our calculated concentration of our product
     on our reactor bed before dilution to the cuvette
    '''

    # Sets min to be 0.0 in case noise causes negative values to occur
    absorbance = max(0.0, absorbance)

    # Convers L to uL
    eps_product_uL_per_mol_cm = EXPERIMENTAL_PARAMETERS["epsilon_product_at_lambda2_L_per_mol_cm"] * 1e6
    # Beer–Lambert at detector (mol/µL)
    concentration_product_mol_per_uL_cuvette = (absorbance /
                                                (eps_product_uL_per_mol_cm * EXPERIMENTAL_PARAMETERS["pathlength_cm"]))

    concentration_product_mol_per_uL_reactor_bed = ((concentration_product_mol_per_uL_cuvette *
                                                     (volume_pump1_uL + volume_pump2_uL + volume_pump3_uL)) /
                                                    (volume_pump1_uL + volume_pump2_uL))

    return concentration_product_mol_per_uL_reactor_bed


def calculate_product_throughput(
        concentration_product_mol_per_uL_reactor_bed: float,
        epsilon_product_at_lambda2_L_per_mol_cm: float,
        pathlength_cm: float,
        reactor_flow_rate_uL_per_min: float,
) -> float:
    '''
    parameters:
     - concentration_product_mol_per_uL_reactor_bed: concentration of product in our reactor bed after experiment
     - epsilon_product_at_lambda2_L_per_mol_cm: molar absorptivity of the product
     - pathlength_cm: pathlength of the cuvette
     - reactor_flow_rate_uL_per_min: What flow rate is our reactor.

    results:
     - throughput_nmol_per_min: Calculated throughput of our product compound
     '''

    if pathlength_cm <= 0:
        raise ValueError("pathlength_cm must be > 0 cm.")
    if reactor_flow_rate_uL_per_min <= 0:
        raise ValueError("volumetric_flow_rate_uL_per_min must be > 0 µL/min.")
    if epsilon_product_at_lambda2_L_per_mol_cm < 1:
        raise ValueError(f"{epsilon_product_at_lambda2_L_per_mol_cm} must be a finite number.")

    # Formula to calculate throughput given concentration of product in the reactor bed
    # and the flow rate of our product in the reactor bed
    throughput_mol_per_min = concentration_product_mol_per_uL_reactor_bed * reactor_flow_rate_uL_per_min

    # Noise can result in below 0 product, will clamp results so it's always above 0
    throughput_mol_per_min = max(0, throughput_mol_per_min)

    throughput_nmol_per_min = throughput_mol_per_min * 1e9

    return throughput_nmol_per_min


def standardize_input(
        experiment_input: Sequence[float], ndp: int = 8
) -> Tuple[float, float, float]:
    """
    The role of this script is to standardize our inputs before run_bayesian_optimization_iteration

    parameters:
     - input: Is a sequence with our flow rate, concentration, and temperature
    return:
     - standardized_input: Standardized format of our input variables for the RESULTS_CACHE
    """

    standardized_input = tuple(
        round(float(parameter), ndp) for parameter in experiment_input
    )
    return standardized_input


def bayesian_optimization_results_csv_path() -> str:
    base_directory = Path(EXPERIMENTAL_PARAMETERS["base_directory"])
    base_directory.mkdir(parents=True, exist_ok=True)
    return str(base_directory / EXPERIMENTAL_PARAMETERS["Fluorescent_Bayesian_Optimization_results_filename"])


# RESULTS_CACHE are keep all our previous runs and if the specific combination of
# flow_rate, volume and concentration has occurred before it checks so we don't
# run the same objective function twice and returns back our percent yield and
# throughput which is needed for a multi-objective optimization function to
# prevent us from rerunning the same function
RESULTS_CACHE: Dict[Tuple[float, float, float], Tuple[float, float]] = {}


def run_bayesian_optimization_iteration(
        experiment: Sequence[float],
) -> Tuple[float, float]:
    """
    1) constrain parameters to specified search space
    2) Write commands CSV for this iteration
    3) Run platform (run_commands)
    4) Analyze and process UV measurements
    5) Return percent yield and throughput of the reaction

    parameters:
     - experiment: Contains a tuple containing our flow_rate, concentration, and temperature
    return:
     - average_absorbance_at_target_wavelength: calculates the absorbance
     after a certain number of residence times

    """

    reactor_bed_flow_rate, concentration, temperature = constrain_to_search_space(
        experiment
    )

    # Standardizes the input before checking if this experiment was done by the 2nd
    # objective function
    experiment_check = standardize_input(
        (reactor_bed_flow_rate, concentration, temperature)
    )

    # If experiment was done previously it just returns the results of the previous experiment
    if experiment_check in RESULTS_CACHE:
        return RESULTS_CACHE[experiment_check]

    iteration["iteration #"] += 1
    k = iteration["iteration #"]

    reactor_bed_concentration_uM = concentration * EXPERIMENTAL_PARAMETERS["stock_concentration_uM"]
    print(
        f"Beginning experiment{k} with flow rate: {reactor_bed_flow_rate} uL/min; "
        f"concentration: {reactor_bed_concentration_uM} uM; "
        f"temperature= {temperature} °C"
    )

    # The instrument config files and experiment files will be generated within these files
    base_directory = Path(EXPERIMENTAL_PARAMETERS["base_directory"])
    base_directory.mkdir(parents=True, exist_ok=True)
    instrument_config = base_directory / "Instrument_Config_File.csv"
    fluorescent_reaction_command_path = (
            base_directory / f"Fluorescent_Optimization_Iteration_{k}"
    )

    print(f"The base directory is {base_directory}")
    print(f"The instrument config file is {instrument_config}")
    print(
        f"The fluorescent reaction command template is {fluorescent_reaction_command_path}"
    )

    # All the Bayesian Optimization Results will be appended here
    fluorescent_bayesian_optimization_results_csv = (
            base_directory
            / EXPERIMENTAL_PARAMETERS["Fluorescent_Bayesian_Optimization_results_filename"]
    )

    print(
        f"The fluorescent reaction bayesian optimization results saved to {fluorescent_bayesian_optimization_results_csv}"
    )

    # Volume to flow through the reactor bed
    volume = int(round(EXPERIMENTAL_PARAMETERS["volume"], 0))

    print(
        "Calculating experimental parameters for this bayesian optimization search point"
    )
    (
        flow_rate_pump1,
        volume_pump1,
        flow_rate_pump2,
        volume_pump2,
        flow_rate_pump3,
        volume_pump3,
    ) = parameters_to_commands(
        reactor_bed_flow_rate,
        concentration,
        EXPERIMENTAL_PARAMETERS["stock_concentration_uM"],
        EXPERIMENTAL_PARAMETERS["target_absorbance_in_the_uv_detector"],
        EXPERIMENTAL_PARAMETERS["max_absorbance_concentration_uM_uv_detector"],
        volume,
        number_of_syringes=EXPERIMENTAL_PARAMETERS["number_of_syringes"],
    )

    print("Completed calculating parameters for experimental equipment")

    print(f"The flow rate of pump 1 is {flow_rate_pump1}")
    print(f"The flow rate of pump 2 is {flow_rate_pump2}")
    print(f"The flow rate of pump 3 is {flow_rate_pump3}")
    print(f"The flow rate in the reactor bed is {flow_rate_pump1 + flow_rate_pump2}")
    print(
        f"The flow rate of the cuvette is {flow_rate_pump1 + flow_rate_pump2 + flow_rate_pump3}"
    )

    print(
        f"There is {iteration['volume_stock_solution1']} in stock solution 1 before the experiment"
    )
    print(
        f"There is {iteration['volume_stock_solution2']} in stock solution 2 before the experiment"
    )
    print(
        f"There is {iteration['volume_stock_solution3']} in stock solution 3 before the experiment"
    )

    if iteration["iteration #"] == 1:
        iteration["volume_stock_solution1"] = EXPERIMENTAL_PARAMETERS[
            "volume_stock_solution1"
        ]
        iteration["volume_stock_solution2"] = EXPERIMENTAL_PARAMETERS[
            "volume_stock_solution2"
        ]
        iteration["volume_stock_solution3"] = EXPERIMENTAL_PARAMETERS[
            "volume_stock_solution3"
        ]

    try:
        # Always check & subtract for the current iteration (including #1)
        iteration["volume_stock_solution1"] = check_volume(
            iteration["volume_stock_solution1"],
            volume_pump1,
            EXPERIMENTAL_PARAMETERS["minimum_volume_required"],
            EXPERIMENTAL_PARAMETERS["name_of_stock_solution1"],
        )
        iteration["volume_stock_solution2"] = check_volume(
            iteration["volume_stock_solution2"],
            volume_pump2,
            EXPERIMENTAL_PARAMETERS["minimum_volume_required"],
            EXPERIMENTAL_PARAMETERS["name_of_stock_solution2"],
        )
        iteration["volume_stock_solution3"] = check_volume(
            iteration["volume_stock_solution3"],
            volume_pump3,
            EXPERIMENTAL_PARAMETERS["minimum_volume_required"],
            EXPERIMENTAL_PARAMETERS["name_of_stock_solution3"],
        )
    except ExperimentAborted as e:
        print(f"[PAUSED] {e}. Safe to resume once stock is topped up.")
        # Hard block until user continues (no partial writes)
        return run_bayesian_optimization_iteration(experiment)

    print(
        f"There is {iteration['volume_stock_solution1']} in stock solution 1 after the experiment"
    )
    print(
        f"There is {iteration['volume_stock_solution2']} in stock solution 2 after the experiment"
    )
    print(
        f"There is {iteration['volume_stock_solution3']} in stock solution 3 after the experiment"
    )

    # This creates Instrument config directory
    if not os.path.exists(instrument_config):
        save_instrument_config_csv(instrument_config)

    syringe_size = EXPERIMENTAL_PARAMETERS["syringe_size"]
    number_of_syringes = EXPERIMENTAL_PARAMETERS["number_of_syringes"]

    print(
        f"There are {number_of_syringes} syringes in our harvard aparatus with "
        f"a syringe size of {syringe_size} mL"
    )

    previous_temperature = (
        iteration["last_temperature"]
        if iteration["last_temperature"] is not None
        else temperature
    )

    print(
        f"The previous temperature of our system was {previous_temperature};"
        f"the system will be heated or cooled to {temperature}."
    )

    save_commands_csv(
        fluorescent_reaction_command_path,
        syringe_size,
        number_of_syringes,
        flow_rate_pump1,
        flow_rate_pump2,
        flow_rate_pump3,
        volume_pump1,
        volume_pump2,
        volume_pump3,
        temperature,
        previous_temperature,
    )

    print(f"Setting temperature to {temperature} celsius")
    # Run the experimental commands to set the temperature of the instrument
    run_commands(
        f"{fluorescent_reaction_command_path}_temperature.csv", instrument_config
    )

    print("Finished setting temperature of the thermocouple")

    reactant_wavelength = EXPERIMENTAL_PARAMETERS["reactant_wavelength"]
    product_wavelength = EXPERIMENTAL_PARAMETERS["product_wavelength"]

    print(f"Reactant wavelength set to {reactant_wavelength}")
    print(f"Product wavelength set to {product_wavelength}")

    print(
        f"Beginning UV recording at reactant wavelength {reactant_wavelength}"
        f"and product wavelength {product_wavelength}"
    )

    uv_vis_detection_object = begin_uv_vis_measurement(
        base_directory, k, target_wavelengths=(reactant_wavelength, product_wavelength)
    )
    try:
        print(
            "Beginning flowing our compound through the reactor bed recording the product"
        )
        run_commands(
            f"{fluorescent_reaction_command_path}_experiment.csv", instrument_config
        )
    finally:
        print(f"Experiment completing, turning off UV recordings for iteration {k}")

        end_uv_vis_measurement(uv_vis_detection_object)

        print("Run he experimental commands to wash the UV-detector to clear it out")

        run_commands(f"{fluorescent_reaction_command_path}_wash.csv", instrument_config)

    print(f"Setting Last temperature to {temperature}")

    iteration["last_temperature"] = temperature

    # This is the post-processing step to calculate UV absorbance before reaching the detector
    # Give the flow rate of the system we will calculate the UV-VIS absorbance after 5 mL flows
    # through the solution
    bayesian_optimization_csv_file_name = (
        f"Fluorescent_Bayesian_Optimization_iteration_{k}.csv"
    )
    bayesian_optimization_csv_file_path = os.path.join(
        base_directory, bayesian_optimization_csv_file_name
    )

    print(
        f"Bayesian Optimization results saved to {bayesian_optimization_csv_file_path}"
    )

    '''
    reactor_bed_target_volume = compute_target_volume(
        volume,
        residence_times=EXPERIMENTAL_PARAMETERS["residence_times"],
        volume_after_residence_times_met=EXPERIMENTAL_PARAMETERS[
            "volume_after_residence_times_met"
        ],
    )
    '''

    # Think of a smarter way to program this later
    reactor_bed_target_volume = volume - 500

    print(
        f"Reactor bed target volume to reach before recording is {reactor_bed_target_volume}"
    )
    print(
        "Post-processing will occur to help select the absorbance after 3-5 residence times"
    )

    uv_vis_recording_post_processing_df = post_process_uv_recording(
        reactor_bed_flow_rate,
        reactor_bed_target_volume,
        bayesian_optimization_csv_file_path,
    )

    average_absorbance_reactant = average_absorbance(
        uv_vis_recording_post_processing_df, reactant_wavelength
    )
    average_absorbance_product = average_absorbance(
        uv_vis_recording_post_processing_df, product_wavelength
    )

    print(
        f"Average absorbance of our reactant at the end of the reaction is {average_absorbance_reactant}"
    )
    print(
        f"Average absorbance of our product at the end of the reaction is {average_absorbance_product}"
    )
    ####Modify the PLD percent yield calculation to the RP pool
    product_percent_yield_original = calculate_percent_yield(
        average_absorbance_reactant,
        EXPERIMENTAL_PARAMETERS["epsilon_reactant_at_lambda1_L_per_mol_cm"],
        average_absorbance_product,
        EXPERIMENTAL_PARAMETERS["epsilon_product_at_lambda2_L_per_mol_cm"],
        EXPERIMENTAL_PARAMETERS["pathlength_cm"],
    )

    # We want product concentration in the reactor bed; use PRODUCT absorbance, not reactant
    concentration_product_mol_per_uL_reactor_bed = calculate_concentration_in_the_reactor_bed(
        absorbance=average_absorbance_product,
        volume_pump1_uL=volume_pump1,
        volume_pump2_uL=volume_pump2,
        volume_pump3_uL=volume_pump3,
    )
    # NEW true yield vs initial concentration in the reactor bed
    product_percent_yield_true = calculate_true_percent_yield(
        concentration_product_mol_per_uL_reactor_bed=concentration_product_mol_per_uL_reactor_bed,
        initial_reactor_concentration_uM=reactor_bed_concentration_uM,
    )

    product_throughput_nmol_per_min = calculate_product_throughput(
        concentration_product_mol_per_uL_reactor_bed,
        EXPERIMENTAL_PARAMETERS["epsilon_product_at_lambda2_L_per_mol_cm"],
        # kept for validation or remove from signature
        EXPERIMENTAL_PARAMETERS["pathlength_cm"],  # not actually needed if concentration was already computed
        reactor_flow_rate_uL_per_min=(flow_rate_pump1 + flow_rate_pump2),
    )

    print(f"The percent yield of our product (final vs initial) is {product_percent_yield_true} %")
    print(f"The throughput of our product is {product_throughput_nmol_per_min} nmol/min")

    # Appends the Bayesian Optimization Results to the csv file
    append_bayesian_experimental_results(
        fluorescent_bayesian_optimization_results_csv,
        {
            "iteration": k,
            "flow_rate": experiment_check[0],
            "concentration": experiment_check[1],
            "reactor_concentration_uM": round(reactor_bed_concentration_uM, 8),
            "temperature": experiment_check[2],
            "target_volume": reactor_bed_target_volume,
            "reactant_wavelength": reactant_wavelength,
            "product_wavelength": product_wavelength,
            "average_absorbance_reactant": average_absorbance_reactant,
            "average_absorbance_product": average_absorbance_product,
            "percent_yield": product_percent_yield_true,
            "percent_conversion_original": product_percent_yield_original,
            "throughput_nmol_per_min": product_throughput_nmol_per_min,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "status": "ok",
            "error_message": "",
        },
    )

    print(
        f"Finished appending the results to csv file: {fluorescent_bayesian_optimization_results_csv}"
    )

    RESULTS_CACHE[experiment_check] = (
        product_percent_yield_true,
        product_throughput_nmol_per_min,
    )
    return RESULTS_CACHE[experiment_check]


####These next two functions could be removed, because they are not used
def objective_percent_yield(experiment: Sequence[float]) -> float:
    """
    Objective function to calculate percent yield
    """
    percent_yield_true, _ = run_bayesian_optimization_iteration(experiment)
    return percent_yield_true  # maximize


def objective_throughput(experiment: Sequence[float]) -> float:
    """
    Objective function to calculate the throughput
    """
    _, throughput = run_bayesian_optimization_iteration(experiment)
    return throughput  # maximize


EXPERIMENTAL_PARAMETERS = {}
# Main function that will begin our bayesian optimization campaign
# ---------------- Ax-backed main ----------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AUTO_ZAHRT with Ax (qNEHVI)")
    parser.add_argument("input_experimental_parameters", help="Path to experiment JSON")
    parser.add_argument("--trials", type=int, default=0,
                        help="How many BO steps to run (0 = run forever)")
    parser.add_argument("--state-path", default="ax_state.json",
                        help="Where to persist Ax experiment state (default: ax_state.json)")
    parser.add_argument("--save-every", type=int, default=1,
                        help="Persist state every K trials (default: 1)")
    parser.add_argument("--objA-threshold", type=float, default=1.0,
                        help="Percent-yield threshold (for HV reference point)")
    parser.add_argument("--objB-threshold", type=float, default=1e-9,
                        help="Throughput threshold (for HV reference point)")
    parser.add_argument("--noise-sem", type=float, default=1e-3,
                        help="Per-metric SEM reported to Ax (keeps GP stable)")
    args = parser.parse_args()

    # Expose SEM globally for evaluate()
    NOISE_SEM = float(args.noise_sem)

    # ---- Load your experimental parameters (unchanged) ----
    EXPERIMENTAL_PARAMETERS = load_experimental_parameters(
        args.input_experimental_parameters
    )
    check_required_experimental_parameters(EXPERIMENTAL_PARAMETERS)

    # Aliases to your search-space bounds
    fr_min, fr_max = EXPERIMENTAL_PARAMETERS["flow_rate"]
    conc_min, conc_max = EXPERIMENTAL_PARAMETERS["concentration"]
    temp_min, temp_max = EXPERIMENTAL_PARAMETERS["temperature"]


    # ---------------- Ax: init or load ----------------
    def _init_or_load_ax(state_path: str) -> AxClient:
        if os.path.exists(state_path):
            ax = AxClient.load_from_json_file(state_path)
            print(f"Resumed Ax experiment with {len(ax.get_trials_data_frame())} trials.")
            return ax

        ax = AxClient()
        ax.create_experiment(
            name="AUTO_ZAHRT_moo_ax",
            parameters=[
                {"name": "flow_rate", "type": "range", "bounds": [fr_min, fr_max], "value_type": "int"},
                {"name": "concentration", "type": "range", "bounds": [conc_min, conc_max], "value_type": "float"},
                {"name": "temperature", "type": "range", "bounds": [temp_min, temp_max], "value_type": "int"},
            ],
            # qNEHVI uses these thresholds as the reference point for hypervolume.
            objectives={
                "percent_yield": ObjectiveProperties(minimize=False, threshold=float(args.objA_threshold)),
                "throughput": ObjectiveProperties(minimize=False, threshold=float(args.objB_threshold)),
            },
        )
        print("Started new Ax experiment.")
        return ax


    ax = _init_or_load_ax(args.state_path)


    # ---------------- Ax evaluator ----------------
    def evaluate_ax(params: dict[str, float]) -> dict[str, tuple[float, float]]:
        """
        Runs ONE lab experiment using your existing pipeline.
        Returns the two objective metrics with (mean, sem) for Ax.
        """
        flow_rate = float(params["flow_rate"])
        concentration = float(params["concentration"])
        temperature = float(params["temperature"])

        try:
            # Use your existing single-run pipeline (no duplication).
            # This is the same computation objective_percent_yield/objective_throughput rely on.
            percent_yield, throughput = run_bayesian_optimization_iteration(
                (flow_rate, concentration, temperature)
            )

            # Your percent_yield is [0,100]; throughput is >= 0.
            # Ax expects (mean, sem): we report your value with a small SEM.
            return {
                "percent_yield": (float(percent_yield), NOISE_SEM),
                "throughput": (float(throughput), NOISE_SEM),
            }

        except Exception as e:
            # If something goes wrong with experiment it continues on
            err_msg = str(e)
            now = time.strftime("%Y-%m-%d %H:%M:%S")

            # Best-effort derived values for the CSV (safe placeholders)
            reactant_concentration_uM = float(
                concentration * EXPERIMENTAL_PARAMETERS.get("stock_concentration_uM", 0.0)
            )

            reactant_wavelength = EXPERIMENTAL_PARAMETERS.get("reactant_wavelength", "")
            product_wavelength = EXPERIMENTAL_PARAMETERS.get("product_wavelength", "")

            append_bayesian_experimental_results(
                bayesian_optimization_results_csv_path(),
                {
                    "iteration": iteration["iteration #"],  # tie error row to Ax trial id
                    "flow_rate": flow_rate,
                    "concentration": concentration,
                    "reactor_concentration_uM": reactant_concentration_uM,
                    "temperature": temperature,
                    "target_volume": "",  # unknown on failure
                    "reactant_wavelength": reactant_wavelength,
                    "product_wavelength": product_wavelength,
                    "average_absorbance_reactant": "",
                    "average_absorbance_product": "",
                    "percent_yield": 0.0,  # safe default
                    "percent_conversion_original": 0.0,
                    "throughput_nmol_per_min": 0.0,  # safe default
                    "timestamp": now,
                    "status": "error",
                    "error_message": (err_msg[:240] + "…") if len(err_msg) > 240 else err_msg,
                },
            )

            # Keep Ax alive with benign metrics
            return {
                "percent_yield": (0.0, NOISE_SEM),
                "throughput": (0.0, NOISE_SEM),
            }


    # ---------------- Run loop ----------------
    step = 0
    target = "∞" if args.trials == 0 else str(args.trials)
    try:
        while True if args.trials == 0 else (step < args.trials):
            params, tid = ax.get_next_trial()
            outcomes = evaluate_ax(params)
            ax.complete_trial(trial_index=tid, raw_data=outcomes)
            step += 1

            if (step % max(1, args.save_every)) == 0:
                ax.save_to_json_file(filepath=args.state_path)

            print(
                f"[Step {step}/{target}] Trial {tid} -> "
                f"percent_yield={outcomes['percent_yield'][0]:.4f}, "
                f"throughput={outcomes['throughput'][0]:.6g} "
                f"at params={params}"
            )
    except KeyboardInterrupt:
        print("\nInterrupted by user; saving Ax state...")
    finally:
        ax.save_to_json_file(filepath=args.state_path)
        print(f"Ax state saved to: {args.state_path}")

        # Optional: show current Pareto set in a version-robust way
        try:
            def _m(v):
                if hasattr(v, "mean"):
                    return float(v.mean)
                if isinstance(v, (tuple, list)) and v:
                    return float(v[0])
                return float(v)


            pareto = ax.get_pareto_optimal_parameters()
            items = pareto.items() if isinstance(pareto, dict) else pareto
            print("\nPareto-optimal parameter sets (approx means):")
            for p, outs in items:
                if isinstance(outs, dict):
                    summary = {m: round(_m(val), 4) for m, val in outs.items()}
                else:
                    summary = outs
                print(p, summary)
        except Exception as e:
            print(f"(Pareto print skipped: {e})")
