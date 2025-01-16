#
# Copyright: Jose Rojas, 2024
#

import csv
from pathlib import Path
from src.utils import CSVColumns, create_timestamp
from src.detector import read_data, GROUND_SPEED_TAKEOFF_THRESHOLD, ENGINE_SPEED_TAKEOFF_THRESHOLD, ALTITUDE_ERROR
from src.geo_utils import on_runway
from shapely import Polygon
import numpy as np
import pandas as pd

ALTITUDE_KERNEL = [1., 0, 0, 0, 0, 0, 0, 0, -1.0]

def determine_runway(df: pd.DataFrame, runways: list[tuple[Polygon, float]]):
    for row_ind, row in df.iterrows():
        for runway in runways:
            if on_runway(row[CSVColumns.Latitude], row[CSVColumns.Longitude], runway):
                return runway
    return None


def test_takeoff_detection():
    # load output file
    data_dir = Path(__file__).parent / ".." / "data" / "cessna_182t" / ""
    with open('output.txt') as fp:
        reader = csv.reader(fp, delimiter=',', quotechar='|')
        for row in reader:
            takeoff_test_indx = -1
            filename = row[0]
            timestamp = float(row[1].strip()) if row[1].strip() != 'None' else None

            df, runways = read_data(Path(data_dir / filename))

            # the correct airport runway must be determined
            runway = determine_runway(df, runways)
            elevation = runway[1] if runway else 0

            # add 'on runway' feature
            if runway is not None:
                df['on_runway'] = [on_runway(lat, long, runway) for lat, long in zip(df[CSVColumns.Latitude], df[CSVColumns.Longitude])]
            else:
                df['on_runway'] = [False] * df[CSVColumns.Latitude].size

            on_runway_true = df['on_runway']

            # find where the airplane leaves the ground
            altitude_on_ground = np.abs(df[CSVColumns.AltMSL].transpose().to_numpy() - elevation) < ALTITUDE_ERROR
            non_zero_ground_speed = (df[CSVColumns.GndSpd].transpose().to_numpy() > GROUND_SPEED_TAKEOFF_THRESHOLD) & on_runway_true & altitude_on_ground
            engine_rpm_reached = (df[CSVColumns.E1_RPM].transpose().to_numpy() > ENGINE_SPEED_TAKEOFF_THRESHOLD) & on_runway_true & altitude_on_ground

            def get_timestamp(item):
                _, row = item
                try:
                    return create_timestamp(
                        row[CSVColumns.LocalDate],
                        row[CSVColumns.LocalTime],
                        row[CSVColumns.UTCOffset]
                    ) == timestamp
                except Exception as e:
                    return False

            takeoff_indx = -1
            if timestamp != None:
                takeoff_indx = list(map(get_timestamp, df.iterrows())).index(True)

                assert(takeoff_indx >= 0)

            speed_where = np.where(np.diff(non_zero_ground_speed, prepend=False))[0]
            engine_where = np.where(np.diff(engine_rpm_reached, prepend=False))[0]

            # find the first rising edge of either the speed and engine threshold's before the plane gets off the ground
            if (len(speed_where) > 0 or len(engine_where) > 0):
                takeoff_test_indx = min(
                    speed_where.min() if len(speed_where) > 0 else 100000,
                    engine_where.min() if len(engine_where) > 0 else 100000
                )
            else:
                # there was never a proper take off
                takeoff_test_indx = -1

            if takeoff_test_indx != -1 and timestamp != None:
                print(takeoff_indx, takeoff_test_indx)
                # test the take off index from the detection algo matches the test's proposed take off index
                assert takeoff_test_indx == takeoff_indx
                # test the plane has reached the necessary ground speed or engine speed
                assert df[CSVColumns.GndSpd].iloc[takeoff_indx] > GROUND_SPEED_TAKEOFF_THRESHOLD or df[CSVColumns.E1_RPM].iloc[takeoff_indx] > ENGINE_SPEED_TAKEOFF_THRESHOLD
            else:
                assert timestamp == None

test_takeoff_detection()