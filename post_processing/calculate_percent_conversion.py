"""
Calculate percent conversion from reactant and product absorbance measurements. Considers the sum of reactant and product concentrations.
Uses Beer-Lambert law to determine concentrations.
"""


def calculate_percent_conversion(
    reactant_absorbance: float,
    epsilon_reactant_at_lambda1_L_per_mol_cm: float,
    product_absorbance: float,
    epsilon_product_at_lambda2_L_per_mol_cm: float,
    pathlength_cm: float,
) -> float:
    """
    Calculate percent conversion based on absorbance of reactant and product.
    
    Uses Beer–Lambert: C = A / (ε * l)
      C_reactant = reactant_absorbance / (epsilon_reactant * pathlength_cm)
      C_product  = product_absorbance  / (epsilon_product * pathlength_cm)
    
    Percent conversion = (C_product / (C_reactant + C_product)) * 100
    
    Parameters:
        reactant_absorbance: Absorbance at reactant wavelength
        epsilon_reactant_at_lambda1_L_per_mol_cm: Molar absorptivity of reactant
        product_absorbance: Absorbance at product wavelength  
        epsilon_product_at_lambda2_L_per_mol_cm: Molar absorptivity of product
        pathlength_cm: Pathlength of UV detector cuvette
        
    Returns:
        Percent conversion (0-100%)
    """
    if pathlength_cm <= 0:
        raise ValueError("pathlength_cm must be > 0 cm.")
    if (
        epsilon_reactant_at_lambda1_L_per_mol_cm <= 0
        or epsilon_product_at_lambda2_L_per_mol_cm <= 0
    ):
        raise ValueError("Molar absorptivities must be >= 0.")
    
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
    
    # Total material = unreacted + reacted
    total_concentration = (
        concentration_reactant_mol_per_L + concentration_product_mol_per_L
    )
    
    if total_concentration <= 0:
        return 0.00
    
    percent_conversion = (concentration_product_mol_per_L / total_concentration) * 100
    
    # Clamp to 0-100% range (noise protection)
    return max(0.0, min(100.0, percent_conversion))