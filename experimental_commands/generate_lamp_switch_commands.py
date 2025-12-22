#TODO : The purpose of this code is to be able to turn the lamp on and off for the UV-VIS detector
# during experimentation in case any issues arise with the lamp during long term experimentation 

# For now 

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
            "DH2000_Lamp",
            "set_lamp_state",
            f"state={lamp_state}",
            f"Setting UV-VIS detector lamp to {lamp_state}",
            "0.5",
        ],
    ]
    return commands

    