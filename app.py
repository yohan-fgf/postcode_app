import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter

# === CONFIG ===
CSV_FILE = "data.csv"   # your CSV file
DOT_SCALE = 50          # adjust dot scaling

# === LOAD CSV ===
df = pd.read_csv(CSV_FILE)

if "postcode" not in df.columns or "count" not in df.columns:
    raise ValueError("CSV must contain 'postcode' and 'count' columns")

print(f"Loaded {len(df)} rows from {CSV_FILE}")

# === GEOCODE POSTCODES ===
geolocator = Nominatim(user_agent="australia_postcode_mapper")
geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)

def get_lat_lon(postcode):
    location = geocode(f"{postcode}, Australia")
    if location:
        return pd.Series([location.latitude, location.longitude])
    else:
        print(f"⚠️ Could not locate postcode {postcode}")
        return pd.Series([None, None])

print("Geocoding postcodes (this may take a few minutes)...")
df[["lat", "lon"]] = df["postcode"].apply(get_lat_lon)
df = df.dropna(subset=["lat", "lon"])

# === LOAD AUSTRALIA MAP (from Natural Earth online) ===
url = "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_110m_admin_0_countries.geojson"
world = gpd.read_file(url)
aus = world[world["ADMIN"] == "Australia"]

# === PLOT MAP ===
fig, ax = plt.subplots(figsize=(10, 10))
aus.plot(ax=ax, color="lightgray", edgecolor="black")

sizes = df["count"] * DOT_SCALE
ax.scatter(df["lon"], df["lat"], s=sizes, color="red", alpha=0.6, edgecolors="k")

plt.title("Australian Postcode Counts", fontsize=16)
plt.xlabel("Longitude")
plt.ylabel("Latitude")
plt.tight_layout()
plt.show()
