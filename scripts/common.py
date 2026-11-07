"""Shared constants and Web Mercator helpers."""
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CACHE = ROOT / "data" / "cache"
WORK = ROOT / "data" / "work"
SITE_DATA = ROOT / "site" / "data"

Z = 12            # GSI DEM10B tiles at zoom 12: about 28 m per pixel at 43°N
TILE = 256

# Terrain used for the horizon search (wider than the map so that
# rays up to 150 km toward the west and north-west stay on real terrain).
DEM_BOUNDS = (141.6, 41.9, 143.85, 43.9)   # W, S, E, N
# Area shown on the map and evaluated as observer points.
MAP_BOUNDS = (142.4, 42.2, 143.8, 43.4)

OBS_STEP = 7      # observer grid = every 7th DEM pixel (about 195 m)
HS_STEP = 3       # hillshade image = every 3rd DEM pixel (about 85 m)

AZ_MIN, AZ_MAX = 180, 310   # degrees, 1° step
MAX_DIST = 150_000.0        # m
REFRACTION_K = 0.13
EARTH_R = 6_371_000.0
EYE_HEIGHT = 1.5            # m above ground

TZ = "Asia/Tokyo"
DATES = {
    "winter": "2026-12-22",
    "equinox": "2026-03-20",
    "summer": "2026-06-21",
    "today": "2026-11-07",
}
WINDOW_MIN = 90


def lonlat_to_px(lon, lat, z=Z):
    n = TILE * 2 ** z
    x = (lon + 180.0) / 360.0 * n
    s = math.sin(math.radians(lat))
    y = (0.5 - math.log((1 + s) / (1 - s)) / (4 * math.pi)) * n
    return x, y


def px_to_lonlat(x, y, z=Z):
    n = TILE * 2 ** z
    lon = x / n * 360.0 - 180.0
    lat = math.degrees(math.atan(math.sinh(math.pi * (1 - 2 * y / n))))
    return lon, lat


def equator_px_m(z=Z):
    return 2 * math.pi * 6378137.0 / (TILE * 2 ** z)
