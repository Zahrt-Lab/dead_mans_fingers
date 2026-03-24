# ------------------------------------------------------------------------------
# Software: project_dead_mans_fingers
# Copyright: (C) 2026 by Professor Andrew Zahrt
# This software is the intellectual property of Professor Andrew Zahrt
# Contributions by graduate students Scott Laverty and Joao are acknowledged.
# All rights reserved.
# ------------------------------------------------------------------------------


import json
import sys
import os

# Add parent directory to path to import modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from preprocessing.check_volume import check_volume
from preprocessing.constrain_to_search_space import constrain_to_search_space
from preprocessing.generate_bo_input import generate_bo_input_file
from preprocessing.parameters_to_commands import parameters_to_commands
from preprocessing.standardize_input import standardize_input
from preprocessing.time_to_reach_target_volume import time_to_reach_target_volume

from bayesian_optimizer.experiment_state import BoCampaignState, IterationState


# Part 1) Generate test cases for each preprocessing function
pytest_check_volume_test_cases = [
                           [6000, 1000, 2000, "test_solution", False, 5000],
                           [3000, 1000, 2000, "test_solution", False, 2000],
                           ]

test_bo_campaign_state = BoCampaignState()
# Load config and extract scalar values for testing
test_bo_campaign_state.update_bo_parameters(json.load(open("test_config_ax_demo.json", "r", encoding="utf-8")))
bo_parameters = test_bo_campaign_state.bo_parameters
# Convert array values to scalars for parameters_to_commands testing
test_bo_parameters = bo_parameters.copy()
test_bo_parameters["xylopyridine_analogs_concentrations_uM"] = bo_parameters["xylopyridine_analogs_concentrations_uM"][0]
test_bo_parameters["max_absorbance_concentration_uM_uv_detector"] = bo_parameters["max_absorbance_concentration_uM_uv_detector"][0]
test_bo_parameters["target_absorbance_in_the_uv_detector"] = bo_parameters["target_absorbance_in_the_uv_detector"][0]
test_bo_campaign_state.update_bo_parameters(test_bo_parameters)
test_iteration_state = IterationState()
test_iteration_state.update_iteration(1)
test_iteration_state.update_trial_conditions({
    "flow_rate": 100,
    "dilution_factor": 0.5,
    "temperature": 25,
    "co_solvent_valve_position": 3,
    "co_solvent_dilution_factor": 0.2,
    "light_intensity": 70
}
)

pytest_constrain_to_search_space_test_cases = [
    [test_bo_campaign_state, test_iteration_state,
     {"flow_rate": round(float(100), 2),
      "dilution_factor": round(float(0.5), 2),
      "temperature": round(float(25), 2),
      "co_solvent_valve_position": float(round(3, 2)),
      "co_solvent_dilution_factor": round(float(0.2), 2),
      "light_intensity": round(float(70), 2)
      }
     ]
]

pytest_generate_bo_input_test_cases = [
    ["test_config_ax_demo.json", "Xylopyridine_Analog_1"]
]

pytest_parameters_to_commands_test_cases = [
    [test_bo_campaign_state, test_iteration_state]
]

pytest_standardize_input_test_cases = [
    [test_iteration_state, {
        "flow_rate": round(float(100), 2),
        "dilution_factor": round(float(0.5), 2),
        "temperature": round(float(25), 2),
        "co_solvent_valve_position": float(round(3, 2)),
        "co_solvent_dilution_factor": round(float(0.2), 2),
        "light_intensity": round(float(70), 2)
    }]
]

pytest_time_to_reach_target_volume_test_cases = [3000, 500, 360.0]


# Part 2) Generate test functions for each preprocessing function
def test_check_volume(test_case):
    current_volume_uL, required_volume_uL, minimum_volume_remaining_uL, solution_name, interactive, expected_remaining = test_case
    assert check_volume(current_volume_uL, required_volume_uL, minimum_volume_remaining_uL, solution_name, interactive=interactive) == expected_remaining

def test_constrain_to_search_space(test_case):
    bo_campaign_state, iteration_state, expected_trial_conditions = test_case
    result_state = constrain_to_search_space(bo_campaign_state, iteration_state)
    assert result_state.trial_conditions == expected_trial_conditions

def test_generate_bo_input(test_case):
    json_file_path, xylopyridine_analog = test_case
    bo_input = generate_bo_input_file(json_file_path, xylopyridine_analog)
    # Just verify it returns a dict with expected keys
    assert isinstance(bo_input, dict)
    assert "base_directory" in bo_input
    assert "xylopyridine_analog_index" in bo_input

# TODO : Update the test so they all generate the instrument commands from parameters_to_commands 
def test_parameters_to_commands(test_case):
    bo_campaign_state, iteration_state = test_case
    commands = parameters_to_commands(bo_campaign_state, iteration_state)
    
    assert isinstance(commands, dict)
    # Verify expected keys are present
    expected_keys = ["flow_rate_pump1", "volume_pump1", "flow_rate_pump2", "volume_pump2",
                     "flow_rate_pump3", "volume_pump3", "position_valve2",
                     "flow_rate_pump4", "volume_pump4", "temperature", "light_intensity"]
    assert all(key in commands for key in expected_keys)

def test_standardize_input(test_case):
    iteration_state, expected_trial_conditions = test_case
    result_state = standardize_input(iteration_state)
    # standardize_input returns an IterationState with rounded trial conditions
    assert isinstance(result_state, IterationState)
    assert result_state.trial_conditions == expected_trial_conditions

def test_time_to_reach_target_volume(test_case):
    volume_uL, flow_rate_uL_per_min, expected_time_min = test_case
    # Note: function expects flow_rate first, then volume
    result = time_to_reach_target_volume(flow_rate_uL_per_min, volume_uL)
    assert result == expected_time_min

# Part 3) Run all the test cases
if __name__ == "__main__":
    print("Running preprocessing unit tests...\n")
    
    # Test 1: check_volume
    print("Test 1: check_volume")
    for i, test_case in enumerate(pytest_check_volume_test_cases):
        try:
            test_check_volume(test_case)
            print(f"  ✓ Test case {i+1} passed")
        except AssertionError as e:
            print(f"  ✗ Test case {i+1} failed: {e}")
        except Exception as e:
            print(f"  ✗ Test case {i+1} error: {e}")
    
    # Test 2: constrain_to_search_space
    print("\nTest 2: constrain_to_search_space")
    for i, test_case in enumerate(pytest_constrain_to_search_space_test_cases):
        try:
            test_constrain_to_search_space(test_case)
            print(f"  ✓ Test case {i+1} passed")
        except AssertionError as e:
            print(f"  ✗ Test case {i+1} failed: {e}")
        except Exception as e:
            print(f"  ✗ Test case {i+1} error: {e}")
    
    # Test 3: generate_bo_input
    print("\nTest 3: generate_bo_input")
    for i, test_case in enumerate(pytest_generate_bo_input_test_cases):
        try:
            test_generate_bo_input(test_case)
            print(f"  ✓ Test case {i+1} passed")
        except AssertionError as e:
            print(f"  ✗ Test case {i+1} failed: {e}")
        except Exception as e:
            print(f"  ✗ Test case {i+1} error: {e}")
    
    # Test 4: parameters_to_commands
    print("\nTest 4: parameters_to_commands")
    for i, test_case in enumerate(pytest_parameters_to_commands_test_cases):
        try:
            test_parameters_to_commands(test_case)
            print(f"  ✓ Test case {i+1} passed")
        except AssertionError as e:
            print(f"  ✗ Test case {i+1} failed: {e}")
        except Exception as e:
            print(f"  ✗ Test case {i+1} error: {e}")
    
    # Test 5: standardize_input
    print("\nTest 5: standardize_input")
    for i, test_case in enumerate(pytest_standardize_input_test_cases):
        try:
            test_standardize_input(test_case)
            print(f"  ✓ Test case {i+1} passed")
        except AssertionError as e:
            print(f"  ✗ Test case {i+1} failed: {e}")
        except Exception as e:
            print(f"  ✗ Test case {i+1} error: {e}")
    
    # Test 6: time_to_reach_target_volume
    print("\nTest 6: time_to_reach_target_volume")
    try:
        test_time_to_reach_target_volume(pytest_time_to_reach_target_volume_test_cases)
        print(f"  ✓ Test passed")
    except AssertionError as e:
        print(f"  ✗ Test failed: {e}")
    except Exception as e:
        print(f"  ✗ Test error: {e}")
    
    print("\nAll tests completed!")