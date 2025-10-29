import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt

# === CONFIG ===
CSV_FILE = "data.csv"                 # Your CSV with postcode,count
POSTCODE_FILE = "aus_postcodes_full.csv"  # Full postcode coordinates: postcode,latitude,longitude
DOT_SCALE = 50                         # Adjust dot size scaling

# === LOAD USER CSV ===
df = pd.read_csv(CSV_FILE)
if "postcode" not in df.columns or "count" not in df.columns:
    raise ValueError("CSV must have 'postcode' and 'count' columns")

df["postcode"] = df["postcode"].astype(str)

# === LOAD FULL POSTCODE COORDINATES ===
postcode_coords = pd.read_csv(POSTCODE_FILE)
postcode_coords["postcode"] = postcode_coords["postcode"].astype(str)

# Join on postcode
merged = df.merge(postcode_coords, left_on="postcode", right_on="postcode", how="left")

missing = merged[merged["latitude"].isna()]
if not missing.empty:
    print(f"⚠️ Warning: {len(missing)} postcodes not found in the full list:")
    print(missing["postcode"].tolist())

# Drop missing postcodes
merged = merged.dropna(subset=["latitude", "longitude"])

# === LOAD AUSTRALIA MAP (GeoJSON online) ===
url = "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_110m_admin_0_countries.geojson"
world = gpd.read_file(url)
aus = world[world["ADMIN"] == "Australia"]

# === PLOT MAP ===
fig, ax = plt.subplots(figsize=(10, 10))
aus.plot(ax=ax, color="lightgray", edgecolor="black")

sizes = merged["count"] * DOT_SCALE
ax.scatter(merged["longitude"], merged["latitude"], s=sizes, color="red", alpha=0.6, edgecolors="k")

plt.title("Australian Postcode Counts", fontsize=16)
plt.xlabel("Longitude")
plt.ylabel("Latitude")
plt.tight_layout()
plt.show()
