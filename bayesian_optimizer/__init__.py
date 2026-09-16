# ------------------------------------------------------------------------------
# Software: dead_mans_fingers
# Copyright (c) 2026 Andrew Zahrt
#
# Contributions by Scott Laverty and Joao Albuquerque are acknowledged.
#
# Licensed under the MIT License. See the LICENSE file in the repository root.
# ------------------------------------------------------------------------------

"""
Bayesian Optimizer Package.

This package contains modules for running Bayesian optimization campaigns
on the AutoZahrt platform. The main orchestration is in experiment_executor,
with supporting modules for setup, volume management, execution, and processing.
"""

# Re-export main public API for backward compatibility
# Circular import removed - import directly from experimental_commands.execute_bo_iteration_commands if needed

__all__ = []

