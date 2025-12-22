# ------------------------------------------------------------------------------
# Software: AUTO_ZAHRT
# Copyright: (C) 2025 by Professor Andrew Zahrt
# This software is the intellectual property of Professor Andrew Zahrt
# Contributions by graduate students Scott Laverty are acknowledged.
# All rights reserved.
# ------------------------------------------------------------------------------

import csv
from typing import List

def generate_instrument_config() -> List[List[str]]:

    """
    This is the instrument configuration of all the instruments that will be used for this
    experiment UV-detector connects automatically and doesn't have an explicit com port
    and was not included

    return:
     -rows: the config file for all the instuments to use in this experiment
    """

    # TODO: Update Instruments config to match actual instruments and COM ports
    header = ["InstrumentType", "DeviceNumber", "Name", "COMPort", "OtherParams"]
    rows = [
        header,
        ["VICI_M6_Pump",	1,	"Pump",	"COM21", ""],
        ["VICI_M6_Pump",	2,	"Pump",	"COM22", ""],
        ["Valve6Way",	1,	"VICI-6Way",	"COM7", ""],
        ["Temperature",	1,	"Temperature",	"COM12", ""],
        ["PhdUltraPump",	1,	"PhDUltraPump",	"COM19", ""],
        ["Isametic",	1,	"Isametic",	"COM14", ""],
    ]
    return rows

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
