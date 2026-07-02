'''
This module contains functions for plotting the results of the analysis.
It contains the functions to plot the pareto front and the individual variables vs yield and throughput.
It plots the absorbance values vs time for each iteration. To do that, it iterates over folders inside the data folder and looks for the UV_detection.csv files.
It also plots the hypervolume improvement, which shows how the hypervolume of the Pareto front evolves over iterations.
'''
import os

import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path
import numpy as np


def plot_pareto_front(df, save_path=None):
    """
    Plot the Pareto front of the results.

    Args:
        df: DataFrame containing the results with 'percent_yield' and 'throughput' columns
        save_path: Optional path to save the figure
    """

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.scatter(df['percent_yield'], df['throughput_nmol_per_min'], c='blue', label='Results')
    ax.set_xlabel('Percent Yield (%)')
    ax.set_ylabel('Throughput (units/time)')
    ax.set_title('Pareto Front')
    ax.legend()
    ax.grid(True)

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Saved Pareto front plot to {save_path}")


def plot_variable_vs_objective(df, save_path=None):
    """
    Plot all variables (flow_rate, reactor_concentration_uM, temperature, co_solvent_dilution_factor) against an objective (percent_yield or throughput_nmol_per_min).

    Args:
        df: DataFrame containing the results
        variable: The variable to plot on the x-axis
        objective: The objective to plot on the y-axis ('percent_yield' or 'throughput')
        save_path: Optional path to save the figure
    """

    variables = ['flow_rate', 'reactor_concentration_uM', 'temperature', 'co_solvent_dilution_factor']
    objectives = ['percent_yield', 'throughput_nmol_per_min']

    for variable in variables:
        for objective in objectives:
            fig, ax = plt.subplots(figsize=(8, 6))
            ax.scatter(df[variable], df[objective], c='green', label=f'{variable} vs {objective}')
            ax.set_xlabel(variable)
            ax.set_ylabel(objective)
            ax.set_title(f'{variable} vs {objective}')
            try:
                # Fit a linear regression line
                # fit a linear regression line
                m, b = np.polyfit(df[variable], df[objective], 1)
                ax.plot(df[variable], m * df[variable] + b, c='red', linestyle='--', label=f'Linear fit: y = {m:.2f}x + {b:.2f}')
                # Calculate and display the R-squared value
                correlation_matrix = np.corrcoef(df[variable], df[objective])
                correlation_xy = correlation_matrix[0, 1]
                r_squared = correlation_xy**2
                # Display the fit equation and R-squared value on the plot
                ax.text(0.05, 0.90, f'Fit: y = {m:.2f}x + {b:.2f}', transform=ax.transAxes, fontsize=12, verticalalignment='top')
                ax.text(0.05, 0.95, f'$R^2 = {r_squared:.3f}$', transform=ax.transAxes, fontsize=12, verticalalignment='top')
            except Exception as e:
                print(f"Could not fit a linear regression line for {variable} vs {objective}: {e}")


            save_file_name = f"{variable}_vs_{objective}.png"
            if save_path:
                full_save_path = Path(save_path) / save_file_name
                plt.savefig(full_save_path, dpi=300, bbox_inches='tight')
                print(f"Saved {variable} vs {objective} plot to {full_save_path}")
    ax.legend()
    ax.grid(True)

def plot_absorbance_vs_time(df, iteration, save_path=None):
    """
    Plot absorbance vs time for both wavelengths.

    Args:
        df: DataFrame with Time(s), and absorbance colums for all wavelengths
        iteration: Iteration number for title
        save_path: Optional path to save the figure
    """
    fig, ax = plt.subplots(figsize=(10, 6))

    for i in range(1, len(df.columns)):
        wavelength = df.columns[i]
        ax.plot(
            df["Time(s)"],
            df[wavelength],
            label=f"{wavelength}",
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

def iterate_over_folders_and_plot_absorbance(data_folder, save_folder):
    """
    Recursively searches for UV_detection.csv files and plots each one.

    Args:
        data_folder (str): Root folder to search.
        save_folder (str): Folder where plots will be saved.
    """
    iteration = 1

    for root, _, files in os.walk(data_folder):
        if "UV_detection.csv" in files:
            csv_path = os.path.join(root, "UV_detection.csv")

            df = pd.read_csv(csv_path)

            save_path = os.path.join(
                save_folder,
                f"absorbance_vs_time_iteration_{iteration}.png"
            )

            plot_absorbance_vs_time(df, iteration, save_path)

            iteration += 1

def plot_hypervolume_improvement(df, save_path=None):
    """
    Plot the hypervolume improvement over iterations.

    Args:
        df: DataFrame containing the results with 'iteration' and 'hypervolume' columns
        save_path: Optional path to save the figure
    """

    fig, ax = plt.subplots(figsize=(8, 6))
    try:
        ax.plot(df['iteration'], df['hypervolume_no_prediction'], marker='o', linestyle='-', color='purple', label='Hypervolume without Prediction')
    except KeyError:
        print("Column 'hypervolume_no_prediction' not found in DataFrame. Skipping this plot.")
    try:
        ax.plot(df['iteration'], df['hypervolume_with_prediction'], marker='o', linestyle='-', color='orange', label='Hypervolume with Prediction')
    except KeyError:
        print("Column 'hypervolume_with_prediction' not found in DataFrame. Skipping this plot.")
    ax.set_xlabel('Iteration')
    ax.set_ylabel('Hypervolume')
    ax.set_title('Hypervolume Improvement Over Iterations')
    ax.grid(True)
    ax.legend()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Saved hypervolume improvement plot to {save_path}")

# csv_file_path = Path(r"G:\\My Drive\\Chenoweth Lab\\Projects\Automated photoflow reactor\\Results\Book1_Experiment61\Book1_Experiment61\\xylopyridine_analog_1\bo_campaign\\run_001\BO_Results_xylopyridine_analog_1_results.csv")
# save_file_path = Path(r"G:\\My Drive\\Chenoweth Lab\\Projects\Automated photoflow reactor\\Results\Book1_Experiment61\Book1_Experiment61\\xylopyridine_analog_1\bo_campaign\\run_001\\plots\\pareto_front_plot.png")
# os.makedirs(save_file_path.parent, exist_ok=True)
# abs_file_path = Path(r"G:\\My Drive\\Chenoweth Lab\\Projects\Automated photoflow reactor\\Results\Book1_Experiment61\Book1_Experiment61\\xylopyridine_analog_1\bo_campaign\\run_001\\Experimental_Log\\2026_06_29\\2026_06_29_09-49-23_Experimental_Log\\UV_detection.csv")

# df = pd.read_csv(csv_file_path)
# df_abs = pd.read_csv(abs_file_path)

# plot_pareto_front(df, save_file_path)
# plot_variable_vs_objective(df, save_file_path)
# iterate_over_folders_and_plot_absorbance(data_folder=csv_file_path.parent, save_folder=save_file_path.parent)