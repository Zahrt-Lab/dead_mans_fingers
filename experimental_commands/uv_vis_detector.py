# Will create UV-detector object and return UV-VIS start time
def begin_uv_vis_measurement(
    output_directory: str,
    iter_index: int,
    *,
    baseline_intensity: int = 10000,
    integration_time: int = 60000,
    num_scans: int = 10,
    target_wavelengths: Tuple[float, float] = (409.0, 506.0),
    file_name: str = "Fluorescent_Bayesian_Optimization",
    measurement_interval: int = 5,
) -> Ocean_Optics_UV_vis:
    """
    The role of this script is to begin the UV measurements which will use the default
    parameters for this experiment

    parameters:
     - output_directory: The directory UV VIS file will be outputed to
     - iteration: What iteration of the Bayesian Optimization is being performed
     - baseline_intensity: Is the intensity reference for calibration
     - integration_time: exposure time in milliseconds for the spectrometer
     - num_scans: number of scans to perform to average the measurement
     - target_wavelengths: The target wavelengths to absorb
     - file_name: UV-VIS output
     - measurement_interval:
    return:
     - UV_VIS_detector_object: UV_VIS_detector python object
    """

    print(
        f"Initiatiating UV-VIS recording for Bayesian Optimization Iteration {iter_index}"
    )
    uv_vis_detector_object = Ocean_Optics_UV_vis(
        output_directory,
        baseline_intensity,
        integration_time,
        num_scans,
        target_wavelengths,
        save_file_path=f"{file_name}_iteration_{iter_index}.csv",
        measurement_interval=measurement_interval,
    )

    uv_vis_detector_object.initialize_Ocean_Optics_UV_VIS()
    uv_vis_detector_object.set_integration_time()
    uv_vis_detector_object.set_number_of_scans(num_scans)
    uv_vis_detector_object.set_measurement_interval(measurement_interval)

    # Our Blank and Dark UV spectrum will be loaded from here
    blank_path = Path(output_directory) / "blank_spectrum.csv"
    dark_path = Path(output_directory) / "dark_spectrum.csv"

    try:
        uv_vis_detector_object.load_blank_spectrum_from_csv(blank_path)
    except (FileNotFoundError, OSError, ValueError) as e:
        print(f"Was unable to successfully load blank spectrum file: {blank_path}")
        print(f"Error: {e}")

    try:
        uv_vis_detector_object.load_dark_spectrum_from_csv(dark_path)
    except (FileNotFoundError, OSError, ValueError) as e:
        print(f"Was unable to successfully load dark spectrum file: {dark_path}")
        print(f"Error: {e}")

    # This will begin the continous UV-measurements for this iteration of the Bayesian Optimization
    uv_vis_detector_object.start_continuous()
    return uv_vis_detector_object


def end_uv_vis_measurement(uv_vis_detector_object: Any) -> None:
    """
    Ends the UV-VIS recording

    return:
     - None
    """

    uv_vis_detector_object.stop_continuous()
