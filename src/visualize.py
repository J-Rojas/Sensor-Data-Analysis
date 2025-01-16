import pandas as pd
from src.utils import (
    CSVColumns
)
from pathlib import Path
import matplotlib.pyplot as plt
from src.detector import read_data

def plot_charts(name: str, df: pd.DataFrame, takeoff_ind: int, save_func=lambda fig, name: fig.savefig(f"plots/plot_{name}.png",  bbox_inches='tight')):

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

    # Adjust layout for better spacing
    plt.tight_layout()

    save_func(fig, name)

    plt.close(fig)  # Close the figure to avoid display in the notebook

if __name__ == "__main__":
    output_file_path = "output.txt"

    df = pd.read_csv(output_file_path, header=None)
    for (row_idx, row) in df.iterrows():
        takeoff_df, runways = read_data(Path(f"data/cessna_182t/{row[0]}"))

        takeoff_ind = row[2]
        plot_charts(row[0], takeoff_df, takeoff_ind)
