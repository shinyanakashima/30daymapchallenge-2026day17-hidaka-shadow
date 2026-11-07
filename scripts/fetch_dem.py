"""Download GSI DEM10B elevation tiles (dem_png, zoom 12) and build a mosaic.

Source: Geospatial Information Authority of Japan (国土地理院), elevation tiles.
"""
import io
import math
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor

import numpy as np
from PIL import Image

from common import CACHE, WORK, Z, TILE, DEM_BOUNDS, lonlat_to_px

URL = "https://cyberjapandata.gsi.go.jp/xyz/dem_png/{z}/{x}/{y}.png"


def fetch(tx, ty):
    path = CACHE / f"{Z}_{tx}_{ty}.png"
    if path.exists():
        return path
    for i in range(5):
        try:
            req = urllib.request.Request(URL.format(z=Z, x=tx, y=ty),
                                         headers={"User-Agent": "hidaka-shadow/1.0"})
            with urllib.request.urlopen(req, timeout=30) as r:
                data = r.read()
            path.write_bytes(data)
            return path
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
            time.sleep(2 ** i)
        except Exception:
            time.sleep(2 ** i)
    raise RuntimeError(f"failed {tx},{ty}")


def decode(path):
    a = np.asarray(Image.open(path).convert("RGB")).astype(np.int64)
    v = (a[..., 0] << 16) + (a[..., 1] << 8) + a[..., 2]
    h = np.where(v < 2 ** 23, v, v - 2 ** 24).astype(np.float32) * 0.01
    h[v == 2 ** 23] = np.nan
    return h


def main():
    CACHE.mkdir(parents=True, exist_ok=True)
    WORK.mkdir(parents=True, exist_ok=True)
    w, s, e, n = DEM_BOUNDS
    x0, y0 = lonlat_to_px(w, n)
    x1, y1 = lonlat_to_px(e, s)
    tx0, ty0 = int(x0 // TILE), int(y0 // TILE)
    tx1, ty1 = int(x1 // TILE), int(y1 // TILE)
    tiles = [(tx, ty) for ty in range(ty0, ty1 + 1) for tx in range(tx0, tx1 + 1)]
    print(f"{len(tiles)} tiles")
    with ThreadPoolExecutor(6) as ex:
        paths = list(ex.map(lambda t: fetch(*t), tiles))
    H = (ty1 - ty0 + 1) * TILE
    W = (tx1 - tx0 + 1) * TILE
    dem = np.full((H, W), np.nan, np.float32)
    for (tx, ty), p in zip(tiles, paths):
        if p is None:
            continue
        r, c = (ty - ty0) * TILE, (tx - tx0) * TILE
        dem[r:r + TILE, c:c + TILE] = decode(p)
    np.save(WORK / "dem.npy", dem)
    np.save(WORK / "dem_origin.npy", np.array([tx0 * TILE, ty0 * TILE], np.float64))
    print("mosaic", dem.shape, "max", np.nanmax(dem), "nan share", np.isnan(dem).mean())


if __name__ == "__main__":
    main()
