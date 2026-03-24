# ------------------------------------------------------------------------------
# Software: project_dead_mans_fingers
# Copyright: (C) 2026 by Professor Andrew Zahrt
# This software is the intellectual property of Professor Andrew Zahrt
# Contributions by graduate students Scott Laverty and Joao are acknowledged.
# All rights reserved.
# ------------------------------------------------------------------------------

"""
Experimental Commands Unit Tests

This test suite validates the experimental command generation functions.

TEST MODES:
-----------
SIMULATION_MODE: 
  - True: Tests can run remotely without hardware
  - False: Indicates tests require hardware access

SKIP_HARDWARE_TESTS:
  - True: Skip tests that require physical equipment (pumps, valves, sensors)
  - False: Run all tests including hardware-dependent ones

TEST CATEGORIES:
----------------
✓ Passed     - Test executed successfully
✗ Failed     - Test failed with assertion error
⊘ Skipped    - Test not implemented yet (TODO)
⊙ Skipped    - Test requires hardware (controlled by SKIP_HARDWARE_TESTS)

SIMULATION TESTS (can run remotely):
  1. generate_instrument_config - Generate instrument configuration
  2. generate_wash_commands - Generate wash/cleaning commands
  3. generate_set_light_intensity_commands - Generate light intensity commands (TODO)
  4. generate_set_temperature_commands - Generate temperature control commands
  5. generate_experimental_commands - Generate full experiment command sequence

HARDWARE TESTS (require physical equipment):
  8. run_commands - Execute commands on hardware
  9. execute_runner - Run experiment runner
  10. execute_bo_iteration_commands - Execute Bayesian optimization iteration

Usage:
------
To run all simulation tests (remote safe):
    python test/experimental_commands_unit_test.py

To run with hardware tests (requires equipment access):
    Edit SKIP_HARDWARE_TESTS = False in the file, then run
"""

import sys
import os

# Add parent directory to path to import modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from experimental_commands.generate_instrument_config import generate_instrument_config
from experimental_commands.generate_wash_commands import generate_wash_commands
#from experimental_commands.generate_set_light_intensity_commands import generate_set_light_intensity_commands
from experimental_commands.generate_temperature_commands import generate_temperature_commands
from experimental_commands.generate_experimental_commands import generate_experimental_commands

# Test configuration
SIMULATION_MODE = True  # Set to False when running with actual hardware
SKIP_HARDWARE_TESTS = True  # Set to False to run hardware-dependent tests

# Part 1) Generate test cases for each experimental command function
test_instrument_config = [
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

test_wash_command = [ 
    ["Component", "Action", "Parameters", "Notes", "delay"],
    ["Valve6Way_2", "go_to_position", "position=1.0", "", "0.5"],
    ["VICI_M6_Pump_1", "dispense", "flow_rate=1000.0, volume=2000.0", "The flow rate of our 0.1 M HCl Water is 1000.0 uL/min and volume is 2000.0", "0.5"],
    ["VICI_M6_Pump_2", "dispense", "flow_rate=1000.0, volume=2000.0", "The flow rate of our cosolvent is 1000.0 uL/min and volume is 2000.0", "0.5"],
    ["Tricontinental_Pump_C24000_2", "aspirate", "flow_rate=2000.0, volume=3000.0", "The flow rate of our 0.1 M HCl water pump is 2000.0 uL/min and volume is 3000.0", "0.5"],
    ["SYNC", "wait_for_pumps", "", "Waiting for XYLO and WATER pumps to complete", "0.5"]
]

# TODO: We haven't programmed the code for this device yet so we are leaving a placeholder test
test_set_light_intensity_command = [
    ["Component", "Action", "Parameters", "Notes", "delay"],
    ["DH2000_1", "set_light_intensity", "light_intensity=70.0", "Setting light intensity to 70.0%", "0.5"]      
]

test_set_temperature_command = [
        ["Component", "Action", "Parameters", "Notes", "delay"],
        ["Temperature_1", "set_temperature", f"temp=25.0, " f"temp_id=1", f"Setting Temperature to 25.0C for the experiment", "0.5"],
        ["Temperature_1", "wait_convergence", f"target_temp=25.0,tolerance=1,duration=60", f"Waiting for temperature to converge to {25.0} before starting experiment", "0.5"]
    ]   

test_set_experimental_commands = [
    ["Component", "Action", "Parameters", "Notes", "delay"],
    ["DH2000_1","shutter_open","","","3.0"],
    ["OceanOptics_UVVis_1","init","","","3.0"],
    ["OceanOptics_UVVis_1","set_params","integration_time=30000,num_scans=10,measurement_interval=5,target_wavelengths=409;506","","","3.0"],
    ["OceanOptics_UVVis_1","record_blank","","","3.0"],
    ["DH2000_1","shutter_close","","","3.0"],
    ["OceanOptics_UVVis_1","record_dark","","","3.0"],
    ["DH2000_1","shutter_open","","","3.0"],
    ["OceanOptics_UVVis_1","start_continuous","stop_upon_convergence=True","","","3.0"],
    ["Tricontinental_Pump_C24000_1","dispense","flow_rate=100.0,volume=400.0","The flow rate of our Xylo compund is 100.0 uL/min and volume is 400.0","0.5"],
    ["VICI_M6_Pump_1","dispense","flow_rate=10.0, volume=40.0","The flow rate of our 0.1 M HCl Water is 10.0 uL/min and volume is 40.0","0.5"],
    ["VICI_M6_Pump_2","dispense","flow_rate=50.0, volume=200.0","The flow rate of our cosolvent is 50.0 uL/min and volume is 200.0","0.5"],
    ["Tricontinental_Pump_C24000_2","aspirate","flow_rate=25.0, volume=100.0","The flow rate of our 0.1 M HCl water pump is 25.0 uL/min and volume is 100.0","0.5"],
    ["SYNC","wait_for_pumps","","Waiting for XYLO and WATER pumps to complete", "0.5"],
    ["OceanOptics_UVVis_1","stop_continuous","","","3.0"]
]

# Part 2) Generate test functions for each preprocessing function
def test_generate_instrument_config():
    instrument_config = generate_instrument_config()
    assert instrument_config == test_instrument_config, f"Expected:\n{test_instrument_config}\n\nGot:\n{instrument_config}"

def test_generate_wash_commands():
    wash_commands = generate_wash_commands(
        flow_rate_pump2=1000.0,
        volume_pump2=2000.0,
        flow_rate_pump3=1000.0,
        volume_pump3=2000.0,
        flow_rate_pump4=2000.0,
        volume_pump4=3000.0,
        cosolvent_valve_position=1.0
    )
    assert wash_commands == test_wash_command, f"Expected:\n{test_wash_command}\n\nGot:\n{wash_commands}"

# TODO : We haven't programmed this device yet so we are leaving a placeholder test
def test_generate_set_light_intensity_commands():
    pass 

def test_generate_set_temperature_commands():
    temperature_commands = generate_temperature_commands(temperature=25.00)
    assert temperature_commands == test_set_temperature_command, f"Expected:\n{test_set_temperature_command}\n\nGot:\n{temperature_commands}"

def test_generate_experimental_commands():
    experimental_commands = generate_experimental_commands(
        flow_rate_pump1=100.0,
        flow_rate_pump2=10.0,
        flow_rate_pump3=50.0,
        flow_rate_pump4=25.0,
        volume_pump1=400.0,
        volume_pump2=40.0,
        volume_pump3=200.0,
        volume_pump4=100.0
    )
    assert experimental_commands == test_set_experimental_commands, f"Expected:\n{test_set_experimental_commands}\n\nGot:\n{experimental_commands}"

# TODO : We need to develop this function further for the complete workflow, bayesian optimzation campaign,
def test_generate_production_run_commands():
    pass

# TODO : Need to figure out how to test the save_commands_to_csv
def test_save_commands_to_csv():
    pass

# TODO : Need to develop this function further for the complete workflow.
def test_run_commands():
    pass

# TODO : Need to develop this function further currently just a placeholder, 
# how to test without running equipment?
def test_execute_runner():
    pass

def test_execute_bo_iteration_commands():
    pass


# Part 3) Run all the test cases
if __name__ == "__main__":
    print("="*70)
    print("Running experimental commands unit tests...")
    print(f"SIMULATION_MODE: {SIMULATION_MODE}")
    print(f"SKIP_HARDWARE_TESTS: {SKIP_HARDWARE_TESTS}")
    print("="*70)
    print()
    
    test_results = []
    
    # Test 1: generate_instrument_config (SIMULATION ONLY)
    print("Test 1: generate_instrument_config")
    try:
        test_generate_instrument_config()
        print("  ✓ Test passed")
        test_results.append(("generate_instrument_config", True, None))
    except Exception as e:
        print(f"  ✗ Test failed: {e}")
        test_results.append(("generate_instrument_config", False, str(e)))
    print()
    
    # Test 2: generate_wash_commands (SIMULATION ONLY)
    print("Test 2: generate_wash_commands")
    try:
        test_generate_wash_commands()
        print("  ✓ Test passed")
        test_results.append(("generate_wash_commands", True, None))
    except Exception as e:
        print(f"  ✗ Test failed: {e}")
        test_results.append(("generate_wash_commands", False, str(e)))
    print()
    
    # Test 3: generate_set_light_intensity_commands (TODO - NOT IMPLEMENTED)
    print("Test 3: generate_set_light_intensity_commands")
    print("  ⊘ Test skipped (not implemented yet)")
    test_results.append(("generate_set_light_intensity_commands", None, "Not implemented"))
    print()
    
    # Test 4: generate_set_temperature_commands (SIMULATION ONLY)
    print("Test 4: generate_set_temperature_commands")
    try:
        test_generate_set_temperature_commands()
        print("  ✓ Test passed")
        test_results.append(("generate_set_temperature_commands", True, None))
    except Exception as e:
        print(f"  ✗ Test failed: {e}")
        test_results.append(("generate_set_temperature_commands", False, str(e)))
    print()
    
    # Test 5: generate_experimental_commands (SIMULATION ONLY)
    print("Test 5: generate_experimental_commands")
    try:
        test_generate_experimental_commands()
        print("  ✓ Test passed")
        test_results.append(("generate_experimental_commands", True, None))
    except Exception as e:
        print(f"  ✗ Test failed: {e}")
        test_results.append(("generate_experimental_commands", False, str(e)))
    print()
    
    # Test 6: generate_production_run_commands (TODO - NOT IMPLEMENTED)
    print("Test 6: generate_production_run_commands")
    print("  ⊘ Test skipped (not implemented yet)")
    test_results.append(("generate_production_run_commands", None, "Not implemented"))
    print()
    
    # Test 7: save_commands_to_csv (TODO - NOT IMPLEMENTED)
    print("Test 7: save_commands_to_csv")
    print("  ⊘ Test skipped (not implemented yet)")
    test_results.append(("save_commands_to_csv", None, "Not implemented"))
    print()
    
    # Test 8: run_commands (HARDWARE TEST)
    print("Test 8: run_commands")
    if SKIP_HARDWARE_TESTS:
        print("  ⊙ Test skipped (requires hardware)")
        test_results.append(("run_commands", None, "Requires hardware"))
    else:
        try:
            test_run_commands()
            print("  ✓ Test passed")
            test_results.append(("run_commands", True, None))
        except Exception as e:
            print(f"  ✗ Test failed: {e}")
            test_results.append(("run_commands", False, str(e)))
    print()
    
    # Test 9: execute_runner (HARDWARE TEST)
    print("Test 9: execute_runner")
    if SKIP_HARDWARE_TESTS:
        print("  ⊙ Test skipped (requires hardware)")
        test_results.append(("execute_runner", None, "Requires hardware"))
    else:
        try:
            test_execute_runner()
            print("  ✓ Test passed")
            test_results.append(("execute_runner", True, None))
        except Exception as e:
            print(f"  ✗ Test failed: {e}")
            test_results.append(("execute_runner", False, str(e)))
    print()
    
    # Test 10: execute_bo_iteration_commands (HARDWARE TEST)
    print("Test 10: execute_bo_iteration_commands")
    if SKIP_HARDWARE_TESTS:
        print("  ⊙ Test skipped (requires hardware)")
        test_results.append(("execute_bo_iteration_commands", None, "Requires hardware"))
    else:
        try:
            test_execute_bo_iteration_commands()
            print("  ✓ Test passed")
            test_results.append(("execute_bo_iteration_commands", True, None))
        except Exception as e:
            print(f"  ✗ Test failed: {e}")
            test_results.append(("execute_bo_iteration_commands", False, str(e)))
    print()
    
    # Summary
    print("="*70)
    print("TEST SUMMARY")
    print("="*70)
    passed = sum(1 for _, result, _ in test_results if result is True)
    failed = sum(1 for _, result, _ in test_results if result is False)
    skipped = sum(1 for _, result, _ in test_results if result is None)
    total = len(test_results)
    
    print(f"Total tests: {total}")
    print(f"✓ Passed: {passed}")
    print(f"✗ Failed: {failed}")
    print(f"⊘ Skipped: {skipped}")
    print()
    
    if failed > 0:
        print("Failed tests:")
        for name, result, error in test_results:
            if result is False:
                print(f"  - {name}: {error}")
    
    print("="*70)

