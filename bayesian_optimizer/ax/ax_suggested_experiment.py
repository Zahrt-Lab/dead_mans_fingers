# ------------------------------------------------------------------------------
# Software: project_dead_mans_fingers
# Copyright: (C) 2025 by Professor Andrew Zahrt
# This software is the intellectual property of Professor Andrew Zahrt
# Contributions by graduate students Scott Laverty and Joao are acknowledged.
# All rights reserved.
# ------------------------------------------------------------------------------

'''
This module evaluates experimental parameters and returns results for Ax optimization
'''

# bayesian_optimizer/evaluate_ax.py
from __future__ import annotations

import time
from typing import Dict

from bayesian_optimizer.deterministic_commands import state
from bayesian_optimizer.deterministic_commands.state import (
    BO_EXPERIMENTAL_PARAMETERS,
    ITERATION,
    bayesian_optimization_results_csv_path,
)
from experimental_commands.execute_bo_iteration_commands import run_bayesian_optimization_iteration


from post_processing.append_bayesian_experimental_results import (
    append_bayesian_experimental_results,
)

def ax_suggested_experiment(
        ax_suggested_experimental_parameters: Dict[str, float],
        xylopyridine_analog: str
        ) -> Dict[str, tuple[float, float]]:
    """
    Runs ONE lab experiment using your existing pipeline.
    Returns the two objective metrics with (mean, sem) for Ax.

    Parameters:
     ax_suggested_experimental_parameters: Dictionary of experimental parameters suggested 
     by Ax for this iteration, with parameter names as keys and parameter values as floats.
     xylopyridine_analog: Name of the xylopyridine analog being optimized
    Returns:
        Dictionary with keys "percent_yield" and "throughput", each mapping to a tuple of (mean, sem) 
        for that objective metric to return to Ax.
    """

    # This first checks experimental cache to avoid redundant experiments
    flow_rate = round(float(ax_suggested_experimental_parameters["flow_rate"]), 2)
    dilution_factor = round(float(ax_suggested_experimental_parameters["dilution_factor"]), 2)
    temperature = round(float(ax_suggested_experimental_parameters["temperature"]), 2)
    co_solvent = round(float(ax_suggested_experimental_parameters["co_solvent"]), 2)
    co_solvent_volume = round(float(ax_suggested_experimental_parameters["co_solvent_volume"]), 2)
    light_intensity = round(float(ax_suggested_experimental_parameters["light_intensity"]), 2)
    
    # It then tries to run the experiment using the run_bayesian_optimization_iteration function, catching errors
    #try:
    percent_yield, throughput = run_bayesian_optimization_iteration(
        (flow_rate, dilution_factor, temperature, co_solvent, co_solvent_volume, light_intensity)
    )

    return {
        "percent_yield": (float(percent_yield), state.NOISE_SEM),
        "throughput": (float(throughput), state.NOISE_SEM),
    }
    '''
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
            "percent_yield": (0.0, state.NOISE_SEM),
            "throughput": (0.0, state.NOISE_SEM),
        }
    '''

