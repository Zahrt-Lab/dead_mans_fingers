# ------------------------------------------------------------------------------
# Software: dead_mans_fingers
# Copyright (c) 2026 Zahrt Research Group
#
# Contributions by Scott Laverty and Joao Albuquerque are acknowledged.
#
# Licensed under the MIT License. See the LICENSE file in the repository root.
# ------------------------------------------------------------------------------

from pathlib import Path
import time
from typing import Optional

def get_latest_experimental_run_csv(
    base_path: Path,
    min_mtime: Optional[float] = None,
    timeout_seconds: float = 15.0,
    poll_interval_seconds: float = 0.5,
) -> str:
    """
    Retrieve the latest UV-VIS `UV_detection.csv` written under an
    AutoZahrt experimental log directory.

    AutoZahrt log layouts can vary by machine/configuration (e.g. date folders
    containing timestamped run folders). This function recursively scans for CSV
    files named `UV_detection.csv` and can optionally require files to be newer
    than ``min_mtime``.

    Parameters:
        base_path: Directory where AutoZahrt writes its timestamped log folders
        min_mtime: Optional minimum file modified time (POSIX timestamp) for
            qualifying CSV files
        timeout_seconds: Maximum time to wait for a qualifying CSV to appear
        poll_interval_seconds: Delay between retry scans while waiting

    Returns:
        str: Path to the latest UV-VIS `UV_detection.csv` file
    """
    base = Path(base_path)

    if not base.exists():
        raise FileNotFoundError(f"Output directory does not exist: {base}")
    if not base.is_dir():
        raise NotADirectoryError(f"Output path is not a directory: {base}")

    deadline = time.monotonic() + max(timeout_seconds, 0.0)
    sleep_seconds = max(poll_interval_seconds, 0.05)

    while True:
        csv_files = [p for p in base.rglob("UV_detection.csv") if p.is_file()]
        if min_mtime is not None:
            csv_files = [p for p in csv_files if p.stat().st_mtime >= min_mtime]

        if csv_files:
            latest_csv = max(csv_files, key=lambda f: f.stat().st_mtime)
            return str(latest_csv)

        if time.monotonic() >= deadline:
            break

        time.sleep(sleep_seconds)

    mtime_hint = ""
    if min_mtime is not None:
        mtime_hint = f" newer than {min_mtime:.3f}"

    raise FileNotFoundError(
        f"No UV_detection.csv files found in output_dir {base}{mtime_hint}"
    )
