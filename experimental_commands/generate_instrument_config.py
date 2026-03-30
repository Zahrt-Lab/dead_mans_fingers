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
    "vici_pump_1":           "COM21",
    "vici_pump_2":           "COM22",
    "valve_xylopyridine":    "COM8",
    "valve_cosolvent":       "COM8",
    "temperature_controller": "COM12",
    "tricontinental_pump_1": "COM19",
    "tricontinental_pump_2": "COM14",
    "dh2000_light_source":   "COM27",
    "ocean_optics_uv_vis":   "COM50",
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
        ["Valve6Way",                 2, "Xylopyridine-Valve",          ports["valve_xylopyridine"],     ""],
        ["Valve6Way",                 2, "Cosolvent-Valve",             ports["valve_cosolvent"],        ""],
        ["Temperature",               1, "Temperature",                 ports["temperature_controller"], ""],
        ["Tricontinental_Pump_C24000",1, "Tricontinental_Pump_C24000",  ports["tricontinental_pump_1"],  ""],
        ["Tricontinental_Pump_C24000",2, "Tricontinental_Pump_C24000",  ports["tricontinental_pump_2"],  ""],
        ["DH2000",                    1, "DH2000",                      ports["dh2000_light_source"],    ""],
        ["OceanOptics_UVVis",         1, "OceanOptics",                 ports["ocean_optics_uv_vis"],    ""],
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
