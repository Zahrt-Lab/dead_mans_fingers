# ------------------------------------------------------------------------------
# Software: AUTO_ZAHRT
# Copyright: (C) 2025 by Professor Andrew Zahrt
# This software is the intellectual property of Professor Andrew Zahrt
# Contributions by graduate students Scott Laverty are acknowledged.
# All rights reserved.
# ------------------------------------------------------------------------------

from typing import List

from utils.is_zero import is_zero

# TODO: The wavelength is currently fixed for the xylopyrdidine analogs, needs to make this more flexible for user inputs
def generate_experimental_commands(
    flow_rate_pump1: float,
    flow_rate_pump2: float,
    flow_rate_pump3: float,
    flow_rate_pump4: float,
    volume_pump1: float,
    volume_pump2: float,
    volume_pump3: float,
    volume_pump4: float,
    light_intensity: float,
    reactant_wavelength: float,
    product_wavelength: float,
    reference_wavelength: float,
    blank_light_intensity_threshold: float,
    wavelength_for_blank_light_intensity_check: float,
    convergence_time: float,
    *,
    zero_tolerance: float = 1e-6,
) -> List[List[str]]:
    
    """
    This will generate the experimental flow reaction commands for this reactor bed

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

    # TODO: Delete specific light intensity workflow, this should be used instead
    commands.append([
            "MirrorBox365nm_1",
            "set_dimmer",
            f"value={light_intensity}",
            f"Setting light intensity to {int(light_intensity)} for the experiment",
            0.5
        ]
    )

    #commands.append([ 
    #    "DH2000_1","halogen_toggle","","","5.0"
    #    ]
    #)
    #commands.append([
    #    "DH2000_1","deuterium_toggle","","","5.0"
    #])
    commands.append([
        "DH2000_1","shutter_open","","","5.0"
    ])
    commands.append([
        "OceanOptics_UVVis_1","init","","","5.0"
    ])

    # TODO: This was set to be fixed for xylopyridine analogs
    # for the future iterations make this more dynamic and flexible for different compounds
    commands.append([
        "OceanOptics_UVVis_1",
        "set_params",
        f"integration_time=30000,num_scans=10,measurement_interval=5,target_wavelengths={reactant_wavelength};{product_wavelength};{reference_wavelength},reference_wavelength={reference_wavelength},blank_light_intensity_threshold={blank_light_intensity_threshold},wavelength_for_blank_light_intensity_check={wavelength_for_blank_light_intensity_check}, convergence_time = {convergence_time}",
        "",
        "5.0"
    ])
    commands.append([
        "OceanOptics_UVVis_1","record_blank","","","5.0"
    ])
    commands.append([
        "DH2000_1","shutter_close","","","5.0"
    ])
    commands.append([
        "OceanOptics_UVVis_1","record_dark","","","5.0"
    ])
    commands.append([
        "DH2000_1","shutter_open","","","5.0"
    ])
    # This begins the UV-Vis data collection in continuous mode until stopped once converged
    # TODO: Need to verify that once convergence is reached all the pumps will stop as well
    commands.append([
        "OceanOptics_UVVis_1","start_continuous","stop_upon_convergence=True","","0.5"
    ])

    commands.append([
        "Tricontinental_C24000_1",
        "dispense",
        f"flow_rate=1000, " f"volume=100",
        f"The tricontnent pump is initializing",
        "0.5",
        ]
    )
    commands.append([
            "SYNC",
            "wait_for_pumps",
            "",
            "Waiting for XYLO and WATER pumps to complete",
            "0.5",
        ])
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
        # commands.append([
        #     "Tecan_pump_2",
        #     "dispense",
        #     f"flow_rate={flow_rate_pump4},volume={volume_pump4}",
        #     f"The flow rate of our 0.1 M HCl water pump after the reactor is {flow_rate_pump4} uL/min and volume is {volume_pump4}",
        #     "0.5"
        # ])
        commands.append([
            "Tricontinental_C24000_1",
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
        ])
    commands.append([
        "OceanOptics_UVVis_1","stop_continuous","","","3.0"
        ])
    
    #commands.append([
    #    "DH2000_1","halogen_toggle","","","3.0"
    #    ])

    #commands.append([
    #    "DH2000_1","deuterium_toggle","","","3.0"
    #    ])
    
    commands.append([
        "DH2000_1","shutter_close","","","3.0"
        ])

    return commands

