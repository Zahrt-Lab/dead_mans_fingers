# ------------------------------------------------------------------------------
# Software: AUTO_ZAHRT
# Copyright: (C) 2025 by Professor Andrew Zahrt
# This software is the intellectual property of Professor Andrew Zahrt
# Contributions by graduate students Scott Laverty are acknowledged.
# All rights reserved.
# ------------------------------------------------------------------------------

from typing import List

# TODO: Need to double check which pump is pump 1 and pump 2 for VICI M6 pumps
# TODO: Need to get rid of number of syringes since we will be swapping it out with the tricontinental pumps
def generate_experimental_commands(
    flow_rate_pump1: float,
    flow_rate_pump2: float,
    flow_rate_pump3: float,
    flow_rate_pump4: float,
    volume_pump1: float,
    volume_pump2: float,
    volume_pump3: float,
    volume_pump4: float,
    *,
    zero_tolerance: float = 1e-6,  # treat |x| <= zero_tol as zero
    log_skips: bool = True,
) -> List[List[str]]:
    
    """
    This will generate the experimental flow reaction commands for this reactor bed

    parameters:
    - flow_rate_pump1: Flow rate of tricontinental pump 1 with our XYLO compound
    - flow_rate_pump2: Flow rate of 0.1 M HCl water for diluting our compound
    before it reaches the detector using the VICI M6 Pump 1
    - flow_rate_pump3: Flow rate of co-solvents for diluting our compound before it reaches the reactor bed
    using the VICI M6 Pump 2
    - flow_rate_pump4: Flow rate of 0.1 M HCL water for diluting our compound
    before it reaches the UV-detector and after the reactor bed using the
    Tricontinental Pump C24000 2
    - volume_pump1: Volume of Xylo compound to pump using tricontinental pump 1
    - volume_pump2: volume 0.1 M HCl water to dilute our Xylo compound solution
    before it reaches the UV-detector
    - volume_pump3: volume of co-solvents to dilute our Xylo compound before
    it reaches the reactor bed using VICI M6 Pump 1
    - volume_pump4: volume 0.1 M HCl water to dilute our Xylo compound solution
    before it reaches the UV-detector

    return:
    - commands: Experimental commands for reacting the flow reaction
    """

    def _is_zero(rate: float, vol: float) -> bool:
        return (abs(rate) <= zero_tolerance) or (abs(vol) <= zero_tolerance)

    header = ["Component", "Action", "Parameters", "Notes", "delay"]
    commands = [header]

    commands.append([ 
        "DH2000_1","shutter_open","","",3.0
        ]
    )
    commands.append([
        "OceanOptics_UVVis_1","init","","",3.0
        ]
    )
    # TODO : Could be useful if this was updated by the user to change the integration time but not urgent
    commands.append([
        "OceanOptics_UVVis_1","set_params",
        "integration_time=30000,"
        "num_scans=10,"
        "measurement_interval=5,"
        "target_wavelengths=409;506",
        "",
        "",
        3.0
        ]
    )
    commands.append([
        "OceanOptics_UVVis_1","record_blank","","",3.0
        ]
    )
    commands.append([
        "DH2000_1","shutter_close","","",3.0
        ]
    )
    commands.append([
        "OceanOptics_UVVis_1","record_dark","","",3.0
        ]
    )
    commands.append([
        "DH2000_1","shutter_open","","",3.0
        ]
    )
    # This begins the UV-Vis data collection in continuous mode until stopped once converged
    # TODO: Need to verify that once convergence is reached all the pumps will stop as well
    commands.append([
        "OceanOptics_UVVis_1","start_continuous","stop_upon_convergence=True","","",3.0
        ]
    )
    # TODO: Need to validate and add these tricontinental pump commands
    commands.append([
            "Tricontinental_Pump_C24000_1",
            "dispense",
            f"flow_rate={flow_rate_pump1},volume={volume_pump1}",
            f"The flow rate of our Xylo compund is {flow_rate_pump1} uL/min and volume is {volume_pump1}",
            0.5,
        ]
    )
    if not _is_zero(flow_rate_pump2, volume_pump2):
        commands.append(
            [
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
    # TODO: Need to validate and add these tricontinental pump commands
    if not _is_zero(flow_rate_pump4, volume_pump4):
        commands.append([
            "Tricontinental_Pump_C24000_2",
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
        ]
    )
    commands.append([
        "OceanOptics_UVVis_1","stop_continuous","","",3.0
        ]
    )

    return commands

