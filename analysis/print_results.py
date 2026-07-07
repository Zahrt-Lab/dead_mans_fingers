'''
This module contains functions to gather results and print them into tables. It is callable from the analysis.py script.

print_flow_rate_iterations: Iterates over the *experiment.csv files and saves the flow rates of each itaration and each pump into a csv file.
'''

import pandas as pd
from pathlib import Path
import os

def print_flow_rate_iterations(csv_dir_path: str, save_dir_path: str):

    csv_dir_path = Path(csv_dir_path)
    save_dir_path = Path(save_dir_path)
    save_dir_path.mkdir(parents=True, exist_ok=True)

    components = [
        "VICI_M6_Pump_1",
        "Tecan_pump_1",
        "Tecan_pump_2",
        "Tecan_pump_3",
    ]

    flow_rate_df = pd.DataFrame({"Pump": components})

    experiment_files = sorted(
        csv_dir_path.glob("*_experiment.csv"),
        key=lambda f: int(f.stem.split("_")[3])
    )

    for experiment_file in experiment_files:

        params = _get_pump_parameters(experiment_file)

        iteration = int(experiment_file.stem.split("_")[3])

        flow_rate_df[f"Iteration_{iteration}"] = (
            flow_rate_df["Pump"].map(params)
        )

    output_file = save_dir_path / "flow_rate_iterations.csv"
    flow_rate_df.to_csv(output_file, index=False)

    print(f"Saved flow rate iterations to {output_file}")

def _get_pump_parameters(csv_file):
    """
    Read an experiment CSV and return the Parameters for the
    specified pumps.

    Parameters
    ----------
    csv_file : str or Path
        Path to the experiment CSV.

    Returns
    -------
    dict
        Dictionary mapping component names to their Parameters.
    """
    components = [
        "VICI_M6_Pump_1",
        "Tecan_pump_1",
        "Tecan_pump_2",
        "Tecan_pump_3",
    ]

    df = pd.read_csv(csv_file)

    return (
        df.loc[df["Component"].isin(components), ["Component", "Parameters"]]
          .set_index("Component")["Parameters"]
          .to_dict()
    )