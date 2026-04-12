# ------------------------------------------------------------------------------
# Software: project_dead_mans_fingers
# Copyright: (C) 2026 by Professor Andrew Zahrt
# This software is the intellectual property of Professor Andrew Zahrt
# Contributions by graduate students Scott Laverty and Joao are acknowledged.
# All rights reserved.
# -----------------------------------------------------------------------------

"""
The purpose of this script is for post-processing the raw UV-Vis absorbance data
recorded during an experiment by extracting the points after the target volume is
reached.

Post-process UV-Vis absorbance data by extracting points after target volume
is reached.

This is used in the results processing step of Bayesian optimization to
calculate percent yield and throughput based on steady-state absorbance values.
"""

import os
import pandas as pd
from preprocessing.time_to_reach_target_volume import time_to_reach_target_volume


def post_process_uv_recording(
    flow_rate: int,
    target_volume: int,
    uv_vis_absorbance_results_csv: str,
    experiment_converged_early: bool = False,
) -> pd.DataFrame:
    """
    Extract all UV-Vis points after the target volume is reached.
    """

    if experiment_converged_early:

        print(
            "Experiment converged early, " \
            "we selected the last 5 minutes of data for post-processing."
        )
        uv_vis_recording = pd.read_csv(uv_vis_absorbance_results_csv)

        # Find the last time point in the UV-VIS data recording
        max_time = uv_vis_recording["Time(s)"].max()

        if max_time < 300:
            raise ValueError(
                f"Experiment converged early but fewer than 5 minutes (300 s) of data "
                f"were recorded (recording ends at {max_time:.1f} s). "
                "Inspect the hardware and UV-Vis recording before continuing."
            )

        # Select only rows where Time(s) is within the last 5 minutes (300 seconds)
        uv_vis_recording_after_target_volume = uv_vis_recording[
            uv_vis_recording["Time(s)"] >= max_time - 300
        ]

        base_name, ext = os.path.splitext(uv_vis_absorbance_results_csv)
        uv_vis_recording_post_processed_filename = f"{base_name}_post_processed{ext}"
        uv_vis_recording_after_target_volume.to_csv(
            uv_vis_recording_post_processed_filename, index=False
        )

        return uv_vis_recording_after_target_volume
    
    # If early convergence criteria is not met, 
    # proceed with normal post-processing based on target volume
    else:

        time_target_volume_is_reached = time_to_reach_target_volume(
            flow_rate, target_volume
        )
        uv_vis_recording = pd.read_csv(uv_vis_absorbance_results_csv)

        if "Time(s)" not in uv_vis_recording.columns:
            raise ValueError(
                f"Expected a Time(s) column in {uv_vis_absorbance_results_csv}"
            )

        # Keep only time points after the target volume is reached
        uv_vis_recording_after_target_volume = uv_vis_recording[
            uv_vis_recording["Time(s)"] >= time_target_volume_is_reached
        ].reset_index(drop=True)

        if uv_vis_recording_after_target_volume.empty:
            raise ValueError(
                f"No UV-Vis data found after target volume cutoff "
                f"({time_target_volume_is_reached:.1f} s) in {uv_vis_absorbance_results_csv}. "
                f"Recording ends at {uv_vis_recording['Time(s)'].max():.1f} s. "
                "Check flow rate, target volume, and recording duration."
            )

        base_name, iteration = os.path.splitext(uv_vis_absorbance_results_csv)
        uv_vis_recording_post_processed_filename = (
            f"{base_name}_post_processed{iteration}"
        )

        uv_vis_recording_after_target_volume.to_csv(
            uv_vis_recording_post_processed_filename, index=False
        )

        return uv_vis_recording_after_target_volume