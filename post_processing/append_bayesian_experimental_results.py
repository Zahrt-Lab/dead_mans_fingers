# ------------------------------------------------------------------------------
# Software: dead_mans_fingers
# Copyright (c) 2026 Andrew Zahrt
#
# Contributions by Scott Laverty and Joao Albuquerque are acknowledged.
#
# Licensed under the MIT License. See the LICENSE file in the repository root.
# ------------------------------------------------------------------------------

"""
The purpose of this code is to append the results of each experiment to a
CSV file that the Bayesian Optimization code can read from to update its
surrogate model and propose the next experiment.
This code will be called at the end of each experiment iteration after
we have analyzed the results and calculated the percent yield and throughput.
"""

import csv
import os
from pathlib import Path

from bayesian_optimizer.experiment_state import BoCampaignState

def append_bayesian_experimental_results(
    results: dict, 
    bo_campaign_state: BoCampaignState
) -> None:
    """
    Append one result row to the Bayesian Optimization code; write header if file is new/empty.

    parameters:
     -bayesian_optimization_csv_path: Name of the file location path and file name
     -results: Results of the optimization which will be appended to this file
    return:
     -None
    """
    bo_parameters = bo_campaign_state.bo_parameters

    print(Path(bo_parameters["base_directory"]) / 
          Path(bo_parameters["Fluorescent_Bayesian_Optimization_results_filename"]))
    bayesian_optimization_csv_path = str(
        Path(bo_parameters["base_directory"]) / bo_parameters["Fluorescent_Bayesian_Optimization_results_filename"]
    )
    file_exists = os.path.exists(bayesian_optimization_csv_path)
    # define a stable column order
    column_names = [
        "iteration",
        "flow_rate",
        "dilution_factor",
        "reactor_concentration_uM",
        "temperature",
        "light_intensity",
        "target_volume",
        "reactant_wavelength",
        "product_wavelength",
        "average_absorbance_reactant",
        "average_absorbance_product",
        "percent_yield",
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
        ) 
