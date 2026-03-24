# ------------------------------------------------------------------------------
# Software: AUTO_ZAHRT
# Copyright: (C) 2026 by Professor Andrew Zahrt
# This software is the intellectual property of Professor Andrew Zahrt
# Contributions by graduate students Scott Laverty and Joao are acknowledged.
# All rights reserved.
# ------------------------------------------------------------------------------



class ExperimentAborted(Exception):
    pass

class HardwareFailure(ExperimentAborted):
    pass

class ValidationError(ExperimentAborted):
    pass

class keyboard_interrupt(ExperimentAborted):
    def __init__(self):
        super().__init__("Experiment was aborted by keyboard interrupt.")
