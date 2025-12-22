import pandas as pd


def average_absorbance(
    uv_vis_absorbance_over_time_df: pd.DataFrame,
    wavelength: float,
) -> float:
    """
    Returns the average absorbance at a specific wavelength of light,
    meant to be performed after target volume is reached

    parameters:
     -uv_vis_absorbance_over_time_df: This is the UV_VIS data recorded in the form of a dataframe
     -wavelength: This is the measured wavelength that will be averaged over
    return:
     -average_absorbance_recorded: Absorbance at the specified wavelenght after the
     UV-VIS results level off
    """

    # Ensure we treat the wavelength as string since column headers are strings
    wavelength_column = str(wavelength)

    if wavelength_column not in uv_vis_absorbance_over_time_df.columns:
        raise ValueError(
            f"Wavelength {wavelength_column} not found in CSV headers: "
            f"{list(uv_vis_absorbance_over_time_df.columns)}"
        )

    average_absorbance_recorded = uv_vis_absorbance_over_time_df[
        wavelength_column
    ].mean()

    return average_absorbance_recorded
