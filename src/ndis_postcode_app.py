import pandas as pd
import folium
from folium import Element

# === CONFIG ===
CSV_FILE = "data/ndis_data.csv"  # your postcode + count file
POSTCODE_URL = "https://app.periscopedata.com/api/fivegoodfriends/chart/csv/4635b224-8c2f-10b1-e556-f4598753a7b5"
MAP_FILE = "output/ndis_leads_map.html"

# === LOAD USER CSV ===
df = pd.read_csv(CSV_FILE)
df["postcode"] = df["postcode"].astype(str)

# Aggregate duplicates (if any)
df = df.groupby("postcode", as_index=False)["count"].sum()

# === LOAD POSTCODE COORDINATES FROM URL ===
print("📥 Fetching postcode coordinates from Periscope Data URL...")
postcode_coords = pd.read_csv(POSTCODE_URL)
postcode_coords["postcode"] = postcode_coords["postcode"].astype(str)

# Try to identify latitude/longitude column names automatically
possible_lat = [c for c in postcode_coords.columns if "lat" in c.lower()]
possible_lon = [c for c in postcode_coords.columns if "lon" in c.lower() or "lng" in c.lower()]

if len(possible_lat) == 0 or len(possible_lon) == 0:
    raise ValueError("Could not find latitude/longitude columns in the Periscope CSV")

lat_col = possible_lat[0]
lon_col = possible_lon[0]

# Drop duplicates, just in case
postcode_coords = postcode_coords.drop_duplicates(subset=["postcode"])

# === MERGE USER COUNTS WITH COORDINATES ===
merged = df.merge(
    postcode_coords[["postcode", lat_col, lon_col]],
    on="postcode",
    how="left"
)

missing = merged[merged[lat_col].isna()]
if not missing.empty:
    print(f"⚠️ Warning: {len(missing)} postcodes not found in Periscope list:")
    print(missing["postcode"].tolist())

merged = merged.dropna(subset=[lat_col, lon_col])

# === CREATE MAP ===
aus_map = folium.Map(location=[-25, 135], zoom_start=4)

# Add circle markers
for _, row in merged.iterrows():
    if row["count"] == 1:
        color = "green"
    elif row["count"] == 2:
        color = "blue"
    else:
        color = "red"

    folium.CircleMarker(
        location=[row[lat_col], row[lon_col]],
        radius=5 + row["count"],
        color=color,
        fill=True,
        fill_opacity=0.6,
        popup=f"Postcode: {row['postcode']}<br>Count: {row['count']}"
    ).add_to(aus_map)

# === ADD TITLE ===
title_html = """
     <h3 align="center" style="font-size:24px"><b>NDIS leads</b></h3>
     """
aus_map.get_root().html.add_child(Element(title_html))

# === SAVE MAP ===
aus_map.save(MAP_FILE)
print(f"✅ Map saved to {MAP_FILE}. Open it in your browser to view.")
