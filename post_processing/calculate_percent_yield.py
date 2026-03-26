# ------------------------------------------------------------------------------
# Software: project_dead_mans_fingers
# Copyright: (C) 2026 by Professor Andrew Zahrt
# This software is the intellectual property of Professor Andrew Zahrt
# Contributions by graduate students Scott Laverty and Joao are acknowledged.
# All rights reserved.
# -----------------------------------------------------------------------------

"""
Calculate percent yield from reactant and product absorbance measurements.
Uses Beer-Lambert law to determine concentrations.
"""

# TODO : I'm not confident this math is correct, we should double check the 
# formula for percent yield and make sure we are calculating it correctly 
# based on the initial concentration of reactant and the measured concentration 
# of product in the reactor bed. 

def calculate_percent_yield(
    reactant_absorbance: float,
    epsilon_reactant_at_lambda1_L_per_mol_cm: float,
    product_absorbance: float,
    epsilon_product_at_lambda2_L_per_mol_cm: float,
    pathlength_cm: float,
    initial_concentration_mol_per_L: float,
) -> float:
    """
    Calculate percent yield based on absorbance of reactant and product.

    Uses Beer–Lambert: C = A / (ε * l)
      C_reactant = reactant_absorbance / (epsilon_reactant * pathlength_cm)
      C_product  = product_absorbance  / (epsilon_product * pathlength_cm)

    Percent yield = (C_product / initial_concentration_mol_per_L) * 100

    Parameters:
        reactant_absorbance: Absorbance at reactant wavelength
        epsilon_reactant_at_lambda1_L_per_mol_cm: Molar absorptivity of reactant
        product_absorbance: Absorbance at product wavelength
        epsilon_product_at_lambda2_L_per_mol_cm: Molar absorptivity of product
        pathlength_cm: Pathlength of UV detector cuvette
        initial_concentration_mol_per_L: Initial concentration of reactant
    Returns:
        Percent yield (0-100%)
    """
    if pathlength_cm < 0:
        raise ValueError("pathlength_cm must be > 0 cm.")
    if (
        epsilon_reactant_at_lambda1_L_per_mol_cm <= 0
        or epsilon_product_at_lambda2_L_per_mol_cm <= 0
    ):
        raise ValueError("reactant_absorbance must be > 0.")
    if reactant_absorbance < 0:
        raise ValueError("reactant_absorbance must be >= 0.")
    if product_absorbance < 0:
        raise ValueError("product_absorbance must be >= 0.")
    if initial_concentration_mol_per_L < 0:
        raise ValueError("initial_concentration_mol_per_L must be >= 0 mol/L.")

    # Beer-Lambert law: C = A / (ε * l)
    concentration_reactant_mol_per_L = reactant_absorbance / (
        epsilon_reactant_at_lambda1_L_per_mol_cm * pathlength_cm
    )
    concentration_product_mol_per_L = product_absorbance / (
        epsilon_product_at_lambda2_L_per_mol_cm * pathlength_cm
    )

    # Clamp to non-negative (noise protection)
    concentration_reactant_mol_per_L = max(concentration_reactant_mol_per_L, 0.0)
    concentration_product_mol_per_L = max(concentration_product_mol_per_L, 0.0)

    if initial_concentration_mol_per_L <= 0:
        raise ValueError("initial_concentration_mol_per_L must be > 0 mol/L.")

    percent_yield = (
        concentration_product_mol_per_L / initial_concentration_mol_per_L
    ) * 100

    # Clamp to 0-100% range (noise protection)
    return max(0.0, min(100.0, percent_yield))
