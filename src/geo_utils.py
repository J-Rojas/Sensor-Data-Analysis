import json
import pathlib
from shapely.geometry import Point, Polygon, shape
from typing import Optional

ASSET_FILEPATH = (
    pathlib.Path(__file__).parent.parent / "data" / "geometry" / "airports.geojson"
)


def load_airport_runways(
    airportId: str = "KSQL",
) -> Optional[tuple[list[Polygon], float]]:
    """
    Load the airport's runways and return polygons of the boundaries, along with the
    elevation of the airport in feet MSL
    """
    with open(ASSET_FILEPATH, "r") as f:
        features = json.load(f)["features"]

        for feat in features:
            if feat["properties"]["airportId"] == airportId:
                return shape(feat["geometry"]), feat["properties"]["elevationFtMSL"]

    print(f"No runways found for airport {airportId}")
    return None


def on_runway(point: Point, runway: Polygon) -> bool:
    return runway.contains(point)
