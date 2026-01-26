import csv
from experimental_commands.generate_experimental_commands import (
    generate_experimental_commands,
)
from experimental_commands.generate_temperature_commands import (
    generate_temperature_commands,
)
from experimental_commands.generate_wash_commands import generate_wash_commands
from experimental_commands.generate_set_light_intensity_commands import generate_light_intensity_commands

# TODO : Need to edit this code so that it pip installs the AutoZahrt_v3 package
# Import AutoZahrt GeneralExperimentMethod from local Auto_Zahrt_v3 package
try:
    from methods import GeneralExperimentMethod
except ImportError:
    # Used cases when for simulation mode or when AutoZahrt hardware is not available
    GeneralExperimentMethod = None

# TODO : Update the current experimental commands to match the new experimental setup

# This saves all the instrument commands to a csv file
def save_commands_csv(
    commands_path: str,
    flow_rate_pump1: float,
    flow_rate_pump2: float,
    flow_rate_pump3: float,
    flow_rate_pump4: float,
    volume_pump1: float,
    volume_pump2: float,
    volume_pump3: float,
    volume_pump4: float,
    valve_position_pump3: int,
    temperature: float,
    fraction_of_cosolvent: float,
    light_intensity: float,
) -> None:
    """
    The role of this csv file is to generate the csv commands for each individual
    iteration of our bayesian optimization and will have three different commands
    to set temperture, flow our compound at various concentrations, and wash the
    system after the experiment is complete

    parameters:
     - commands_path: Output directory and csv prefix for all our instrument commands
     - flow_rate_pump1: Flow rate of harvard apparatus with our XYLO compound
     - flow_rate_pump2: Flow rate of 0.1 M HCl water for diluting our compound
     before it reaches the detector using the VICI M6 Pump 1
     - flow_rate_pump3: Flow rate of 0.1 M HCL water for diluting our compound
     before it reaches the UV-detector and after the reactor bed using the
     VICI M6 Pump 2
     - volume_pump1: Volume of Xylo compound to pump using harvard aparatus
     - volume_pump2: volume 0.1 M HCl water to dilute our Xylo compound before
     it reaches the reactor bed
     - volume_pump3: volume 0.1 M HCl water to dilute our Xylo compound solution
     before it reaches the UV-detector
     - temperature: Temperature to set the thermal couple to for the experiment
     - previous_temperature: Previous temperature the thermal couple was set for
     the previous experiment
    return:
     - None
    """
    temperature_commands_csv = f"{commands_path}_temperature.csv"
    wash_commands_csv = f"{commands_path}_wash.csv"
    light_intensity_commands_csv = f"{commands_path}_light_intensity.csv"
    experiment_commands_csv = f"{commands_path}_experiment.csv"

    # Generate temperature commands
    with open(temperature_commands_csv, "w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerows(
            generate_temperature_commands(temperature)
        )

    # Generate light intensity commands
    with open(light_intensity_commands_csv, "w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerows(
            generate_light_intensity_commands(light_intensity)
        )

    # Generate experiment commands
    with open(experiment_commands_csv, "w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerows(
            generate_experimental_commands(
                flow_rate_pump1,
                flow_rate_pump2,
                flow_rate_pump3,
                flow_rate_pump4,
                volume_pump1,
                volume_pump2,
                volume_pump3,
                volume_pump4,
            )
        )

    # Generate wash commands
    with open(wash_commands_csv, "w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerows(
            generate_wash_commands(
                flow_rate_pump2,
                volume_pump2,
                flow_rate_pump3,
                volume_pump3,
                flow_rate_pump4,
                volume_pump4,
                valve_position_pump3,
            )
        )




def run_commands(experiment_commands, instrument_config_file) -> None:
    """
    This runs all of our experimental commands given the command and instrument config files

    parameters:
     - experiment_commands: Experimental Commands in the form of a csv
     - instrument_config_file: Instrument config file to help us to determine what equipment
     is being used
    """

    # TODO: Need to connect this code to the AutoZahrt GeneralExperimentMethod
    
    # Check if we're in simulation mode by importing the flag
    from bayesian_optimizer.state import SIMULATION_MODE
    
    if SIMULATION_MODE:
        print(f"[SIMULATION] Would run commands from: {experiment_commands}")
        return
    
    if GeneralExperimentMethod is None:
        raise RuntimeError(
            "GeneralExperimentMethod not available. "
            "Run in simulation mode with --simulation flag or install AutoZahrt hardware package."
        )

    fluorescent_reaction_optimization_experiment = GeneralExperimentMethod(
        experiment_commands, instrument_config_file
    )
    fluorescent_reaction_optimization_experiment.run_experiment()

