# ------------------------------------------------------------------------------
# Software: project_dead_mans_fingers
# Copyright: (C) 2026 by Professor Andrew Zahrt
# This software is the intellectual property of Professor Andrew Zahrt
# Contributions by graduate students Scott Laverty and Joao are acknowledged.
# All rights reserved.
# ------------------------------------------------------------------------------

"""
Volume tracking for the Bayesian Optimization campaign.

Tracks stock solution and waste volumes across iterations and between campaigns:
 - Initializes volumes from a prior volume_state.json or from the JSON config.
 - Calculates volumes consumed by each experiment run and wash cycle.
 - Calls check_volume / check_waste_volume before each experiment and updates state.
 - Persists a per-iteration volume log CSV and an end-of-campaign volume_state.json.

Pump 1 and Pump 3 are connected to 6-way selector valves, each position holding a
separate reservoir.  Volumes are tracked per valve position for both pumps:

  Pump 1 — XyLo analog selector valve:
    volume_stock_solutions["pump1_volumes_uL"]  is a list indexed by
    bo_parameters["xylopyridine_analog_index"].
    The active position is fixed for the entire campaign.

  Pump 3 — co-solvent selector valve:
    volume_stock_solutions["pump3_volumes_uL"]  is a list indexed by
    (co_solvent_valve_position − 1), which changes each iteration.

Pump 2 and Pump 4 have no selector valve, so a single scalar volume is tracked.
"""

import csv
import json
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from bayesian_optimizer.experiment_state import BoCampaignState
from preprocessing.check_volume import check_volume
from preprocessing.check_waste_volume import check_waste_volume


# Wash volumes (µL) applied after every experiment run (from commands.py).
# pump2_wash = 6000 × (1 − D_cosolvent)
# pump3_wash = 6000 × D_cosolvent
# pump4_wash = 3000  (constant)
_PUMP4_WASH_VOLUME_uL = 3000.0

_VOLUME_LOG_COLUMNS = [
    "iteration",
    "timestamp",
    "pump1_active_analog",
    "pump1_consumed_uL",
    "pump1_remaining_uL",
    "pump2_consumed_uL",
    "pump2_remaining_uL",
    "pump3_active_cosolvent",
    "pump3_consumed_uL",
    "pump3_remaining_uL",
    "pump4_consumed_uL",
    "pump4_remaining_uL",
    "waste_generated_uL",
    "waste_total_uL",
]


def _to_float_list(value: Any) -> List[float]:
    """Return a list of floats from a value that may be a list or a scalar."""
    if isinstance(value, (list, tuple)):
        return [float(v) for v in value]
    return [float(value)]


def _extract_scalar(value: Any) -> float:
    """Return a scalar float from a value that may be a list or a number."""
    if isinstance(value, (list, tuple)):
        return float(value[0])
    return float(value)


def initialize_volume_state(
    bo_parameters: Dict[str, Any],
    volume_state_json_path: str,
) -> Dict[str, Any]:
    """
    Return the starting volumes for all pumps and the waste container.

    If *volume_state_json_path* exists, load values from that file (campaign
    continuation).  Otherwise seed from *bo_parameters* as read from the JSON
    config.

    Returns a dict with keys:
        pump1_volumes_uL  — list of floats, one per analog valve position
        pump2_volume_uL   — scalar float
        pump3_volumes_uL  — list of floats, one per co-solvent valve position
        pump4_volume_uL   — scalar float
        waste_volume_uL   — scalar float
    """
    path = Path(volume_state_json_path)
    if path.exists():
        state = load_volume_state_json(volume_state_json_path)
        if state is not None:
            print(f"Loaded volume state from previous campaign: {volume_state_json_path}")
            return state

    # Seed from config
    volumes: Dict[str, Any] = {
        "pump1_volumes_uL": _to_float_list(
            bo_parameters["pump1_xylopyridine_analogs_volume_stock_solution"]
        ),
        "pump2_volume_uL": _extract_scalar(
            bo_parameters["pump2_0.1M_HCl_water_volume_stock_solution"]
        ),
        "pump3_volumes_uL": _to_float_list(
            bo_parameters["pump3_co-solvents_volume_stock_solutions"]
        ),
        "pump4_volume_uL": _extract_scalar(
            bo_parameters["pump4_0.1M_HCl_water_volume_stock_solution"]
        ),
        "waste_volume_uL": _extract_scalar(
            bo_parameters.get("waste_volume_current_uL", 0.0)
        ),
    }
    print("Initialized volume state from config.")
    return volumes


def calculate_volumes_used(
    instrument_parameters: Dict[str, Any],
    co_solvent_dilution_factor: float,
) -> Dict[str, float]:
    """
    Calculate the total volume consumed per pump for one iteration.

    Total = experiment volume + wash volume for each pump.

    Wash volumes (from commands.py):
        pump2_wash = 6000 × (1 − D_cosolvent)
        pump3_wash = 6000 × D_cosolvent
        pump4_wash = 3000

    Returns a dict with keys:
        pump1, pump2, pump3, pump4, waste
    where *waste* is the sum of all pump volumes (everything pumped enters waste).
    """
    d = float(co_solvent_dilution_factor)

    exp_pump1 = float(instrument_parameters["volume_pump1"])
    exp_pump2 = float(instrument_parameters["volume_pump2"])
    exp_pump3 = float(instrument_parameters["volume_pump3"])
    exp_pump4 = float(instrument_parameters["volume_pump4"])

    wash_pump2 = 6000.0 * (1.0 - d)
    wash_pump3 = 6000.0 * d
    wash_pump4 = _PUMP4_WASH_VOLUME_uL

    pump1_used = exp_pump1
    pump2_used = exp_pump2 + wash_pump2
    pump3_used = exp_pump3 + wash_pump3
    pump4_used = exp_pump4 + wash_pump4

    waste_generated = pump1_used + pump2_used + pump3_used + pump4_used

    return {
        "pump1": pump1_used,
        "pump2": pump2_used,
        "pump3": pump3_used,
        "pump4": pump4_used,
        "waste": waste_generated,
    }


def check_and_update_all_volumes(
    bo_campaign_state: BoCampaignState,
    volumes_used: Dict[str, float],
    iteration: int = 0,
    co_solvent_valve_position: int = 1,
    *,
    interactive: bool = True,
) -> None:
    """
    Run volume checks for all pumps and the waste container, then update state.

    Pump 1 volumes are tracked per analog valve position; only the position
    given by bo_parameters["xylopyridine_analog_index"] is decremented.

    Pump 3 volumes are tracked per co-solvent valve position; only the position
    given by *co_solvent_valve_position* (1-indexed) is decremented.

    Pumps 2 and 4 have no selector valve and use a single scalar volume.

    Updates bo_campaign_state.volume_stock_solutions and waste_volume_uL in-place.
    Appends a per-iteration entry to bo_campaign_state.volume_log.

    Parameters:
        bo_campaign_state: Current campaign state (mutated in place)
        volumes_used: Dict from calculate_volumes_used()
        iteration: Current iteration number (for log entry)
        co_solvent_valve_position: Active 1-indexed co-solvent valve position
        interactive: When False, raises ExperimentAborted instead of prompting
    """
    bo_parameters = bo_campaign_state.bo_parameters
    volumes = bo_campaign_state.volume_stock_solutions
    minimum_reserve = float(bo_parameters.get("minimum_volume_required", 2000.0))
    max_waste = float(bo_parameters.get("waste_max_volume_uL", 4_000_000.0))
    waste_buffer = float(bo_parameters.get("waste_buffer_volume_uL", 1_000_000.0))

    # --- Pump 1: XyLo analog selector valve ---
    analog_index = int(bo_parameters.get("xylopyridine_analog_index", 0))
    analog_names: List[str] = bo_parameters.get(
        "name_of_xylopyridine_analogs_stock_solutions", []
    )
    analog_name = (
        analog_names[analog_index]
        if analog_index < len(analog_names)
        else f"analog position {analog_index + 1}"
    )
    pump1_volumes = list(volumes.get("pump1_volumes_uL", [0.0]))
    pump1_volumes[analog_index] = check_volume(
        pump1_volumes[analog_index],
        volumes_used["pump1"],
        minimum_reserve,
        f"Pump 1 - {analog_name}",
        interactive=interactive,
    )

    # --- Pump 2: single reservoir ---
    pump2_remaining = check_volume(
        float(volumes.get("pump2_volume_uL", 0.0)),
        volumes_used["pump2"],
        minimum_reserve,
        "Pump 2 (0.1M HCl water)",
        interactive=interactive,
    )

    # --- Pump 3: co-solvent selector valve ---
    position_index = int(co_solvent_valve_position) - 1  # valve is 1-indexed
    cosolvent_names: List[str] = bo_parameters.get("name_of_co-solvent_stock_solutions", [])
    cosolvent_name = (
        cosolvent_names[position_index]
        if position_index < len(cosolvent_names)
        else f"co-solvent position {co_solvent_valve_position}"
    )
    pump3_volumes = list(volumes.get("pump3_volumes_uL", [0.0]))
    pump3_volumes[position_index] = check_volume(
        pump3_volumes[position_index],
        volumes_used["pump3"],
        minimum_reserve,
        f"Pump 3 - {cosolvent_name}",
        interactive=interactive,
    )

    # --- Pump 4: single reservoir ---
    pump4_remaining = check_volume(
        float(volumes.get("pump4_volume_uL", 0.0)),
        volumes_used["pump4"],
        minimum_reserve,
        "Pump 4 (0.1M HCl water)",
        interactive=interactive,
    )

    # Persist updated volumes back to state
    bo_campaign_state.update_volume_stock_solutions(
        {
            "pump1_volumes_uL": pump1_volumes,
            "pump2_volume_uL": pump2_remaining,
            "pump3_volumes_uL": pump3_volumes,
            "pump4_volume_uL": pump4_remaining,
        }
    )

    # --- Waste ---
    current_waste = bo_campaign_state.waste_volume_uL
    updated_waste = check_waste_volume(
        current_waste,
        volumes_used["waste"],
        max_waste,
        waste_buffer,
        interactive=interactive,
    )
    updated_waste_after = updated_waste + volumes_used["waste"]
    bo_campaign_state.update_waste_volume(updated_waste_after)

    # --- Volume log entry ---
    entry = {
        "iteration": iteration,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "pump1_active_analog": analog_name,
        "pump1_consumed_uL": round(volumes_used["pump1"], 2),
        "pump1_remaining_uL": round(pump1_volumes[analog_index], 2),
        "pump2_consumed_uL": round(volumes_used["pump2"], 2),
        "pump2_remaining_uL": round(pump2_remaining, 2),
        "pump3_active_cosolvent": cosolvent_name,
        "pump3_consumed_uL": round(volumes_used["pump3"], 2),
        "pump3_remaining_uL": round(pump3_volumes[position_index], 2),
        "pump4_consumed_uL": round(volumes_used["pump4"], 2),
        "pump4_remaining_uL": round(pump4_remaining, 2),
        "waste_generated_uL": round(volumes_used["waste"], 2),
        "waste_total_uL": round(updated_waste_after, 2),
    }
    bo_campaign_state.append_volume_log_entry(entry)


def save_volume_log_csv(volume_log: list, output_path: str) -> None:
    """
    Write the per-iteration volume log to a CSV file.

    Parameters:
        volume_log: List of dicts produced by check_and_update_all_volumes()
        output_path: Absolute or relative path for the output CSV
    """
    if not volume_log:
        return

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=_VOLUME_LOG_COLUMNS)
        writer.writeheader()
        writer.writerows(volume_log)


def save_volume_state_json(
    bo_campaign_state: BoCampaignState,
    output_path: str,
) -> None:
    """
    Persist the final volume state to a JSON file for the next campaign.

    pump1_volumes_uL and pump3_volumes_uL are saved as lists so the next
    campaign can restore volumes for every valve position.

    Parameters:
        bo_campaign_state: Campaign state after the final iteration
        output_path: Path to write volume_state.json
    """
    volumes = bo_campaign_state.volume_stock_solutions
    state: Dict[str, Any] = {
        "pump1_volumes_uL": volumes.get("pump1_volumes_uL", []),
        "pump2_volume_uL": volumes.get("pump2_volume_uL", 0.0),
        "pump3_volumes_uL": volumes.get("pump3_volumes_uL", []),
        "pump4_volume_uL": volumes.get("pump4_volume_uL", 0.0),
        "waste_volume_uL": bo_campaign_state.waste_volume_uL,
    }
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)


def load_volume_state_json(path: str) -> Optional[Dict[str, Any]]:
    """
    Load volume state from a JSON file written by save_volume_state_json().

    Returns None if the file does not exist or cannot be parsed.
    """
    p = Path(path)
    if not p.exists():
        return None
    try:
        with open(p, encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return None
