# TODO: The purpose of this code is to execute all hardware commands generated for the experimental setup per iteration

# TODO: This will need to have a better future interface with light source control

import time
from typing import Tuple, Sequence

from bayesian_optimizer.state import (
    EXPERIMENTAL_PARAMETERS,
    iteration,
    RESULTS_CACHE,
    SIMULATION_MODE,
)

from experimental_commands.commands import save_commands_csv, run_commands
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

    #TODO : Constrain to search space function needs to be defined
    reactor_bed_flow_rate, dilution_factor, temperature, cosolvent_valve_position, fraction_of_cosolvent = constrain_to_search_space(
        experiment
    )

    #TODO: Define standardize input function
    # Standardizes the input before checking if this experiment was done by the 2nd
    # objective function
    experiment_check = standardize_input(
        (reactor_bed_flow_rate, dilution_factor, temperature, cosolvent_valve_position, fraction_of_cosolvent)
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
        cosolvent_valve_position,
        flow_rate_pump4,
        volume_pump4,

    ) = parameters_to_commands(
        reactor_bed_flow_rate,
        dilution_factor,
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
    print(f"The flow rate of pump 4 is {flow_rate_pump4}")
    print(f"The flow rate in the reactor bed is {flow_rate_pump1 + flow_rate_pump2 + flow_rate_pump3}")
    print(
        f"The flow rate of the cuvette is {flow_rate_pump1 + flow_rate_pump2 + flow_rate_pump3 +flow_rate_pump4}"
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
    print(
        f"There is {iteration['volume_stock_solution4']} in stock solution 4 before the experiment"
    )

    # TODO : Need to define check volume function for co-solvents
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


    # TODO: Need to define experimental parameters to add more volume to the co-solvent stock solution
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

    product_percent_yield = calculate_percent_yield(
        average_absorbance_reactant,
        EXPERIMENTAL_PARAMETERS["epsilon_reactant_at_lambda1_L_per_mol_cm"],
        average_absorbance_product,
        EXPERIMENTAL_PARAMETERS["epsilon_product_at_lambda2_L_per_mol_cm"],
        EXPERIMENTAL_PARAMETERS["pathlength_cm"],
        reactor_bed_concentration_uM / 1e6,  # Convert uM to mol/L
    )

    # We want product concentration in the reactor bed; use PRODUCT absorbance, not reactant
    concentration_product_mol_per_uL_reactor_bed = calculate_concentration_in_the_reactor_bed(
        absorbance=average_absorbance_product,
        volume_pump1_uL=volume_pump1,
        volume_pump2_uL=volume_pump2,
        volume_pump3_uL=volume_pump3,
    )

    product_throughput_nmol_per_min = calculate_product_throughput(
        concentration_product_mol_per_uL_reactor_bed,
        EXPERIMENTAL_PARAMETERS["epsilon_product_at_lambda2_L_per_mol_cm"],
        # kept for validation or remove from signature
        EXPERIMENTAL_PARAMETERS["pathlength_cm"],  # not actually needed if concentration was already computed
        reactor_flow_rate_uL_per_min= (flow_rate_pump1 + flow_rate_pump2),
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




    

    
    
    
