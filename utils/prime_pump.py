'''This script wraps the methods to prime pump 1 (Xylopyridine solution) before starting the optimization campaign. 
It generates the commands to prime pump 1 and saves them to a csv file. The commands include setting the valve position 
and dispensing the Xylopyridine solution at the specified flow rate and volume.'''

# ------------------------------------------------------------------------------
# Software: AUTO_ZAHRT
#TODO: DEcide wheter this goes into experimental commands or utils. It is a bit of both, but leaning towards utils since it is a helper function to generate the prime commands and save them to a csv file.

from datetime import datetime
import os
from experimental_commands.generate_instrument_config import save_instrument_config_csv
from experimental_commands.generate_prime_commands import generate_prime_commands
from experimental_commands.commands import run_commands, save_prime_commands_to_csv



def prime_pump1(
        flow_rate_pump1: float,
        volume_pump1: float,
        valve1_position: int,
        base_directory: str,
        *,
        zero_tolerance: float = 1e-6) -> None:
    """
    This function generates the commands to prime pump 1 (Xylopyridine solution) and saves them to a csv file.

    Parameters:
     - flow_rate_pump1: Flow rate of Xylopyridine solution to prime pump 1
        - volume_pump1: Volume of Xylopyridine solution to prime pump 1
        - valve1_position: Position of valve1
        - commands_path: Output directory and csv prefix for all our instrument commands
    """
# Need to create the folder where the files will be saved. THe current implementation 
# creates a folder with the date and time of the experiment. I need to keep the same consistent
# folder structure.
    date_only = datetime.now().strftime("%Y_%m_%d") 
    date_time = datetime.now().strftime("%Y_%m_%d-%H-%M-%S")
    experiment_folder = base_directory + f"/{date_only}/{date_time}"
    os.makedirs(experiment_folder, exist_ok=True)

#     1) Generate the instrument config (done inside the save commands)

#     2) Save the instrument config to a csv file
    intrument_config_path = experiment_folder + "/instrument_config.csv"
    save_instrument_config_csv(intrument_config_path)

#     3) Generate the commands to prime pump 1
    commands = generate_prime_commands(
        flow_rate_pump1=flow_rate_pump1,
        volume_pump1=volume_pump1,
        valve1_position=valve1_position,
        zero_tolerance=zero_tolerance,
    )

#     4) Save the commands to a csv file
    commands_path = experiment_folder + "/prime_commands.csv"
    save_prime_commands_to_csv(commands_path, commands)

#     5) Run the commands to prime pump 1
    print(f"Running the commands to prime pump 1. The commands are saved in {commands_path} and the instrument config is saved in {intrument_config_path}.")
    run_commands(commands_path, intrument_config_path, experiment_folder + "/output.csv")

