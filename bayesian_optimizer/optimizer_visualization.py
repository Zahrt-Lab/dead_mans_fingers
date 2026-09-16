# ------------------------------------------------------------------------------
# Software: dead_mans_fingers
# Copyright (c) 2026 Andrew Zahrt
#
# Contributions by Scott Laverty and Joao Albuquerque are acknowledged.
#
# Licensed under the MIT License. See the LICENSE file in the repository root.
# ------------------------------------------------------------------------------
"""
This file is retained for reference but is not used in the final
workflow reported in the manuscript.
"""
from ax.service.ax_client import AxClient


def hypervolume_calculator(ax: AxClient) -> float:
    """
    TODO: Compute and return the current observed hypervolume of the Pareto front.
    Intended implementation: use ax.modelbridge and observed_hypervolume() from
    ax.modelbridge.modelbridge_utils, with objective thresholds from the experiment config.
    """
    raise NotImplementedError("hypervolume_calculator is not yet implemented.")