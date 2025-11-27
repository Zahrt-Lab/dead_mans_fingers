def generate_instrument_config() -> List[List[str]]:
    """
    This is the instrument configuration of all the instruments that will be used for this
    experiment UV-detector connects automatically and doesn't have an explicit com port
    and was not included

    return:
     -rows: the config file for all the instuments to use in this experiment
    """
    header = ["InstrumentType", "DeviceNumber", "Name", "COMPort", "OtherParams"]
    rows = [
        header,
        ["Temperature", "1", "Temperature", "COM12", ""],
        ["Pump", "1", "Pump", "COM21", ""],
        ["Pump", "2", "Pump", "COM22", ""],
        ["HarvardPump", "1", "HarvardPump", "COM19", ""],
    ]
    return rows

# This saves the output instrument config file to a csv file
def save_instrument_config_csv(config_file: str) -> None:
    """
    This saves the output instrument config file to a csv file

    config_file:
     - This contains the instrument configuration file of all equipment used for this project

    return:
     - None
    """

    with open(config_file, "w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerows(generate_instrument_config())
