import pandas as pd
import folium
from folium import Map, Element

# === CONFIG ===
CSV_FILE = "ndis_data.csv"
POSTCODE_FILE = "aus_postcodes_full.csv"
MAP_FILE = "ndis_leads_map.html"

# === LOAD USER CSV ===
df = pd.read_csv(CSV_FILE)
df["postcode"] = df["postcode"].astype(str)

# === AGGREGATE DUPLICATE POSTCODES (in case of repeats) ===
df = df.groupby("postcode", as_index=False)["count"].sum()

# === LOAD FULL POSTCODE COORDINATES ===
postcode_coords = pd.read_csv(POSTCODE_FILE)
postcode_coords["postcode"] = postcode_coords["postcode"].astype(str)

# Keep only one entry per postcode
postcode_coords = postcode_coords.drop_duplicates(subset=["postcode"])

# Merge user data with coordinates
merged = df.merge(postcode_coords, on="postcode", how="left")

missing = merged[merged["latitude"].isna()]
if not missing.empty:
    print(f"⚠️ Warning: {len(missing)} postcodes not found in the full list:")
    print(missing["postcode"].tolist())

merged = merged.dropna(subset=["latitude", "longitude"])

# === CREATE FOLIUM MAP ===
aus_map = Map(location=[-25, 135], zoom_start=4)

# Add circle markers with color coding
for _, row in merged.iterrows():
    if row["count"] == 1:
        color = "green"
    elif row["count"] == 2:
        color = "blue"
    else:
        color = "red"
    
    folium.CircleMarker(
        location=[row["latitude"], row["longitude"]],
        radius=5 + row["count"],
        color=color,
        fill=True,
        fill_opacity=0.6,
        popup=f"Postcode: {row['postcode']}<br>Count: {row['count']}"
    ).add_to(aus_map)

# === ADD A TITLE TO THE PAGE ===
title_html = """
     <h3 align="center" style="font-size:24px"><b>NDIS Leads</b></h3>
     """
aus_map.get_root().html.add_child(Element(title_html))

# === SAVE MAP ===
aus_map.save(MAP_FILE)
print(f"Map saved to {MAP_FILE}. Open it in your browser to view.")
