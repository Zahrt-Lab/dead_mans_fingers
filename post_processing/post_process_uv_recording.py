def post_process_uv_recording(
    flow_rate: int,
    target_volume: int,
    uv_vis_absorbance_over_time_csv_file: str,
    *,
    baseline_points: int = 10,
) -> pd.DataFrame:
    """
    The role of this script is to run post-processing to extract all the points
    after the target volume is reached

    parameters:
     -flow_rate: volume of fluid exiting the pumps at a given time period
     -target_volume: target volume to reach after our reactor bed has experienced
      3-5 residence times
     -uv_vis_absorbance_over_time_csv_file:
    return:
     -uv_vis_recording_after_target_volume
    """

    time_target_volume_is_reached = time_to_reach_target_volume(
        flow_rate, target_volume
    )
    uv_vis_recording = pd.read_csv(uv_vis_absorbance_over_time_csv_file)

    if "Time(s)" not in uv_vis_recording.columns:
        raise ValueError(
            f"Expected a Time(s) column in {uv_vis_absorbance_over_time_csv_file}"
        )

    absorbance_columns = [
        absorbance_column for absorbance_column in uv_vis_recording.columns if absorbance_column != "Time(s)"
    ]

    # Baseline-correct all absorbance columns (everything except Time)
    for absorbance_column in absorbance_columns:
        absorbance_pd_series = pd.to_numeric(uv_vis_recording[absorbance_column], errors="coerce")
        baseline_shift = min(len(absorbance_pd_series), baseline_points)
        if baseline_shift == 0:
            continue
        absorbance_baseline = absorbance_pd_series.iloc[:baseline_shift].mean()
        uv_vis_recording[absorbance_column] = absorbance_pd_series - absorbance_baseline

    # This performs the filtering to only keep time points after the target volume is reached
    uv_vis_recording_after_target_volume = uv_vis_recording[
        uv_vis_recording["Time(s)"] >= time_target_volume_is_reached
    ].reset_index(drop=True)

    base, ext = os.path.splitext(uv_vis_absorbance_over_time_csv_file)
    uv_vis_recording_baseline_corrected_filename = f"{base}_baseline_corrected{ext}"
    uv_vis_recording_baseline_corrected_after_target_volume_filename = f"{base}_post_processed{ext}"

    uv_vis_recording.to_csv(
        uv_vis_recording_baseline_corrected_filename, index=False
    )
    uv_vis_recording_after_target_volume.to_csv(
        uv_vis_recording_baseline_corrected_after_target_volume_filename, index=False
    )

    return uv_vis_recording_after_target_volume
