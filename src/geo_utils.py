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


def on_runway(lat: float, long: float, runways: tuple[Polygon, float] | list[tuple[Polygon, float]]) -> bool:
    if type(runways) == list:
        return any([runway[0].contains(Point(long, lat)) for runway in runways])

    runway: Polygon = runways[0] # type: ignore
    return runway.contains(Point(long, lat))
