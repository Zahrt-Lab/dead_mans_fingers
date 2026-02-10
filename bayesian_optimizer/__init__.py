# ------------------------------------------------------------------------------
# Software: project_dead_mans_fingers
# Copyright: (C) 2025 by Professor Andrew Zahrt
# This software is the intellectual property of Professor Andrew Zahrt
# Contributions by graduate students Scott Laverty are acknowledged.
# All rights reserved.
# ------------------------------------------------------------------------------

"""
Bayesian Optimizer Package.

This package contains modules for running Bayesian optimization campaigns
on the AutoZahrt platform. The main orchestration is in experiment_executor,
with supporting modules for setup, volume management, execution, and processing.
"""

# Re-export main public API for backward compatibility
from bayesian_optimizer.experiment_executor import (
    run_bayesian_optimization_iteration,
    objective_function_percent_yield,
    objective_function_throughput,
)

__all__ = [
    "run_bayesian_optimization_iteration",
    "objective_function_percent_yield", 
    "objective_function_throughput",
]

