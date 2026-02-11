import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import Point
from adjustText import adjust_text

try:
    df_raw = pd.read_csv("location_counts.csv")

    df = df_raw[(df_raw["Shown_On_Map"] == "Yes") & (df_raw["Latitude"].notna())].copy()

    if df.empty:
        print("No mappable locations found in the CSV.")
        exit()
except FileNotFoundError:
    print("Error: 'location_counts.csv' not found. Run the export script first.")
    exit()

geometry = [Point(xy) for xy in zip(df["Longitude"], df["Latitude"])]
gdf = gpd.GeoDataFrame(df, geometry=geometry)

# india map structure
india_geojson_url = "https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson"

try:
    india_map = gpd.read_file(india_geojson_url)

    fig, ax = plt.subplots(figsize=(15, 15))

    india_map.plot(ax=ax, color="#f4f4f4", edgecolor="#999999", linewidth=0.8)

    # Plot city
    sizes = df["Startup_Count"] * 10
    gdf.plot(
        ax=ax,
        markersize=sizes,
        color="#263FBA",
        alpha=0.6,
        edgecolor="#0E131F",
        linewidth=0.5,
    )

    texts = []
    for x, y, label, count in zip(
        df["Longitude"], df["Latitude"], df["Location"], df["Startup_Count"]
    ):
        label_text = f"{label} ({int(count)})"
        texts.append(
            plt.text(x, y, label_text, fontsize=9, weight="bold", color="#1a1a1a")
        )

    # adjust_text is used here to avoid two names overlapping
    adjust_text(
        texts,
        ax=ax,
        arrowprops=dict(arrowstyle="-", color="gray", lw=0.5),
        expand_points=(1.5, 1.5),
        force_points=(0.1, 0.2),
    )

    plt.title("Startup Count by Location in India", fontsize=18, pad=20, weight="bold")
    plt.axis("off")

    plt.savefig("india_startup_map.png", dpi=300, bbox_inches="tight")
    plt.show()
    print(f"Map created! Processed {len(df)} locations.")

except Exception as e:
    print(f"Error: {e}")
