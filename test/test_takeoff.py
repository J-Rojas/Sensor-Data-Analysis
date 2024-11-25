#
# Copyright: Jose Rojas, 2024
#

import csv
from pathlib import Path
from utils import CSVColumns, create_timestamp
from takeoff_detector import read_data, GROUND_SPEED_TAKEOFF_THRESHOLD, ENGINE_SPEED_TAKEOFF_THRESHOLD
import numpy as np
import math

ALTITUDE_KERNEL = [1., 0, 0, 0, 0, 0, 0, 0, -1.0]

def test_takeoff_detection():
    # load output file
    data_dir = Path(__file__).parent / ".." / "data" / "cessna_182t" / ""
    with open('output.txt') as fp:
        reader = csv.reader(fp, delimiter=',', quotechar='|')
        for row in reader:
            filename = row[0]
            timestamp = float(row[1].strip()) if row[1].strip() != 'None' else None

            df = read_data(Path(data_dir / filename))

            # find where the airplane leaves the ground
            altitude_delta = np.convolve(df[CSVColumns.AltB].transpose().to_numpy(), ALTITUDE_KERNEL, 'same')
            non_zero_ground_speed = df[CSVColumns.GndSpd].transpose().to_numpy() > GROUND_SPEED_TAKEOFF_THRESHOLD
            engine_rpm_reached = df[CSVColumns.E1_RPM].transpose().to_numpy() > ENGINE_SPEED_TAKEOFF_THRESHOLD

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

            ind_where = np.where((altitude_delta > 100) & non_zero_ground_speed)
            speed_where = np.where(np.diff(non_zero_ground_speed, prepend=False))[0]
            engine_where = np.where(np.diff(engine_rpm_reached, prepend=False))[0]

            #print(filename)

            if len(ind_where[0]) > 0:
                leave_ground_indx = ind_where[0][0]

                #print(leave_ground_indx)

                #print(engine_where)
                #print(speed_where[speed_where < leave_ground_indx])
                #print(engine_where[engine_where < leave_ground_indx])

                # find the first rising edge of either the speed and engine threshold's before the plane gets off the ground
                if len(speed_where[speed_where < leave_ground_indx]) > 0 or len(engine_where[engine_where < leave_ground_indx]) > 0:
                    takeoff_test_indx = min(
                        speed_where[speed_where < leave_ground_indx].max() if len(speed_where) > 0 else 100000,
                        engine_where[engine_where < leave_ground_indx].max() if len(engine_where)> 0 else 100000
                    )
                else:
                    # there was never a proper take off
                    takeoff_test_indx = -1

                leave_ground_timestamp = create_timestamp(
                    df[CSVColumns.LocalDate].iloc[leave_ground_indx],
                    df[CSVColumns.LocalTime].iloc[leave_ground_indx],
                    df[CSVColumns.UTCOffset].iloc[leave_ground_indx]
                )

                if takeoff_test_indx != -1:
                    print(takeoff_indx, takeoff_test_indx)
                    # test the take off index from the detection algo matches the test's proposed take off index
                    assert takeoff_test_indx == takeoff_indx
                    # test that the first time the plane gets in the air is within 60 seconds after the takeoff initiation
                    assert (leave_ground_timestamp > timestamp) and (leave_ground_timestamp - timestamp) < 60.0
                    # test the plane has reached the necessary ground speed or engine speed
                    assert df[CSVColumns.GndSpd].iloc[takeoff_indx] > GROUND_SPEED_TAKEOFF_THRESHOLD or df[CSVColumns.E1_RPM].iloc[takeoff_indx] > ENGINE_SPEED_TAKEOFF_THRESHOLD
                else:
                    assert timestamp == None
            else:
                assert timestamp == None

test_takeoff_detection()