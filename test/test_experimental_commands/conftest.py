# ------------------------------------------------------------------------------
# Software: dead_mans_fingers
# Copyright (c) 2026 Zahrt Research Group
#
# Contributions by Scott Laverty are acknowledged.
#
# Licensed under the MIT License. See the LICENSE file in the repository root.
# ------------------------------------------------------------------------------

"""
conftest.py for test_experimental_commands.

Detects available serial COM ports at test startup and automatically skips
any test marked @pytest.mark.hardware when no instrument ports are found.
"""

import pytest
import serial.tools.list_ports

# COM ports assigned to instruments in generate_instrument_config.py
INSTRUMENT_PORTS = {"COM8", "COM12", "COM14", "COM19", "COM21", "COM22", "COM27", "COM50"}


def _detected_instrument_ports() -> set:
    """Return the subset of INSTRUMENT_PORTS that are currently available."""
    available = {p.device for p in serial.tools.list_ports.comports()}
    return available.intersection(INSTRUMENT_PORTS)


def pytest_collection_modifyitems(config, items):
    """Auto-skip @pytest.mark.hardware tests when no instrument ports are detected."""
    if _detected_instrument_ports():
        return  # Hardware present — let all tests run

    skip_marker = pytest.mark.skip(reason="No instrument COM ports detected — hardware tests skipped")
    for item in items:
        if "hardware" in item.keywords:
            item.add_marker(skip_marker)


@pytest.fixture(scope="session")
def hardware_available() -> bool:
    """Session-scoped fixture: True if at least one instrument COM port is detected."""
    return bool(_detected_instrument_ports())


@pytest.fixture(scope="session")
def detected_ports() -> set:
    """Session-scoped fixture: returns the set of detected instrument COM ports."""
    return _detected_instrument_ports()
