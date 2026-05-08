# ------------------------------------------------------------------------------
# Software: project_dead_mans_fingers
# Copyright: (C) 2026 by Professor Andrew Zahrt
# This software is the intellectual property of Professor Andrew Zahrt
# Contributions by graduate students Scott Laverty and Joao are acknowledged.
# All rights reserved.
# ------------------------------------------------------------------------------

"""
Detect whether a UV-Vis experiment recording ended before its expected duration.
"""

import pandas as pd


def detect_early_convergence(
    csv_file_path: str,
    flow_rate: float,
    total_volume: float,
    tolerance_seconds: float = 60.0,
) -> bool:
    """
    Return True if the UV-Vis recording ended earlier than expected.

    Compares the max recorded time in the CSV against the nominal experiment
    duration (total_volume / flow_rate * 60 s). A 60-second tolerance avoids
    false positives from minor hardware timing jitter.

    # TODO: Currently treats ALL short experiments as intentional early
    # convergence (steady-state detected by the UV-Vis hardware). In the future,
    # distinguish intentional convergence from unintentional short runs (e.g.
    # hardware error, instrument failure). A status flag written by the hardware
    # or a dedicated convergence log file would enable this distinction.

    Parameters:
        csv_file_path: Path to the UV-Vis results CSV file.
        flow_rate: Flow rate through the reactor bed in uL/min.
        total_volume: Total volume to flow through the reactor bed in uL.
        tolerance_seconds: Allowable shortfall in seconds before treating the
            experiment as converged early (default 60 s).

    Returns:
        True if the recording ended more than tolerance_seconds before the
        expected experiment duration, False otherwise.
    """
    try:
        df = pd.read_csv(csv_file_path)
    except pd.errors.EmptyDataError:
        return False
    if df.empty or "Time(s)" not in df.columns:
        return False
    actual_max_time = df["Time(s)"].max()
    expected_duration = (total_volume / flow_rate) * 60
    return bool(actual_max_time < expected_duration - tolerance_seconds)
