# ------------------------------------------------------------------------------
# Software: project_dead_mans_fingers
# Copyright: (C) 2026 by Professor Andrew Zahrt
# This software is the intellectual property of Professor Andrew Zahrt
# Contributions by graduate students Scott Laverty and Joao are acknowledged.
# All rights reserved.
# -----------------------------------------------------------------------------

"""
Calculate product throughput from reactor bed concentration and flow rate.
Throughput = concentration × flow rate (nmol/min).
"""


def calculate_product_throughput(
    concentration_product_mol_per_uL_reactor_bed: float,
    reactor_flow_rate_uL_per_min: float,
) -> float:
    """
    Calculate product throughput in the reactor.

    Throughput = concentration × volumetric flow rate

    Parameters:
        concentration_product_mol_per_uL_reactor_bed: Product concentration in reactor
        reactor_flow_rate_uL_per_min: Flow rate through reactor (µL/min)

    Returns:
        Product throughput (nmol/min)
    """

    # Throughput = concentration (mol/µL) × flow rate (µL/min) = mol/min
    throughput_mol_per_min = (
        concentration_product_mol_per_uL_reactor_bed * reactor_flow_rate_uL_per_min
    )

    # Convert to nmol/min
    throughput_nmol_per_min = throughput_mol_per_min * 1e9

    # Clamp to non-negative (noise protection)
    throughput_nmol_per_min = max(0.0, throughput_nmol_per_min)

    return throughput_nmol_per_min
