# ------------------------------------------------------------------------------
# Software: dead_mans_fingers
# Copyright (c) 2026 Zahrt Research Group
#
# Contributions by Scott Laverty and Joao Albuquerque are acknowledged.
#
# Licensed under the MIT License. See the LICENSE file in the repository root.
# ------------------------------------------------------------------------------

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
import seaborn as sns


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
    ax.set_ylabel('Throughput (nmol/min)')
    ax.set_title('Pareto Front')
    ax.set_xlim(0, 100)  # Set x-axis limits from 0 to 100
    ax.set_ylim(0, df['throughput_nmol_per_min'].max() * 1.2)  # Set y-axis limits
    ax.legend()
    ax.grid(True)

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Saved Pareto front plot to {save_path}")

def plot_pareto_front_with_color_iteration(
    df,
    save_path=None,
    batch_point=None,
    tradeoff_point=None
):
    """
    Plot yield vs throughput with color indicating experimental iteration.

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame containing 'percent_yield',
        'throughput_nmol_per_min', and 'iteration'.

    save_path : str, optional
        Base path used to save PNG and PDF versions.

    batch_point : tuple, optional
        Batch reference point as (yield, throughput).
        Example: batch_point=(60, 1.5)
    """

    # Publication formatting
    plt.rcParams.update({
        'font.family': 'Arial',
        'font.size': 8,
        'axes.labelsize': 8,
        'xtick.labelsize': 7,
        'ytick.labelsize': 7,
        'axes.linewidth': 0.5,
        'xtick.major.width': 0.8,
        'ytick.major.width': 0.8,
        'xtick.major.size': 3,
        'ytick.major.size': 3,
    })

    fig, ax = plt.subplots(figsize=(3.3, 2.6))

    # Autonomous experiments
    scatter = ax.scatter(
        df['percent_yield'],
        df['throughput_nmol_per_min'],
        c=df['iteration'],
        cmap='Blues',
        s=28,
        edgecolor='black',
        linewidth=0.4,
        zorder=2,
        label='Optimization'
    )

    # Batch reference
    if batch_point[0] is not None:
        batch_yield, batch_throughput = batch_point

        ax.scatter(
            batch_yield,
            batch_throughput,
            marker='*',
            s=35,
            facecolor='maroon',
            edgecolor='black',
            linewidth=0.4,
            label='Batch',
            zorder=4
        )
    if tradeoff_point[0] is not None:
        tradeoff_yield, tradeoff_throughput = tradeoff_point

        ax.scatter(
            tradeoff_yield,
            tradeoff_throughput,
            marker='o',
            s=28,
            facecolor='orange',
            edgecolor='black',
            linewidth=0.4,
            zorder=5,
            label='Selected Trade-off',
        )

    # Axis labels
    ax.set_xlabel('Yield (%)')
    ax.set_ylabel(r'Throughput (nmol min$^{-1}$)')

    ax.set_xlim(-5, 105)

    # Determine y-axis limit including batch point
    max_throughput = df['throughput_nmol_per_min'].max()

    if batch_point is not None:
        max_throughput = max(max_throughput, batch_point[1])

    ax.set_ylim(-5, max_throughput * 1.10)

    # Iteration color bar
    cbar = fig.colorbar(
        scatter,
        ax=ax,
        pad=0.03,
        fraction=0.06
    )

    cbar.set_label('Iteration', fontsize=8)
    cbar.ax.tick_params(
        labelsize=7,
        width=0.8,
        length=3
    )

    # Only show legend if batch reference is included
    if batch_point is not None:
        ax.legend(
            frameon=True,
            fontsize=7,
            loc='best'
        )

    # Light grid
    ax.grid(
        True,
        linestyle=':',
        linewidth=0.5,
        alpha=0.5
    )

    fig.tight_layout()

    if save_path:
        fig.savefig(
            f'{save_path}.png',
            dpi=600,
            bbox_inches='tight'
        )

        fig.savefig(
            f'{save_path}.pdf',
            bbox_inches='tight'
        )

        print(
            f'Saved to {save_path}.png '
            f'and {save_path}.pdf'
        )

    return fig, ax

def plot_variable_vs_objective(df, save_path=None):
    """
    Plot all variables (flow_rate, reactor_concentration_uM, temperature, light_intensity) against an objective (percent_yield or throughput_nmol_per_min).

    Args:
        df: DataFrame containing the results
        variable: The variable to plot on the x-axis
        objective: The objective to plot on the y-axis ('percent_yield' or 'throughput')
        save_path: Optional path to save the figure
    """

    variables = ['flow_rate', 'reactor_concentration_uM', 'temperature', 'light_intensity']
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
    Plot hypervolume improvement over iterations.

    Args:
        df: DataFrame containing 'iteration' and
            'hypervolume_no_prediction' columns
        save_path: Optional base path to save PNG and PDF files
    """

    # Publication formatting
    # Publication formatting
    plt.rcParams.update({
        'font.family': 'Arial',
        'font.size': 8,
        'axes.labelsize': 8,
        'xtick.labelsize': 7,
        'ytick.labelsize': 7,
        'axes.linewidth': 0.5,
        'xtick.major.width': 0.8,
        'ytick.major.width': 0.8,
        'xtick.major.size': 3,
        'ytick.major.size': 3,
    })

    fig, ax = plt.subplots(figsize=(3.3, 2.6))

    try:
        ax.plot(
            df['iteration'],
            df['hypervolume_no_prediction'],
            marker='o',
            linestyle='-',
            markersize=4,
            linewidth=1.2,
            color='purple'
        )
    except KeyError:
        print(
            "Column 'hypervolume_no_prediction' "
            "not found in DataFrame."
        )
        return fig, ax

    ax.set_xlabel('Iteration')
    ax.set_ylabel('Hypervolume')

    ax.grid(
        True,
        linestyle=':',
        linewidth=0.5,
        alpha=0.5
    )

    fig.tight_layout()

    if save_path:
        fig.savefig(
            f'{save_path}.png',
            dpi=600,
            bbox_inches='tight'
        )

        fig.savefig(
            f'{save_path}.pdf',
            bbox_inches='tight'
        )

        print(
            f'Saved to {save_path}.png '
            f'and {save_path}.pdf'
        )

    return fig, ax

def plot_parallel_coordinate_plot(df, save_path=None):
    """
    Plot parallel coordinate plots for the optimization variables,
    colored by yield and throughput.

    Args:
        df: DataFrame containing the results
        save_path: Optional base path used to save PNG and PDF files
    """

    from pandas.plotting import parallel_coordinates
    from matplotlib import colormaps
    from matplotlib.colors import Normalize
    from matplotlib.cm import ScalarMappable
    from pathlib import Path

    # Publication formatting
    plt.rcParams.update({
        'font.family': 'Arial',
        'font.size': 8,
        'axes.labelsize': 8,
        'xtick.labelsize': 7,
        'ytick.labelsize': 7,
        'axes.linewidth': 0.5,
        'xtick.major.width': 0.8,
        'ytick.major.width': 0.8,
        'xtick.major.size': 3,
        'ytick.major.size': 3,
    })

    # Variables shown in the parallel coordinate plot
    cols = [
        'flow_rate',
        'reactor_concentration_uM',
        'temperature',
        'light_intensity'
    ]

    plot_df = df[cols + ['iteration']].copy()

    # Normalize each variable from 0 to 1
    for col in cols:
        plot_df[col] = (
            plot_df[col] - plot_df[col].min()
        ) / (
            plot_df[col].max() - plot_df[col].min()
        )

    # Dummy categorical column required by parallel_coordinates
    plot_df['iteration_label'] = plot_df['iteration'].astype(str)

    # Better display labels
    display_labels = [
        'Flow rate',
        'Concentration',
        'Temperature',
        'Light intensity'
    ]

    # ============================================================
    # Yield-colored plot
    # ============================================================

    color_by = 'percent_yield'

    cmap = colormaps['Blues']
    norm = Normalize(
        df[color_by].min(),
        df[color_by].max()
    )
    from matplotlib.colors import PowerNorm

    norm = PowerNorm(
        gamma=2.0,
        vmin=df[color_by].min(),
        vmax=df[color_by].max()
)
    yield_order = df.sort_values('percent_yield', ascending=True)

    yield_plot_df = plot_df.loc[yield_order.index]

    colors = [cmap(norm(v)) for v in yield_order['percent_yield']]

    fig, ax = plt.subplots(figsize=(3.3, 2.6))

    parallel_coordinates(
        yield_plot_df[cols + ['iteration_label']],
        class_column='iteration_label',
        color=colors,
        linewidth=1.0,
        alpha=0.75,
        ax=ax
    )

    ax.legend_.remove()

    ax.set_ylabel('Normalized value')
    ax.set_xticklabels(display_labels)

    sm = ScalarMappable(
        norm=norm,
        cmap=cmap
    )
    sm.set_array([])

    cbar = fig.colorbar(
        sm,
        ax=ax,
        pad=0.03,
        fraction=0.06
    )

    cbar.set_label('Yield (%)', fontsize=8)
    cbar.ax.tick_params(
        labelsize=7,
        width=0.8,
        length=3
    )

    fig.tight_layout()

    if save_path:
        save_path = Path(save_path)

        yield_base = (
            save_path.parent /
            f'{save_path.stem}_yield'
        )

        fig.savefig(
            f'{yield_base}.png',
            dpi=600,
            bbox_inches='tight'
        )

        fig.savefig(
            f'{yield_base}.pdf',
            bbox_inches='tight'
        )

        print(
            f'Saved to {yield_base}.png '
            f'and {yield_base}.pdf'
        )

    # ============================================================
    # Throughput-colored plot
    # ============================================================

    color_by = 'throughput_nmol_per_min'

    cmap = colormaps['Blues']
    norm = Normalize(
        df[color_by].min(),
        df[color_by].max()
    )

    from matplotlib.colors import PowerNorm

    norm = PowerNorm(
        gamma=2.0,
        vmin=df[color_by].min(),
        vmax=df[color_by].max()
)

    throughput_order = df.sort_values(
        'throughput_nmol_per_min',
        ascending=True
    )

    throughput_plot_df = plot_df.loc[throughput_order.index]

    colors = [
        cmap(norm(v))
        for v in throughput_order['throughput_nmol_per_min']
    ]
    fig, ax = plt.subplots(figsize=(3.3, 2.6))

    parallel_coordinates(
        throughput_plot_df[cols + ['iteration_label']],
        class_column='iteration_label',
        color=colors,
        linewidth=1.0,
        alpha=0.75,
        ax=ax
    )

    ax.legend_.remove()

    ax.set_ylabel('Normalized value')
    ax.set_xticklabels(display_labels)

    sm = ScalarMappable(
        norm=norm,
        cmap=cmap
    )
    sm.set_array([])

    cbar = fig.colorbar(
        sm,
        ax=ax,
        pad=0.03,
        fraction=0.06
    )

    cbar.set_label(
        r'Throughput (nmol min$^{-1}$)',
        fontsize=8
    )

    cbar.ax.tick_params(
        labelsize=7,
        width=0.8,
        length=3
    )

    fig.tight_layout()

    if save_path:
        throughput_base = (
            save_path.parent /
            f'{save_path.stem}_throughput'
        )

        fig.savefig(
            f'{throughput_base}.png',
            dpi=600,
            bbox_inches='tight'
        )

        fig.savefig(
            f'{throughput_base}.pdf',
            bbox_inches='tight'
        )

        print(
            f'Saved to {throughput_base}.png '
            f'and {throughput_base}.pdf'
        )

def plot_correlation_heat_map(df, save_path=None):
    """
    Plot a correlation heatmap for the variables and objectives.

    Args:
        df: DataFrame containing the results
        save_path: Optional path to save the figure
    """

    # Select only the relevant columns for the correlation heatmap
    cols = ['flow_rate', 'reactor_concentration_uM', 'temperature', 'light_intensity', 'percent_yield', 'throughput_nmol_per_min']
    corr_df = df[cols].copy()

    # Calculate the correlation matrix
    corr_matrix = corr_df.corr()

    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(corr_matrix, annot=True, fmt=".2f", cmap="coolwarm", cbar=True, ax=ax)
    ax.set_title("Correlation Heatmap of Variables and Objectives")

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Saved correlation heatmap to {save_path}")

def plot_pair_plot(df, save_path=None):
    """
    Plot a pair plot for the variables and objectives.

    Args:
        df: DataFrame containing the results
        save_path: Optional path to save the figure
    """

    # Select only the relevant columns for the pair plot
    cols = ['flow_rate', 'reactor_concentration_uM', 'temperature', 'light_intensity', 'percent_yield', 'throughput_nmol_per_min']
    pair_df = df[cols].copy()

    # Create the pair plot
    sns.pairplot(pair_df)
    plt.suptitle("Pair Plot of Variables and Objectives", y=1.02)

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Saved pair plot to {save_path}")

# csv_file_path = Path(r"G:\\My Drive\\Chenoweth Lab\\Projects\Automated photoflow reactor\\Results\Book1_Experiment61\Book1_Experiment61\\xylopyridine_analog_1\bo_campaign\\run_001\BO_Results_xylopyridine_analog_1_results.csv")
# save_file_path = Path(r"G:\\My Drive\\Chenoweth Lab\\Projects\Automated photoflow reactor\\Results\Book1_Experiment61\Book1_Experiment61\\xylopyridine_analog_1\bo_campaign\\run_001\\plots\\pareto_front_plot.png")
# os.makedirs(save_file_path.parent, exist_ok=True)
# abs_file_path = Path(r"G:\\My Drive\\Chenoweth Lab\\Projects\Automated photoflow reactor\\Results\Book1_Experiment61\Book1_Experiment61\\xylopyridine_analog_1\bo_campaign\\run_001\\Experimental_Log\\2026_06_29\\2026_06_29_09-49-23_Experimental_Log\\UV_detection.csv")

# df = pd.read_csv(csv_file_path)
# df_abs = pd.read_csv(abs_file_path)

# plot_pareto_front(df, save_file_path)
# plot_variable_vs_objective(df, save_file_path)
# iterate_over_folders_and_plot_absorbance(data_folder=csv_file_path.parent, save_folder=save_file_path.parent)