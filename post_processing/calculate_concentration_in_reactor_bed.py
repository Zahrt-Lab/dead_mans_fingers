# ------------------------------------------------------------------------------
# Software: project_dead_mans_fingers
# Copyright: (C) 2026 by Professor Andrew Zahrt
# This software is the intellectual property of Professor Andrew Zahrt
# Contributions by graduate students Scott Laverty and Joao are acknowledged.
# All rights reserved.
# -----------------------------------------------------------------------------

"""
Calculate product concentration in reactor bed from UV detector measurements.
Accounts for dilution that occurs after the reactor but before the detector.
"""
from bayesian_optimizer.experiment_state import BoCampaignState, IterationState

def calculate_concentration_in_the_reactor_bed(
    absorbance: float,
    experiment_state: BoCampaignState,
    iteration_state: IterationState
    ) -> float:
    """
    Calculate product concentration in reactor bed from detector absorbance.

    The detector measures diluted product (after pump4 dilution).
    This function back-calculates the concentration before dilution.

    Flow Chemistry Setup:
      pump1 (reactant (Xylopyridine Analogs) in 0.1 M HCl Water)
      + pump2 (0.1 M HCl Water)
      + pump3 (cosolvent) → reactor output

      reactor output + pump4 (dilution) → detector

    Parameters:
        absorbance: Measured absorbance of product at UV detector
        experiment_state: ExperimentState object containing experimental parameters
    Returns:
        Product concentration in reactor bed (mol/µL)
    """
    # Clamp to non-negative (noise protection)
    A = max(0.0, absorbance)

    # Convert epsilon from L/(mol·cm) to µL/(mol·cm)
    epsilon = experiment_state.bo_parameters["epsilon_product_at_lambda2_L_per_mol_cm"] * 1e6

    l = experiment_state.bo_parameters["pathlength_cm"]

    # Beer–Lambert at detector: C = A / (ε * l)
    c_cuvette = A / (epsilon * l)

    volume_reactor_uL = iteration_state.instrument_parameters["volume_pump1"] + \
                        iteration_state.instrument_parameters["volume_pump2"] + \
                        iteration_state.instrument_parameters["volume_pump3"]

    if iteration_state.instrument_parameters["volume_pump4"] < 0:
        raise ValueError(f"volume_pump4 must be >= 0, got {iteration_state.instrument_parameters['volume_pump4']}")

    volume_detector_uL = volume_reactor_uL + iteration_state.instrument_parameters["volume_pump4"]

    c_reactor = c_cuvette * (volume_detector_uL / volume_reactor_uL)

    # Return the calculated concentration in the reactor bed, ensuring it's non-negative
    # TODO : Need to double check if these units are correct.
    # Units are in mol/µL
    return max(0.0, c_reactor)
