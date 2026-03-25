# ------------------------------------------------------------------------------
# Software: project_dead_mans_fingers
# Copyright: (C) 2025 by Professor Andrew Zahrt
# This software is the intellectual property of Professor Andrew Zahrt
# Contributions by graduate students Scott Laverty and Joao are acknowledged.
# All rights reserved.
# ------------------------------------------------------------------------------

"""
This module evaluates experimental parameters and returns results for Ax optimization
"""

# bayesian_optimizer/evaluate_ax.py
from __future__ import annotations

from typing import Dict

from bayesian_optimizer.experiment_state import BoCampaignState, IterationState
from experimental_commands.execute_bo_iteration_commands import (
    run_bayesian_optimization_iteration,
)


def ax_suggested_experiment(
    bo_campaign_state: BoCampaignState,
    iteration_state: IterationState,
) -> Dict[str, tuple[float, float]]:
    """
    Runs ONE lab experiment using your existing pipeline.
    Returns the two objective metrics with (mean, sem) for Ax.

    Parameters:
     - experiment_trial_conditions: Dictionary containing the trial conditions for this experiment
    Returns:
        Dictionary with keys "percent_yield" and "throughput"
    """

    trial_conditions = iteration_state.trial_conditions

    # This first checks experimental cache to avoid redundant experiments
    iteration_state.update_trial_conditions(
        {
        "flow_rate": trial_conditions["flow_rate"],
        "dilution_factor": trial_conditions["dilution_factor"],
        "temperature": trial_conditions["temperature"],
        "co_solvent_valve_position": trial_conditions["co_solvent_valve_position"],
        "co_solvent_dilution_factor": trial_conditions["co_solvent_dilution_factor"],
        "light_intensity": trial_conditions["light_intensity"]
        }
    )

    # It then begins to run the bayesian optimization iteration
    # try:
    percent_yield, throughput = run_bayesian_optimization_iteration(
        bo_campaign_state,
        iteration_state,
    )

    return {
        "percent_yield": (float(percent_yield), bo_campaign_state.noise_sem),
        "throughput": (float(throughput), bo_campaign_state.noise_sem),
    }