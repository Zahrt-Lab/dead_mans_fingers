# ------------------------------------------------------------------------------
# Software: project_dead_mans_fingers
# Copyright: (C) 2025 by Professor Andrew Zahrt
# This software is the intellectual property of Professor Andrew Zahrt
# Contributions by graduate students Scott Laverty and Joao are acknowledged.
# All rights reserved.
# ------------------------------------------------------------------------------

"""
Constrains experimental parameters to valid search space ranges.
Ensures Bayesian optimization suggestions stay within specified experimental boundaries limits.
"""

from typing import Sequence, Tuple
from bayesian_optimizer.deterministic_commands.state import BO_EXPERIMENTAL_PARAMETERS


def constrain_to_search_space(
    experiment_conditions: Sequence[float],
) -> Tuple[float, float, float, float, float, float]:
    """
    Keep Bayesian optimization suggestions within valid parameter ranges.

    For 5D optimization:
    - flow_rate: rounds to int, clamps to [min, max]
    - dilution_factor: clamps to [min, max] float
    - temperature: rounds to int, clamps to [min, max]
    - cosolvent_valve_position: rounds to int, clamps to [min, max]
    - fraction_of_cosolvent: clamps to [min, max] float
    - light_intensity: clamps to [min, max] float

    Parameters:
        experiment_conditions: (flow_rate, dilution_factor, temperature,
                               cosolvent_valve_position, fraction_of_cosolvent, light_intensity)
    Note: fraction_of_cosolvent refers to the experimental_dilution_factor of the co-solvent.

    Returns:
        Tuple of constrained values matching input order
    """
    if len(experiment_conditions) != 6:
        raise ValueError(
            f"Expected 6 parameters (flow_rate, dilution_factor, temperature, "
            f"cosolvent_valve_position, fraction_of_cosolvent, light_intensity), "
            f"got {len(experiment_conditions)}"
        )

    # Extract and constrain flow_rate based on user input bounds
    flow_rate_min, flow_rate_max = BO_EXPERIMENTAL_PARAMETERS["flow_rate"]
    flow_rate = round(experiment_conditions[0],2)
    flow_rate = round(min(flow_rate_max, max(flow_rate_min, flow_rate)),2)

    # Extract and constrain dilution_factor (concentration fraction)
    dilution_min, dilution_max = BO_EXPERIMENTAL_PARAMETERS["dilution_factor"]
    if dilution_min < 0 or dilution_max > 1:
        raise ValueError(
            f"Dilution factor bounds must be between 0 and 1."
            f"Got min: {dilution_min}, max: {dilution_max}"
        )
    dilution_factor = round(float(
        min(max(experiment_conditions[1], dilution_min), dilution_max)), 2)

    # Extract and constrain temperature
    temp_min, temp_max = BO_EXPERIMENTAL_PARAMETERS["temperature"]
    temperature = round(float(experiment_conditions[2]),2)
    temperature = round(min(temp_max, max(temp_min, temperature)),2)

    # Validate against physical instrument limits (0-100°C)
    if temperature < 0 or temperature > 100:
        raise ValueError(
            f"Temperature {temperature}°C is outside heater module boundaries (0-100°C)"
        )

    # Extract and constrain cosolvent valve position
    cosolvent_min, cosolvent_max = BO_EXPERIMENTAL_PARAMETERS["cosolvents_valve_position"]
    cosolvent_valve_position = float(round(experiment_conditions[3]))
    cosolvent_valve_position = float(
        min(cosolvent_max, max(cosolvent_min, cosolvent_valve_position))
    )

    # Validate valve position against physical limits (1-6)
    if not (1 <= cosolvent_valve_position <= 6):
        raise ValueError(
            f"Cosolvent valve position {cosolvent_valve_position} is outside valid range (1-6)"
        )

    # Extract and constrain co-solvent fraction
    fraction_min, fraction_max = BO_EXPERIMENTAL_PARAMETERS["co_solvent_dilution_factor"]
    fraction_of_cosolvent = round(float(
        min(max(experiment_conditions[4], fraction_min), fraction_max)
    ), 2)
    if fraction_of_cosolvent < 0 or fraction_of_cosolvent > 1:
        raise ValueError(
            f"Fraction of co-solvent {fraction_of_cosolvent} must be between 0 and 1"
        )

    light_intensity_min, light_intensity_max = BO_EXPERIMENTAL_PARAMETERS[
        "light_intensity"
    ]
    light_intensity = round(float(
        min(max(experiment_conditions[5], light_intensity_min), light_intensity_max)
    ), 2)
    if light_intensity < 0 and light_intensity > 100:
        raise ValueError(
            f"Light intensity {light_intensity} must be between 0 and 100%"
        )

    return (
        flow_rate,
        dilution_factor,
        temperature,
        cosolvent_valve_position,
        fraction_of_cosolvent,
        light_intensity,
    )
