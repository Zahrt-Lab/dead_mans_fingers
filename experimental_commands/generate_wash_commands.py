# ------------------------------------------------------------------------------
# Software: AUTO_ZAHRT
# Copyright: (C) 2025 by Professor Andrew Zahrt
# This software is the intellectual property of Professor Andrew Zahrt
# Contributions by graduate students Scott Laverty and Joao are acknowledged.
# All rights reserved.
# ------------------------------------------------------------------------------

from typing import List

from utils.is_zero import is_zero

def generate_wash_commands(
        flow_rate_pump2: float,
        volume_pump2: float,
        flow_rate_pump3: float,
        volume_pump3: float,
        flow_rate_pump4: float,
        volume_pump4: float,
        cosolvent_valve_position: float,
        *,
        zero_tolerance: float = 1e-6) -> List[List[str]]:
    """
    These are the experimental parameters to feed into our equipment to wash the XYLO compound
    out of the detector before the next reaction

    Parameters:
     - flow_rate_pump2: Flow rate of 0.1 M HCl water to dilute our compound before it reaches the detector
     - volume_pump2: Volume of 0.1 M HCl water to dilute our compound before it reaches the detector
     - flow_rate_pump3: Flow rate of cosolvent for diluting our compound before it reaches the UV-detector
     - volume_pump3: Volume of cosolvent for diluting our compound before it reaches the UV-detector
     - flow_rate_pump4: Flow rate of 0.1 M HCl water for diluting our compound after it reaches the reactor bed and before it reaches the UV-detector
     - volume_pump4: Volume of 0.1 M HCl water for diluting our compound after it reaches the reactor bed
     - cosolvent_valve_position: valve position for the VICI M6 pump 2 which pumps the co-solvent.

    return:
    - commands: The commands to wash the Xylo compound out of the detector
    """

    header = ["Component", "Action", "Parameters", "Notes", "delay"]
    commands = [header]
    
    commands.append([
            "Valve6Way_2",
            "go_to_position",
            f"position={cosolvent_valve_position}",
            "",
            "0.5",
        ]
    )
    if not is_zero(flow_rate_pump2, volume_pump2, zero_tolerance):
        commands.append([
            "Tecan_pump_1",
            "dispense",
            f"flow_rate={flow_rate_pump2}, " f"volume={volume_pump2}",
            f"The flow rate of our 0.1 M HCl Water is {flow_rate_pump2} uL/min and volume is {volume_pump2}",
            "0.5",
            ]
        )

   
    if not is_zero(flow_rate_pump3, volume_pump3, zero_tolerance):
        commands.append([
            "VICI_M6_Pump_2",
            "dispense",
            f"flow_rate={flow_rate_pump3}, volume={volume_pump3}",
            f"The flow rate of our cosolvent is {flow_rate_pump3} uL/min and volume is {volume_pump3}",
            "0.5",
            ]
        )

    if not is_zero(flow_rate_pump4, volume_pump4, zero_tolerance):
        commands.append([
            "Tecan_pump_2",
            "dispense",
            f"flow_rate={flow_rate_pump4}, " f"volume={volume_pump4}",
            f"The flow rate of our 0.1 M HCl water pump is {flow_rate_pump4} uL/min and volume is {volume_pump4}",
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
