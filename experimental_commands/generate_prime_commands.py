# ------------------------------------------------------------------------------
# Software: dead_mans_fingers
# Copyright (c) 2026 Zahrt Research Group
#
# Contributions by Scott Laverty and Joao Albuquerque are acknowledged.
#
# Licensed under the MIT License. See the LICENSE file in the repository root.
# ------------------------------------------------------------------------------

from typing import List

from utils.is_zero import is_zero

def generate_prime_commands(
        flow_rate_pump1: float,
        volume_pump1: float,
        valve1_position: float,
        *,
        zero_tolerance: float = 1e-6) -> List[List[str]]:
    """
    These are the experimental parameters to feed into our equipment to prime the pump 1 (Xylopyridine solution) before starting the optimization campaign.

    Parameters:
     - flow_rate_pump1: Flow rate of Xylopyridine solution to prime pump 1
     - volume_pump1: Volume of Xylopyridine solution to prime pump 1
     - valve1_position: Position of valve1
    return:
    - commands: The commands to prime pump 1
    """

    header = ["Component", "Action", "Parameters", "Notes", "delay"]
    commands = [header]
    
    commands.append([
            "Valve6Way_2",
            "go_to_position",
            f"position={valve1_position}",
            "",
            "0.5",
        ]
    )
    if not is_zero(flow_rate_pump1, volume_pump1, zero_tolerance):
        commands.append([
            "VICI_M6_Pump_1",
            "dispense",
            f"flow_rate={flow_rate_pump1}, " f"volume={volume_pump1}",
            f"The flow rate of our xylopyridine solution (valve position: {valve1_position}) is {flow_rate_pump1} uL/min and volume is {volume_pump1}",
            "0.5",
            ]
        )

    commands.append([
            "SYNC",
            "wait_for_pumps",
            "",                                         
            "Waiting for XYLO and WATER pumps to complete",
            "0.5",
        ]   )

    return commands
