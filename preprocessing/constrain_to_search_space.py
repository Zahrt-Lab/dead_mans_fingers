"""
Constrains experimental parameters to valid search space ranges.
Ensures Bayesian optimization suggestions stay within specified experimental boundaries limits.
"""

from typing import Sequence, Tuple
from bayesian_optimizer.state import EXPERIMENTAL_PARAMETERS


def constrain_to_search_space(
    experiment_conditions: Sequence[float],
) -> Tuple[float, float, float, float, float]:
    """
    Keep Bayesian optimization suggestions within valid parameter ranges.
    
    For 5D optimization:
    - flow_rate: rounds to int, clamps to [min, max]
    - dilution_factor: clamps to [min, max] float
    - temperature: rounds to int, clamps to [min, max]
    - cosolvent_valve_position: rounds to int, clamps to [min, max]
    - fraction_of_cosolvent: clamps to [min, max] float
    
    Parameters:
        experiment_conditions: (flow_rate, dilution_factor, temperature, 
                               cosolvent_valve_position, fraction_of_cosolvent)
    
    Returns:
        Tuple of constrained values matching input order
    """
    if len(experiment_conditions) != 5:
        raise ValueError(
            f"Expected 5 parameters (flow_rate, dilution_factor, temperature, "
            f"cosolvent_valve_position, fraction_of_cosolvent), got {len(experiment_conditions)}"
        )
    
    # Extract and constrain flow_rate
    flow_rate_min, flow_rate_max = EXPERIMENTAL_PARAMETERS["flow_rate"]
    flow_rate = int(round(experiment_conditions[0]))
    flow_rate = int(min(flow_rate_max, max(flow_rate_min, flow_rate)))
    
    # Extract and constrain dilution_factor (concentration fraction)
    dilution_min, dilution_max = EXPERIMENTAL_PARAMETERS["dilution_factor"]
    dilution_factor = float(
        min(max(experiment_conditions[1], dilution_min), dilution_max)
    )
    
    # Extract and constrain temperature
    temp_min, temp_max = EXPERIMENTAL_PARAMETERS["temperature"]
    temperature = int(round(experiment_conditions[2]))
    temperature = int(min(temp_max, max(temp_min, temperature)))
    
    # Validate against physical instrument limits (0-100°C)
    if temperature < 0 or temperature > 100:
        raise ValueError(
            f"Temperature {temperature}°C is outside heater module boundaries (0-100°C)"
        )
    
    # Extract and constrain cosolvent valve position
    cosolvent_min, cosolvent_max = EXPERIMENTAL_PARAMETERS["cosolvents_valve_position"]
    cosolvent_valve_position = int(round(experiment_conditions[3]))
    cosolvent_valve_position = int(min(cosolvent_max, max(cosolvent_min, cosolvent_valve_position)))

    # Validate valve position against physical limits (1-6)
    if not (1 <= cosolvent_valve_position <= 6):
        raise ValueError(
            f"Cosolvent valve position {cosolvent_valve_position} is outside valid range (1-6)"
        )
    
    # Extract and constrain co-solvent fraction
    fraction_min, fraction_max = EXPERIMENTAL_PARAMETERS["co_solvent_dilution_factor"]
    fraction_of_cosolvent = float(
        min(max(experiment_conditions[4], fraction_min), fraction_max)
    )
    
    return (
        flow_rate,
        dilution_factor,
        temperature,
        cosolvent_valve_position,
        fraction_of_cosolvent,
    )
