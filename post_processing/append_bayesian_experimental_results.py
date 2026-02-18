# ------------------------------------------------------------------------------
# Software: project_dead_mans_fingers
# Copyright: (C) 2026 by Professor Andrew Zahrt
# This software is the intellectual property of Professor Andrew Zahrt
# Contributions by graduate students Scott Laverty and Joao are acknowledged.
# All rights reserved.
# -----------------------------------------------------------------------------

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

from bayesian_optimizer.deterministic_commands import state

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

    print("Hey Hey you you where are the csv files,"
          f"{bayesian_optimization_csv_path}")
    print(state.BO_EXPERIMENTAL_PARAMETERS["base_directory"])
    print(type(bayesian_optimization_csv_path))
    print(type(state.BO_EXPERIMENTAL_PARAMETERS["base_directory"]))
    bayesian_optimization_csv_path = str(
        Path(state.BO_EXPERIMENTAL_PARAMETERS["base_directory"]) / bayesian_optimization_csv_path
    )
    file_exists = os.path.exists(bayesian_optimization_csv_path)
    # define a stable column order
    column_names = [
        "iteration",
        "flow_rate",
        "dilution_factor",
        "reactor_concentration_uM",
        "temperature",
        "co_solvent",
        "co_solvent_volume",
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
