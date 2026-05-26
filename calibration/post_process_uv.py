''' This script is responsible for post-process the UV data, getting the last 30 seconds of the recording.
'''

import pandas as pd

def post_process_uv_data(uv_data_dir_path: str) -> pd.DataFrame:
       
        # Put the UV data into a dataframe
        uv_vis_recording_df = pd.read_csv(uv_data_dir_path)
        #Select only the last minute of the recording for post-processing
        max_time = uv_vis_recording_df["Time(s)"].max()
        uv_vis_recording_post_processing_df = uv_vis_recording_df[
            uv_vis_recording_df["Time(s)"] >= max_time - 30
        ] 
        return uv_vis_recording_post_processing_df