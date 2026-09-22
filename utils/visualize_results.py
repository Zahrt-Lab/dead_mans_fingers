# ------------------------------------------------------------------------------
# Software: dead_mans_fingers
# Copyright (c) 2026 Zahrt Research Group
#
# Contributions by Scott Laverty and Joao Albuquerque are acknowledged.
#
# Licensed under the MIT License. See the LICENSE file in the repository root.
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


def plot_absorbances_progress(csv_path: str):
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
