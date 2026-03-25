"""
Run simulated Bayesian Optimization experiments with real-time UV-Vis monitoring.
"""

import time
from pathlib import Path
from typing import Callable, Optional, Tuple

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

from utils.visualize_results import plot_absorbances_progress, plot_bo_results
from utils.simulated_data import simulate_uvvis_data


def run_simulated_experiment(
    reactor_bed_flow_rate: float,
    temperature: float,
    dilution_factor: float,
    volume: int,
    iteration_number: int,
    reactant_wavelength: int,
    product_wavelength: int,
    base_directory: Path,
    rate_constant_fn: Optional[Callable[[float, float, float], float]] = None,
) -> str:
    """
    Generate simulated UV-VIS data for a Bayesian optimization experiment.

    Simulates the reaction kinetics based on temperature, concentration, and flow rate,
    then saves the simulated absorbance data to a CSV file.

    Parameters:
        reactor_bed_flow_rate: Flow rate through reactor in uL/min.
        temperature: Reaction temperature in °C.
        dilution_factor: Dilution factor of stock solution (0.1-1.0).
        volume: Total volume to flow through reactor in uL.
        iteration_number: Current BO iteration number.
        reactant_wavelength: Wavelength for reactant absorbance (nm).
        product_wavelength: Wavelength for product absorbance (nm).
        base_directory: Directory to save simulated data CSV.
        rate_constant_fn: Optional callable with signature
            ``(flow_rate, temperature, dilution_factor) -> float``.
            When provided, its return value is used as the first-order rate
            constant instead of the default temperature/dilution formula.
            Intended for testing with known analytical response surfaces.

    Returns:
        Path to the saved CSV file containing simulated UV-VIS data.
    """
    print("[SIMULATION] Skipping UV-VIS hardware and running simulated experiment")
    print(
        "[SIMULATION] Skipping run_commands - would run:"
        "_temperature.csv, _light_intensity.csv, _experiment.csv and _wash.csv"
    )
    print("[SIMULATION] Generating simulated UV-VIS data...")

    # Calculate experiment time based on flow rate and volume
    experiment_time_seconds = (
        (volume / reactor_bed_flow_rate) * 60 if reactor_bed_flow_rate > 0 else 600
    )

    # Compute the first-order rate constant.
    # If a custom rate_constant_fn is provided (e.g. for testing), use it;
    # otherwise fall back to the default temperature/dilution formula.
    if rate_constant_fn is not None:
        rate_constant = rate_constant_fn(
            reactor_bed_flow_rate, temperature, dilution_factor
        )
    else:
        base_rate = 0.01
        temp_factor = (temperature - 5) / 85  # Normalize temperature (5-90°C range)
        dilution_norm = (dilution_factor - 0.1) / 0.9  # Normalize dilution (0.1-1.0 range)
        rate_constant = base_rate + (0.04 * temp_factor) + (0.02 * dilution_norm)
        rate_constant = max(0.005, min(0.08, rate_constant))  # Clamp to realistic range
    
    # Generate simulated data
    simulated_data_df = simulate_uvvis_data(
        time_end=int(experiment_time_seconds),
        time_step=5,
        rate_constant=rate_constant,
        initial_absorbance=1.0,
        noise_level=0.01,
        random_seed=42 + iteration_number,
        start_delay=min(60, experiment_time_seconds * 0.2),
    )
    
    # Rename columns to match expected format for post_process_uv_recording
    # Column format: "Time(s)" and wavelength as string (e.g., "409", "506")
    simulated_data_df = simulated_data_df.rename(
        columns={
            "Time_s": "Time(s)",
            "Absorbance_409nm": str(reactant_wavelength),
            "Absorbance_506nm": str(product_wavelength),
        }
    )
    
    # Save simulated data to CSV (same path post_process_uv_recording expects)
    csv_filename = f"Fluorescent_Bayesian_Optimization_iteration_{iteration_number}.csv"
    csv_filepath = Path(base_directory) / Path(csv_filename)
    simulated_data_df.to_csv(csv_filepath, index=False)
    
    print(f"[SIMULATION] Saved simulated UV-VIS data to {csv_filepath}")
    
    return str(csv_filepath)


def run_simulation(
    flow_rate: float,
    concentration: float,
    temperature: float,
    co_solvent: float,
    co_solvent_volume: float,
    reactor_concentration_uM: float,
    iteration_num: int,
    experimental_parameters: dict,
    csv_path: str,
    append_results_func,
    volume_pump1: float = None,
    volume_pump2: float = None,
    volume_pump3: float = None,
    flow_rate_pump1: float = None,
) -> Tuple[float, float]:
    """
    Run simulated experiment with real-time UV-Vis monitoring.

    Args:
        flow_rate: Flow rate in µL/min
        concentration: Relative concentration (0-1)
        temperature: Temperature in °C
        reactor_concentration_uM: Absolute concentration in µM
        iteration_num: Current iteration number
        experimental_parameters: Dictionary of experimental parameters
        csv_path: Path to CSV file for results
        append_results_func: Function to append results to CSV
        volume_pump1: Volume to dispense from pump 1 (µL)
        volume_pump2: Volume to dispense from pump 2 (µL)
        volume_pump3: Volume to dispense from pump 3 (µL)
        flow_rate_pump1: Flow rate of pump 1 (µL/min)

    Returns:
        (percent_yield, throughput)
    """
    print("Starting real-time UV-Vis monitoring...")

    # Simulate the reaction kinetics based on parameters
    base_rate = 0.01
    temp_factor = (temperature - 5) / 85  # Normalize temp to 0-1
    conc_factor = (concentration - 0.5) / 0.5  # Normalize conc to 0-1

    # Add co-solvent effects if parameters are defined
    co_solvent_effect = 0.0
    if "co_solvent" in experimental_parameters:
        co_solvent_min, co_solvent_max = experimental_parameters["co_solvent"]
        co_solvent_norm = (
            (co_solvent - co_solvent_min) / (co_solvent_max - co_solvent_min)
            if co_solvent_max > co_solvent_min
            else 0
        )
        co_solvent_effect = 0.01 * co_solvent_norm

    rate_constant = (
        base_rate + (0.04 * temp_factor) + (0.02 * conc_factor) + co_solvent_effect
    )
    rate_constant = max(0.005, min(0.08, rate_constant))  # Clamp to reasonable range

    # Calculate actual experiment time from pump volumes and flow rates
    # The slowest pump determines the total experiment time
    if volume_pump1 is not None and flow_rate_pump1 is not None and flow_rate_pump1 > 0:
        # Time in minutes = volume (µL) / flow_rate (µL/min)
        # Convert to seconds
        experiment_time_seconds = (volume_pump1 / flow_rate_pump1) * 60.0
    else:
        # Fallback to default if parameters not provided
        experiment_time_seconds = 120.0
    
    # Time speedup factor: 1 real second = 60 simulated seconds
    TIME_SPEEDUP = 60
    
    # Actual wall-clock time will be experiment_time_seconds / TIME_SPEEDUP
    real_time_duration = experiment_time_seconds / TIME_SPEEDUP
    
    # Reaction starts after some delay (simulate filling reactor)
    start_delay_seconds = min(60.0, experiment_time_seconds * 0.2)  # 20% of total time or 60s max

    # Setup for real-time data collection
    time_step = 5  # simulated seconds per step
    max_time = experiment_time_seconds  # Total simulated experiment time in seconds
    start_delay = start_delay_seconds  # Reaction starts after delay in simulated seconds
    
    # Real-time sleep interval between updates (simulated time / speedup)
    real_time_step = time_step / TIME_SPEEDUP

    collected_data = {
        "Time_s": [],
        "Absorbance_409nm": [],
        "Absorbance_506nm": [],
    }

    # Setup live plotting
    plt.ion()  # Enable interactive mode
    fig, ax = plt.subplots(figsize=(10, 6))
    (line_409,) = ax.plot([], [], "b-", label="409 nm (Reactant)", linewidth=2)
    (line_506,) = ax.plot([], [], "r-", label="506 nm (Product)", linewidth=2)
    ax.set_xlabel("Time (s)", fontsize=12)
    ax.set_ylabel("Absorbance", fontsize=12)
    ax.set_title(
        f"Real-time UV-Vis Monitoring - Iteration {iteration_num}", fontsize=14
    )
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)
    ax.set_xlim(0, max_time)
    ax.set_ylim(-0.1, 1.2)
    plt.tight_layout()

    converged = False
    current_time = 0

    print(f"\nSimulation parameters:")
    print(f"  - Experiment time: {max_time:.1f}s (simulated) = {real_time_duration:.1f}s (real-time, {TIME_SPEEDUP}x speedup)")
    print(f"  - Reaction starts at: {start_delay:.1f}s (simulated)")
    print(f"  - Rate constant: {rate_constant:.4f}")
    if volume_pump1 is not None:
        print(f"  - Based on pump1: {volume_pump1:.0f} µL at {flow_rate_pump1:.0f} µL/min")
    print(f"\nMonitoring started (updating every {time_step}s simulated = {real_time_step:.2f}s real)...\n")

    # Simulate data point by point (every 5 seconds)
    current_time = 0

    while current_time <= max_time:
        # Generate data for this single time point
        time_shifted = max(current_time - start_delay, 0)

        # First-order kinetics
        np.random.seed(42 + iteration_num + int(current_time))

        if current_time < start_delay:
            abs_409 = np.random.normal(0, 0.005)
            abs_506 = np.random.normal(0, 0.005)
        else:
            reactant_fraction = np.exp(-rate_constant * time_shifted)
            product_fraction = 1 - reactant_fraction
            abs_409 = reactant_fraction + np.random.normal(0, 0.005)
            abs_506 = product_fraction + np.random.normal(0, 0.005)

        # Clip to reasonable range
        abs_409 = np.clip(abs_409, 0, 1.1)
        abs_506 = np.clip(abs_506, 0, 1.1)

        # Collect data
        collected_data["Time_s"].append(current_time)
        collected_data["Absorbance_409nm"].append(abs_409)
        collected_data["Absorbance_506nm"].append(abs_506)

        # Update live plot
        line_409.set_data(collected_data["Time_s"], collected_data["Absorbance_409nm"])
        line_506.set_data(collected_data["Time_s"], collected_data["Absorbance_506nm"])
        fig.canvas.draw()
        fig.canvas.flush_events()

        # Print status update
        print(
            f"t={current_time:3d}s | A409={abs_409:.4f} | A506={abs_506:.4f} | Monitoring..."
        )

        # Simulate the time step delay (simulated time / speedup factor)
        time.sleep(real_time_step)  # Real-time sleep based on speedup
        current_time += time_step

    print(f"\n✓ Simulation complete at t={current_time}s")

    # Save the live plot
    base_directory = Path(experimental_parameters["base_directory"])
    base_directory.mkdir(parents=True, exist_ok=True)
    plot_path = base_directory / f"realtime_uvvis_iteration_{iteration_num}.png"
    plt.savefig(plot_path, dpi=300, bbox_inches="tight")
    print(f"Saved real-time plot to {plot_path}")
    plt.close(fig)
    plt.ioff()  # Disable interactive mode

    # Convert to DataFrame
    data = pd.DataFrame(collected_data)

    # Calculate average absorbances from last 10 measurements (or all if less)
    n_avg = min(10, len(data))
    avg_abs_409 = data["Absorbance_409nm"].iloc[-n_avg:].mean()
    avg_abs_506 = data["Absorbance_506nm"].iloc[-n_avg:].mean()

    # Calculate percent yield (simplified - product/total)
    total_signal = avg_abs_409 + avg_abs_506
    percent_yield = (avg_abs_506 / total_signal * 100) if total_signal > 0 else 0.0

    # Calculate throughput (nmol/min)
    throughput = reactor_concentration_uM * flow_rate / 1000.0

    # Save results
    now = time.strftime("%Y-%m-%d %H:%M:%S")
    append_results_func(
        csv_path,
        {
            "iteration": iteration_num,
            "flow_rate": flow_rate,
            "concentration": concentration,
            "reactor_concentration_uM": reactor_concentration_uM,
            "temperature": temperature,
            "co_solvent": co_solvent,
            "co_solvent_volume": co_solvent_volume,
            "target_volume": "",
            "reactant_wavelength": experimental_parameters.get(
                "reactant_wavelength", ""
            ),
            "product_wavelength": experimental_parameters.get("product_wavelength", ""),
            "average_absorbance_reactant": round(avg_abs_409, 4),
            "average_absorbance_product": round(avg_abs_506, 4),
            "percent_yield": round(percent_yield, 2),
            "throughput_nmol_per_min": round(throughput, 2),
            "timestamp": now,
            "status": "completed",
            "error_message": "",
        },
    )

    # Update summary plots after each iteration
    print("\nUpdating optimization summary plots...")
    try:
        plot_bo_results(csv_path, str(base_directory))
        plot_absorbances_progress(csv_path, str(base_directory))
        print("✓ Summary plots updated\n")
    except Exception as e:
        print(f"⚠ Could not update summary plots: {e}\n")

    return percent_yield, throughput
