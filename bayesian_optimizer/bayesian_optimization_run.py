# ------------------------------------------------------------------------------
# Software: project_dead_mans_fingers
# Copyright: (C) 2025 by Professor Andrew Zahrt
# This software is the intellectual property of Professor Andrew Zahrt
# Contributions by graduate students Scott Laverty are acknowledged.
# All rights reserved.
# ------------------------------------------------------------------------------

"""
Bayesian optimization experiment functions.
Supports both simulated data and real AutoZahrt hardware with real-time monitoring.
"""
from typing import Tuple

from bayesian_optimizer.state import (
    EXPERIMENTAL_PARAMETERS,
    iteration,
    RESULTS_CACHE,
    bayesian_optimization_results_csv_path,
)
from post_processing.append_bayesian_experimental_results import (
    append_bayesian_experimental_results,
)
from utils.run_simulation import run_simulation

# TODO: This will need to have a better future interface with light source control from the UV-Vis detector
# TODO: Need to be able to program the light intensity of the UV-Vis detector in future iterations

import os
import time
from pathlib import Path
from typing import Tuple, Sequence

from bayesian_optimizer import state
from bayesian_optimizer.state import (
    EXPERIMENTAL_PARAMETERS,
    iteration,
    RESULTS_CACHE,
)

from preprocessing.standardize_input import standardize_input
from preprocessing.constrain_to_search_space import constrain_to_search_space
from preprocessing.parameters_to_commands import parameters_to_commands
from preprocessing.check_volume import check_volume
from preprocessing.experimental_parameters import ExperimentAborted

from experimental_commands.commands import save_commands_csv, run_commands
from experimental_commands.generate_instrument_config import generate_instrument_config, save_instrument_config_csv
# TODO : This is outdated code and will be removed now that the UV-VIS detector class is implemented in AutoZahrt_v3

# UV-VIS detector imports - only needed for real hardware mode
try:
    from experimental_commands.uv_vis_detector import begin_uv_vis_measurement, end_uv_vis_measurement
except ImportError:
    # Stub functions for simulation mode
    def begin_uv_vis_measurement(*args, **kwargs):
        raise NotImplementedError("UV-VIS hardware not available - use --simulation mode")
    def end_uv_vis_measurement(*args, **kwargs):
        pass

from post_processing.post_process_uv_recording import post_process_uv_recording
from post_processing.average_absorbance import average_absorbance
from post_processing.calculate_percent_yield import calculate_percent_yield
from post_processing.calculate_concentration_in_reactor_bed import calculate_concentration_in_the_reactor_bed
from post_processing.calculate_product_throughput import calculate_product_throughput

from utils.run_simulation import run_simulation

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

    reactor_bed_flow_rate, dilution_factor, temperature, cosolvent_valve_position, fraction_of_cosolvent, light_intensity = constrain_to_search_space(
        experiment
    )

    # Standardizes the input before checking if this experiment was done by the 2nd
    # objective function
    experiment_check = standardize_input(
        (reactor_bed_flow_rate, dilution_factor, temperature, cosolvent_valve_position, fraction_of_cosolvent, light_intensity)
    )

    # TODO: Need to figure out how to load cache of results from previous experiments from state.py and all other parameters
    # If experiment was done previously it just returns the results of the previous experiment
    if experiment_check in RESULTS_CACHE:
        return RESULTS_CACHE[experiment_check]

    iteration["iteration #"] += 1
    k = iteration["iteration #"]

    reactor_bed_concentration_uM = dilution_factor * EXPERIMENTAL_PARAMETERS["stock_concentration_uM"]
    print(
        f"Beginning experiment{k} with flow rate: {reactor_bed_flow_rate} uL/min; "
        f"concentration: {reactor_bed_concentration_uM} uM; "
        f"temperature= {temperature} °C; "
    )

    print("Setting up directories and file paths for this experiment")
    # The instrument config files and experiment files will be generated within these files
    base_directory = Path(EXPERIMENTAL_PARAMETERS["base_directory"])
    # Create the base directory if it doesn't exist (allow it to exist for subsequent iterations)
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

    instrument_parameter = parameters_to_commands(
        flow_rate_uL_per_min=reactor_bed_flow_rate,
        dilution_factor=dilution_factor,
        cosolvent_valve_position=int(cosolvent_valve_position),
        cosolvent_fraction=fraction_of_cosolvent,
        light_intensity=light_intensity,
        stock_concentration_uM=EXPERIMENTAL_PARAMETERS["stock_concentration_uM"],
        target_absorbance_in_the_uv_detector=EXPERIMENTAL_PARAMETERS["target_absorbance_in_the_uv_detector"],
        max_absorbance_concentration_uM_uv_detector=EXPERIMENTAL_PARAMETERS["max_absorbance_concentration_uM_uv_detector"],
        volume_uL=volume,
        number_of_syringes=EXPERIMENTAL_PARAMETERS["number_of_syringes"],
    )
    
    flow_rate_pump1 = instrument_parameter["flow_rate_pump1"]
    volume_pump1 = instrument_parameter["volume_pump1"]
    flow_rate_pump2 = instrument_parameter["flow_rate_pump2"]
    volume_pump2 = instrument_parameter["volume_pump2"]
    flow_rate_pump3 = instrument_parameter["flow_rate_pump3"]
    volume_pump3 = instrument_parameter["volume_pump3"]
    cosolvent_valve_position_output = instrument_parameter["position_valve1"]
    flow_rate_pump4 = instrument_parameter["flow_rate_pump4"]
    volume_pump4 = instrument_parameter["volume_pump4"]

    print("Completed calculating parameters for experimental equipment")

    print(f"The flow rate of pump 1 is {flow_rate_pump1}")
    print(f"The flow rate of pump 2 is {flow_rate_pump2}")
    print(f"The flow rate of pump 3 is {flow_rate_pump3}")
    print(f"The flow rate of pump 4 is {flow_rate_pump4}")
    print(f"The flow rate in the reactor bed is {flow_rate_pump1 + flow_rate_pump2 + flow_rate_pump3}")
    print(
        f"The flow rate of the cuvette is {flow_rate_pump1 + flow_rate_pump2 + flow_rate_pump3 + flow_rate_pump4}"
    )


    # TODO: Need to evaluate how this code works when performing this using the state.py code
    # Initialize stock solution volumes on first iteration
    if iteration["iteration #"] == 1:
        pump1_vol = EXPERIMENTAL_PARAMETERS["pump1_xylopyridine_analogs_volume_stock_solution"]
        # Handle both single value and list formats
        iteration["volume_stock_solution1"] = pump1_vol[0] if isinstance(pump1_vol, list) else pump1_vol
        
        iteration["volume_stock_solution2"] = EXPERIMENTAL_PARAMETERS[
            "pump2_0.1M_HCl_water_volume_stock_solution"
        ]
        iteration["volume_stock_solution3"] = EXPERIMENTAL_PARAMETERS[
            "pump3_co-solvents_volume_stock_solutions"
        ]
        iteration["volume_stock_solution4"] = EXPERIMENTAL_PARAMETERS[
            "pump4_0.1M_HCl_water_volume_stock_solution"
        ]

    print(
        f"There is {iteration['volume_stock_solution1']} in stock solution 1 before the experiment"
    )
    print(
        f"There is {iteration['volume_stock_solution2']} in stock solution 2 before the experiment"
    )
    print(
        f"There is {iteration['volume_stock_solution3']} in stock solution 3 before the experiment"
    )
    print(
        f"There is {iteration['volume_stock_solution4']} in stock solution 4 before the experiment"
    )
    # Volume checking and management
    if not state.SIMULATION_MODE:
        # TODO: Need to define experimental parameters to add more volume to the co-solvent stock solution
        try:
            # Always check & subtract for the current iteration (including #1)
            iteration["volume_stock_solution1"] = check_volume(
                iteration["volume_stock_solution1"],
                volume_pump1,
                EXPERIMENTAL_PARAMETERS["minimum_volume_required"],
                EXPERIMENTAL_PARAMETERS.get("name_of_stock_solution1", "Reactant"),
            )
            iteration["volume_stock_solution2"] = check_volume(
                iteration["volume_stock_solution2"],
                volume_pump2,
                EXPERIMENTAL_PARAMETERS["minimum_volume_required"],
                EXPERIMENTAL_PARAMETERS.get("name_of_stock_solution2", "Buffer"),
            )
            # Handle co-solvent volume - could be single value or list
            cosolvent_vol = iteration["volume_stock_solution3"]
            if isinstance(cosolvent_vol, list):
                # For multiple co-solvents, update the specific valve position
                valve_idx = int(cosolvent_valve_position_output) - 1  # 1-indexed to 0-indexed
                cosolvent_vol[valve_idx] = check_volume(
                    cosolvent_vol[valve_idx],
                    volume_pump3,
                    EXPERIMENTAL_PARAMETERS["minimum_volume_required"],
                    EXPERIMENTAL_PARAMETERS.get("name_of_co-solvent_stock_solutions", ["Co-solvent"])[valve_idx],
                )
                iteration["volume_stock_solution3"] = cosolvent_vol
            else:
                iteration["volume_stock_solution3"] = check_volume(
                    cosolvent_vol,
                    volume_pump3,
                    EXPERIMENTAL_PARAMETERS["minimum_volume_required"],
                    EXPERIMENTAL_PARAMETERS.get("name_of_stock_solution3", "Co-solvent"),
                )
            iteration["volume_stock_solution4"] = check_volume(
                iteration["volume_stock_solution4"],
                volume_pump4,
                EXPERIMENTAL_PARAMETERS["minimum_volume_required"],
                EXPERIMENTAL_PARAMETERS.get("name_of_stock_solution4", "Dilution Water"),
            )
        except ExperimentAborted as e:
            print(f"[PAUSED] {e}. Safe to resume once stock is topped up.")
            # Hard block until user continues (no partial writes)
            return run_bayesian_optimization_iteration(experiment)
    else:
        # In simulation mode, just subtract volumes
        iteration["volume_stock_solution1"] -= volume_pump1
        iteration["volume_stock_solution2"] -= volume_pump2
        # Handle co-solvent volume - could be single value or list
        cosolvent_vol = iteration["volume_stock_solution3"]
        if isinstance(cosolvent_vol, list):
            # For multiple co-solvents, update the specific valve position
            valve_idx = int(cosolvent_valve_position_output) - 1  # 1-indexed to 0-indexed
            cosolvent_vol[valve_idx] -= volume_pump3
            iteration["volume_stock_solution3"] = cosolvent_vol
        else:
            iteration["volume_stock_solution3"] -= volume_pump3
        # Handle dilution pump volume - could be single value or list
        pump4_vol = iteration["volume_stock_solution4"]
        if isinstance(pump4_vol, list):
            # If list, update total (sum) - though this shouldn't normally happen for pump4
            total_volume = sum(pump4_vol) - volume_pump4
            iteration["volume_stock_solution4"] = total_volume
        else:
            iteration["volume_stock_solution4"] -= volume_pump4
    
    # TODO : Need to define new co-solvent stock solution check volume function here to print
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

    save_commands_csv(
        fluorescent_reaction_command_path,
        flow_rate_pump1,
        flow_rate_pump2,
        flow_rate_pump3,
        flow_rate_pump4,
        volume_pump1,
        volume_pump2,
        volume_pump3,
        volume_pump4,
        cosolvent_valve_position_output,
        temperature,
        fraction_of_cosolvent,
        light_intensity,
    )

    print(f"Setting temperature to {temperature} celsius")
    # Run the experimental commands to set the temperature of the instrument
    if not state.SIMULATION_MODE:
        run_commands(
            f"{fluorescent_reaction_command_path}_temperature.csv", instrument_config
        )
        print("Finished setting temperature of the thermocouple")
    else:
        print("Skipping hardware temperature commands (simulation mode)")
    
    print("Running experimental wash commands to clear out the UV-detector")
    # Run the experimental commands to wash the UV-detector to clear it out
    if not state.SIMULATION_MODE:
        print("Run the experimental commands to wash the UV-detector to clear it out")
        run_commands(f"{fluorescent_reaction_command_path}_wash.csv", instrument_config)
    else:
        print("Skipping hardware wash commands (simulation mode)")

    reactant_wavelength = EXPERIMENTAL_PARAMETERS["reactant_wavelength"]
    product_wavelength = EXPERIMENTAL_PARAMETERS["product_wavelength"]

    print(f"Reactant wavelength set to {reactant_wavelength}")
    print(f"Product wavelength set to {product_wavelength}")

    # Use the main Bayesian Optimization results CSV file for all iterations
    # This ensures all results are in one file for easy plotting and analysis
    bayesian_optimization_csv_file_path = fluorescent_bayesian_optimization_results_csv

    print(
        f"Bayesian Optimization results will be appended to {bayesian_optimization_csv_file_path}"
    )

    print(
        f"Beginning UV recording at reactant wavelength {reactant_wavelength}"
        f"and product wavelength {product_wavelength}"
    )

    if not state.SIMULATION_MODE:
        print("Running experiment on experimental hardware")
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
            

    else:
        print("Running experiment in simulation mode")
        # Run simulated experiment - appends data to main CSV file
        percent_yield_sim, throughput_sim = run_simulation(
            flow_rate=reactor_bed_flow_rate,
            concentration=dilution_factor,
            temperature=temperature,
            co_solvent=cosolvent_valve_position,
            co_solvent_volume=fraction_of_cosolvent,
            reactor_concentration_uM=reactor_bed_concentration_uM,
            iteration_num=k,
            experimental_parameters=EXPERIMENTAL_PARAMETERS,
            csv_path=fluorescent_bayesian_optimization_results_csv,
            append_results_func=append_bayesian_experimental_results,
            volume_pump1=volume_pump1,
            volume_pump2=volume_pump2,
            volume_pump3=volume_pump3,
            flow_rate_pump1=flow_rate_pump1,
        )
        print(f"Simulation complete: {percent_yield_sim:.2f}% yield, {throughput_sim:.2f} nmol/min")

    '''
    reactor_bed_target_volume = compute_target_volume(
        volume,
        residence_times=EXPERIMENTAL_PARAMETERS["residence_times"],
        volume_after_residence_times_met=EXPERIMENTAL_PARAMETERS[
            "volume_after_residence_times_met"
        ],
    )
    '''

    # TODO: Think of a smarter way to program this later
    reactor_bed_target_volume = volume - 500

    print(
        f"Reactor bed target volume to reach before recording is {reactor_bed_target_volume}"
    )
    print(
        "Post-processing will occur to help select the absorbance after 3-5 residence times"
    )

    if not state.SIMULATION_MODE:
        # Real hardware mode: post-process UV recordings from hardware
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
    else:
        # Simulation mode: data already calculated and saved by run_simulation
        # We can skip post-processing and just return the values from simulation
        # For now, use the simulation results stored in percent_yield_sim and throughput_sim
        print("Skipping post-processing in simulation mode (data already calculated)")
        # Return the simulation results directly
        return percent_yield_sim, throughput_sim

    print(
        f"Average absorbance of our reactant at the end of the reaction is {average_absorbance_reactant}"
    )
    print(
        f"Average absorbance of our product at the end of the reaction is {average_absorbance_product}"
    )

    # TODO : Need to evaluate this calculate percent yield function here to make sure it is accurate
    product_percent_yield = calculate_percent_yield(
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
        volume_pump4_uL=volume_pump4,
    )

    product_throughput_nmol_per_min = calculate_product_throughput(
        concentration_product_mol_per_uL_reactor_bed,
        reactor_flow_rate_uL_per_min= (flow_rate_pump1 + flow_rate_pump2 + flow_rate_pump3),
    )

    print(f"The percent yield of our product is {product_percent_yield} %")
    print(f"The throughput of our product is {product_throughput_nmol_per_min} nmol/min")

    # Appends the Bayesian Optimization Results to the csv file
    append_bayesian_experimental_results(
        fluorescent_bayesian_optimization_results_csv,
        {
            "iteration": k,
            "flow_rate": experiment_check[0],
            "dilution_factor": experiment_check[1],
            "reactor_concentration_uM": round(reactor_bed_concentration_uM, 8),
            "temperature": experiment_check[2],
            "co_solvent": experiment_check[3],
            "co_solvent_volume": experiment_check[4],
            "light_intensity": experiment_check[5],
            "target_volume": reactor_bed_target_volume,
            "reactant_wavelength": reactant_wavelength,
            "product_wavelength": product_wavelength,
            "average_absorbance_reactant": average_absorbance_reactant,
            "average_absorbance_product": average_absorbance_product,
            "percent_yield": product_percent_yield,
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
        product_percent_yield,
        product_throughput_nmol_per_min,
    )
    return RESULTS_CACHE[experiment_check]

def objective_function_percent_yield(
    experiment: Tuple[float, float, float, float, float],
) -> float:
    """Objective function for percent yield."""
    percent_yield, _ = run_bayesian_optimization_iteration(experiment)
    return percent_yield


def objective_function_throughput(experiment: Tuple[float, float, float, float, float]) -> float:
    """Objective function for throughput."""
    _, throughput = run_bayesian_optimization_iteration(experiment)
    return throughput


    

    
    
    

