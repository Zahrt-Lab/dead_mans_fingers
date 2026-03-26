# ------------------------------------------------------------------------------
# Software: project_dead_mans_fingers
# Copyright: (C) 2026 by Professor Andrew Zahrt
# This software is the intellectual property of Professor Andrew Zahrt
# Contributions by graduate students Scott Laverty and Joao are acknowledged.
# All rights reserved.
# ------------------------------------------------------------------------------

"""
Test cases for experimental_commands/generate_instrument_config.py
"""

import csv
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))

from experimental_commands.generate_instrument_config import (
    generate_instrument_config,
    save_instrument_config_csv,
)

_EXPECTED_HEADER = ["InstrumentType", "DeviceNumber", "Name", "COMPort", "OtherParams"]
_EXPECTED_COLUMN_COUNT = 5
_INSTRUMENT_CONFIG = [
        ["InstrumentType", "DeviceNumber", "Name", "COMPort", "OtherParams"],
        ["VICI_M6_Pump",	1,	"Pump",	"COM21", ""],
        ["VICI_M6_Pump",	2,	"Pump",	"COM22", ""],
        ["Valve6Way",	2,	"Xylopyridine-Valve",	"COM8", ""],
        ["Valve6Way",	2,	"Cosolvent-Valve",	"COM8", ""],
        ["Temperature",	1,	"Temperature",	"COM12", ""],
        ["Tricontinental_Pump_C24000",	1,	"Tricontinental_Pump_C24000",	"COM19", ""],
        ["Tricontinental_Pump_C24000",	2,	"Tricontinental_Pump_C24000",	"COM14", ""],
        ["DH2000", 1, "DH2000", "COM27", ""],
        ["OceanOptics_UVVis", 1, "OceanOptics", "COM50", ""]
        ]


def test_generate_instrument_config_returns_list_of_lists():
    rows = generate_instrument_config()
    assert isinstance(rows, list)
    assert all(isinstance(row, list) for row in rows)


def test_generate_instrument_config_header_is_correct():
    rows = generate_instrument_config()
    assert rows[0] == _EXPECTED_HEADER


def test_generate_instrument_config_has_instrument_rows():
    rows = generate_instrument_config()
    # Must have at least one row beyond the header
    assert len(rows) > 1


def test_generate_instrument_config_all_rows_have_correct_column_count():
    rows = generate_instrument_config()
    for row in rows:
        assert len(row) == _EXPECTED_COLUMN_COUNT, (
            f"Row {row} has {len(row)} columns, expected {_EXPECTED_COLUMN_COUNT}"
        )

def test_generate_instrument_config_matches_expected_config():
    rows = generate_instrument_config()
    assert rows == _INSTRUMENT_CONFIG


def test_save_instrument_config_csv_creates_file(tmp_path: Path) -> None:
    config_path = tmp_path / "Instrument_Config_File.csv"
    save_instrument_config_csv(str(config_path))
    assert config_path.exists()


def test_save_instrument_config_csv_header_matches(tmp_path: Path) -> None:
    config_path = tmp_path / "Instrument_Config_File.csv"
    save_instrument_config_csv(str(config_path))

    with open(config_path, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader)

    assert header == _EXPECTED_HEADER


def test_save_instrument_config_csv_row_count_matches(tmp_path: Path) -> None:
    config_path = tmp_path / "Instrument_Config_File.csv"
    save_instrument_config_csv(str(config_path))

    with open(config_path, newline="", encoding="utf-8") as f:
        rows = list(csv.reader(f))

    expected_rows = generate_instrument_config()
    assert len(rows) == len(expected_rows)
