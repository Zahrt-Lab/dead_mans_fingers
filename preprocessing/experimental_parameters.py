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
from utils.experiment_aborted import ExperimentAborted

# TODO Fix imports below
#from AUTO_ZAHRT.Methods.General_Methods_v9 import GeneralExperimentMethod
#from AUTO_ZAHRT.UV_VIS_Detector.UV_VIS_platform_v2 import Ocean_Optics_UV_vis


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

# TODO: Needs to update the code to include parameters for light intensity and xylopyridine analogs
# TODO: We should use a different name for volume variables to avoid confusion of what it for

def check_required_experimental_parameters(
    experimental_parameters: Dict[str, Any], simulation_mode: bool = False
) -> None:
    """
    Checks to make sure all our necessary inputs are present

    Parameters:
    - experimental_parameters: Dictionary of experimental parameters
    - simulation_mode: If False, the AutoZahrt commands generated will be sent to the automated platform to be executed.
                     If True, the AutoZahrt commands will be generated but not sent to the platform to executed

    Returns:
     -None
    """
    experimental_parameters = [
          "budget",
          "volume",
          "base_directory",
          "minimum_volume_required",
          "pump1_xylopyridine_analogs_volume_stock_solution",
          "pump2_0.1M_HCl_water_volume_stock_solution",
          "pump3_co-solvents_volume_stock_solutions",
          "pump4_0.1M_HCl_water_volume_stock_solution",
          "name_of_co-solvent_stock_solutions",
          "Fluorescent_Bayesian_Optimization_results_filename",
          "syringe_size",
          "number_of_syringes",
          "flow_rate",
          "dilution_factor",
          "cosolvents_valve_position",
          "co_solvent_dilution_factor",
          "stock_concentration_uM",
          "target_absorbance_in_the_uv_detector",
          "max_absorbance_concentration_uM_uv_detector",
          "reactant_wavelength",
          "product_wavelength",
          "epsilon_reactant_at_lambda1_L_per_mol_cm",
          "epsilon_product_at_lambda1_L_per_mol_cm",
          "epsilon_reactant_at_lambda2_L_per_mol_cm",
          "epsilon_product_at_lambda2_L_per_mol_cm",
          "pathlength_cm"
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


