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

# TODO : I want to update this function so it doesn't take in the entire BoCampaignState and IterationState objects
# Just the bo_campaign boundaries and the current trial conditions.

from bayesian_optimizer.experiment_state import BoCampaignState, IterationState


def constrain_to_search_space(bo_campaign_state: BoCampaignState,
                            iteration_state: IterationState
                              ) -> IterationState:
    """
    Keep Bayesian optimization suggestions within valid parameter ranges.

    Parameters:
        experiment_conditions: (flow_rate, dilution_factor, temperature,
                               cosolvent_valve_position, fraction_of_cosolvent, light_intensity)
    Note: fraction_of_cosolvent refers to the experimental_dilution_factor of the co-solvent.

    Returns:
        Updated experiment state with constrained trial parameters.
    """

    bo_parameters = bo_campaign_state.bo_parameters
    trial_conditions = iteration_state.trial_conditions

    if len(trial_conditions) != 6:
        raise ValueError(
            f"Expected 6 parameters (flow_rate, dilution_factor, temperature, "
            f"cosolvent_valve_position, fraction_of_cosolvent, light_intensity), "
            f"got {len(trial_conditions)}"
        )
    
    # Part 1) Constrain parameters to user-defined search space

    # Extract and constrain flow_rate based on user input bounds
    flow_rate_min, flow_rate_max = bo_parameters["flow_rate"]
    flow_rate = round(trial_conditions["flow_rate"], 2)
    flow_rate = round(min(flow_rate_max, max(flow_rate_min, flow_rate)),2)

    # Extract and constrain dilution_factor (concentration fraction)
    dilution_min, dilution_max = bo_parameters["dilution_factor"]
    dilution_factor = round(float(
        min(max(trial_conditions["dilution_factor"], dilution_min), dilution_max)), 2)

    # Extract and constrain temperature
    temp_min, temp_max = bo_parameters["temperature"]
    temperature = round(float(trial_conditions["temperature"]),2)
    temperature = round(min(temp_max, max(temp_min, temperature)),2)

    # Extract and constrain cosolvent valve position
    cosolvent_min, cosolvent_max = bo_parameters["cosolvents_valve_position"]
    cosolvent_valve_position = float(round(trial_conditions["co_solvent_valve_position"]))
    cosolvent_valve_position = float(
        min(cosolvent_max, max(cosolvent_min, cosolvent_valve_position))
    )

    # Extract and constrain co-solvent fraction
    fraction_min, fraction_max = bo_parameters["co_solvent_dilution_factor"]
    fraction_of_cosolvent = round(float(
        min(max(trial_conditions["co_solvent_dilution_factor"], fraction_min), fraction_max)
    ), 2)

    # Extract and constrain light intensity
    light_intensity_min, light_intensity_max = bo_parameters["light_intensity"]
    light_intensity = round(float(
        min(max(trial_conditions["light_intensity"], light_intensity_min), light_intensity_max)
    ), 2)
    
    # Part 2) Physical constraints enforced

    # Validate dilution factor bounds (0-1) 
    if dilution_min < 0 or dilution_max > 1:
        raise ValueError(
            f"Dilution factor bounds must be between 0 and 1."
            f"Current min: {dilution_min}, max: {dilution_max}"
        )
    
    # Validate against physical instrument limits (0-100°C)
    if temperature < 0 or temperature > 100:
        raise ValueError(
            f"Temperature {temperature}°C is outside heater module boundaries (0-100°C)"
        )
    
    # Validate valve position against physical limits (1-6)
    if not (1 <= cosolvent_valve_position <= 6):
        raise ValueError(
            f"Cosolvent valve position {cosolvent_valve_position} is outside valid range (1-6)"
        )

    # Validate co-solvent fraction bounds (0-1)    
    if fraction_of_cosolvent < 0 or fraction_of_cosolvent > 1:
        raise ValueError(
            f"Fraction of co-solvent {fraction_of_cosolvent} must be between 0 and 1"
        )
    
    # Validate co-solvent fraction bounds (0-1)
    if light_intensity < 0 or light_intensity > 100:
        raise ValueError(
            f"Light intensity {light_intensity} must be between 0 and 100%"
        )
    
    iteration_state.update_trial_conditions({
        "flow_rate": flow_rate,
        "dilution_factor": dilution_factor,
        "temperature": temperature,
        "co_solvent_valve_position": cosolvent_valve_position,
        "co_solvent_dilution_factor": fraction_of_cosolvent,
        "light_intensity": light_intensity,
    })

    return iteration_state
