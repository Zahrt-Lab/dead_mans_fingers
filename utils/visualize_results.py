# ------------------------------------------------------------------------------
# Software: project_dead_mans_fingers
# Copyright: (C) 2025 by Professor Andrew Zahrt
# This software is the intellectual property of Professor Andrew Zahrt
# Contributions by graduate students Scott Laverty are acknowledged.
# All rights reserved.
# ------------------------------------------------------------------------------

"""
Visualization utilities for Bayesian optimization results.
"""

import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path


def plot_absorbance_time_series(
    data: pd.DataFrame, iteration: int, save_path: str = None
):
    """
    Plot absorbance vs time for both wavelengths.

    Args:
        data: DataFrame with Time_s, Absorbance_409nm, Absorbance_506nm
        iteration: Iteration number for title
        save_path: Optional path to save the figure
    """
    fig, ax = plt.subplots(figsize=(10, 6))

    ax.plot(
        data["Time_s"],
        data["Absorbance_409nm"],
        "b-",
        label="409 nm (Reactant)",
        linewidth=2,
    )
    ax.plot(
        data["Time_s"],
        data["Absorbance_506nm"],
        "r-",
        label="506 nm (Product)",
        linewidth=2,
    )

    ax.set_xlabel("Time (s)", fontsize=12)
    ax.set_ylabel("Absorbance", fontsize=12)
    ax.set_title(f"UV-Vis Absorbance vs Time - Iteration {iteration}", fontsize=14)
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches="tight")
        print(f"Saved plot to {save_path}")

    return fig


def plot_bo_results(csv_path: str, save_dir: str = None):
    """
    Plot Bayesian optimization results showing optimization progress.

    Args:
        csv_path: Path to the BO results CSV file
        save_dir: Optional directory to save plots
    """
    df = pd.read_csv(csv_path)

    if save_dir:
        save_dir = Path(save_dir)
        save_dir.mkdir(parents=True, exist_ok=True)

    # Create a figure with multiple subplots
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    # 1. Percent yield over iterations
    ax = axes[0, 0]
    ax.plot(df["iteration"], df["percent_yield"], "o-", color="blue", markersize=8)
    ax.set_xlabel("Iteration", fontsize=11)
    ax.set_ylabel("Percent Yield (%)", fontsize=11)
    ax.set_title("Percent Yield vs Iteration", fontsize=12)
    ax.grid(True, alpha=0.3)

    # 2. Throughput over iterations
    ax = axes[0, 1]
    ax.plot(
        df["iteration"], df["throughput_nmol_per_min"], "o-", color="red", markersize=8
    )
    ax.set_xlabel("Iteration", fontsize=11)
    ax.set_ylabel("Throughput (nmol/min)", fontsize=11)
    ax.set_title("Throughput vs Iteration", fontsize=12)
    ax.grid(True, alpha=0.3)

    # 3. Pareto front (yield vs throughput)
    ax = axes[1, 0]
    scatter = ax.scatter(
        df["throughput_nmol_per_min"],
        df["percent_yield"],
        c=df["iteration"],
        cmap="viridis",
        s=100,
        alpha=0.7,
    )
    ax.set_xlabel("Throughput (nmol/min)", fontsize=11)
    ax.set_ylabel("Percent Yield (%)", fontsize=11)
    ax.set_title("Pareto Front: Yield vs Throughput", fontsize=12)
    ax.grid(True, alpha=0.3)
    cbar = plt.colorbar(scatter, ax=ax)
    cbar.set_label("Iteration", fontsize=10)

    # 4. Parameter exploration (temperature vs flow rate, colored by yield)
    ax = axes[1, 1]
    scatter = ax.scatter(
        df["flow_rate"],
        df["temperature"],
        c=df["percent_yield"],
        cmap="RdYlGn",
        s=100,
        alpha=0.7,
    )
    ax.set_xlabel("Flow Rate (µL/min)", fontsize=11)
    ax.set_ylabel("Temperature (°C)", fontsize=11)
    ax.set_title("Parameter Space Exploration", fontsize=12)
    ax.grid(True, alpha=0.3)
    cbar = plt.colorbar(scatter, ax=ax)
    cbar.set_label("Percent Yield (%)", fontsize=10)

    plt.tight_layout()

    if save_dir:
        save_path = save_dir / "bo_optimization_summary.png"
        plt.savefig(save_path, dpi=300, bbox_inches="tight")
        print(f"Saved optimization summary to {save_path}")

    return fig


def plot_absorbances_progress(csv_path: str, save_dir: str = None):
    """
    Plot how absorbances evolve over iterations.

    Args:
        csv_path: Path to the BO results CSV file
        save_dir: Optional directory to save plots
    """
    df = pd.read_csv(csv_path)

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # Absorbance at 409 nm over iterations
    ax = axes[0]
    ax.plot(
        df["iteration"],
        df["average_absorbance_reactant"],
        "o-",
        color="blue",
        markersize=8,
    )
    ax.set_xlabel("Iteration", fontsize=11)
    ax.set_ylabel("Average Absorbance at 409 nm", fontsize=11)
    ax.set_title("Reactant Absorbance (409 nm) vs Iteration", fontsize=12)
    ax.grid(True, alpha=0.3)

    # Absorbance at 506 nm over iterations
    ax = axes[1]
    ax.plot(
        df["iteration"],
        df["average_absorbance_product"],
        "o-",
        color="red",
        markersize=8,
    )
    ax.set_xlabel("Iteration", fontsize=11)
    ax.set_ylabel("Average Absorbance at 506 nm", fontsize=11)
    ax.set_title("Product Absorbance (506 nm) vs Iteration", fontsize=12)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()

    if save_dir:
        save_dir = Path(save_dir)
        save_dir.mkdir(parents=True, exist_ok=True)
        save_path = save_dir / "absorbance_progress.png"
        plt.savefig(save_path, dpi=300, bbox_inches="tight")
        print(f"Saved absorbance progress to {save_path}")

    return fig


if __name__ == "__main__":
    # Example usage
    import sys

    if len(sys.argv) > 1:
        csv_file = sys.argv[1]
        save_directory = sys.argv[2] if len(sys.argv) > 2 else None

        print(f"Plotting results from {csv_file}")
        plot_bo_results(csv_file, save_directory)
        plot_absorbances_progress(csv_file, save_directory)
        plt.show()
    else:
        print("Usage: python visualize_results.py <csv_path> [save_directory]")
