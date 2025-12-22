import csv
import os


def append_bayesian_experimental_results(
    bayesian_optimization_csv_path: str, results: dict
) -> None:
    """
    Append one result row to the Bayesian Optimization code; write header if file is new/empty.

    parameters:
     -bayesian_optimization_csv_path: Name of the file location path and file name
     -results: Results of the optimization which will be appended to this file
    return:
     -None
    """

    file_exists = os.path.exists(bayesian_optimization_csv_path)
    # define a stable column order
    column_names = [
        "iteration",
        "flow_rate",
        "concentration",
        "reactor_concentration_uM",
        "temperature",
        "co_solvent",
        "co_solvent_volume",
        "target_volume",
        "reactant_wavelength",
        "product_wavelength",
        "average_absorbance_reactant",
        "average_absorbance_product",
        "percent_yield",
        "throughput_nmol_per_min",
        "timestamp",
        "status",
        "error_message",
    ]
    with open(
        bayesian_optimization_csv_path, "a", newline="", encoding="utf-8"
    ) as bayesian_optimization_file:
        writer = csv.DictWriter(bayesian_optimization_file, fieldnames=column_names)
        if not file_exists or os.path.getsize(bayesian_optimization_csv_path) == 0:
            writer.writeheader()
        writer.writerow(results)
        bayesian_optimization_file.flush()
        os.fsync(
            bayesian_optimization_file.fileno()
        )  # ensure it hits disk (useful on Windows)


# ---------------- Iteration counter for filenames ----------------
iteration = {
    "iteration #": 0,
    "last_temperature": None,
    "volume_stock_solution1": None,
    "volume_stock_solution2": None,
    "volume_stock_solution3": None,
}
