# ------------------------------------------------------------------------------
# Software: dead_mans_fingers
# Copyright (c) 2026 Zahrt Research Group
#
# Contributions by Scott Laverty and Joao Albuquerque are acknowledged.
#
# Licensed under the MIT License. See the LICENSE file in the repository root.
# ------------------------------------------------------------------------------



class ExperimentAborted(Exception):
    pass

class HardwareFailure(ExperimentAborted):
    pass

class ValidationError(ExperimentAborted):
    pass

class PostProcessingError(ExperimentAborted):
    pass

class keyboard_interrupt(ExperimentAborted):
    def __init__(self):
        super().__init__("Experiment was aborted by keyboard interrupt.")
