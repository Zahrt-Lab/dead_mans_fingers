# ------------------------------------------------------------------------------
# Software: AUTO_ZAHRT
# Copyright: (C) 2025 by Professor Andrew Zahrt
# This software is the intellectual property of Professor Andrew Zahrt
# Contributions by graduate students Scott Laverty and Joao are acknowledged.
# All rights reserved.
# ------------------------------------------------------------------------------

#TODO : This code will open and close the shutter to calibrate the UV-VIS lamp
#TODO : Double check AutoZahrt commands for DH2000 and Ocean Optics UV-VIS detector

def generate_lamp_switch_commands(lamp_state: str):
    """
    Generate commands to switch the lamp of the UV-VIS detector on or off.

    parameters:
     - lamp_state: Desired state of the lamp ('on' or 'off')

    return:
        - commands: List of commands to switch the lamp state
    """

    header = ["Component", "Action", "Parameters", "Notes", "delay"]
    commands = [
        header,
        [
            "DH2000",
            "shutter open",
            "",
            f"Opening the lamp shutter",
            "0.5",
        ],
        [
            "OceanOptics_UVVis",
            "set_params",
            "",
            f"Setting parameters for UV-VIS detector",
            "0.5",
        ],
        [
            "OceanOptics_UVVis",
            "record_blank",
            "",
            f"Setting parameters for UV-VIS detector",
            "0.5",
        ],
        [
            "DH2000",
            "shutter close",
            "",
            f"Closing the lamp shutter",
            "0.5",
        ],
        [
            "OceanOptics_UVVis",
            "record_dark",
            "",
            f"Setting parameters for UV-VIS detector",
            "0.5",
        ],
        [
            "DH2000",
            "shutter open",
            "",
            f"Opening the lamp shutter",
            "0.5",
        ],
    ]
    return commands

    