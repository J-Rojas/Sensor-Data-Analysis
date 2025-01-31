import json
import pathlib
from shapely import contains
from shapely.geometry import Point, Polygon, shape
from typing import Optional

ASSET_FILEPATH = (
    pathlib.Path(__file__).parent.parent / "data" / "geometry" / "runways.geojson"
)

def load_airport_runways(
    airportId: str,
) -> list[tuple[Polygon, float]]:
    """
    Load the airport's runways and return polygons of the boundaries, along with the
    elevation of the airport in feet MSL
    """
    with open(ASSET_FILEPATH, "r") as f:
        features = json.load(f)["features"]

        retval = []

        for feat in features:
            if feat["properties"]["airportId"] == airportId:
                retval.append((shape(feat["geometry"]), feat["properties"]["elevationFtMSL"])) #type: ignore

        return retval

def find_index_of_first_true(lst):
    return next((i for i, x in enumerate(lst) if x), -1)

def get_points_near(center: Point, radius: float, points: list[Point]) -> list[Point]:
    return [x for x in points if center.distance(x) < radius]

def on_runway(lat: float, long: float, runways: tuple[Polygon, float] | list[tuple[Polygon, float]]) -> int:

    """
    Returns the runway id of the intersecting runway, otherwise -1
    """

    if type(runways) == list:
        return find_index_of_first_true([runway[0].contains(Point(long, lat)) for runway in runways])

    runway: Polygon = runways[0] # type: ignore
    return 0 if runway.contains(Point(long, lat)) else -1
