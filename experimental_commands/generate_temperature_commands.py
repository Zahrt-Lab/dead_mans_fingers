# ------------------------------------------------------------------------------
# Software: dead_mans_fingers
# Copyright (c) 2026 Zahrt Research Group
#
# Contributions by Scott Laverty are acknowledged.
#
# Licensed under the MIT License. See the LICENSE file in the repository root.
# ------------------------------------------------------------------------------

from typing import List

def generate_temperature_commands(
    temperature: float
    ) -> List[List[str]]:
    """
    These are the experimental parameters to feed into our equipment to be performed

    parameters:
     - temperature: The temperature to set our experiment to for this experiment
     - previous_temperature: The temperature our temperature controller was
     previously set to
    return:
     - commands: The instrument commands to heat the reaction will be used
    """



    header = ["Component", "Action", "Parameters", "Notes", "delay"]
    commands = [
        header,
        [
            "Temperature_1",
            "set_temperature",
            f"temp={temperature}, " f"temp_id=1",
            f"Setting Temperature to {temperature}C for the experiment",
            "0.5",
        ],

        [
            "Temperature_1",
            "wait_convergence",
            f"target_temp={temperature},tolerance=1,duration=60",
            f"Waiting for temperature to converge to {temperature} before starting experiment",
            "0.5"
        ],
    ]
    return commands
