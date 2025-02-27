import pandas as pd
from src.utils import (
    CSVColumns
)
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.lines as mlines
from src.detector import read_data
from src.geo_utils import get_points_near
import os
import io
import requests
import urllib.parse
import urllib.request
from PIL import Image as image_open
from shapely import Polygon, Point
from datetime import datetime
from IPython.display import Image, display

def plot_charts(name: str, df: pd.DataFrame, takeoff_ind: int, runway: tuple[Polygon, float]|None, save_func=lambda fig, name: fig.savefig(f"plots/plot_{name}.png",  bbox_inches='tight')):

    # Iterate through each row in the DataFrame
    # Create a new figure for each row
    fig, axes = plt.subplots(nrows=2, ncols=2, figsize=(12, 8))  # 2x2 grid of plots
    axes = axes.flatten()  # Flatten the axes array to make it easier to iterate over

    # Plot Ground Speed for this specific row
    axes[0].plot(df.index, df[CSVColumns.GndSpd], label="Ground Speed (Knots)")
    axes[0].set_title(f"Ground Speed Over Time")
    axes[0].set_xlabel("Time (Index)")
    axes[0].set_ylabel("Ground Speed (Knots)")
    # Add a dot at the takeoff moment (if found)
    if takeoff_ind != -1:
        axes[0].plot(df.index[takeoff_ind], df[CSVColumns.GndSpd][takeoff_ind], "bo", label='Takeoff Moment')
    axes[0].legend(loc='upper right')


    # Plot Engine RPM for this specific row
    axes[1].plot(df.index, df[CSVColumns.E1_RPM], label="Engine RPM", color="orange")
    axes[1].set_title(f"Engine RPM Over Time")
    axes[1].set_xlabel("Time (Index)")
    axes[1].set_ylabel("Engine RPM")

    if takeoff_ind != -1:
        axes[1].plot(df.index[takeoff_ind], df[CSVColumns.E1_RPM][takeoff_ind], "o", color="orange", label='Takeoff Moment')
    axes[1].legend(loc='upper right')  # Explicitly set the legend location

    # Plot Altitude for this specific row
    axes[2].plot(df.index, df[CSVColumns.AltMSL], label="Altitude (ft)", color="green")
    axes[2].set_title(f"Altitude Over Time")
    axes[2].set_xlabel("Time (Index)")
    axes[2].set_ylabel("Altitude (ft)")

    if takeoff_ind != -1:
        axes[2].plot(df.index[takeoff_ind], df[CSVColumns.AltMSL][takeoff_ind], "go", label='Takeoff Moment')
    axes[2].legend(loc='upper right')  # Explicitly set the legend location

    if runway:

        marker_data = None
        if takeoff_ind != -1:
            marker_data = {
                'location': f"{df[CSVColumns.Latitude][takeoff_ind]},{df[CSVColumns.Longitude][takeoff_ind]}",
                'color': "0xFF00FF",
                'label': ''
            }

        # Plot the flight, zooming into the runway
        runway_poly = runway[0]
        centroid = runway_poly.centroid
        gps_points = list(map(lambda x: Point(x[1], x[0]), zip(df[CSVColumns.Latitude], df[CSVColumns.Longitude])))[:takeoff_ind+200]
        points_near_centroid = get_points_near(centroid, 0.015, gps_points)[::5]

        flight_path_config = {
            "color": "0xFF00FF80",
            "points": points_near_centroid
        }

        url = generate_static_map_url(centroid.y, centroid.x, poly=[flight_path_config], marker_config=marker_data)

        # Open the URL and read the image
        with urllib.request.urlopen(url) as response:
            img_data = response.read()

        # Convert the response data to a Pillow Image
        img = image_open.open(io.BytesIO(img_data))

        axes[3].imshow(img)
        axes[3].set_title("Runway")
        axes[3].axis('off')

        # --- Add Legend to Subplot ---
        legend_patch = mpatches.Patch(color="magenta", label="flight path") # Create patch for THIS subplot
        marker_legend_line = mlines.Line2D([], [], color="magenta", marker='o', linestyle='None',
                                markersize=10, label="Takeoff Moment") # Line2D for marker representation

        axes[3].legend(handles=[legend_patch, marker_legend_line], labels=[legend_patch.get_label(), marker_legend_line.get_label()], loc='upper right', frameon=False) # Add legend to the AXES, remove frame

    # Adjust layout for better spacing
    plt.tight_layout()

    save_func(fig, name)

    plt.close(fig)  # Close the figure to avoid display in the notebook

def generate_static_map_url(center_lat, center_lng, zoom=15, size="600x400", map_type="satellite", poly:list[dict]|None=None, marker_config=None):
    base_url = "https://maps.googleapis.com/maps/api/staticmap"
    params = [
        ("center", f"{center_lat},{center_lng}"),
        ("zoom", zoom),
        ("size", size),
        ("maptype", map_type),
        ("key", os.getenv('GOOGLE_MAPS_API_KEY'))
    ]

    if marker_config and marker_config['location']:
        marker_style = f"color:{marker_config['color']}|size:3|label:{marker_config['label']}|"
        params.append(('markers', marker_style + marker_config['location']))

    query_string = urllib.parse.urlencode(
        params,
        safe="|:,",  # Do not URL-encode these characters
        quote_via=urllib.parse.quote
    )

    if poly:
        for pline in poly:
            color = pline['color']
            points = pline['points']
            polyl = f"color:{color}|weight:3|" + "|".join(list(map(lambda p: f"{p.y},{p.x}", points)))
            query_string += f"&path={polyl}"


    return f"{base_url}?{query_string}"

def display_static_map(url, size="400x400"):
    response = requests.get(url)
    if response.status_code == 200:
        display(Image(data=response.content, embed=True, format='png', width=int(size.split('x')[0]), height=int(size.split('x')[1])))
    else:
        print(f"Failed to retrieve the static map. Status code: {response.status_code}")

if __name__ == "__main__":
    output_file_path = "output.txt"

    df = pd.read_csv(output_file_path, header=None)
    for (row_idx, row) in df.iterrows():
        takeoff_df, runways = read_data(Path(f"data/cessna_182t/{row[0]}"))

        takeoff_ind = row[2]
        plot_charts(row[0], takeoff_df, runways[row[1]], takeoff_ind)
