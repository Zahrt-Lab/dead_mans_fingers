# ------------------------------------------------------------------------------
# Software: AUTO_ZAHRT
# Copyright: (C) 2025 by Professor Andrew Zahrt
# This software is the intellectual property of Professor Andrew Zahrt
# Contributions by graduate students Scott Laverty and Joao are acknowledged.
# All rights reserved.
# ------------------------------------------------------------------------------

"""
The purpose of this code is to load the experimental parameters from our json file
and check that all the necessary parameters are present for our bayesian
optimization campaign. This code will be used in our run_bo_campaign.py script
to load the experimental parameters before starting the optimization campaign.
"""

from typing import Any, Dict
import json

def load_experimental_parameters(input_json_file: str) -> Dict[str, Any]:
    """
        This script loads our json file as experimental parameters for this bayesian optimization

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
    experimental_parameters = [
        "trials",
        "volume",
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
        "epsilon_reactant_at_lambda1_L_per_mol_cm",
        "epsilon_product_at_lambda1_L_per_mol_cm",
        "epsilon_reactant_at_lambda2_L_per_mol_cm",
        "epsilon_product_at_lambda2_L_per_mol_cm",
        "pathlength_cm",
    ]

    missing_experimental_parameter = [
        parameter
        for parameter in experimental_parameters
        if parameter not in experimental_parameters
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
