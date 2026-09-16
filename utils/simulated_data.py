# ------------------------------------------------------------------------------
# Software: dead_mans_fingers
# Copyright (c) 2026 Andrew Zahrt
#
# Contributions by Scott Laverty and Joao Albuquerque are acknowledged.
#
# Licensed under the MIT License. See the LICENSE file in the repository root.
# ------------------------------------------------------------------------------

"""
Docstring for utils.simulated_data
This module provides utilities for generating and handling simulated data
used to simulate UV experimental results in the project_dead_mans_fingers framework.
"""

import numpy as np
import pandas as pd


def simulate_uvvis_data(
    time_end=300,  # total time in seconds
    time_step=5,  # record every 5 seconds
    rate_constant=0.05,
    initial_absorbance=1.0,
    noise_level=0.01,
    random_seed=42,
    start_delay=60,  # delay before reaction starts (in seconds)
) -> pd.DataFrame: 
    """
    Simulate UV-Vis absorbance data for a reactant-to-product conversion.

    Reactant absorbs at 409 nm
    Product absorbs at 506 nm
    Data recorded every 5 seconds

    The simulation starts at absorbance ~0 for the first start_delay seconds,
    then the reaction begins and absorbances evolve according to first-order kinetics.

    Parameters:
       - time_end: Total duration of the simulated experiment in seconds
       - time_step: Time interval between recorded measurements in seconds
       - rate_constant: First-order rate constant for the reaction (1/s)
       - initial_absorbance: Initial absorbance of the reactant at time=0
       - noise_level: Standard deviation of Gaussian noise added to absorbance
       - random_seed: Seed for reproducibility of the random noise
       - start_delay: Time in seconds before the reaction starts (absorbance ~0)

    Returns:
       - DataFrame with columns: Time_s, Absorbance_409nm, Absorbance_506nm
    """

    np.random.seed(random_seed)

    # Time axis (every 5 seconds)
    time = np.arange(0, time_end + time_step, time_step)

    # Shifted time for kinetics (starts at 0 after delay)
    time_shifted = np.maximum(time - start_delay, 0)

    # First-order kinetics (only active after delay)
    reactant_fraction = np.exp(-rate_constant * time_shifted)
    product_fraction = 1 - reactant_fraction

    # Before delay: both absorbances near 0
    # After delay: reactant starts at initial_absorbance and decreases
    mask_before_delay = time < start_delay

    absorbance_409 = np.zeros_like(time, dtype=float)
    absorbance_506 = np.zeros_like(time, dtype=float)

    # After delay period, apply kinetics
    absorbance_409[~mask_before_delay] = (
        initial_absorbance * reactant_fraction[~mask_before_delay]
    )
    absorbance_506[~mask_before_delay] = (
        initial_absorbance * product_fraction[~mask_before_delay]
    )

    # Add experimental noise to all measurements
    absorbance_409 += np.random.normal(0, noise_level, size=len(time))
    absorbance_506 += np.random.normal(0, noise_level, size=len(time))

    # Clip to ensure absorbances stay in reasonable range [0, ~1]
    absorbance_409 = np.clip(absorbance_409, 0, initial_absorbance * 1.1)
    absorbance_506 = np.clip(absorbance_506, 0, initial_absorbance * 1.1)

    # Output as DataFrame
    data = pd.DataFrame(
        {
            "Time_s": time,
            "Absorbance_409nm": absorbance_409,
            "Absorbance_506nm": absorbance_506,
        }
    )

    return data
