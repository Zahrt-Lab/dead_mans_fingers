"""
Calculate product concentration in reactor bed from UV detector measurements.
Accounts for dilution that occurs after the reactor but before the detector.
"""
from bayesian_optimizer.state import EXPERIMENTAL_PARAMETERS


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
    
    Flow path:
      pump1 (reactant in 0.1 M HCl Water) + pump2 (0.1 M HCl Water) + pump3 (cosolvent) → reactor
      reactor output + pump4 (dilution) → detector
    
    Parameters:
        absorbance: Measured absorbance of product at UV detector
        volume_pump1_uL: Volume from pump 1 (reactant)
        volume_pump2_uL: Volume from pump 2 (pre-reactor dilution)
        volume_pump3_uL: Volume from pump 3 (co-solvent)
        volume_pump4_uL: Volume from pump 4 (post-reactor bed dilution to detector)
        
    Returns:
        Product concentration in reactor bed (mol/µL)
    """
    # Clamp to non-negative (noise protection)
    absorbance = max(0.0, absorbance)
    
    # Convert epsilon from L/(mol·cm) to µL/(mol·cm)
    eps_product_uL_per_mol_cm = (
        EXPERIMENTAL_PARAMETERS["epsilon_product_at_lambda2_L_per_mol_cm"] * 1e6
    )
    
    # Beer–Lambert at detector: C = A / (ε * l)
    concentration_product_mol_per_uL_cuvette = absorbance / (
        eps_product_uL_per_mol_cm * EXPERIMENTAL_PARAMETERS["pathlength_cm"]
    )
    
    # Back-calculate reactor concentration accounting for pump4 dilution
    # C_reactor * V_reactor = C_cuvette * V_cuvette
    # C_reactor = C_cuvette * (V_cuvette / V_reactor)
    # where V_cuvette = V_reactor + volume_pump4
    #       V_reactor = volume_pump1 + volume_pump2 + volume_pump3
    
    volume_reactor = volume_pump1_uL + volume_pump2_uL + volume_pump3_uL
    volume_cuvette = volume_reactor + volume_pump4_uL  # pump4 is dilution to cuvette
    
    concentration_product_mol_per_uL_reactor_bed = (
        concentration_product_mol_per_uL_cuvette * volume_cuvette / volume_reactor
    )
    
    return concentration_product_mol_per_uL_reactor_bed
