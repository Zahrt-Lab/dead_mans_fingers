"""
Calculate product throughput from reactor bed concentration and flow rate.
Throughput = concentration × flow rate (nmol/min).
"""


def calculate_product_throughput(
    concentration_product_mol_per_uL_reactor_bed: float,
    epsilon_product_at_lambda2_L_per_mol_cm: float,
    pathlength_cm: float,
    reactor_flow_rate_uL_per_min: float,
) -> float:
    """
    Calculate product throughput in the reactor.
    
    Throughput = concentration × volumetric flow rate
    
    Parameters:
        concentration_product_mol_per_uL_reactor_bed: Product concentration in reactor
        epsilon_product_at_lambda2_L_per_mol_cm: Molar absorptivity (for validation)
        pathlength_cm: Pathlength of cuvette (for validation)
        reactor_flow_rate_uL_per_min: Flow rate through reactor (µL/min)
        
    Returns:
        Product throughput (nmol/min)
    """
    if pathlength_cm <= 0:
        raise ValueError("pathlength_cm must be > 0 cm.")
    if reactor_flow_rate_uL_per_min <= 0:
        raise ValueError("volumetric_flow_rate_uL_per_min must be > 0 µL/min.")
    if epsilon_product_at_lambda2_L_per_mol_cm < 1:
        raise ValueError(
            f"epsilon_product must be >= 1, got {epsilon_product_at_lambda2_L_per_mol_cm}"
        )
    
    # Throughput = concentration (mol/µL) × flow rate (µL/min) = mol/min
    throughput_mol_per_min = (
        concentration_product_mol_per_uL_reactor_bed * reactor_flow_rate_uL_per_min
    )
    
    # Convert to nmol/min
    throughput_nmol_per_min = throughput_mol_per_min * 1e9
    
    # Clamp to non-negative (noise protection)
    throughput_nmol_per_min = max(0.0, throughput_nmol_per_min)
    
    return throughput_nmol_per_min
