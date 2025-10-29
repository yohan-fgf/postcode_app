import pandas as pd
import folium

# === CONFIG ===
CSV_FILE = "data.csv"                 # Your CSV with postcode,count
POSTCODE_FILE = "aus_postcodes_full.csv"  # Full postcode coordinates: postcode,latitude,longitude
MAP_FILE = "aus_postcode_map.html"    # Output HTML file

# === LOAD USER CSV ===
df = pd.read_csv(CSV_FILE)
if "postcode" not in df.columns or "count" not in df.columns:
    raise ValueError("CSV must have 'postcode' and 'count' columns")

df["postcode"] = df["postcode"].astype(str)

# === LOAD FULL POSTCODE COORDINATES ===
postcode_coords = pd.read_csv(POSTCODE_FILE)
postcode_coords["postcode"] = postcode_coords["postcode"].astype(str)

# Join on postcode
merged = df.merge(postcode_coords, on="postcode", how="left")

missing = merged[merged["latitude"].isna()]
if not missing.empty:
    print(f"⚠️ Warning: {len(missing)} postcodes not found in the full list:")
    print(missing["postcode"].tolist())

merged = merged.dropna(subset=["latitude", "longitude"])

# === CREATE FOLIUM MAP ===
# Center map roughly in Australia
aus_map = folium.Map(location=[-25, 135], zoom_start=4)

# Add circle markers
for _, row in merged.iterrows():
    folium.CircleMarker(
        location=[row["latitude"], row["longitude"]],
        radius=5 + row["count"],  # size proportional to count
        color="red",
        fill=True,
        fill_opacity=0.6,
        popup=f"Postcode: {row['postcode']}<br>Count: {row['count']}"
    ).add_to(aus_map)

# Save map to HTML
aus_map.save(MAP_FILE)
print(f"Map saved to {MAP_FILE}. Open it in your browser to view.")
