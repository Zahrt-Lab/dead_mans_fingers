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

from preprocessing.parameters_to_commands import parameters_to_commands

def calculate_production_run_parameters(
    reactor_bed_flow_rate,
    dilution_factor,
    temperature,
    light_intensity,
    throughput_nmol_per_min,
    desired_mols,
    xylopyridine_analogs_concentrations_uM
) -> dict:
    """
    This function will calculate equipment parameters for the production run based
    on the optimal experimental parameters we got from our bayesian optimization campaign
    as well as the desired amount of product we want to produce in our production run.

    Returns:
        dict: Instrument parameters for the production run (pump flow rates, volumes,
              valve position, temperature, light intensity).
    """

    reaction_time_min = calculate_production_run_reaction_time(
        desired_nmols=desired_mols, throughput_nmol_per_min=throughput_nmol_per_min
    )

    production_run_volume_uL = calculate_production_run_volume(
        reactor_bed_flow_rate=reactor_bed_flow_rate, reaction_time_min=reaction_time_min
    )

    trial_conditions = {
        "flow_rate": reactor_bed_flow_rate,
        "dilution_factor": dilution_factor,
        "temperature": temperature,
        "light_intensity": light_intensity,
    }

    # The absorbance is not used in production run
    instrument_commands = parameters_to_commands(trial_conditions=trial_conditions, 
                           total_volume_through_reactor_bed=production_run_volume_uL, 
                           xylopyridine_analogs_concentrations_uM=xylopyridine_analogs_concentrations_uM,
                           max_absorbance_concentration_uM_uv_detector=0.0, 
                           target_absorbance_in_the_uv_detector=0.0,
                           production_run=True
                           )
    return instrument_commands


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
        - reactor_bed_flow_rate: The flow rate we got from our bayesian optimization campaign in uL/min.
        - reaction_time_min: The reaction time calculated from desired_nmols / throughput_nmol_per_min.

    Returns:
        float: Production volume in µL (flow_rate_uL_per_min × reaction_time_min).
    """
    production_run_volume_uL = reactor_bed_flow_rate * reaction_time_min

    return production_run_volume_uL
