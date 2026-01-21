# ------------------------------------------------------------------------------
# Software: AUTO_ZAHRT
# Copyright: (C) 2025 by Professor Andrew Zahrt
# This software is the intellectual property of Professor Andrew Zahrt
# Contributions by graduate students Scott Laverty and Joao are acknowledged.
# All rights reserved.
# ------------------------------------------------------------------------------

from typing import List

def generate_wash_commands(
        flow_rate_pump2,
        volume_pump2,
        flow_rate_pump3,
        volume_pump3,
        flow_rate_pump4,
        volume_pump4,
        cosolvent_valve_position: int,
        *,
        zero_tolerance: float = 1e-6) -> List[List[str]]:
    """
    These are the experimental parameters to feed into our equipment to wash the XYLO compound
    out of the detector before the next reaction

    return:
    - commands: The commands to wash the Xylo compound out of the detector
    """

    def _is_zero(rate: float, vol: float) -> bool:
        return (abs(rate) <= zero_tolerance) or (abs(vol) <= zero_tolerance)

    header = ["Component", "Action", "Parameters", "Notes", "delay"]
    commands = [header]
    
    commands.append([
            "Valve6Way_1",
            "go_to_position",
            f"position={cosolvent_valve_position}",
            "",
            0.5,
        ]
    )
    if not _is_zero(flow_rate_pump2, volume_pump2):
        commands.append([
            "VICI_M6_Pump_1",
            "dispense",
            f"flow_rate={flow_rate_pump2}, " f"volume={volume_pump2}",
            f"The flow rate of our 0.1 M HCl Water is {flow_rate_pump2} uL/min and volume is {volume_pump2}",
            0.5,
            ]
        )
    if not _is_zero(flow_rate_pump3, volume_pump3):
        commands.append([
            "VICI_M6_Pump_2",
            "dispense",
            f"flow_rate={flow_rate_pump3}, volume={volume_pump3}",
            f"The flow rate of our cosolvent is {flow_rate_pump3} uL/min and volume is {volume_pump3}",
            0.5,
            ]
        )
    if not _is_zero(flow_rate_pump4, volume_pump4):
        commands.append([
            "Isametic_1",
            "aspirate",
            f"flow_rate={flow_rate_pump4}, volume={volume_pump4}",
            f"The flow rate of our 0.1 M HCl water pump is {flow_rate_pump4} uL/min and volume is {volume_pump4}",
            0.5,
            ]
        )
    commands.append([
            "SYNC",
            "wait_for_pumps",
            "",                                         
            "Waiting for XYLO and WATER pumps to complete",
            0.5,
        ]   )

    return commands
