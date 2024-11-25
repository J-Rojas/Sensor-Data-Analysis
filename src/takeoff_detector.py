#
# Copyright: Jose Rojas, 2024
#

import pandas as pd
from pathlib import Path
from shapely import Point, Polygon
import sys

VISUALIZE = False
GROUND_SPEED_TAKEOFF_THRESHOLD = 25
ENGINE_SPEED_PREFLIGHT_THRESHOLD = 1500
ENGINE_SPEED_TAKEOFF_THRESHOLD = 1200
ALTITUDE_ERROR = 50

from utils import (
    create_timestamp,
    CSVColumns,
    low_pass_filter,
    moving_average_filter,
    plot_flight,
    SpikeDetect
)


def get_filepaths() -> list[Path]:
    data_dir = Path(__file__).parent / ".." / "data" / "cessna_182t"
    data_files = data_dir.glob("*.csv")
    return list(data_files)


def read_data(filepath: Path) -> pd.DataFrame:
    columns = [
        CSVColumns.LocalDate,
        CSVColumns.LocalTime,
        CSVColumns.UTCOffset,
        CSVColumns.Latitude,
        CSVColumns.Longitude,
        CSVColumns.GndSpd,
        CSVColumns.E1_RPM,
        CSVColumns.AltGPS,
        CSVColumns.AltB,
        CSVColumns.HDG,
        CSVColumns.Pitch,
        CSVColumns.Roll,
        CSVColumns.AltMSL,
        CSVColumns.IAS
    ]

    # the column header names are contained in the 2nd row of the file, thus header=1
    # the CSV file contains tabs and extra spaces to separates columns so a regex is required for the delimiter
    df = pd.read_csv(filepath, usecols=columns, header=1, delimiter=r',\s*')

    # Smooth the speed, engine rpm, altimeter values
    for col in [CSVColumns.GndSpd, CSVColumns.E1_RPM, CSVColumns.AltB]:
        df_in = df[col].to_numpy().transpose()
        df_smoothed = moving_average_filter(
           df_in, window_size=10 # increased the moving average window to further reduce noise based on empirical analysis of the dataset
        )
        # ensure the smoothed data is the same size as original data samples
        assert df_in.shape == df_smoothed.shape
        df[col] = pd.DataFrame(df_smoothed.transpose())

    # low pass filter to smooth out engine rpm noise that can cause some false positives
    df[CSVColumns.E1_RPM] = low_pass_filter(df[CSVColumns.E1_RPM], alpha=0.9)

    return df


def detect_valid_takeoff_timestamp(df: pd.DataFrame) -> tuple[float | None, int]:

    takeoff_idx = -1
    last_on_ground_speed_ind = -1
    last_alt_at_zero = 0
    spike_detect = SpikeDetect()

    def on_ground_check(row_idx):
        return last_on_ground_speed_ind != -1 and last_on_ground_speed_ind <= row_idx and row[CSVColumns.AltB] < last_alt_at_zero + ALTITUDE_ERROR

    def has_done_preflight_engine_check(row_idx):
        return spike_detect.rise_idx != -1 and spike_detect.fall_idx != -1 and spike_detect.rise_idx < row_idx and spike_detect.fall_idx < row_idx

    for row_idx, row in df.iterrows():

        # check the altitude and preflight engine check to detect presence near runway before take-off
        if row[CSVColumns.GndSpd] == 0.0:
            last_on_ground_speed_ind = row_idx
            last_alt_at_zero = row[CSVColumns.AltB]
            spike_detect.detect(row_idx, row[CSVColumns.E1_RPM], ENGINE_SPEED_PREFLIGHT_THRESHOLD, ENGINE_SPEED_TAKEOFF_THRESHOLD)

        # test that the plane is on the ground (having measured the ground altitude at zero ground speed) AND
        # the plane is on the runway (the 'preflight engine check' RPM spike has occurred off the runway just prior to takeoff) AND
        # the plane has reached either the takeoff ground speed or the engine RPM takeoff speed
        #
        if on_ground_check(row_idx) and \
           has_done_preflight_engine_check(row_idx) and \
            (row[CSVColumns.GndSpd] > GROUND_SPEED_TAKEOFF_THRESHOLD or row[CSVColumns.E1_RPM] > ENGINE_SPEED_TAKEOFF_THRESHOLD):
            takeoff_idx = row_idx
            break

    utc_timestamp = create_timestamp(
        df.iloc[takeoff_idx][CSVColumns.LocalDate],
        df.iloc[takeoff_idx][CSVColumns.LocalTime],
        df.iloc[takeoff_idx][CSVColumns.UTCOffset],
    ) if takeoff_idx >= 0 else 'None'

    return utc_timestamp, takeoff_idx


def main(output_file_path: str):

    output_data = []

    data_filepaths = get_filepaths()
    print(data_filepaths)
    for fp in data_filepaths:
        print(f"Reading {fp}...")

        df = read_data(fp)
        ts, ts_ind = detect_valid_takeoff_timestamp(df)

        if VISUALIZE:

            # Visualize with wandb
            import wandb

            # start a new wandb run to track this script
            wandb.init(
                # set the wandb project where this run will be logged
                project="Beacon-AI-Test",
                name=f"run-{fp}",
                reinit=True  # Ensure new runs can be started in the same script
            )

            for index, row in df.iterrows():
                row_data = row.to_dict()  # Convert the row to a dictionary

                if ts_ind == index:
                    row_data['Timestamp'] = ts

                wandb.log(
                    row_data,  # Log all data including the timestamp
                    step=index  # Use the DataFrame index as the time step
                )

        output_data.append(f"{fp.name}, {ts}\n")

    with open(output_file_path, "w") as f:
        f.writelines(output_data)


if __name__ == "__main__":
    output_file_path = "output.txt"
    if len(sys.argv) > 1:
        output_file_path = sys.argv[1]

    main(output_file_path)
