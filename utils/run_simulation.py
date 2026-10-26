# ------------------------------------------------------------------------------
# Software: dead_mans_fingers
# Copyright (c) 2026 Zahrt Research Group
#
# Contributions by Scott Laverty are acknowledged.
#
# Licensed under the MIT License. See the LICENSE file in the repository root.
# ------------------------------------------------------------------------------

"""
Run simulated Bayesian Optimization experiments with real-time UV-Vis monitoring.
"""

from pathlib import Path
from typing import Callable, Optional

import pandas as pd
import numpy as np

from utils.simulated_data import simulate_uvvis_data


def run_simulated_experiment(
    reactor_bed_flow_rate: float,
    temperature: float,
    dilution_factor: float,
    volume: int,
    iteration_number: int,
    reactant_wavelength: int,
    product_wavelength: int,
    base_directory: Path,
    rate_constant_fn: Optional[Callable[[float, float, float], float]] = None,
) -> str:
    """
    Generate simulated UV-VIS data for a Bayesian optimization experiment.

    Simulates the reaction kinetics based on temperature, concentration, and flow rate,
    then saves the simulated absorbance data to a CSV file.

    Parameters:
        reactor_bed_flow_rate: Flow rate through reactor in uL/min.
        temperature: Reaction temperature in °C.
        dilution_factor: Dilution factor of stock solution (0.1-1.0).
        volume: Total volume to flow through reactor in uL.
        iteration_number: Current BO iteration number.
        reactant_wavelength: Wavelength for reactant absorbance (nm).
        product_wavelength: Wavelength for product absorbance (nm).
        base_directory: Directory to save simulated data CSV.
        rate_constant_fn: Optional callable with signature
            ``(flow_rate, temperature, dilution_factor) -> float``.
            When provided, its return value is used as the first-order rate
            constant instead of the default temperature/dilution formula.
            Intended for testing with known analytical response surfaces.

    Returns:
        Path to the saved CSV file containing simulated UV-VIS data.
    """
    print("[SIMULATION] Skipping UV-VIS hardware and running simulated experiment")
    print(
        "[SIMULATION] Skipping run_commands - would run:"
        "_temperature.csv, _light_intensity.csv, _experiment.csv and _wash.csv"
    )
    print("[SIMULATION] Generating simulated UV-VIS data...")

    # Calculate experiment time based on flow rate and volume
    experiment_time_seconds = (
        (volume / reactor_bed_flow_rate) * 60 if reactor_bed_flow_rate > 0 else 600
    )

    # Compute the first-order rate constant.
    # If a custom rate_constant_fn is provided (e.g. for testing), use it;
    # otherwise fall back to the default temperature/dilution formula.
    if rate_constant_fn is not None:
        rate_constant = rate_constant_fn(
            reactor_bed_flow_rate, temperature, dilution_factor
        )
    else:
        base_rate = 0.01
        temp_factor = (temperature - 5) / 85  # Normalize temperature (5-90°C range)
        dilution_norm = (dilution_factor - 0.1) / 0.9  # Normalize dilution (0.1-1.0 range)
        rate_constant = base_rate + (0.04 * temp_factor) + (0.02 * dilution_norm)
        rate_constant = max(0.005, min(0.08, rate_constant))  # Clamp to realistic range
    
    # Generate simulated data
    simulated_data_df = simulate_uvvis_data(
        time_end=int(experiment_time_seconds),
        time_step=5,
        rate_constant=rate_constant,
        initial_absorbance=1.0,
        noise_level=0.01,
        random_seed=42 + iteration_number,
        start_delay=min(60, experiment_time_seconds * 0.2),
    )
    
    # Rename columns to match expected format for post_process_uv_recording
    # Column format: "Time(s)" and wavelength as string (e.g., "409", "506")
    simulated_data_df = simulated_data_df.rename(
        columns={
            "Time_s": "Time(s)",
            "Absorbance_409nm": str(reactant_wavelength),
            "Absorbance_506nm": str(product_wavelength),
        }
    )
    
    # Save simulated data to CSV (same path post_process_uv_recording expects)
    csv_filename = f"Fluorescent_Bayesian_Optimization_iteration_{iteration_number}.csv"
    csv_filepath = Path(base_directory) / Path(csv_filename)
    simulated_data_df.to_csv(csv_filepath, index=False)
    
    print(f"[SIMULATION] Saved simulated UV-VIS data to {csv_filepath}")

    return str(csv_filepath)
