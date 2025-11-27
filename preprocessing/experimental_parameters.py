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

from AUTO_ZAHRT.Methods.General_Methods_v9 import GeneralExperimentMethod
from AUTO_ZAHRT.UV_VIS_Detector.UV_VIS_platform_v2 import Ocean_Optics_UV_vis


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
