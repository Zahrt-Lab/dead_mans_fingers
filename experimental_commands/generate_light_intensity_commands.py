# ------------------------------------------------------------------------------
# Software: dead_mans_fingers
# Copyright (c) 2026 Zahrt Research Group
#
# Contributions by Scott Laverty and Joao Albuquerque are acknowledged.
#
# Licensed under the MIT License. See the LICENSE file in the repository root.
# ------------------------------------------------------------------------------

from typing import List

def generate_light_intensity_commands(
    light_intensity: float
    ) -> List[List[str]]:
    """
    The light intensity is an experimental parameter to feed into our bayesian optimizer

    parameters:
     - light_intensity: The light intensity to set our experiment to 0 (brightest) to 100 (dimmest))
    return:
     - commands: The instrument commands to set the light intensity
    """

    header = ["Component", "Action", "Parameters", "Notes", "delay"]
    commands = [
        header,
        [
            "MirrorBox365nm_1",
            "set_dimmer",
            f"value={light_intensity}",
            f"Setting light intensity to {int(light_intensity)} for the experiment",
            0.5
        ]
    ]
    return commands