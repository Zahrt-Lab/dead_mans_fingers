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
from bayesian_optimizer.deterministic_commands.state import BO_EXPERIMENTAL_PARAMETERS

from bayesian_optimizer.deterministic_commands import state

def calculate_concentration_in_the_reactor_bed(
    absorbance: float,
    volume_pump1_uL: float,
    volume_pump2_uL: float,
    volume_pump3_uL: float,
    volume_pump4_uL: float,
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
        volume_pump1_uL: Volume from pump 1 (Xylopyridine Analogs)
        volume_pump2_uL: Volume from pump 2 (pre-reactor dilution)
        volume_pump3_uL: Volume from pump 3 (co-solvent)
        volume_pump4_uL: Volume from pump 4 (post-reactor bed dilution to detector)

    Returns:
        Product concentration in reactor bed (mol/µL)
    """
    # Clamp to non-negative (noise protection)
    A = max(0.0, absorbance)

    # Convert epsilon from L/(mol·cm) to µL/(mol·cm)
    epsilon = state.BO_EXPERIMENTAL_PARAMETERS["epsilon_product_at_lambda2_L_per_mol_cm"] * 1e6

    l = state.BO_EXPERIMENTAL_PARAMETERS["pathlength_cm"]

    # Beer–Lambert at detector: C = A / (ε * l)
    c_cuvette = A / (epsilon * l)

    volume_reactor_uL = volume_pump1_uL + volume_pump2_uL + volume_pump3_uL

    if volume_pump4_uL < 0:
        raise ValueError(f"volume_pump4_uL must be >= 0, got {volume_pump4_uL}")

    volume_detector_uL = volume_reactor_uL + volume_pump4_uL

    c_reactor = c_cuvette * (volume_detector_uL / volume_reactor_uL)

    # Return the calculated concentration in the reactor bed, ensuring it's non-negative
    # TODO : Need to double check if these units are correct.
    # Units are in mol/µL
    return max(0.0, c_reactor)
