# ------------------------------------------------------------------------------
# Software: dead_mans_fingers
# Copyright (c) 2026 Andrew Zahrt
#
# Contributions by Scott Laverty and Joao Albuquerque are acknowledged.
#
# Licensed under the MIT License. See the LICENSE file in the repository root.
# ------------------------------------------------------------------------------

from typing import List

from utils.is_zero import is_zero

def generate_production_run_commands(
    flow_rate_pump1: float,
    flow_rate_pump2: float,
    flow_rate_pump3: float,
    flow_rate_pump4: float,
    volume_pump1: float,
    volume_pump2: float,
    volume_pump3: float,
    volume_pump4: float,
    *,
    zero_tolerance: float = 1e-6,
) -> List[List[str]]:
    
    """
    This will generate the production run commands for this reactor bed

    parameters:
    - flow_rate_pump1: Flow rate of the VICI M6 Pump 1 with our XYLO compound
    - flow_rate_pump2: Flow rate of 0.1 M HCl water for diluting our compound
    before it reaches the detector using the Tecan Pump 1
    - flow_rate_pump3: Flow rate of co-solvents for diluting our compound before it reaches the reactor bed
    using the VICI M6 Pump 2
    - flow_rate_pump4: Flow rate of 0.1 M HCL water for diluting our compound
    before it reaches the UV-detector and after the reactor bed using the
    Tecan Pump 2
    - volume_pump1: Volume of Xylo compound to pump using VICI M6 Pump 1
    - volume_pump2: volume 0.1 M HCl water to dilute our Xylo compound solution
    before it reaches the UV-detector using the tecan Pump 1
    - volume_pump3: volume of co-solvents to dilute our Xylo compound before
    it reaches the reactor bed using VICI M6 Pump 2
    - volume_pump4: volume 0.1 M HCl water to dilute our Xylo compound solution
    after it reaches the UV-detector using the tecan Pump 2

    return:
    - commands: Experimental commands for reacting the flow reaction
    """

    header = ["Component", "Action", "Parameters", "Notes", "delay"]
    commands = [header]

    if not is_zero(flow_rate_pump1, volume_pump1, zero_tolerance):
        commands.append([
            "VICI_M6_Pump_1",
            "dispense",
            f"flow_rate={flow_rate_pump1},volume={volume_pump1}",
            f"The flow rate of our Xylo compund is {flow_rate_pump1} uL/min and volume is {volume_pump1}",
            "0.5"
        ])
    if not is_zero(flow_rate_pump2, volume_pump2, zero_tolerance):
        commands.append([
            "Tecan_pump_1",
            "dispense",
            f"flow_rate={flow_rate_pump2},volume={volume_pump2}",
            f"The flow rate of our 0.1 M HCl Water is {flow_rate_pump2} uL/min and volume is {volume_pump2}",
            "0.5"
        ])
    

    if not is_zero(flow_rate_pump3, volume_pump3, zero_tolerance):
        commands.append([
            "Tecan_pump_3",
            "dispense",
            f"flow_rate={flow_rate_pump3},volume={volume_pump3}",
            f"The flow rate of our cosolvent is {flow_rate_pump3} uL/min and volume is {volume_pump3}",
            "0.5"
        ])

    if not is_zero(flow_rate_pump4, volume_pump4, zero_tolerance):
        commands.append([
            "Tecan_pump_2",
            "dispense",
            f"flow_rate={flow_rate_pump4},volume={volume_pump4}",
            f"The flow rate of our 0.1 M HCl water pump after the reactor is {flow_rate_pump4} uL/min and volume is {volume_pump4}",
            "0.5"
        ])
    commands.append([
            "SYNC",
            "wait_for_pumps",
            "",
            "Waiting for XYLO and WATER pumps to complete",
            "0.5",
        ])

    return commands

