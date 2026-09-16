# ------------------------------------------------------------------------------
# Software: dead_mans_fingers
# Copyright (c) 2026 Andrew Zahrt
#
# Contributions by Scott Laverty and Joao Albuquerque are acknowledged.
#
# Licensed under the MIT License. See the LICENSE file in the repository root.
# ------------------------------------------------------------------------------

"""
Factory for creating known analytical rate constant functions used in Bayesian
Optimization pipeline tests.

``make_peaked_rate_constant`` returns a callable that can be passed to
``run_simulated_experiment`` via its ``rate_constant_fn`` parameter.  The
returned function has a single Gaussian peak at a specified interior point in
the (flow_rate, temperature, dilution_factor) subspace, so the BO must steer
towards that region to achieve high product yield and throughput.

Bounds match ``test_config_ax_demo.json``::

    flow_rate       : [40, 200]   µL/min (int)
    dilution_factor : [0.05, 0.5]
    temperature     : [20, 60]    °C
"""

import numpy as np

from typing import Callable, Tuple

# ---------------------------------------------------------------------------
# Search-space bounds  (from test_config_ax_demo.json)
# ---------------------------------------------------------------------------

# TODO : We cshould add more parameters to this test function in 
_FLOW_RATE_BOUNDS: Tuple[float, float] = (40.0, 200.0)
_DILUTION_BOUNDS: Tuple[float, float] = (0.05, 0.5)
_TEMPERATURE_BOUNDS: Tuple[float, float] = (20.0, 60.0)

# Rate constant limits shared by all surfaces.
RATE_CONSTANT_MAX: float = 0.08   # 1/s – value at the exact optimum
RATE_CONSTANT_MIN: float = 0.005  # 1/s – baseline far from the optimum

_SIGMA: float = 0.35  # Gaussian width in normalised 3-D subspace


def _norm(value: float, lo: float, hi: float) -> float:
    """Normalise *value* to [0, 1] given its lower and upper bounds."""
    return (value - lo) / (hi - lo)


def make_peaked_rate_constant(
    flow_rate: float,
    temperature: float,
    dilution_factor: float,
) -> Callable[[float, float, float], float]:
    """
    Return a rate constant function with a single Gaussian peak at the given point.

    The returned callable also accepts ``(flow_rate, temperature, dilution_factor)``
    and returns a rate constant in [``RATE_CONSTANT_MIN``, ``RATE_CONSTANT_MAX``].

    When injected into ``run_simulated_experiment`` via ``rate_constant_fn``, it
    shapes the first-order reaction kinetics so that the BO must find the supplied
    ``flow_rate``, ``temperature``, and ``dilution_factor`` to observe high product
    conversion at steady state.

    Args:
        flow_rate: Flow rate at which the peak occurs (µL/min).
        temperature: Temperature at which the peak occurs (°C).
        dilution_factor: Dilution factor at which the peak occurs.

    Returns:
        A callable ``(flow_rate, temperature, dilution_factor) -> float``.
    """
    opt_fr = _norm(flow_rate, *_FLOW_RATE_BOUNDS)
    opt_temp = _norm(temperature, *_TEMPERATURE_BOUNDS)
    opt_df = _norm(dilution_factor, *_DILUTION_BOUNDS)
    amplitude = RATE_CONSTANT_MAX - RATE_CONSTANT_MIN

    def _rate_constant_fn(
        flow_rate: float,
        temperature: float,
        dilution_factor: float,
    ) -> float:
        fr_norm = _norm(flow_rate, *_FLOW_RATE_BOUNDS)
        temp_norm = _norm(temperature, *_TEMPERATURE_BOUNDS)
        df_norm = _norm(dilution_factor, *_DILUTION_BOUNDS)
        dist_sq = (
            (fr_norm - opt_fr) ** 2
            + (temp_norm - opt_temp) ** 2
            + (df_norm - opt_df) ** 2
        )
        return float(
            RATE_CONSTANT_MIN + amplitude * np.exp(-dist_sq / (2.0 * _SIGMA**2))
        )

    return _rate_constant_fn