# ------------------------------------------------------------------------------
# Software: project_dead_mans_fingers
# Copyright: (C) 2026 by Professor Andrew Zahrt
# This software is the intellectual property of Professor Andrew Zahrt
# Contributions by graduate students Scott Laverty and Joao are acknowledged.
# All rights reserved.
# ------------------------------------------------------------------------------

"""
Test cases for volume preprocessing functions in check_volume.py
"""

import pytest
import sys
from pathlib import Path

# Add the parent directory to the system path to import check_volume
sys.path.append(str(Path(__file__).parent.parent.parent)
                )
from preprocessing.check_volume import check_volume
from utils.experiment_aborted import ExperimentAborted