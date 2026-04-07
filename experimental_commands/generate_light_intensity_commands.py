# ------------------------------------------------------------------------------
# Software: AUTO_ZAHRT
# Copyright: (C) 2025 by Professor Andrew Zahrt
# This software is the intellectual property of Professor Andrew Zahrt
# Contributions by graduate students Scott Laverty and Joao are acknowledged.
# All rights reserved.
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