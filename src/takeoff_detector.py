import pandas as pd
from pathlib import Path
from shapely import Point, Polygon
import sys

from utils import (
    create_timestamp,
    CSVColumns,
    low_pass_filter,
    moving_average_filter,
    plot_flight,
)


def get_filepaths() -> list[Path]:
    data_dir = Path(__file__) / ".." / "data" / "cessna_182t"
    data_files = data_dir.glob("*.csv")
    return list(data_files)


def read_data(filepath: Path) -> pd.DataFrame:
    columns = [
        CSVColumns.LocalDate,
        CSVColumns.LocalTime,
        CSVColumns.UTCOffset,
        CSVColumns.Latitude,
        CSVColumns.Longitude,
    ]

    df = pd.read_csv(filepath, usecols=columns)

    # Smooth the speed and engine rpm values
    df[[CSVColumns.VSpd, CSVColumns.E1_RPM]] = moving_average_filter(
        df[[CSVColumns.VSpd, CSVColumns.E1_RPM]], window_size=5
    )

    return df


def detect_valid_takeoff_timestamp(df: pd.DataFrame) -> float | None:
    takeoff_idx = 0
    for row_idx, row in df.iterrows():
        if row[CSVColumns.VSpd] > 25 and row[CSVColumns.E1_RPM] > 1200:
            takeoff_idx = row_idx
            break

    utc_timestamp = create_timestamp(
        df.iloc[takeoff_idx][CSVColumns.LocalDate],
        df.iloc[takeoff_idx][CSVColumns.LocalTime],
        df.iloc[takeoff_idx][CSVColumns.UTCOffset],
    )

    return utc_timestamp


def main(output_file_path: str):
    output_data = []

    data_filepaths = get_filepaths()
    for fp in data_filepaths:
        print(f"Reading {fp}...")
        df = read_data(fp)

        ts = detect_valid_takeoff_timestamp(df)

        output_data.append(f"{fp.name}, {ts}\n")

    with open(output_file_path, "w") as f:
        f.writelines(output_data)


if __name__ == "__main__":
    output_file_path = "output.txt"
    if len(sys.argv) > 1:
        output_file_path = sys.argv[1]

    main(output_file_path)
