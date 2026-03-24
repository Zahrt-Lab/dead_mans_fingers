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

def test_check_volume_sufficient():
    assert check_volume(5000, 2000, 2000, "Methanol") == 3000  # Should pass
    assert check_volume(3000, 1000, 1500, "Water") == 2000  # Should pass
    assert check_volume(4000, 1500, 2000, "Acetonitrile") == 2500  # Should pass

def test_check_volume_insufficient():
    with pytest.raises(ExperimentAborted):
        check_volume(2000, 3000, 2000, "Methanol", interactive=False)  # Should fail
    with pytest.raises(ExperimentAborted):
        check_volume(2500, 2000, 3000, "Water", interactive=False)  # Should fail
    with pytest.raises(ExperimentAborted):
        check_volume(3500, 2500, 3000, "Acetonitrile", interactive=False)  # Should fail

def test_check_volume_edge_cases():
    assert check_volume(0, 0, 0, "Methanol") == 0  # Should pass
    with pytest.raises(ExperimentAborted):
        check_volume(0, 1000, 2000, "Water", interactive=False)  # Should fail
    with pytest.raises(ExperimentAborted):
        check_volume(1000, 0, 2000, "Acetonitrile", interactive=False)  # Should fail
    with pytest.raises(ExperimentAborted):
        check_volume(1000, 2000, 0, "Methanol", interactive=False)  # Should fail