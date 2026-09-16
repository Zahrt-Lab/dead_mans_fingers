# ------------------------------------------------------------------------------
# Software: dead_mans_fingers
# Copyright (c) 2026 Andrew Zahrt
#
# Contributions by Scott Laverty and Joao Albuquerque are acknowledged.
#
# Licensed under the MIT License. See the LICENSE file in the repository root.
# ------------------------------------------------------------------------------

"""
The purpose of this code is to load the experimental parameters from our json file
and check that all the necessary parameters are present for our bayesian
optimization campaign. This code will be used in our run_bo_campaign.py script
to load the experimental parameters before starting the optimization campaign.
"""

from typing import Any, Dict

def load_experimental_parameters(input_experimental_parameter_dictionary: dict) -> Dict[str, Any]:
    """
        This script loads our json file as experimental parameters for this bayesian optimization

        parameters:
         - input_experimental_parameter_dictionary: The input experimental parameter dictionary that is generated from our json file for this bayesian optimization campaign
         (this is generated from our generate_bo_input.py script)
         return:
         - experimental_parameters_dictionary: A dictionary of all the experimental
    parameters used in our dicionary
    """

    if not isinstance(input_experimental_parameter_dictionary, dict):
        raise TypeError("Input must be a dictionary.")

    experimental_parameters_dictionary = input_experimental_parameter_dictionary
    if not isinstance(experimental_parameters_dictionary, dict):
        raise ValueError(
            "Experimental parameters JSON must be an object at the top level."
        )
    return experimental_parameters_dictionary

# TODO : Need to develop this function further for complete workflow, bayesian optimzation campaign, 
# and production run parameters. This is just a placeholder for now.
def check_required_complete_workflow_parameters(
    experimental_parameters: Dict[str, Any],
) -> None:
    """
    Checks to make sure all our necessary inputs are present

    Parameters:
    - experimental_parameters: Dictionary of experimental parameters

    Returns:
     -None
    """

    # TODO : Make sure the final specified inputs match the actual inputs 
    # we need for our campaign and update this function accordingly. 
    # This is just a placeholder for now.
    experimental_parameters_check = [
        "trials",
        "total_volume_through_reactor_bed",
        "target_volume_through_reactor_bed",
        "base_directory",
        "name_of_xylopyridine_analogs_stock_solutions",
        "name_of_stock_solution2",
        "name_of_co-solvent_stock_solutions" ,
        "name_of_stock_solution4",
        "pump1_xylopyridine_analogs_volume_stock_solution",
        "pump2_0.1M_HCl_water_volume_stock_solution",
        "pump3_co-solvents_volume_stock_solutions",
        "pump4_0.1M_HCl_water_volume_stock_solution",
        "minimum_volume_required",
        "Fluorescent_Bayesian_Optimization_results_filename_prefix",
        "flow_rate",
        "dilution_factor",
        "temperature",
        "cosolvents_valve_position",
        "co_solvent_dilution_factor",
        "light_intensity",
        "xylopyridine_analogs_concentrations_uM",
        "target_absorbance_in_the_uv_detector",
        "max_absorbance_concentration_uM_uv_detector",
        "reactant_wavelength",
        "product_wavelength",
        "reference_wavelength",
        "blank_light_intensity_threshold",
        "wavelength_for_blank_light_intensity_check",
        "epsilon_reactant_at_lambda1_L_per_mol_cm",
        "epsilon_product_at_lambda1_L_per_mol_cm",
        "epsilon_reactant_at_lambda2_L_per_mol_cm",
        "epsilon_product_at_lambda2_L_per_mol_cm",
        "pathlength_cm",
        "product_run",
        "production_run_quantity_nmol",
        "instrument_com_ports"
    ]

    missing_experimental_parameter = [
        parameter
        for parameter in experimental_parameters
        if parameter not in experimental_parameters_check
    ]
    if missing_experimental_parameter:
        raise KeyError(
            f"Missing required EXPERIMENTAL_PARAMETERS keys: {missing_experimental_parameter}"
        )

    missing_experimental_parameter = [
        parameter
        for parameter in experimental_parameters
        if parameter not in experimental_parameters
    ]
    if missing_experimental_parameter:
        raise KeyError(
            f"Missing required EXPERIMENTAL_PARAMETERS keys: {missing_experimental_parameter}"
        )

def check_required_bo_campaign_parameters(
    experimental_parameters: Dict[str, Any],
) -> None:
    """
    Checks to make sure all our necessary inputs are present for our bayesian optimization campaign

    Parameters:
    - experimental_parameters: Dictionary of experimental parameters

    Returns:
     -None
    """

    # TODO : Make sure the final specified inputs match the actual inputs 
    # we need for our campaign and update this function accordingly. 
    # This is just a placeholder for now.

    required_parameters = [
        "trials", 
        "total_volume_through_reactor_bed",
        "target_volume_through_reactor_bed",
        "base_directory", 
        "name_of_xylopyridine_analogs_stock_solutions", 
        "name_of_stock_solution2", 
        "name_of_co-solvent_stock_solutions", 
        "name_of_stock_solution4", 
        "pump1_xylopyridine_analogs_volume_stock_solution", 
        "pump2_0.1M_HCl_water_volume_stock_solution", 
        "pump3_co-solvents_volume_stock_solutions", 
        "pump4_0.1M_HCl_water_volume_stock_solution", 
        "minimum_volume_required", 
        "Fluorescent_Bayesian_Optimization_results_filename_prefix", 
        "flow_rate", 
        "dilution_factor", 
        "temperature", 
        "cosolvents_valve_position", 
        "co_solvent_dilution_factor", 
        "light_intensity", 
        "xylopyridine_analogs_concentrations_uM", 
        "target_absorbance_in_the_uv_detector", 
        "max_absorbance_concentration_uM_uv_detector", 
        "reactant_wavelength",
        "product_wavelength",
        "reference_wavelength",
        "blank_light_intensity_threshold",
        "wavelength_for_blank_light_intensity_check",
        "epsilon_reactant_at_lambda1_L_per_mol_cm", 
        "epsilon_product_at_lambda1_L_per_mol_cm", 
        "epsilon_reactant_at_lambda2_L_per_mol_cm", 
        "epsilon_product_at_lambda2_L_per_mol_cm", 
        "pathlength_cm", 
        "Fluorescent_Bayesian_Optimization_results_filename", 
        "name_of_xylopyridine_analogs_to_optimize", 
        "xylopyridine_analog_index",
    ]

    missing_experimental_parameter = [
        parameter
        for parameter in required_parameters
        if parameter not in experimental_parameters
    ]
    if missing_experimental_parameter:
        raise KeyError(
            f"Missing required EXPERIMENTAL_PARAMETERS keys: {missing_experimental_parameter}"
        )


def check_required_production_run_parameters(
    experimental_parameters: Dict[str, Any],
) -> None:
    """
    Checks to make sure all our necessary inputs are present for our production run

    Parameters:
    - experimental_parameters: Dictionary of experimental parameters

    Returns:
     -None
    """

    # TODO : Make sure the final specified inputs match the actual inputs 
    # we need for our campaign and update this function accordingly. 
    # This is just a placeholder for now.