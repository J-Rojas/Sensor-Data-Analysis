from datetime import datetime, timedelta
from matplotlib import pyplot as plt
import numpy as np
import pandas as pd
from shapely.geometry import Polygon, shape

DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
OFFSET_FORMAT = "%z"


class CSVColumns:
    LocalDate = "Lcl Date"
    LocalTime = "Lcl Time"
    UTCOffset = "UTCOfst"
    ActiveWaypoint = "AtvWpt"
    Latitude = "Latitude"
    Longitude = "Longitude"
    AltB = "AltB"
    BaroA = "BaroA"
    AltMSL = "AltMSL"
    OAT = "OAT"
    IAS = "IAS"
    GndSpd = "GndSpd"
    VSpd = "VSpd"
    Pitch = "Pitch"
    Roll = "Roll"
    LatAc = "LatAc"
    NormAc = "NormAc"
    HDG = "HDG"
    TRK = "TRK"
    volt1 = "volt1"
    volt2 = "volt2"
    amp1 = "amp1"
    amp2 = "amp2"
    FQtyL = "FQtyL"
    FQtyR = "FQtyR"
    E1_FFlow = "E1 FFlow"
    E1_OilT = "E1 OilT"
    E1_OilP = "E1 OilP"
    E1_MAP = "E1 MAP"
    E1_RPM = "E1 RPM"
    E1_CHT1 = "E1 CHT1"
    E1_CHT2 = "E1 CHT2"
    E1_CHT3 = "E1 CHT3"
    E1_CHT4 = "E1 CHT4"
    E1_CHT5 = "E1 CHT5"
    E1_CHT6 = "E1 CHT6"
    E1_EGT1 = "E1 EGT1"
    E1_EGT2 = "E1 EGT2"
    E1_EGT3 = "E1 EGT3"
    E1_EGT4 = "E1 EGT4"
    E1_EGT5 = "E1 EGT5"
    E1_EGT6 = "E1 EGT6"
    AltGPS = "AltGPS"
    TAS = "TAS"
    HSIS = "HSIS"
    CRS = "CRS"
    NAV1 = "NAV1"
    NAV2 = "NAV2"
    COM1 = "COM1"
    COM2 = "COM2"
    HCDI = "HCDI"
    VCDI = "VCDI"
    WndSpd = "WndSpd"
    WndDr = "WndDr"
    WptDst = "WptDst"
    WptBrg = "WptBrg"
    MagVar = "MagVar"
    AfcsOn = "AfcsOn"
    RollM = "RollM"
    PitchM = "PitchM"
    RollC = "RollC"
    PichC = "PichC"
    VSpdG = "VSpdG"
    GPSfix = "GPSfix"
    HAL = "HAL"
    VAL = "VAL"
    HPLwas = "HPLwas"
    HPLfd = "HPLfd"
    VPLwas = "VPLwas"


def create_timestamp(date: str, time: str, utc_offset: str) -> float:
    offset_dt = datetime.strptime(utc_offset, OFFSET_FORMAT)
    timestamp = datetime.strptime(f"{date} {time}", DATETIME_FORMAT)

    utc_timestamp = timestamp + timedelta(offset_dt.hour, offset_dt.minute)

    return utc_timestamp.timestamp()


def low_pass_filter(arr: np.ndarray, alpha: float) -> np.ndarray:
    """
    This is a simple discrete-time realization of a low-pass filter.

    Params:
        arr: (n,m) array of sensor values to filter. This function will filter along
            columns if the array is two dimensional
        alpha: Smoothing parameter. Higher alpha means more smoothing

    Returns:
        Smoothed array
    """
    smoothed = np.zeros_like(arr)
    smoothed[0] = alpha * arr[0]
    for i in range(1, arr.shape[0]):
        smoothed[i] = (1 - alpha) * smoothed[i - 1] + alpha * arr[i]

    return smoothed


def moving_average_filter(arr: np.ndarray, window_size: int) -> np.ndarray:
    """
    This is a simple moving average filter.

    Params:
        arr: 1D array of sensor values to filter.
        window_size: How many values to include in the average

    Returns:
        Smoothed array
    """
    kernel = 1 / window_size * np.ones(window_size)
    smoothed = np.convolve(arr, kernel)
    return smoothed


def plot_flight(df: pd.DataFrame, runways: list, filename: str):
    fig, ax = plt.subplots()

    # Show runway outlines
    for rw in runways:
        x, y = shape(rw["geometry"]).exterior.xy

        ax.plot(x, y, color="blue", linewidth=2, linestyle="-", label="Polygon")
        ax.fill(x, y, color="lightblue", alpha=0.5)

    # Plot flight

    # Save image
    plt.savefig(filename, format="png")
