# ------------------------------------------------------------------------------
# Software: dead_mans_fingers
# Copyright (c) 2026 Zahrt Research Group
#
# Contributions by Scott Laverty and Joao Albuquerque are acknowledged.
#
# Licensed under the MIT License. See the LICENSE file in the repository root.
# ------------------------------------------------------------------------------

import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path

def plot_comparison(csv_file, output_directory):

    '''
    This fonction reads a csv file containing the first column as iteration and the other columns as different seeds
    used in different experiments. It plots all the seeds in the same graph and saves the plot in the specified output directory.
    '''
    # Ensure the output directory exists
    csv_file_path = Path(csv_file)
    output_directory_path = Path(output_directory)
    output_directory_path.mkdir(parents=True, exist_ok=True)

    # Read the CSV file into a DataFrame
    df = pd.read_csv(csv_file)

    # Create a plot comparing the two columns
    fig, ax = plt.subplots(figsize=(8, 6))
    seed_columns = df.columns[1:]  # Assuming the first column is an index or identifier
    first_column_name = df.columns[0]
    for column in seed_columns:
        ax.plot(df[first_column_name], df[column], label=column, marker='o', linestyle='-')
    ax.set_xlabel(first_column_name)
    ax.set_ylabel('Hypervolume')
    ax.set_title('Comparison of Hypervolume Across Different Seeds')
    ax.grid(True)
    ax.legend()
        
    # Save the plot to the specified output directory
    output_file_path = output_directory_path / "comparison_plot.png"
    plt.savefig(output_file_path)
    plt.close()

def plot_pareto_comparison(csv_file, output_directory):
    '''
    This function reads a csv file containing the first column as iteration and the other columns as 
    the yield and throughput of different seeds. It plots the points in the same chart, with different colors 
    for each seed, and earlier iterations are fainter than later iterations. It saves the plot in the specified output directory. 
    The first column is the iteration. The second column is yield and third is throughput for seed 1. The
    fourth column is yield and fifth is throughput for seed 2, and so on.
    '''
    # Ensure the output directory exists
    csv_file_path = Path(csv_file)
    output_directory_path = Path(output_directory)
    output_directory_path.mkdir(parents=True, exist_ok=True)

    # Read the CSV file into a DataFrame
    df = pd.read_csv(csv_file)

    # Create a plot comparing the two columns
    fig, ax = plt.subplots(figsize=(8, 6))
    first_column_name = df.columns[0]
    num_seeds = (len(df.columns) - 1) // 2  # Assuming each seed has two columns (yield and throughput)
    colors = ['blue', 'orange', 'green', 'red', 'purple', 'brown', 'pink', 'gray', 'olive', 'cyan']  # Extend this list if more seeds are used  
    for seed in range(num_seeds):
        yield_column = df.columns[1 + seed * 2]
        throughput_column = df.columns[2 + seed * 2]
        seed_label = df.columns[1 + seed * 2]
        for iteration in range(len(df)-1):
            alpha_value = (iteration + 1) / len(df)  # Fainter for earlier iterations
            ax.scatter(df[yield_column][iteration], df[throughput_column][iteration],                     
                       c=colors[seed], alpha=alpha_value,s=80, edgecolor='black', linewidth=0.5)
        alpha_value = 1.0  # Full opacity for the last iteration
        ax.scatter(df[yield_column].iloc[-1], df[throughput_column].iloc[-1], c=colors[seed], alpha=alpha_value, label=seed_label, s=80, edgecolor='black', linewidth=0.5)

    ax.set_xlabel('Yield')
    ax.set_ylabel('Throughput')
    ax.set_title('Pareto Comparison of Different Seeds')
    ax.grid(True)
    ax.legend()

    # Save the plot to the specified output directory
    output_file_path = output_directory_path / "pareto_comparison_plot.png"
    plt.savefig(output_file_path)
    plt.close()

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Plot comparison of hypervolume across different seeds.")
    parser.add_argument("csv_file", help="Path to the CSV file containing the data.")
    parser.add_argument("pareto_file", help="Path to the CSV file containing the pareto data.")
    parser.add_argument("output_directory", help="Directory to save the comparison plot.")
    args = parser.parse_args()

    plot_comparison(args.csv_file, args.output_directory)
    plot_pareto_comparison(args.pareto_file, args.output_directory)