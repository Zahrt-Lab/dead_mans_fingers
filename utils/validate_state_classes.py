# ------------------------------------------------------------------------------
# Software: dead_mans_fingers
# Copyright (c) 2026 Andrew Zahrt
#
# Contributions by Scott Laverty and Joao Albuquerque are acknowledged.
#
# Licensed under the MIT License. See the LICENSE file in the repository root.
# ------------------------------------------------------------------------------

"""
Validate the state of BoCampaignState and IterationState objects.
Called as a quick sanity check before each BO iteration since these objects
are threaded through the entire pipeline.
"""

from bayesian_optimizer.experiment_state import BoCampaignState, IterationState

_REQUIRED_BO_KEYS = {
    "base_directory",
    "xylopyridine_analogs_concentrations_uM",
    "total_volume_through_reactor_bed",
    "target_volume_through_reactor_bed",
    "reactant_wavelength",
    "product_wavelength",
    "reference_wavelength",
    "blank_light_intensity_threshold",
    "wavelength_for_blank_light_intensity_check",
    "Fluorescent_Bayesian_Optimization_results_filename",
    "epsilon_reactant_at_lambda1_L_per_mol_cm",
    "epsilon_product_at_lambda2_L_per_mol_cm",
    "pathlength_cm",
    "max_absorbance_concentration_uM_uv_detector",
    "target_absorbance_in_the_uv_detector",
}

_REQUIRED_TRIAL_KEYS = {
    "flow_rate",
    "dilution_factor",
    "temperature",
    "light_intensity",
}


def validate_bo_campaign_state(state: BoCampaignState) -> None:
    """
    Validate a BoCampaignState object.

    Parameters:
        state: The BoCampaignState to validate.
    Raises:
        TypeError: If state is not a BoCampaignState.
        ValueError: If required fields are missing or invalid.
    """
    if not isinstance(state, BoCampaignState):
        raise TypeError(f"Expected BoCampaignState, got {type(state).__name__}")
    if not isinstance(state.simulation_mode, bool):
        raise ValueError(
            f"simulation_mode must be bool, got {type(state.simulation_mode).__name__}"
        )
    if state.noise_sem_percent_yield <= 0:
        raise ValueError(f"noise_sem_percent_yield must be > 0, got {state.noise_sem_percent_yield}")
    if state.noise_sem_throughput <= 0:
        raise ValueError(f"noise_sem_throughput must be > 0, got {state.noise_sem_throughput}")
    missing = _REQUIRED_BO_KEYS - set(state.bo_parameters.keys())
    if missing:
        raise ValueError(
            f"bo_parameters is missing required keys: {sorted(missing)}"
        )


def validate_iteration_state(state: IterationState) -> None:
    """
    Validate an IterationState object.

    Parameters:
        state: The IterationState to validate.
    Raises:
        TypeError: If state is not an IterationState.
        ValueError: If required fields are missing or invalid.
    """
    if not isinstance(state, IterationState):
        raise TypeError(f"Expected IterationState, got {type(state).__name__}")
    if state.iteration < 0:
        raise ValueError(f"iteration must be >= 0, got {state.iteration}")
    missing = _REQUIRED_TRIAL_KEYS - set(state.trial_conditions.keys())
    if missing:
        raise ValueError(
            f"trial_conditions is missing required keys: {sorted(missing)}"
        )
    if state.reactor_bed_concentration_uM < 0:
        raise ValueError(
            f"reactor_bed_concentration_uM must be >= 0, "
            f"got {state.reactor_bed_concentration_uM}"
        )
