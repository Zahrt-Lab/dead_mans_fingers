# ------------------------------------------------------------------------------
# Software: dead_mans_fingers
# Copyright (c) 2026 Andrew Zahrt
#
# Contributions by Scott Laverty and Joao Albuquerque are acknowledged.
#
# Licensed under the MIT License. See the LICENSE file in the repository root.
# ------------------------------------------------------------------------------
'''
This is the entry point for the analysis. It is responsible to handle the argument parser and call the appropriate functions to plot the results.
'''
import argparse
import os
from pathlib import Path
import pandas as pd
from analysis.plot_results import plot_pareto_front, plot_variable_vs_objective, iterate_over_folders_and_plot_absorbance, plot_hypervolume_improvement, plot_pareto_front_with_color_iteration, plot_parallel_coordinate_plot, plot_correlation_heat_map, plot_pair_plot
from analysis.print_results import print_flow_rate_iterations

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Analysis of the results of the bayesian optimization campaign")
    parser.add_argument("csv_dir_path", help="Path to the directory containing the CSV files with the results of the bayesian optimization campaign")
    parser.add_argument(
        "--save-dir-path",
        type=str,
        default=None,
        help="Path to save the plots (default: None, plots will be shown but not saved)",
    )
    parser.add_argument(
        "--yield-point",
        type=float,
        default=None,
        help="Yield point to plot (default: 1.0)",
    )

    parser.add_argument(
        "--throughput-point",
        type=float,
        default=None,
        help="Throughput point to plot (default: 1.0)",
    )

    parser.add_argument(
        "--trade-off-yield",
        type=float,
        default=None,
        help="Yield point for the trade-off plot (default: 1.0)",
    )

    parser.add_argument(
        "--trade-off-throughput",
        type=float,
        default=None,
        help="Throughput point for the trade-off plot (default: 1.0)",
    )

    return parser.parse_args()

def main():
    args = parse_args()
    csv_dir_path = Path(args.csv_dir_path)
    save_dir_path = args.save_dir_path
    if save_dir_path is not None:
        save_dir_path = Path(save_dir_path)
        print(f"Using provided save directory path: {save_dir_path}")
    else:
        save_dir_path = csv_dir_path / "publication_plots"
        print(f"No save directory path provided. Using default: {save_dir_path}")

    if not csv_dir_path.exists():
        raise FileNotFoundError(f"The specified CSV directory path does not exist: {csv_dir_path}")

    # Create the save directory if it doesn't exist
    if not save_dir_path.exists():
        os.makedirs(save_dir_path)

    csv_file_path = next(csv_dir_path.glob("BO_Results_*_results.csv"), None)

    if csv_file_path is None:
        raise FileNotFoundError("No BO results file found.")
    
    # Read the CSV file into a DataFrame
    df = pd.read_csv(csv_file_path)
    plot_save_dir = save_dir_path / "plots"
    if not plot_save_dir.exists():
        os.makedirs(plot_save_dir)
    pareto_plot_path = plot_save_dir / "pareto_front.png"

    batch_point = (args.yield_point, args.throughput_point)
    tradeoff_point = (args.trade_off_yield, args.trade_off_throughput)

    # Plot the Pareto front and variable vs objective plots
    #plot_pareto_front(df, pareto_plot_path)
    plot_pareto_front_with_color_iteration(df, plot_save_dir / "pareto_front_with_color_iteration.png", batch_point=batch_point, tradeoff_point=tradeoff_point)
    plot_parallel_coordinate_plot(df, plot_save_dir / "parallel_coordinate_plot.png")
    #plot_correlation_heat_map(df, plot_save_dir / "correlation_heatmap.png")
    #plot_pair_plot(df, plot_save_dir / "pair_plot.png")
    #plot_variable_vs_objective(df, plot_save_dir)

    #Plot hypervolume improvement
    hypervolume_plot_path = csv_dir_path / "hypervolume_results.csv"
    hypervolume_save_path = plot_save_dir / "hypervolume_improvement.png"
    if hypervolume_plot_path.exists():
        df_hv = pd.read_csv(hypervolume_plot_path)
        plot_hypervolume_improvement(df_hv, hypervolume_save_path)
    else:
        print(f"No hypervolume results file found at {hypervolume_plot_path}")
    
    # Iterate over folders and plot absorbance vs time
    #iterate_over_folders_and_plot_absorbance(data_folder=csv_dir_path, save_folder=plot_save_dir)

    # Print the flow rate iterations to a CSV file
    csv_save_dir = save_dir_path / "table_results"
    #print_flow_rate_iterations(csv_dir_path, csv_save_dir)

if __name__ == "__main__":
    main()