# ------------------------------------------------------------------------------
# Software: AUTO_ZAHRT
# Copyright: (C) 2026 by Professor Andrew Zahrt
# This software is the intellectual property of Professor Andrew Zahrt
# Contributions by graduate students Scott Laverty and Joao are acknowledged.
# All rights reserved.
# ------------------------------------------------------------------------------

"""
This script will calculate equipment parameters for the production run based
on the optimal experimental parameters we got from our bayesian optimization campaign
as well as the desired amount of product we want to produce in our production run.
"""


def calculate_production_run_parameters(
    reactor_bed_flow_rate,
    dilution_factor,
    temperature,
    cosolvent_valve_position,
    fraction_of_cosolvent,
    light_intensity,
    throughput_nmol_per_min,
    desired_mols,
) -> None:
    """
    This function will calculate equipment parameters for the production run based
    on the optimal experimental parameters we got from our bayesian optimization campaign
    as well as the desired amount of product we want to produce in our production run.

     - None
    """

    reaction_time_min = calculate_production_run_reaction_time(
        desired_nmols=desired_mols, throughput_nmol_per_min=throughput_nmol_per_min
    )

    production_run_volume_uL = calculate_production_run_volume(
        reactor_bed_flow_rate=reactor_bed_flow_rate, reaction_time_min=reaction_time_min
    )

    


def calculate_production_run_reaction_time(desired_nmols, throughput_nmol_per_min):
    """
    This function will calculate the reaction time needed to produce the desired amount of product
    based on the throughput we got from our bayesian optimization campaign.

    parameters:
        - desired_nmols: The desired amount of product we want to produce in our production run.
        - throughput_nmol_per_min: The throughput we got from our bayesian optimization campaign in nmol/min.
    """
    reaction_time_min = desired_nmols / throughput_nmol_per_min

    return reaction_time_min


def calculate_production_run_volume(reactor_bed_flow_rate, reaction_time_min) -> float:
    """
    This function will calculate the volume of the reaction mixture needed to produce the desired amount of product
    based on the flow rate and the reaction time.

    parameters:
        - reactor_bed_flow_rate: The flow rate we got from our bayesian optimization campaign in mL/min.
        - reaction_time_min: The reaction time we calculated based on the desired amount of product and
    """
    production_run_volume_uL = reactor_bed_flow_rate * reaction_time_min

    return production_run_volume_uL
