#
# Copyright: Jose Rojas, 2024
#

import pandas as pd
from pathlib import Path
from shapely import Polygon, Point
from src.geo_utils import load_airport_runways, on_runway
import sys

VISUALIZE = True
GROUND_SPEED_TAKEOFF_THRESHOLD = 25
ENGINE_SPEED_PREFLIGHT_THRESHOLD = 1500
ENGINE_SPEED_TAKEOFF_THRESHOLD = 1200
ALTITUDE_ERROR = 50

from src.utils import (
    create_timestamp,
    CSVColumns,
    moving_average_filter
)


def get_filepaths() -> list[Path]:
    data_dir = Path(__file__).parent / ".." / "data" / "cessna_182t"
    data_files = data_dir.glob("*.csv")
    return list(data_files)


def read_data(filepath: Path) -> tuple[pd.DataFrame, list[tuple[Polygon, float]]]:
    columns = [
        CSVColumns.Latitude,
        CSVColumns.Longitude,
        CSVColumns.UTCOffset,
        CSVColumns.LocalDate,
        CSVColumns.LocalTime,
        CSVColumns.GndSpd,
        CSVColumns.E1_RPM,
        CSVColumns.AltMSL
    ]

    # the column header names are contained in the 2nd row of the file, thus header=1
    # the CSV file contains tabs and extra spaces to separates columns so a regex is required for the delimiter
    df = pd.read_csv(filepath, usecols=columns, header=1, delimiter=r',\s*', engine='python')

    # Smooth the speed, engine rpm, altimeter values
    for col in [CSVColumns.GndSpd, CSVColumns.E1_RPM, CSVColumns.AltMSL]:
        df_in = df[col].to_numpy().transpose()
        df_smoothed = moving_average_filter(
           df_in, window_size=5
        )
        # ensure the smoothed data is the same size as original data samples
        assert df_in.shape == df_smoothed.shape
        df[col] = pd.DataFrame(df_smoothed.transpose())

    # parse airport code
    airport_code = str(filepath).replace('.csv', '').split("_")[-1]

    # read the airport file
    runways = load_airport_runways(airport_code)

    return df, runways


def detect_valid_takeoff_timestamp(df: pd.DataFrame, runways: list[tuple[Polygon, float]]) -> tuple[float | None, int, int]:

    runway_id = -1
    takeoff_idx = -1
    elevation = runways[0][1]

    def on_ground_check(row_idx):
        return abs(row[CSVColumns.AltMSL] - elevation) < ALTITUDE_ERROR

    def check_on_runway(row):
        lng, lat = row[CSVColumns.Longitude], row[CSVColumns.Latitude]
        return on_runway(lat, lng, runways)

    for row_idx, row in df.iterrows():

         # Ensure row_idx is an integer index or position
        row_idx = int(row_idx) # type: ignore

        # test that the aircraft is on the ground (having measured the ground altitude at zero ground speed) AND
        # the plane is on the runway (by checking the runway geometry and current location) AND
        # the plane has reached either the takeoff ground speed or the engine RPM takeoff speed

        runway_id = check_on_runway(row)

        if on_ground_check(row_idx) and runway_id != -1 and \
            (row[CSVColumns.GndSpd] > GROUND_SPEED_TAKEOFF_THRESHOLD or row[CSVColumns.E1_RPM] > ENGINE_SPEED_TAKEOFF_THRESHOLD):
            takeoff_idx = row_idx
            break

    utc_timestamp = create_timestamp(
        str(df.iloc[takeoff_idx][CSVColumns.LocalDate]),
        str(df.iloc[takeoff_idx][CSVColumns.LocalTime]),
        str(df.iloc[takeoff_idx][CSVColumns.UTCOffset]),
    ) if takeoff_idx >= 0 else None

    return utc_timestamp, takeoff_idx, runway_id


def main(output_file_path: str):

    output_data = []

    data_filepaths = get_filepaths()

    for idx, fp in enumerate(data_filepaths):
        print(f"Reading {fp.name}...")

        df, runways = read_data(fp)
        if len(runways) > 0:
            ts, ts_ind, runway_id = detect_valid_takeoff_timestamp(df, runways)
        else:
            ts = 'None'
            ts_ind = -1
            runway_id = -1

        output_data.append(f"{fp.name}, {runway_id}, {ts}, {ts_ind}\n")

    with open(output_file_path, "w") as f:
        f.writelines(output_data)


if __name__ == "__main__":
    output_file_path = "output.txt"
    if len(sys.argv) > 1:
        output_file_path = sys.argv[1]

    main(output_file_path)
