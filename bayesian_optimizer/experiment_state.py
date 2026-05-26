# ------------------------------------------------------------------------------
# Software: project_dead_mans_fingers
# Copyright: (C) 2025 by Professor Andrew Zahrt
# This software is the intellectual property of Professor Andrew Zahrt
# Contributions by graduate students Scott Laverty and Joao are acknowledged.
# All rights reserved.
# ------------------------------------------------------------------------------

"""
Purpose of this code is to hold the state of the experiment across a single bo campaign,
and provide utility functions to update the state between iterations and experiments.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Tuple
import pandas as pd


@dataclass
class BoCampaignState:
    """
    Data class to hold the state of a single Bayesian optimization campaign.
    """

    bo_parameters: Dict[str, Any] = field(default_factory=dict)
    simulation_mode: bool = field(default=False)
    results_cache: Dict[Tuple, Tuple] = field(default_factory=dict)
    noise_sem_percent_yield: float = field(default=1.0)
    noise_sem_throughput: float = field(default=1.0)
    volume_stock_solutions: Dict[str, Any] = field(default_factory=dict)
    waste_volume_uL: float = field(default=0.0)
    volume_log: list = field(default_factory=list)
    bo_csv_path: str = field(default="")

    def update_bo_parameters(self, bo_parameters: Dict[str, Any]) -> None:
        """
        Update the Bayesian optimization experimental parameters.
        """
        self.bo_parameters.clear()
        self.bo_parameters.update(bo_parameters)

    def set_simulation_mode(self, simulation_mode: bool) -> None:
        """
        Set the simulation mode flag.
        """
        self.simulation_mode = simulation_mode

    def update_results_cache(self, key: Tuple, value: Tuple) -> None:
        """
        Update the results cache with a new key-value pair.
        """
        self.results_cache[key] = value

    def set_noise_sem(self, noise_sem_percent_yield: float, noise_sem_throughput: float) -> None:
        """
        Set the per-metric noise SEM values reported to Ax.

        # TODO: Determine empirical SEM values from repeated measurements at the
        # same conditions once experimental repeat data is available.

        Parameters:
            noise_sem_percent_yield: SEM for percent yield (absolute %, e.g. 1.0 = ±1%)
            noise_sem_throughput: SEM for throughput (nmol/min, e.g. 1.0 = ±1 nmol/min)
        """
        self.noise_sem_percent_yield = noise_sem_percent_yield
        self.noise_sem_throughput = noise_sem_throughput

    def update_volume_stock_solutions(
        self, volume_stock_solutions: Dict[str, Any]
    ) -> None:
        """
        Update the volume stock solutions for the current iteration.
        """
        self.volume_stock_solutions.clear()
        self.volume_stock_solutions.update(volume_stock_solutions)

    def update_waste_volume(self, waste_volume_uL: float) -> None:
        """
        Update the current waste container volume.
        """
        self.waste_volume_uL = waste_volume_uL

    def append_volume_log_entry(self, entry: dict) -> None:
        """
        Append a per-iteration volume snapshot to the volume log.
        """
        self.volume_log.append(entry)

    def set_bo_csv_path(self, bo_csv_path: str) -> None:
        """
        Set the file path for saving Bayesian optimization results CSV.
        """
        self.bo_csv_path = bo_csv_path

    def get_parameter_bounds(self) -> Dict[str, Any]:
        """
        Extract all parameter bounds from experimental parameters.

        Returns:
            Dictionary containing min/max bounds for all optimization parameters:
            - flow_rate_min, flow_rate_max
            - dilution_factor_min, dilution_factor_max
            - temperature_min, temperature_max
            - co_solvent_valve_position_min, co_solvent_valve_position_max
            - co_solvent_dilution_factor_min, co_solvent_dilution_factor_max
            - light_intensity_min, light_intensity_max
        """
        flow_rate_min, flow_rate_max = self.bo_parameters["flow_rate"]
        dilution_factor_min, dilution_factor_max = self.bo_parameters["dilution_factor"]
        temperature_min, temperature_max = self.bo_parameters["temperature"]
        co_solvent_valve_position_min, co_solvent_valve_position_max = self.bo_parameters["cosolvents_valve_position"]
        co_solvent_dilution_factor_min, co_solvent_dilution_factor_max = self.bo_parameters[
            "co_solvent_dilution_factor"
        ]
        light_intensity_min, light_intensity_max = self.bo_parameters["light_intensity"]

        return {
            "flow_rate_min": flow_rate_min,
            "flow_rate_max": flow_rate_max,
            "dilution_factor_min": dilution_factor_min,
            "dilution_factor_max": dilution_factor_max,
            "temperature_min": temperature_min,
            "temperature_max": temperature_max,
            "cosolvent_valve_position_min": co_solvent_valve_position_min,
            "cosolvent_valve_position_max": co_solvent_valve_position_max,
            "co_solvent_dilution_factor_min": co_solvent_dilution_factor_min,
            "co_solvent_dilution_factor_max": co_solvent_dilution_factor_max,
            "light_intensity_min": light_intensity_min,
            "light_intensity_max": light_intensity_max,
        }


@dataclass
class IterationState:
    """
    Data class to hold the state of a single iteration within a Bayesian optimization campaign.
    """

    # BO Campaign iteration and trial conditions
    iteration: int = field(default=0)
    trial_conditions: Dict[str, Any] = field(default_factory=dict)
    reactor_bed_concentration_uM: float = field(default=0.0)

    # Experimental equipment settings for the current trial conditions
    instrument_parameters: Dict[str, Any] = field(default_factory=dict)

    # Checks to see if the code has converged early based on the UV-Vis data
    converged_early: bool = field(default=False)

    # Steady state absorbance values for reactant and product during the current trial
    absorbance_at_steady_state: Dict[str, float] = field(default_factory=dict)

    def update_iteration(self, iteration: int) -> None:
        """
        Update the iteration metadata.
        """
        self.iteration = iteration

    def update_trial_conditions(self, trial_conditions: Dict[str, Any]) -> None:
        """
        Update the trial conditions for the current iteration.
        """
        self.trial_conditions = trial_conditions

    def update_reactor_bed_concentration_uM(self, reactor_bed_concentration_uM: float) -> None:
        """
        Update the calculated reactor bed concentration in uM for the current trial conditions.
        """
        self.reactor_bed_concentration_uM = reactor_bed_concentration_uM

    def update_instrument_parameters(self, instrument_parameters: Dict[str, Any]) -> None:
        """
        Update the instrument parameters for the current trial conditions.
        """
        self.instrument_parameters = instrument_parameters

    def update_steady_state_absorbance(
        self, absorbance_at_steady_state: Dict[str, float]
    ) -> None:
        """
        Update the steady state absorbance values for reactant and product.
        """
        for species, absorbance in absorbance_at_steady_state.items():
            self.absorbance_at_steady_state[species] = absorbance

@dataclass
class CalibrationState:
    """
    Data class to hold the state of a single calibration campaign.
    """

    # Calibration parameters
    calibration_parameters: Dict[str, Any] = field(default_factory=dict)
    is_simulation: bool = field(default=False)
    calibration_iteration: int = field(default=0)
    commands_dir: Path = field(default=Path(""))
    results_dir: Path = field(default=Path(""))
    instrument_config_path: Path = field(default=Path(""))
    calibration_results_df: pd.DataFrame = field(default_factory=lambda: pd.DataFrame(columns=[
        "concentration_M",
        "average_absorbance_std"
    ]))
    dilution_factor: float = field(default=1.0)
    

    def update_calibration_parameters(self, calibration_parameters: Dict[str, Any]) -> None:
        """
        Update the calibration parameters.
        """
        self.calibration_parameters.clear()
        self.calibration_parameters.update(calibration_parameters)

    def set_simulation_mode(self, is_simulation: bool) -> None:
        """
        Set the simulation mode flag for the calibration campaign.
        """
        self.is_simulation = is_simulation
    
    def update_calibration_iteration(self, calibration_iteration: int) -> None:
        """
        Update the current calibration iteration number.
        """
        self.calibration_iteration = calibration_iteration
    
    def update_commands_dir(self, commands_dir: Path) -> None:
        """
        Update the directory path for saving experimental command CSV files.
        """
        self.commands_dir = commands_dir

    def update_results_dir(self, results_dir: Path) -> None:
        """
        Update the directory path for saving experimental results CSV files.
        """
        self.results_dir = results_dir

    def update_instrument_config_path(self, instrument_config_path: Path) -> None:
        """
        Update the file path for the instrument configuration CSV.
        """
        self.instrument_config_path = instrument_config_path
    
    def update_calibration_results_df(self, concentration_M: float, average_absorbance_std: float) -> None:
        """
        Update the calibration results dataframe with new results from the current iteration.
        """
        new_entry_df = pd.DataFrame({
            "concentration_M": [concentration_M],
            "average_absorbance_std": [average_absorbance_std]
        })
        self.calibration_results_df = pd.concat([self.calibration_results_df, new_entry_df], ignore_index=True)
    
    def update_dilution_factor(self, dilution_factor: float) -> None:
        """
        Update the dilution factor for the current iteration.
        """
        self.dilution_factor = dilution_factor
        