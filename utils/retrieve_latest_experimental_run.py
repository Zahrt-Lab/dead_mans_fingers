from pathlib import Path


def get_latest_experimental_run_csv(base_path: Path) -> str:
    """
    Retrieve the UV-VIS CSV from the most recent AutoZahrt experimental log directory.

    AutoZahrt creates a timestamped subdirectory inside base_path for each run
    (e.g. {datetime}_Experimental_Log/). This function finds the most recently
    modified subdirectory, then returns the most recently modified CSV inside it.

    Parameters:
        base_path: Directory where AutoZahrt writes its timestamped log folders

    Returns:
        str: Path to the latest UV-VIS CSV file
    """
    base = Path(base_path)

    # Step 1: find the most recently modified subdirectory (the timestamped log dir)
    subdirs = [p for p in base.iterdir() if p.is_dir()]
    if not subdirs:
        raise FileNotFoundError(f"No subdirectories found in output_dir: {base}")
    latest_subdir = max(subdirs, key=lambda d: d.stat().st_mtime)

    # Step 2: find the most recently modified CSV inside that subdir
    csv_files = list(latest_subdir.glob("*.csv"))
    if not csv_files:
        raise FileNotFoundError(f"No CSV files found in latest log directory: {latest_subdir}")

    latest_csv = max(csv_files, key=lambda f: f.stat().st_mtime)
    return str(latest_csv)
