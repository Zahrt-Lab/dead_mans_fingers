# ------------------------------------------------------------------------------
# Software: project_dead_mans_fingers
# Copyright: (C) 2025 by Professor Andrew Zahrt
# This software is the intellectual property of Professor Andrew Zahrt
# Contributions by graduate students Scott Laverty and Joao are acknowledged.
# All rights reserved.
# ------------------------------------------------------------------------------

from ax.service.ax_client import AxClient


def hypervolume_calculator(ax: AxClient) -> float:
    """
    TODO: Compute and return the current observed hypervolume of the Pareto front.
    Intended implementation: use ax.modelbridge and observed_hypervolume() from
    ax.modelbridge.modelbridge_utils, with objective thresholds from the experiment config.
    """
    raise NotImplementedError("hypervolume_calculator is not yet implemented.")