# ------------------------------------------------------------------------------
# Software: dead_mans_fingers
# Copyright (c) 2026 Andrew Zahrt
#
# Contributions by Scott Laverty and Joao Albuquerque are acknowledged.
#
# Licensed under the MIT License. See the LICENSE file in the repository root.
# ------------------------------------------------------------------------------

"""
Calculate percent yield from product concentration in the reactor bed.
"""


def calculate_percent_yield(
    concentration_product_mol_per_L: float,
    initial_concentration_mol_per_L: float,
) -> float:
    """
    Calculate percent yield from reactor bed product concentration.

    Percent yield = (C_product_reactor / C_initial_reactor) * 100

    Both concentrations must be at the reactor bed (i.e. pump 4 dilution
    must already be back-calculated before calling this function).

    Parameters:
        concentration_product_mol_per_L: Product concentration in reactor bed (mol/L)
        initial_concentration_mol_per_L: Initial reactant concentration in reactor bed (mol/L)
    Returns:
        Percent yield (0-100%)
    """
    if concentration_product_mol_per_L < 0:
        raise ValueError("concentration_product_mol_per_L must be >= 0 mol/L.")
    if initial_concentration_mol_per_L <= 0:
        raise ValueError("initial_concentration_mol_per_L must be > 0 mol/L.")

    percent_yield = (concentration_product_mol_per_L / initial_concentration_mol_per_L) * 100

    # Clamp to 0-100% range (noise protection)
    return max(0.0, min(100.0, percent_yield))
