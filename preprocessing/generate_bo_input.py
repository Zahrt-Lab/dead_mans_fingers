# ------------------------------------------------------------------------------
# Software: AUTO_ZAHRT
# Copyright: (C) 2025 by Professor Andrew Zahrt
# This software is the intellectual property of Professor Andrew Zahrt
# Contributions by graduate students Scott Laverty and Joao are acknowledged.
# All rights reserved.
# ------------------------------------------------------------------------------

"""
This script will generate the json input file for an individual xylopyridine analog
bayesian optimization campaign
"""

import json
import copy
from typing import Dict, Any
import os


def generate_bo_input_file(
    complete_workflow_input_json_file: str,
    xylopyridine_analog: str,
) -> tuple[Dict[str, Any], str]:
    """
    This function will generate the json input file for an individual xylopyridine analog
    bayesian optimization campaign.
    This will be used in as a dictionary in the state.py file for our bayesian optimization
    campaign for a specific xylopyridine analog.

    parameters:
     - complete_workflow_input_json_file: The complete workflow input json file that 
       contains all the necessary information for our bayesian optimization campaign
     - xylopyrdine_analog: The name of the xylopyridine analog we are optimizing for
       in our campaign
    return:
      - Tuple of (bo_workflow_parameters dict, file_path where it was saved)
    """
    complete_workflow_parameters = {}
    # Load the complete workflow input json file as a dictionary
    with open(complete_workflow_input_json_file, "r", encoding="utf-8") as f:
        complete_workflow_parameters = json.load(f)

    bo_workflow_parameters = copy.deepcopy(complete_workflow_parameters)

    # Remove the parameters that are not necessary for the bayesian optimization campaign
    del bo_workflow_parameters["product_run"]
    del bo_workflow_parameters["production_run_quantity_nmol"]

    # Update directory and filename parameters per xylopyridine analog
    bo_workflow_parameters["base_directory"] = (
        complete_workflow_parameters["base_directory"]
        + f"/{xylopyridine_analog}/bo_campaign"
    )
    bo_workflow_parameters["Fluorescent_Bayesian_Optimization_results_filename"] = (
        complete_workflow_parameters[
            "Fluorescent_Bayesian_Optimization_results_filename_prefix"
        ]
        + f"_{xylopyridine_analog}_results.csv"
    )

    # Update the xylopyrdine index value for the stock solution of the xylopyridine analog we are optimizing for in our campaign
    bo_workflow_parameters["name_of_xylopyridine_analogs_to_optimize"] = xylopyridine_analog
    

    # Update the index value for the xylopyridine analog we are optimizing for in our campaign
    bo_workflow_parameters["xylopyridine_analog_index"] = complete_workflow_parameters[
        "name_of_xylopyridine_analogs_stock_solutions"
    ].index(xylopyridine_analog)

    xylopyridine_analog_index = bo_workflow_parameters["xylopyridine_analog_index"]

    # Update the UV-VIS parameters for the xylopyridine analog we are optimizing for
    bo_workflow_parameters["xylopyridine_analogs_concentrations_uM"] = (
        complete_workflow_parameters["xylopyridine_analogs_concentrations_uM"][
            xylopyridine_analog_index
        ]
    )
    bo_workflow_parameters["target_absorbance_in_the_uv_detector"] = (
        complete_workflow_parameters["target_absorbance_in_the_uv_detector"][
            xylopyridine_analog_index
        ]
    )
    bo_workflow_parameters["max_absorbance_concentration_uM_uv_detector"] = (
        complete_workflow_parameters["max_absorbance_concentration_uM_uv_detector"][
            xylopyridine_analog_index
        ]
    )
    bo_workflow_parameters["reactant_wavelength"] = complete_workflow_parameters[
        "reactant_wavelength"
    ][xylopyridine_analog_index]

    bo_workflow_parameters["product_wavelength"] = complete_workflow_parameters[
        "product_wavelength"
    ][xylopyridine_analog_index]

    bo_workflow_parameters["reference_wavelength"] = complete_workflow_parameters[
        "reference_wavelength"
    ][xylopyridine_analog_index]
    
    bo_workflow_parameters["epsilon_reactant_at_lambda1_L_per_mol_cm"] = (
        complete_workflow_parameters["epsilon_reactant_at_lambda1_L_per_mol_cm"][
            xylopyridine_analog_index
        ]
    )
    bo_workflow_parameters["epsilon_product_at_lambda1_L_per_mol_cm"] = (
        complete_workflow_parameters["epsilon_product_at_lambda1_L_per_mol_cm"][
            xylopyridine_analog_index
        ]
    )
    bo_workflow_parameters["epsilon_reactant_at_lambda2_L_per_mol_cm"] = (
        complete_workflow_parameters["epsilon_reactant_at_lambda2_L_per_mol_cm"][
            xylopyridine_analog_index
        ]
    )
    bo_workflow_parameters["epsilon_product_at_lambda2_L_per_mol_cm"] = (
        complete_workflow_parameters["epsilon_product_at_lambda2_L_per_mol_cm"][
            xylopyridine_analog_index
        ]
    )

    # Save the updated workflow parameters to a new json file in the analog's output directory
    os.makedirs(bo_workflow_parameters["base_directory"], exist_ok=True)
    output_file_path = os.path.join(
        bo_workflow_parameters["base_directory"],
        f"{xylopyridine_analog}_bo_input.json"
    )
    with open(output_file_path, "w", encoding="utf-8") as f:
        json.dump(bo_workflow_parameters, f, indent=2)

    return bo_workflow_parameters, output_file_path
