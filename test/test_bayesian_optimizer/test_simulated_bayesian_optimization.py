# ------------------------------------------------------------------------------
# Software: project_dead_mans_fingers
# Copyright: (C) 2026 by Professor Andrew Zahrt
# This software is the intellectual property of Professor Andrew Zahrt
# Contributions by graduate students Scott Laverty and Joao are acknowledged.
# All rights reserved.
# ------------------------------------------------------------------------------

"""
Integration tests for the Bayesian Optimization campaign in simulation mode.

All three tests exercise the complete simulation pipeline end-to-end:

    Ax suggestion
    → parameters_to_commands  (pump flow rates and volumes)
    → run_simulated_experiment (UV-Vis CSV via first-order kinetics)
    → analyze_experiment_results (Beer-Lambert → percent yield and throughput)
    → ax.complete_trial

Each test injects a different ``rate_constant_fn`` with a known interior peak.
The BO must steer towards that peak to achieve high product throughput.  A small
reactor volume (200 µL, target 150 µL) is used so that the rate constant
meaningfully determines the steady-state product fraction at each parameter set.

After 50 iterations the best observed throughput must reach
``_THROUGHPUT_THRESHOLD`` nmol/min.  This threshold is set conservatively (70 %
of the analytical maximum) so the test reliably passes while still catching
regressions that would cause the pipeline to return near-zero results.

Intended to run on the daily CI/CD pipeline to catch obvious bugs in the full
code path without requiring hardware.
"""

import sys
from pathlib import Path
from typing import Callable

sys.path.append(str(Path(__file__).parent.parent))

from ax.service.ax_client import AxClient

from bayesian_optimizer.experiment_state import BoCampaignState, IterationState
from bayesian_optimizer.init_or_load_ax import _init_or_load_ax
from post_processing.post_processing_results import analyze_experiment_results
from preprocessing.parameters_to_commands import parameters_to_commands
from utils.run_simulation import run_simulated_experiment
from utils.test_response_surfaces import make_peaked_rate_constant

# ---------------------------------------------------------------------------
# Test constants
# ---------------------------------------------------------------------------

_N_ITERATIONS: int = 50
_NOISE_SEM: float = 1e-3

# Minimum throughput (nmol/min) the BO must reach in any of the three tests.
# Set to 70 % of the analytical maximum (~29 nmol/min) at the known optima.
_THROUGHPUT_THRESHOLD: float = 20.0

# Search-space bounds from test_config_ax_demo.json
_FLOW_RATE_MIN: float = 40.0
_FLOW_RATE_MAX: float = 200.0
_DILUTION_MIN: float = 0.05
_DILUTION_MAX: float = 0.5
_TEMP_MIN: float = 20.0
_TEMP_MAX: float = 60.0
_VALVE_MIN: float = 1.0
_VALVE_MAX: float = 3.0
_COSOLVENT_DILUTION_MIN: float = 0.0
_COSOLVENT_DILUTION_MAX: float = 0.4
_LIGHT_MIN: float = 0.0
_LIGHT_MAX: float = 100.0

# Three known optima – each test uses a different peak location so that
# different regions of the search space are validated.
_SURFACE_1 = {"flow_rate": 120.0, "temperature": 50.0, "dilution_factor": 0.28}
_SURFACE_2 = {"flow_rate": 80.0, "temperature": 55.0, "dilution_factor": 0.42}
_SURFACE_3 = {"flow_rate": 170.0, "temperature": 45.0, "dilution_factor": 0.22}


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------


def _make_ax_client(ax_json_path: Path) -> AxClient:
    """Create a fresh AxClient using the test_config_ax_demo.json search space."""
    experimental_bounds = {
        "flow_rate_min": _FLOW_RATE_MIN,
        "flow_rate_max": _FLOW_RATE_MAX,
        "dilution_factor_min": _DILUTION_MIN,
        "dilution_factor_max": _DILUTION_MAX,
        "temperature_min": _TEMP_MIN,
        "temperature_max": _TEMP_MAX,
        "cosolvent_valve_position_min": _VALVE_MIN,
        "cosolvent_valve_position_max": _VALVE_MAX,
        "co_solvent_dilution_factor_min": _COSOLVENT_DILUTION_MIN,
        "co_solvent_dilution_factor_max": _COSOLVENT_DILUTION_MAX,
        "light_intensity_min": _LIGHT_MIN,
        "light_intensity_max": _LIGHT_MAX,
    }
    return _init_or_load_ax(
        ax_previous_run_json_file_path=str(ax_json_path),
        experimental_bounds=experimental_bounds,
        percent_yield_threshold=10.0,
        throughput_threshold=5.0,
    )


def _make_bo_state(base_directory: Path) -> BoCampaignState:
    """
    Build a BoCampaignState for pipeline tests.

    A small reactor volume (200 µL, target 150 µL) ensures the rate constant
    meaningfully affects the steady-state product fraction.  At the default
    large volume the reaction always reaches near-completion regardless of
    kinetics, making the response surface effectively flat.

    Chemical constants match analog-0 from test_config_ax_demo.json.
    """
    state = BoCampaignState()
    state.update_bo_parameters(
        {
            "total_volume_through_reactor_bed": 200,
            "target_volume_through_reactor_bed": 150,
            "xylopyridine_analogs_concentrations_uM": 1000.0,
            "max_absorbance_concentration_uM_uv_detector": 88.0,
            "target_absorbance_in_the_uv_detector": 1.0,
            "reactant_wavelength": 409,
            "product_wavelength": 506,
            "epsilon_reactant_at_lambda1_L_per_mol_cm": 11367.0,
            "epsilon_product_at_lambda2_L_per_mol_cm": 12994.57,
            "pathlength_cm": 1.0,
            "base_directory": str(base_directory),
            "Fluorescent_Bayesian_Optimization_results_filename": str(
                base_directory / "bo_results.csv"
            ),
        }
    )
    return state


def _run_bo_pipeline(
    tmp_path: Path,
    rate_constant_fn: Callable[[float, float, float], float],
    ax_json_name: str,
) -> float:
    """
    Run the full simulation pipeline for ``_N_ITERATIONS`` and return the best
    throughput observed across all trials.

    This helper drives the complete code path from Ax parameter suggestion through
    UV-Vis CSV generation and Beer-Lambert post-processing back to Ax trial
    completion.  It is shared by all three pipeline tests below.

    Args:
        tmp_path: Pytest temporary directory for CSV and Ax JSON output.
        rate_constant_fn: Callable injected into run_simulated_experiment.  Shapes
            the first-order kinetics so the BO must find the known peak.
        ax_json_name: Filename for the Ax state JSON (must be unique per test).

    Returns:
        Best throughput (nmol/min) observed across all 50 iterations.
    """
    ax = _make_ax_client(tmp_path / ax_json_name)
    bo_state = _make_bo_state(tmp_path)
    best_throughput: float = 0.0

    for step in range(_N_ITERATIONS):
        params, trial_idx = ax.get_next_trial()

        iter_state = IterationState()
        iter_state.update_iteration(step + 1)
        iter_state.update_trial_conditions(params)
        iter_state.update_reactor_bed_concentration_uM(
            float(params["dilution_factor"])
            * bo_state.bo_parameters["xylopyridine_analogs_concentrations_uM"]
        )

        instrument_params = parameters_to_commands(
            iter_state.trial_conditions,
            bo_state.bo_parameters["total_volume_through_reactor_bed"],
            bo_state.bo_parameters["xylopyridine_analogs_concentrations_uM"],
            bo_state.bo_parameters["max_absorbance_concentration_uM_uv_detector"],
            bo_state.bo_parameters["target_absorbance_in_the_uv_detector"],
        )
        iter_state.update_instrument_parameters(instrument_params)

        csv_path = run_simulated_experiment(
            reactor_bed_flow_rate=float(params["flow_rate"]),
            temperature=float(params["temperature"]),
            dilution_factor=float(params["dilution_factor"]),
            volume=bo_state.bo_parameters["total_volume_through_reactor_bed"],
            iteration_number=step,
            reactant_wavelength=bo_state.bo_parameters["reactant_wavelength"],
            product_wavelength=bo_state.bo_parameters["product_wavelength"],
            base_directory=tmp_path,
            rate_constant_fn=rate_constant_fn,
        )

        _, _, pct_yield, throughput = analyze_experiment_results(
            bo_state, iter_state, csv_path
        )

        ax.complete_trial(
            trial_index=trial_idx,
            raw_data={
                "percent_yield": (pct_yield, _NOISE_SEM),
                "throughput": (throughput, _NOISE_SEM),
            },
        )
        best_throughput = max(best_throughput, throughput)

    return best_throughput


# ---------------------------------------------------------------------------
# Pipeline test 1: balanced interior optimum
# ---------------------------------------------------------------------------


def test_bo_pipeline_balanced_interior_optimum(tmp_path: Path) -> None:
    """
    Pipeline test with rate constant peak at a balanced interior point.

    Known optimum: flow_rate=120 µL/min, temperature=50 °C, dilution_factor=0.28.
    This places the optimum near the centre of each parameter range.
    """
    rate_fn = make_peaked_rate_constant(**_SURFACE_1)
    best_throughput = _run_bo_pipeline(tmp_path, rate_fn, "ax_surface1.json")

    assert best_throughput >= _THROUGHPUT_THRESHOLD, (
        f"Best throughput {best_throughput:.2f} nmol/min did not reach "
        f"{_THROUGHPUT_THRESHOLD:.1f} nmol/min for surface 1 "
        f"(optimum at flow={_SURFACE_1['flow_rate']}, "
        f"temp={_SURFACE_1['temperature']}, "
        f"dilution={_SURFACE_1['dilution_factor']})"
    )


# ---------------------------------------------------------------------------
# Pipeline test 2: high dilution, low flow, high temperature optimum
# ---------------------------------------------------------------------------


def test_bo_pipeline_high_dilution_optimum(tmp_path: Path) -> None:
    """
    Pipeline test with rate constant peak in the high-dilution, low-flow regime.

    Known optimum: flow_rate=80 µL/min, temperature=55 °C, dilution_factor=0.42.
    This validates that the BO explores the high-concentration, slow-flow region.
    """
    rate_fn = make_peaked_rate_constant(**_SURFACE_2)
    best_throughput = _run_bo_pipeline(tmp_path, rate_fn, "ax_surface2.json")

    assert best_throughput >= _THROUGHPUT_THRESHOLD, (
        f"Best throughput {best_throughput:.2f} nmol/min did not reach "
        f"{_THROUGHPUT_THRESHOLD:.1f} nmol/min for surface 2 "
        f"(optimum at flow={_SURFACE_2['flow_rate']}, "
        f"temp={_SURFACE_2['temperature']}, "
        f"dilution={_SURFACE_2['dilution_factor']})"
    )


# ---------------------------------------------------------------------------
# Pipeline test 3: high flow, moderate temperature, moderate dilution optimum
# ---------------------------------------------------------------------------


def test_bo_pipeline_high_flow_optimum(tmp_path: Path) -> None:
    """
    Pipeline test with rate constant peak in the high-flow regime.

    Known optimum: flow_rate=170 µL/min, temperature=45 °C, dilution_factor=0.22.
    This validates that the BO explores the fast-flow, lower-dilution region.
    """
    rate_fn = make_peaked_rate_constant(**_SURFACE_3)
    best_throughput = _run_bo_pipeline(tmp_path, rate_fn, "ax_surface3.json")

    assert best_throughput >= _THROUGHPUT_THRESHOLD, (
        f"Best throughput {best_throughput:.2f} nmol/min did not reach "
        f"{_THROUGHPUT_THRESHOLD:.1f} nmol/min for surface 3 "
        f"(optimum at flow={_SURFACE_3['flow_rate']}, "
        f"temp={_SURFACE_3['temperature']}, "
        f"dilution={_SURFACE_3['dilution_factor']})"
    )