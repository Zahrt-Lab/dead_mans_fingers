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

import time
from typing import Dict

from bayesian_optimizer.experiment_state import BoCampaignState, IterationState
from experimental_commands.execute_bo_iteration_commands import (
    run_bayesian_optimization_iteration,
)

from post_processing.append_bayesian_experimental_results import (
    append_bayesian_experimental_results,
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
    # TODO : We should update this try except block later in this code
    """
    except Exception as e:
        err_msg = str(e)
        now = time.strftime("%Y-%m-%d %H:%M:%S")

        reactant_concentration_uM = float(
            dilution_factor * BO_EXPERIMENTAL_PARAMETERS.get("xylopyridine_analogs_concentrations_uM", 0.0)
        )

        reactant_wavelength = BO_EXPERIMENTAL_PARAMETERS.get("reactant_wavelength", "")
        product_wavelength = BO_EXPERIMENTAL_PARAMETERS.get("product_wavelength", "")

        append_bayesian_experimental_results(
            bayesian_optimization_results_csv_path(xylopyridine_analog),
            {
                "iteration": ITERATION["iteration #"],
                "flow_rate": flow_rate,
                "concentration": dilution_factor,
                "reactor_concentration_uM": reactant_concentration_uM,
                "temperature": temperature,
                "co_solvent": co_solvent,
                "co_solvent_volume": co_solvent_volume,
                "light_intensity": light_intensity,
                "target_volume": "",
                "reactant_wavelength": reactant_wavelength,
                "product_wavelength": product_wavelength,
                "average_absorbance_reactant": "",
                "average_absorbance_product": "",
                "percent_yield": 0.0,
                "throughput_nmol_per_min": 0.0,
                "timestamp": now,
                "status": "error",
                "error_message": (
                    (err_msg[:240] + "…") if len(err_msg) > 240 else err_msg
                ),
            },
        )

        # A value of 0 for both percent yield and throughput indicates a failed experiment to Ax and will not be considered
        # within future optimization steps and it shouldn't crash the optimization loop
        return {
            "percent_yield": (0.0, bo_campaign_state.noise_sem),
            "throughput": (0.0, bo_campaign_state.noise_sem),
        }
    }
    """