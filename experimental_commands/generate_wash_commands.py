def generate_wash_commands() -> List[List[str]]:
    """
    These are the experimental parameters to feed into our equipment to wash the XYLO compound
    out of the detector before the next reaction

    return:
    - commands: The commands to wash the Xylo compound out of the detector
    """

    header = ["Component", "Action", "Parameters", "Output", "Notes", "delay"]
    commands = [
        header,
        [
            "Pump",
            "aspirating",
            "flow_rate=3000, volume=3000.0, pump_id=2",
            "The flow rate of our Water is 3000 uL/min",
            "",
            0.5,
        ],
        [
            "SYNC",
            "wait_for_pumps",
            "",
            "Waiting for flushing of water to complete",
            "",
            0.5,
        ],
    ]
    return commands
