def generate_temperature_commands(
    temperature: float, previous_temperature: float
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

    # For every 1 degree the temperature controller will take an extra 30 second to
    # heat up or cool down if it reaches minimum time of 300 seconds.
    # Ex. If previous_temperature = 54 and temperature = 26;
    # (abs(26C - 54C) * 30 = 28C * 30 seconds = 840 seconds,
    # mininum warm up time is 300 seconds
    warm_up_time = max(300, int(abs(temperature - previous_temperature) * 30))

    header = ["Component", "Action", "Parameters", "Output", "Notes", "delay"]
    commands = [
        header,
        [
            "Temperature",
            "set_temperature",
            f"temp={temperature}, " f"temp_id=1",
            f"Setting Temperature to {temperature}C with a {warm_up_time} seconds warm up time",
            "",
            warm_up_time,
        ],
    ]
    return commands
