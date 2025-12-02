# auto_zahrt/ax_runner.py
from __future__ import annotations

import os
import time
from typing import Dict

from ax.service.ax_client import AxClient, ObjectiveProperties

from auto_zahrt import state
from auto_zahrt.state import (
    EXPERIMENTAL_PARAMETERS,
    iteration,
    bayesian_optimization_results_csv_path,
)
from auto_zahrt.experiment import (
    run_bayesian_optimization_iteration,
    objective_percent_yield,   # optional, but nice to export if needed
    objective_throughput,
    append_bayesian_experimental_results,  # wherever this is defined in experiment.py
)
# Also import your config helpers from the module where they currently live.
# If they are in experiment.py, this works:
from auto_zahrt.experiment import (
    load_experimental_parameters,
    check_required_experimental_parameters,
)

def _init_or_load_ax(
    state_path: str,
    fr_min: float,
    fr_max: float,
    conc_min: float,
    conc_max: float,
    temp_min: float,
    temp_max: float,
    objA_threshold: float,
    objB_threshold: float,
) -> AxClient:
    """
    Initialize a new AxClient or resume from a JSON state file.
    """
    if os.path.exists(state_path):
        ax = AxClient.load_from_json_file(state_path)
        print(f"Resumed Ax experiment with {len(ax.get_trials_data_frame())} trials.")
        return ax

    ax = AxClient()
    ax.create_experiment(
        name="AUTO_ZAHRT_moo_ax",
        parameters=[
            {
                "name": "flow_rate",
                "type": "range",
                "bounds": [fr_min, fr_max],
                "value_type": "int",
            },
            {
                "name": "concentration",
                "type": "range",
                "bounds": [conc_min, conc_max],
                "value_type": "float",
            },
            {
                "name": "temperature",
                "type": "range",
                "bounds": [temp_min, temp_max],
                "value_type": "int",
            },
        ],
        objectives={
            "percent_yield": ObjectiveProperties(
                minimize=False, threshold=float(objA_threshold)
            ),
            "throughput": ObjectiveProperties(
                minimize=False, threshold=float(objB_threshold)
            ),
        },
    )
    print("Started new Ax experiment.")
    return ax

def evaluate_ax(params: Dict[str, float]) -> Dict[str, tuple[float, float]]:
    """
    Runs ONE lab experiment using your existing pipeline.
    Returns the two objective metrics with (mean, sem) for Ax.
    """
    flow_rate = float(params["flow_rate"])
    concentration = float(params["concentration"])
    temperature = float(params["temperature"])

    try:
        percent_yield, throughput = run_bayesian_optimization_iteration(
            (flow_rate, concentration, temperature)
        )

        return {
            "percent_yield": (float(percent_yield), state.NOISE_SEM),
            "throughput": (float(throughput), state.NOISE_SEM),
        }

    except Exception as e:
        err_msg = str(e)
        now = time.strftime("%Y-%m-%d %H:%M:%S")

        reactant_concentration_uM = float(
            concentration * EXPERIMENTAL_PARAMETERS.get("stock_concentration_uM", 0.0)
        )

        reactant_wavelength = EXPERIMENTAL_PARAMETERS.get("reactant_wavelength", "")
        product_wavelength = EXPERIMENTAL_PARAMETERS.get("product_wavelength", "")

        append_bayesian_experimental_results(
            bayesian_optimization_results_csv_path(),
            {
                "iteration": iteration["iteration #"],
                "flow_rate": flow_rate,
                "concentration": concentration,
                "reactor_concentration_uM": reactant_concentration_uM,
                "temperature": temperature,
                "target_volume": "",
                "reactant_wavelength": reactant_wavelength,
                "product_wavelength": product_wavelength,
                "average_absorbance_reactant": "",
                "average_absorbance_product": "",
                "percent_yield": 0.0,
                "percent_conversion_original": 0.0,
                "throughput_nmol_per_min": 0.0,
                "timestamp": now,
                "status": "error",
                "error_message": (
                    err_msg[:240] + "…"
                ) if len(err_msg) > 240 else err_msg,
            },
        )

        return {
            "percent_yield": (0.0, state.NOISE_SEM),
            "throughput": (0.0, state.NOISE_SEM),
        }

def run_bo_campaign(
    input_experimental_parameters: str,
    trials: int,
    state_path: str,
    save_every: int,
    objA_threshold: float,
    objB_threshold: float,
    noise_sem: float,
) -> None:
    """
    Top-level driver that:
      1) Loads experimental parameters into global state
      2) Initializes / resumes Ax
      3) Runs the BO loop
      4) Prints Pareto front on exit
    """
    # 1) Setup global state
    params = load_experimental_parameters(input_experimental_parameters)
    check_required_experimental_parameters(params)
    state.set_experimental_parameters(params)
    state.set_noise_sem(noise_sem)

    fr_min, fr_max = EXPERIMENTAL_PARAMETERS["flow_rate"]
    conc_min, conc_max = EXPERIMENTAL_PARAMETERS["concentration"]
    temp_min, temp_max = EXPERIMENTAL_PARAMETERS["temperature"]

    # 2) Ax init/load
    ax = _init_or_load_ax(
        state_path,
        fr_min,
        fr_max,
        conc_min,
        conc_max,
        temp_min,
        temp_max,
        objA_threshold,
        objB_threshold,
    )

    # 3) Run the loop
    step = 0
    target = "∞" if trials == 0 else str(trials)
    try:
        while True if trials == 0 else (step < trials):
            params_dict, tid = ax.get_next_trial()
            outcomes = evaluate_ax(params_dict)
            ax.complete_trial(trial_index=tid, raw_data=outcomes)
            step += 1

            if (step % max(1, save_every)) == 0:
                ax.save_to_json_file(filepath=state_path)

            print(
                f"[Step {step}/{target}] Trial {tid} -> "
                f"percent_yield={outcomes['percent_yield'][0]:.4f}, "
                f"throughput={outcomes['throughput'][0]:.6g} "
                f"at params={params_dict}"
            )
    except KeyboardInterrupt:
        print("\nInterrupted by user; saving Ax state...")
    finally:
        ax.save_to_json_file(filepath=state_path)
        print(f"Ax state saved to: {state_path}")

        # 4) optional Pareto print (same as your original)
        try:
            def _m(v):
                if hasattr(v, "mean"):
                    return float(v.mean)
                if isinstance(v, (tuple, list)) and v:
                    return float(v[0])
                return float(v)

            pareto = ax.get_pareto_optimal_parameters()
            items = pareto.items() if isinstance(pareto, dict) else pareto
            print("\nPareto-optimal parameter sets (approx means):")
            for p, outs in items:
                if isinstance(outs, dict):
                    summary = {m: round(_m(val), 4) for m, val in outs.items()}
                else:
                    summary = outs
                print(p, summary)
        except Exception as e:
            print(f"(Pareto print skipped: {e})")
