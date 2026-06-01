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
# TODO : Change os to pathlib
import os

from production_run.extract_best_reaction_conditions import extract_best_reaction_conditions
from production_run.calculate_production_run_parameters import calculate_production_run_parameters
from experimental_commands.commands import save_production_run_commands_to_csv, run_commands
from experimental_commands.generate_instrument_config import save_instrument_config_csv


def production_run(
    bo_results: str,
    yield_threshold: float,
    desired_mols: float,
    xylopyridine_analogs_concentrations_uM: float,
    output_dir: str,
) -> None:
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
        - xylopyridine_analogs_concentrations_uM: Stock solution concentration in µM,
          used to calculate pump flow rates via mass-balance dilution math.
        - output_dir: Directory in which to write the command and instrument config CSVs.
    Return:
     - None
    """
    os.makedirs(output_dir, exist_ok=True)

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
        throughput_nmol_per_min,
        desired_mols,
        xylopyridine_analogs_concentrations_uM,
    )

    commands_path = f"{output_dir}/production_run_commands"
    instrument_config_path = f"{output_dir}/production_run_instrument_config.csv"

    save_production_run_commands_to_csv(
        commands_path=commands_path,
        flow_rate_pump1=experimental_parameters["flow_rate_pump1"],
        flow_rate_pump2=experimental_parameters["flow_rate_pump2"],
        flow_rate_pump3=experimental_parameters["flow_rate_pump3"],
        flow_rate_pump4=experimental_parameters["flow_rate_pump4"],
        volume_pump1=experimental_parameters["volume_pump1"],
        volume_pump2=experimental_parameters["volume_pump2"],
        volume_pump3=experimental_parameters["volume_pump3"],
        volume_pump4=experimental_parameters["volume_pump4"],
        valve_position_pump3=experimental_parameters["position_valve2"],
        temperature=experimental_parameters["temperature"],
        fraction_of_cosolvent=fraction_of_cosolvent,
        light_intensity=experimental_parameters["light_intensity"],
    )
    save_instrument_config_csv(instrument_config_path)

    run_commands(f"{commands_path}_wash.csv", instrument_config_path, output_dir)
    run_commands(f"{commands_path}_temperature.csv", instrument_config_path, output_dir)
    run_commands(f"{commands_path}_light_intensity.csv", instrument_config_path, output_dir)
    run_commands(f"{commands_path}_production_run.csv", instrument_config_path, output_dir)



    
