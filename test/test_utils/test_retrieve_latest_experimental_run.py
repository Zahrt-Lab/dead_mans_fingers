# ------------------------------------------------------------------------------
# Software: dead_mans_fingers
# Copyright (c) 2026 Zahrt Research Group
#
# Contributions by Scott Laverty are acknowledged.
#
# Licensed under the MIT License. See the LICENSE file in the repository root.
# ------------------------------------------------------------------------------

"""
Test cases for utils/retrieve_latest_experimental_run.py
"""

import sys
import time
from pathlib import Path

import pytest

sys.path.append(str(Path(__file__).parent.parent.parent))

from utils.retrieve_latest_experimental_run import get_latest_experimental_run_csv


def test_get_latest_experimental_run_csv_finds_nested_latest_uv_detection(tmp_path):
    date_dir = tmp_path / "2026_04_23"
    run_dir_older = date_dir / "2026_04_23_11-00-09_Experimental_Log"
    run_dir_newer = date_dir / "2026_04_23_11-07-27_Experimental_Log"
    run_dir_older.mkdir(parents=True)
    run_dir_newer.mkdir(parents=True)

    older_csv = run_dir_older / "UV_detection.csv"
    newer_csv = run_dir_newer / "UV_detection.csv"
    older_csv.write_text("Time(s),409.0,506.0\n0,0.1,0.2\n", encoding="utf-8")
    time.sleep(0.01)
    newer_csv.write_text("Time(s),409.0,506.0\n0,0.3,0.4\n", encoding="utf-8")

    result = get_latest_experimental_run_csv(tmp_path)

    assert result == str(newer_csv)


def test_get_latest_experimental_run_csv_respects_min_mtime(tmp_path):
    run_dir = tmp_path / "2026_04_23" / "2026_04_23_11-07-27_Experimental_Log"
    run_dir.mkdir(parents=True)

    csv_file = run_dir / "UV_detection.csv"
    csv_file.write_text("Time(s),409.0,506.0\n0,0.3,0.4\n", encoding="utf-8")

    with pytest.raises(FileNotFoundError, match="newer than"):
        get_latest_experimental_run_csv(
            tmp_path,
            min_mtime=time.time() + 5.0,
            timeout_seconds=0.0,
        )


def test_get_latest_experimental_run_csv_prefers_uv_detection_name(tmp_path):
    run_dir = tmp_path / "2026_04_23" / "2026_04_23_17-53-21_Experimental_Log"
    run_dir.mkdir(parents=True)

    experimental_log = run_dir / "2026_04_23_17-53-21_Experimental_Log.csv"
    status_log = run_dir / "2026_04_23_17-53-21_Status_Log.csv"
    uv_detection = run_dir / "UV_detection.csv"

    uv_detection.write_text("Time(s),409.0,506.0\n0,0.1,0.2\n", encoding="utf-8")
    time.sleep(0.01)
    experimental_log.write_text("Time,Component,Action\n1,a,b\n", encoding="utf-8")
    time.sleep(0.01)
    status_log.write_text("Timestamp,Elapsed_Time_s\n2026-04-23,1\n", encoding="utf-8")

    result = get_latest_experimental_run_csv(tmp_path)

    assert result == str(uv_detection)


def test_get_latest_experimental_run_csv_raises_when_uv_detection_missing(tmp_path):
    run_dir = tmp_path / "2026_04_23" / "2026_04_23_17-53-21_Experimental_Log"
    run_dir.mkdir(parents=True)

    (run_dir / "2026_04_23_17-53-21_Experimental_Log.csv").write_text(
        "Time,Component,Action\n1,a,b\n", encoding="utf-8"
    )

    with pytest.raises(FileNotFoundError, match="No UV_detection.csv files found"):
        get_latest_experimental_run_csv(tmp_path, timeout_seconds=0.0)
