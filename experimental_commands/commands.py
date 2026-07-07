import csv

from experimental_commands.generate_production_run_commands import generate_production_run_commands
from experimental_commands.generate_experimental_commands import (
    generate_experimental_commands,
)
from experimental_commands.generate_temperature_commands import (
    generate_temperature_commands,
)
from experimental_commands.generate_wash_commands import generate_wash_commands
from experimental_commands.generate_light_intensity_commands import generate_light_intensity_commands

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
    light_intensity: float,
    reactant_wavelength: float,
    product_wavelength: float,
    reference_wavelength: float,
    blank_light_intensity_threshold: float,
    wavelength_for_blank_light_intensity_check: float,
    convergence_time: float,
) -> None:
    """
    The role of this csv file is to generate the csv commands for each individual
    iteration of our bayesian optimization and will have four different commands
    to set temperture, set the light intesnity, flow our compound at various 
    concentrations, and wash the system after the experiment is complete

    parameters:
     - commands_path: Output directory and csv prefix for all our instrument commands
     - flow_rate_pump1: Flow rate of harvard apparatus with our XYLO compound using the 
     VICI M6 Pump 1
     - flow_rate_pump2: Flow rate of 0.1 M HCl water for diluting our compound
     before it reaches the detector using the tri-continent pump 1
     - flow_rate_pump3: Flow rate of cosolvents for diluting our compound
     before it reaches the reactor UV-detector and after the reactor bed using the
     VICI M6 Pump 2
     - flow_rate_pump4: Flow rate of 0.1 M HCl water for diluting our compound
     before it reaches the reactor UV-detector and after the reactor bed using the
     tri-continent pump 2
     - volume_pump1: Volume of Xylo compound to pump using harvard aparatus
     - volume_pump2: volume 0.1 M HCl water to dilute our Xylo compound before
     it reaches the reactor bed
     - volume_pump3: volume 0.1 M cosolvent to dilute our Xylo compound solution
     before it reaches the UV-detector
     - volume_pump4: volume 0.1 M HCl water to dilute our Xylo compound solution
     after it reaches the reactor bed and before it reaches the UV-detector.
    - valve_position_pump3: valve position for the VICI M6 pump 2 which pumps the co-solvent.
     - temperature: Temperature to set the thermal couple to for the experiment
     - fraction_of_cosolvent: Fraction of co-solvent to use for the experiment
     - light_intensity: Light intensity to set the mirror box to for the experiment
     - reactant_wavelength: wavelength of the reactant to set the UV-detector to for the experiment
     - product_wavelength: wavelength of the product to set the UV-detector to for the experiment
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
                light_intensity,
                reactant_wavelength,
                product_wavelength,
                reference_wavelength,
                blank_light_intensity_threshold,
                wavelength_for_blank_light_intensity_check,
                convergence_time=convergence_time,
            )
        )

    # Generate wash commands
    # We wanted to keep wash flow rate at 3000 uL/min when washing the total_flow_rate
    total_flow_rate = flow_rate_pump1 + flow_rate_pump2 + flow_rate_pump3 + flow_rate_pump4
    # This wash scaling will make the wash flow rate constant at 3000 uL/min
    wash_scaling = total_flow_rate / 3000
    wash_flow_rate_pump2 = (flow_rate_pump1 + flow_rate_pump2) / wash_scaling
    wash_flow_rate_pump3 = flow_rate_pump3 / wash_scaling
    wash_flow_rate_pump4 = flow_rate_pump4 / wash_scaling
    wash_total_flow_rate = wash_flow_rate_pump2 + wash_flow_rate_pump3 + wash_flow_rate_pump4
    wash_volume_pump2 = 6000 * (wash_flow_rate_pump2 / wash_total_flow_rate)
    wash_volume_pump3 = 6000 * (wash_flow_rate_pump3 / wash_total_flow_rate)
    wash_volume_pump4 = 6000 * (wash_flow_rate_pump4 / wash_total_flow_rate)

    with open(wash_commands_csv, "w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerows(
            generate_wash_commands(
                wash_flow_rate_pump2,
                wash_volume_pump2,
                wash_flow_rate_pump3,
                wash_volume_pump3,
                wash_flow_rate_pump4,
                wash_volume_pump4,
                valve_position_pump3,
            )
        )

def save_production_run_commands_to_csv(commands_path: str,
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
                         light_intensity: float,) -> None:
    """
    Save a list of instrument commands to a CSV file.

    parameters:
     - commands: A list of instrument commands, where each command is a list of strings
     representing the command and its parameters.
     - commands_path: The path to the CSV file where the commands should be saved.

    return:
     - None
    """
    temperature_commands_csv = f"{commands_path}_temperature.csv"
    wash_commands_csv = f"{commands_path}_wash.csv"
    light_intensity_commands_csv = f"{commands_path}_light_intensity.csv"
    experiment_commands_csv = f"{commands_path}_production_run.csv"

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
            generate_production_run_commands(
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
    fraction_of_cosolvent = 1
    # Generate wash commands
    # We wanted to keep wash flow rate at 3000 uL/min when washing the total_flow_rate
    total_flow_rate = flow_rate_pump1 + flow_rate_pump2 + flow_rate_pump3 + flow_rate_pump4
    # This wash scaling will make the wash flow rate constant at 3000 uL/min
    wash_scaling = total_flow_rate / 3000
    wash_flow_rate_pump2 = (flow_rate_pump1 + flow_rate_pump2) / wash_scaling
    wash_flow_rate_pump3 = flow_rate_pump3 / wash_scaling
    wash_flow_rate_pump4 = flow_rate_pump4 / wash_scaling
    wash_volume_pump2 = 4000 * (1 - fraction_of_cosolvent)
    wash_volume_pump3 = 4000 * fraction_of_cosolvent
    wash_volume_pump4 = wash_flow_rate_pump4 * 4

    with open(wash_commands_csv, "w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerows(
            generate_wash_commands(
                wash_flow_rate_pump2,
                wash_volume_pump2,
                wash_flow_rate_pump3,
                wash_volume_pump3,
                wash_flow_rate_pump4,
                wash_volume_pump4,
                valve_position_pump3,
            )
        )

def run_commands(command_file: str, instrument_config_file: str, output_dir: str) -> None:
    """
    Run a single CSV command file against the connected instruments.

    parameters:
     - command_file: Path to the CSV command file to execute
     - instrument_config_file: Path to the instrument configuration CSV
     - output_dir: Path to the directory where output files should be saved
    """
    if GeneralExperimentMethod is None:
        raise RuntimeError(
            "GeneralExperimentMethod not available. "
            "Install the AutoZahrt hardware package or run in simulation mode."
        )

    experiment = GeneralExperimentMethod(command_file, instrument_config_file, output_dir)
    experiment.run_experiment()

def save_prime_commands_to_csv(commands_path: str, commands) -> None:
    """
    Save a list of prime commands to a CSV file.

    parameters:
     - commands_path: The path to the CSV file where the commands should be saved.
     - commands: A list of prime commands, where each command is a list of strings representing the command and its parameters.
    """
    with open(commands_path, "w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerows(commands)
