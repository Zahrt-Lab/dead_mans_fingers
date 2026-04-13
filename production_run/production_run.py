# ------------------------------------------------------------------------------
# Software: AUTO_ZAHRT
# Copyright: (C) 2026 by Professor Andrew Zahrt
# This software is the intellectual property of Professor Andrew Zahrt
# Contributions by graduate students Scott Laverty and Joao are acknowledged.
# All rights reserved.
# ------------------------------------------------------------------------------

"""
The purpose of this script is to run the production run after
we've converged on a set of optimal experimental parameters from our
bayesian optimization campaign.

This will allow us to run the experiment with the optimal parameters and
collect the data
"""

import pandas as pd

from extract_best_reaction_conditions import extract_best_reaction_conditions
from calculate_production_run_parameters import calculate_production_run_parameters
from experimental_commands.commands import save_commands_csv, run_commands

def production_run(bo_results : str, yield_threshold: float, desired_mols: float, output_dir: str) -> None:
    """
    This function will run the production run after we've converged on a set of optimal
    experimental parameters from our bayesian optimization campaign.

    parameters:
        - bo_results: The results from our bayesian optimization campaign that contains
        the optimal experimental parameters, in the form of a csv file.
        - yield_threshold: The percent yield threshold above which we want to consider the
          experimental parameters for our production run.
        - desired_mols: The desired number of moles of product we want to produce in
        our production run. This will be used to calculate how many runs we need to do
        to produce the desired amount of product based on the yield we got from our
        bayesian optimization campaign.

     - None
    """
    (
        reactor_bed_flow_rate,
        dilution_factor,
        temperature,
        cosolvent_valve_position,
        fraction_of_cosolvent,
        light_intensity,
        throughput_nmol_per_min,
    ) = extract_best_reaction_conditions(bo_results, yield_threshold=yield_threshold)
    
    experimental_parameters = calculate_production_run_parameters(
        reactor_bed_flow_rate,
        dilution_factor,
        temperature,
        cosolvent_valve_position,
        fraction_of_cosolvent,
        light_intensity,
        desired_mols,
        throughput_nmol_per_min,
    )

    save_commands_csv(commands_path=f"{output_dir}/production_run_commands.csv", 
                      flow_rate_pump1=experimental_parameters["flow_rate_pump1"],
                      flow_rate_pump2=experimental_parameters["flow_rate_pump2"],
                      flow_rate_pump3=experimental_parameters["flow_rate_pump3"],
                      flow_rate_pump4=experimental_parameters["flow_rate_pump4"],
                      volume_pump1=experimental_parameters["volume_pump1"],
                      volume_pump2=experimental_parameters["volume_pump2"],
                      volume_pump3=experimental_parameters["volume_pump3"],
                      volume_pump4=experimental_parameters["volume_pump4"],
                      valve_position_pump3=experimental_parameters["valve_position_pump3"],
                      temperature=experimental_parameters["temperature"],
                      fraction_of_cosolvent=experimental_parameters["fraction_of_cosolvent"],
                      light_intensity=experimental_parameters["light_intensity"]
                      )
    run_commands(f"{output_dir}/production_run_commands.csv")



    
