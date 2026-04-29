# ------------------------------------------------------------------------------
# Software: AUTO_ZAHRT
# Copyright: (C) 2025 by Professor Andrew Zahrt
# This software is the intellectual property of Professor Andrew Zahrt
# Contributions by graduate students Scott Laverty are acknowledged.
# All rights reserved.
# ------------------------------------------------------------------------------

import csv
from typing import Dict, List, Optional

# Default COM port assignments — used when no instrument_com_ports key is
# present in the config JSON.  Override by adding "instrument_com_ports" to
# the experiment config file so ports can be changed per machine without
# editing source code.
_DEFAULT_COM_PORTS: Dict[str, str] = {
    "vici_pump_1":           "COM22",
    "vici_pump_2":           "COM21",
    "valve_xylopyridine":    "COM7",
    "valve_cosolvent":       "COM11",
    "temperature_controller": "COM12",
    "Tricontinental_C24000_1": "COM17",
    "Tricontinental_C24000_2": "COM25",
    "Tecan_pump_1":          "COM20",
    "Tecan_pump_2":          "COM6",
    "dh2000_light_source":   "COM27",
    "ocean_optics_uv_vis":   "COM50", 
    "MirrorBox365nm":        "COM18",

}


def generate_instrument_config(
    com_ports: Optional[Dict[str, str]] = None,
) -> List[List]:
    """
    Build the instrument configuration rows for the AutoZahrt platform.

    Parameters:
        com_ports: Optional dict mapping instrument keys to COM port strings.
            If None or a key is missing, the corresponding _DEFAULT_COM_PORTS
            value is used.  Add "instrument_com_ports" to the experiment JSON
            to configure ports per machine.

    Returns:
        List of rows (including header) suitable for writing to a CSV file.
    """
    ports = _DEFAULT_COM_PORTS.copy()
    if com_ports:
        ports.update(com_ports)

    header = ["InstrumentType", "DeviceNumber", "Name", "COMPort", "OtherParams"]
    rows = [
        header,
        ["VICI_M6_Pump",              1, "Pump",                       ports["vici_pump_1"],            ""],
        ["VICI_M6_Pump",              2, "Pump",                       ports["vici_pump_2"],            ""],
        ["Valve6Way",                 1, "Xylopyridine-Valve",          ports["valve_xylopyridine"],     ""],
        ["Valve6Way",                 2, "Cosolvent-Valve",             ports["valve_cosolvent"],        ""],
        ["Temperature",               1, "Temperature",                 ports["temperature_controller"], ""],
        #["Tricontinental_C24000",     1, "Tricontinental_C24000",       ports["Tricontinental_C24000_1"],  ""],
        # TODO: Due to mechanical issues with pump 4 this has been commented out til resolved.
        #["Tricontinental_C24000",     2, "Tricontinental_C24000",       ports["Tricontinental_C24000_2"],  ""],  
        ["Tecan_pump",                1, "Tecan_pump",                 ports["Tecan_pump_1"],  ""],
        ["Tecan_pump",                2, "Tecan_pump",                 ports["Tecan_pump_2"],  ""],        
        #["Tecan_pump",                1, "Tecan_pump",                 ports["Tecan_pump_3"],  ""],           
        ["DH2000",                    1, "DH2000",                      ports["dh2000_light_source"],    ""],
        ["OceanOptics_UVVis",         1, "OceanOptics",                 ports["ocean_optics_uv_vis"],    ""],
        ["MirrorBox365nm",            1, "MirrorBox365nm",              ports["MirrorBox365nm"],         ""]
    ]
    return rows


def save_instrument_config_csv(
    config_file: str,
    com_ports: Optional[Dict[str, str]] = None,
) -> None:
    """
    Write the instrument configuration to a CSV file.

    Parameters:
        config_file: Destination file path.
        com_ports: Optional COM port overrides (see generate_instrument_config).
    """
    with open(config_file, "w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerows(generate_instrument_config(com_ports))
