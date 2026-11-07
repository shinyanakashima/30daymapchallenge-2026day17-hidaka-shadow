"""Horizon angles, terrain sunsets and shadow frames for the Hidaka shadow clock.

Steps
1. Horizon angle for every observer point (about 195 m grid) toward
   azimuths 180-310° (1° step), marching over the 28 m DEM up to 150 km.
   Earth curvature and atmospheric refraction (k = 0.13) are corrected.
2. Sun position from pvlib (NREL SPA, apparent elevation includes refraction).
3. Flat-horizon sunset: true elevation of the sun's centre = -0.833°.
   Terrain sunset: last moment before that when the sun's upper limb
   (apparent elevation + 0.267°) is above the terrain horizon.
4. Shadow frames: every minute in the 90 minutes before Obihiro's flat sunset.
"""
import json
import math
import time

import numpy as np
import pandas as pd
import pvlib
from numba import njit, prange
from PIL import Image

from common import (WORK, SITE_DATA, Z, MAP_BOUNDS, OBS_STEP, HS_STEP, AZ_MIN, AZ_MAX,
                    MAX_DIST, REFRACTION_K, EARTH_R, EYE_HEIGHT, TZ, DATES, WINDOW_MIN,
                    lonlat_to_px, px_to_lonlat, equator_px_m)

SEMIDIAM = 0.2666
FLAT_H = -0.833
SAMPLE_S = 20
WINDOW_START = "11:30"

TOWNS = [
    ("obihiro", "Obihiro", "帯広", 42.9236, 143.1966),
    ("memuro", "Memuro", "芽室", 42.9117, 143.0510),
    ("sarabetsu", "Sarabetsu", "更別", 42.6481, 143.1873),
    ("nakasatsunai", "Nakasatsunai", "中札内", 42.6990, 143.1338),
    ("shimizu", "Shimizu", "清水", 43.0115, 142.8848),
    ("shintoku", "Shintoku", "新得", 43.0797, 142.8389),
    ("shikaoi", "Shikaoi", "鹿追", 43.0994, 142.9933),
    ("otofuke", "Otofuke", "音更", 42.9940, 143.1981),
    ("shihoro", "Shihoro", "士幌", 43.1676, 143.2465),
    ("kamishihoro", "Kamishihoro", "上士幌", 43.2333, 143.2964),
    ("makubetsu", "Makubetsu", "幕別", 42.9086, 143.3542),
    ("ikeda", "Ikeda", "池田", 42.9228, 143.4489),
    ("taiki", "Taiki", "大樹", 42.4975, 143.2763),
    ("hiroo", "Hiroo", "広尾", 42.2861, 143.3114),
    ("toyokoro", "Toyokoro", "豊頃", 42.8036, 143.5097),
    ("honbetsu", "Honbetsu", "本別", 43.1240, 143.6100),
    ("urahoro", "Urahoro", "浦幌", 42.8090, 143.6587),
    ("ashoro", "Ashoro", "足寄", 43.2444, 143.5544),
]


# ---------------------------------------------------------------- kernels
@njit(parallel=True, fastmath=True, cache=True)
def horizon_kernel(dem, cosrow, obs_r, obs_c, az_deg, eqpx, zmax, eye, k, R, maxd):
    n = obs_r.size
    na = az_deg.size
    H, W = dem.shape
    out = np.empty((n, na), np.float32)
    for i in prange(n):
        r0 = obs_r[i] + 0.5
        c0 = obs_c[i] + 0.5
        z0 = dem[obs_r[i], obs_c[i]] + eye
        for a in range(na):
            az = math.radians(az_deg[a])
            sa = math.sin(az)
            ca = math.cos(az)
            r = r0
            c = c0
            d = 0.0
            best = -1.0
            while True:
                step = 28.0 if d < 7000.0 else d * 0.004
                pm = eqpx * cosrow[int(r)]
                d += step
                c += sa * step / pm
                r -= ca * step / pm
                if d > maxd or r < 0.5 or c < 0.5 or r >= H - 1.5 or c >= W - 1.5:
                    break
                drop = d * d * (1.0 - k) / (2.0 * R)
                if (zmax - z0 - drop) / d < best:
                    break
                rr = r - 0.5
                cc = c - 0.5
                ir = int(rr)
                ic = int(cc)
                fr = rr - ir
                fc = cc - ic
                z = (dem[ir, ic] * (1 - fr) * (1 - fc) + dem[ir, ic + 1] * (1 - fr) * fc
                     + dem[ir + 1, ic] * fr * (1 - fc) + dem[ir + 1, ic + 1] * fr * fc)
                t = (z - drop - z0) / d
                if t > best:
                    best = t
            out[i, a] = math.degrees(math.atan(best))
    return out


@njit(cache=True, fastmath=True)
def interp_h(hz, az, az0, naz):
    x = az - az0
    if x <= 0:
        return hz[0]
    if x >= naz - 1:
        return hz[naz - 1]
    j = int(x)
    f = x - j
    return hz[j] * (1 - f) + hz[j + 1] * f


@njit(parallel=True, fastmath=True, cache=True)
def sunset_kernel(horiz, valid, wts, idx, geo, app, azi, tsec, az0):
    """Return flat sunset, terrain sunset (seconds), flag (0 ok, 1 no sun in window)."""
    n = horiz.shape[0]
    naz = horiz.shape[1]
    nt = tsec.size
    flat = np.full(n, np.nan)
    terr = np.full(n, np.nan)
    flag = np.zeros(n, np.uint8)
    for i in prange(n):
        if not valid[i]:
            continue
        w0, w1, w2, w3 = wts[i, 0], wts[i, 1], wts[i, 2], wts[i, 3]
        n0, n1, n2, n3 = idx[i, 0], idx[i, 1], idx[i, 2], idx[i, 3]
        # flat sunset: last sample with true elevation above -0.833
        jf = -1
        for j in range(nt - 1, -1, -1):
            g = w0 * geo[n0, j] + w1 * geo[n1, j] + w2 * geo[n2, j] + w3 * geo[n3, j]
            if g > -0.833:
                jf = j
                break
        if jf < 0 or jf == nt - 1:
            continue
        g0 = w0 * geo[n0, jf] + w1 * geo[n1, jf] + w2 * geo[n2, jf] + w3 * geo[n3, jf]
        g1 = w0 * geo[n0, jf + 1] + w1 * geo[n1, jf + 1] + w2 * geo[n2, jf + 1] + w3 * geo[n3, jf + 1]
        tf = tsec[jf] + (g0 + 0.833) / (g0 - g1) * (tsec[jf + 1] - tsec[jf])
        flat[i] = tf
        # terrain: last sample up to jf where upper limb is above horizon
        prev = 0.0
        found = False
        for j in range(jf + 1, -1, -1):
            e = w0 * app[n0, j] + w1 * app[n1, j] + w2 * app[n2, j] + w3 * app[n3, j]
            a = w0 * azi[n0, j] + w1 * azi[n1, j] + w2 * azi[n2, j] + w3 * azi[n3, j]
            f = e + 0.2666 - interp_h(horiz[i], a, az0, naz)
            if f > 0:
                if j == jf + 1:
                    tt = tf
                else:
                    tt = tsec[j] + f / (f - prev) * (tsec[j + 1] - tsec[j])
                terr[i] = min(tt, tf)
                found = True
                break
            prev = f
        if not found:
            terr[i] = tsec[0]
            flag[i] = 1
    return flat, terr, flag


@njit(parallel=True, fastmath=True, cache=True)
def frames_kernel(horiz, valid, wts, idx, geo, app, azi, az0):
    n = horiz.shape[0]
    naz = horiz.shape[1]
    nf = geo.shape[1]
    lit = np.zeros((nf, n), np.uint8)
    for i in prange(n):
        if not valid[i]:
            continue
        w0, w1, w2, w3 = wts[i, 0], wts[i, 1], wts[i, 2], wts[i, 3]
        n0, n1, n2, n3 = idx[i, 0], idx[i, 1], idx[i, 2], idx[i, 3]
        for j in range(nf):
            g = w0 * geo[n0, j] + w1 * geo[n1, j] + w2 * geo[n2, j] + w3 * geo[n3, j]
            if g <= -0.833:
                continue
            e = w0 * app[n0, j] + w1 * app[n1, j] + w2 * app[n2, j] + w3 * app[n3, j]
            a = w0 * azi[n0, j] + w1 * azi[n1, j] + w2 * azi[n2, j] + w3 * azi[n3, j]
            if e + 0.2666 > interp_h(horiz[i], a, az0, naz):
                lit[j, i] = 1
    return lit


# ---------------------------------------------------------------- helpers
def node_grid(nlon=8, nlat=8):
    w, s, e, n = MAP_BOUNDS
    lons = np.linspace(w - 0.05, e + 0.05, nlon)
    lats = np.linspace(s - 0.05, n + 0.05, nlat)
    return lons, lats


def sun_at_nodes(lons, lats, times):
    geo, app, azi = [], [], []
    for la in lats:
        for lo in lons:
            sp = pvlib.solarposition.get_solarposition(times, la, lo, altitude=0)
            geo.append(sp["elevation"].to_numpy())
            app.append(sp["apparent_elevation"].to_numpy())
            azi.append(sp["azimuth"].to_numpy())
    return (np.array(geo, np.float64), np.array(app, np.float64), np.array(azi, np.float64))


def bilinear_weights(lon, lat, lons, lats):
    nlon = lons.size
    fx = np.clip((lon - lons[0]) / (lons[1] - lons[0]), 0, nlon - 1 - 1e-9)
    fy = np.clip((lat - lats[0]) / (lats[1] - lats[0]), 0, lats.size - 1 - 1e-9)
    ix, iy = fx.astype(int), fy.astype(int)
    ax, ay = fx - ix, fy - iy
    idx = np.stack([iy * nlon + ix, iy * nlon + ix + 1,
                    (iy + 1) * nlon + ix, (iy + 1) * nlon + ix + 1], 1).astype(np.int64)
    wts = np.stack([(1 - ax) * (1 - ay), ax * (1 - ay), (1 - ax) * ay, ax * ay], 1)
    return wts, idx


def hhmm(sec):
    sec = int(round(sec))
    return f"{sec // 3600:02d}:{sec % 3600 // 60:02d}:{sec % 60:02d}"


def ramp(t):
    """0 -> pale warm light, 1 -> deep night."""
    stops = np.array([
        [0.00, 0xf6, 0xe7, 0xc8],
        [0.15, 0xe9, 0xb9, 0x7e],
        [0.35, 0xb9, 0x72, 0x55],
        [0.60, 0x6a, 0x3f, 0x52],
        [0.85, 0x2c, 0x23, 0x3d],
        [1.00, 0x12, 0x11, 0x1d],
    ], float)
    out = np.zeros(t.shape + (3,), float)
    for ch in range(3):
        out[..., ch] = np.interp(t, stops[:, 0], stops[:, ch + 1])
    return out.astype(np.uint8)


# ---------------------------------------------------------------- main
def main():
    SITE_DATA.mkdir(parents=True, exist_ok=True)
    dem = np.load(WORK / "dem.npy")
    ox, oy = np.load(WORK / "dem_origin.npy")
    sea = np.isnan(dem)
    dem = np.where(sea, 0.0, dem).astype(np.float32)
    Hh, Ww = dem.shape
    eqpx = equator_px_m()
    rows = np.arange(Hh)
    lat_rows = np.array([px_to_lonlat(0, oy + r + 0.5)[1] for r in rows])
    cosrow = np.cos(np.radians(lat_rows))

    # map window in DEM pixel coords, aligned to the observer step
    w, s, e, n = MAP_BOUNDS
    x0, y0 = lonlat_to_px(w, n)
    x1, y1 = lonlat_to_px(e, s)
    c0 = int(math.floor(x0 - ox)); r0 = int(math.floor(y0 - oy))
    ncol = int((x1 - ox - c0) // (OBS_STEP * HS_STEP)) * HS_STEP
    nrow = int((y1 - oy - r0) // (OBS_STEP * HS_STEP)) * HS_STEP
    c1 = c0 + ncol * OBS_STEP; r1 = r0 + nrow * OBS_STEP
    lon_w, lat_n = px_to_lonlat(ox + c0, oy + r0)
    lon_e, lat_s = px_to_lonlat(ox + c1, oy + r1)
    coords = [[lon_w, lat_n], [lon_e, lat_n], [lon_e, lat_s], [lon_w, lat_s]]
    print("observer grid", nrow, ncol, coords)

    # observers at block centres
    rr, cc = np.meshgrid(r0 + OBS_STEP // 2 + OBS_STEP * np.arange(nrow),
                         c0 + OBS_STEP // 2 + OBS_STEP * np.arange(ncol), indexing="ij")
    obs_r = rr.ravel().astype(np.int64); obs_c = cc.ravel().astype(np.int64)
    valid = ~sea[obs_r, obs_c]
    obs_lon = np.array([px_to_lonlat(ox + c + 0.5, 0)[0] for c in cc[0]])
    obs_lat = np.array([px_to_lonlat(0, oy + r + 0.5)[1] for r in rr[:, 0]])
    lon_g = np.broadcast_to(obs_lon[None, :], (nrow, ncol)).ravel()
    lat_g = np.broadcast_to(obs_lat[:, None], (nrow, ncol)).ravel()

    az_deg = np.arange(AZ_MIN, AZ_MAX + 1, 1.0)
    hpath = WORK / "horizon.npy"
    if hpath.exists():
        horiz = np.load(hpath)
    else:
        t = time.time()
        horiz = horizon_kernel(dem, cosrow, obs_r, obs_c, az_deg, eqpx, float(dem.max()),
                               EYE_HEIGHT, REFRACTION_K, EARTH_R, MAX_DIST)
        print(f"horizon {time.time() - t:.0f}s")
        np.save(hpath, horiz)

    lons, lats = node_grid()
    wts, idx = bilinear_weights(lon_g, lat_g, lons, lats)
    town_ix = []
    for key, en, ja, la, lo in TOWNS:
        i = int(np.argmin(np.abs(obs_lat - la))) * ncol + int(np.argmin(np.abs(obs_lon - lo)))
        town_ix.append(i)

    meta = {
        "grid": {"rows": nrow, "cols": ncol, "coords": coords},
        "hillshade": {"coords": coords},
        "dates": {},
        "towns": [],
        "conditions": {
            "dem": "GSI DEM10B (zoom 12, about 28 m)",
            "observer_spacing_m": round(eqpx * math.cos(math.radians(42.8)) * OBS_STEP),
            "dem_spacing_m": round(eqpx * math.cos(math.radians(42.8))),
            "azimuth": [AZ_MIN, AZ_MAX], "max_distance_km": MAX_DIST / 1000,
            "refraction_k": REFRACTION_K, "eye_height_m": EYE_HEIGHT,
            "dem_bounds": list(__import__("common").DEM_BOUNDS),
        },
        "nodes": {"lons": lons.tolist(), "lats": lats.tolist()},
    }
    town_rows = {t[0]: {"key": t[0], "en": t[1], "ja": t[2], "lat": t[3], "lon": t[4]} for t in TOWNS}

    for dkey, dstr in DATES.items():
        times = pd.date_range(f"{dstr} {WINDOW_START}", f"{dstr} 20:30", freq=f"{SAMPLE_S}s", tz=TZ)
        geo, app, azi = sun_at_nodes(lons, lats, times)
        midnight = pd.Timestamp(dstr, tz=TZ)
        tsec = ((times - midnight).total_seconds()).to_numpy()
        flat, terr, flag = sunset_kernel(horiz, valid, wts, idx, geo, app, azi, tsec, float(AZ_MIN))
        taken = (flat - terr) / 60.0
        taken = np.where(valid, taken, np.nan)

        # flat sunset at nodes (for the client to interpolate)
        node_flat = []
        for k_ in range(geo.shape[0]):
            g = geo[k_]
            j = np.where(g > FLAT_H)[0][-1]
            node_flat.append(tsec[j] + (g[j] - FLAT_H) / (g[j] - g[j + 1]) * SAMPLE_S)

        # data png: R,G = taken in 0.1 min, B = flag (0 ok, 1 no sun after 11:30, 2 sea)
        v = np.where(valid, np.clip(np.round(np.nan_to_num(taken) * 10), 0, 65000), 0).astype(np.uint16)
        b = np.where(~valid, 2, flag).astype(np.uint8)
        rgb = np.stack([(v >> 8).astype(np.uint8), (v & 255).astype(np.uint8), b], 1).reshape(nrow, ncol, 3)
        Image.fromarray(rgb, "RGB").save(SITE_DATA / f"taken_{dkey}.png", optimize=True)

        # visual png
        tv = np.clip(np.nan_to_num(taken) / 60.0, 0, 1) ** 0.75
        col = ramp(tv).reshape(nrow, ncol, 3)
        alpha = np.where(valid, 255, 0).astype(np.uint8).reshape(nrow, ncol, 1)
        Image.fromarray(np.concatenate([col, alpha], 2), "RGBA").save(
            SITE_DATA / f"takenmap_{dkey}.png", optimize=True)

        # shadow frames: 90 minutes before Obihiro flat sunset, every minute
        obi = town_ix[0]
        t_end = math.floor(flat[obi] / 60.0) * 60
        ftimes = [midnight + pd.Timedelta(seconds=t_end - 60 * m) for m in range(WINDOW_MIN, -1, -1)]
        fidx = pd.DatetimeIndex(ftimes)
        fgeo, fapp, fazi = sun_at_nodes(lons, lats, fidx)
        lit = frames_kernel(horiz, valid, wts, idx, fgeo, fapp, fazi, float(AZ_MIN))
        fdir = SITE_DATA / "frames" / dkey
        fdir.mkdir(parents=True, exist_ok=True)
        shade_share = []
        for j in range(lit.shape[0]):
            m = (lit[j].reshape(nrow, ncol) == 0) & valid.reshape(nrow, ncol)
            im = Image.fromarray(m.astype(np.uint8), "P")
            im.putpalette([0, 0, 0, 18, 18, 34])
            im.info["transparency"] = 0
            im.save(fdir / f"{j:02d}.png", optimize=True, transparency=0, bits=1)
            shade_share.append(round(float(m.sum() / valid.sum()), 4))

        sp = pvlib.solarposition.get_solarposition(fidx, TOWNS[0][3], TOWNS[0][4], altitude=0)
        sun = [[round(float(a), 2), round(float(z), 1)] for a, z in zip(sp["apparent_elevation"], sp["azimuth"])]
        meta["dates"][dkey] = {
            "date": dstr,
            "flat_nodes": [round(x, 1) for x in node_flat],
            "frames": {"start": t_end - 60 * WINDOW_MIN, "step": 60, "count": WINDOW_MIN + 1,
                       "shade_share": shade_share, "sun": sun},
            "sun_az_at_obihiro_sunset": round(float(np.interp(flat[obi], tsec,
                                                              azi[int(np.argmin(np.abs(lats - 42.92)) * lons.size + np.argmin(np.abs(lons - 143.2)))])), 1),
        }
        vt = taken[valid]
        imax = int(np.nanargmax(np.where(valid & (flag == 0), taken, -1)))
        meta["dates"][dkey]["max_point"] = {"lon": round(float(lon_g[imax]), 4), "lat": round(float(lat_g[imax]), 4),
                                            "taken": round(float(taken[imax]), 1)}
        meta["dates"][dkey]["no_sun_share"] = round(float((flag[valid] == 1).mean()), 4)
        print(dkey, "obihiro flat", hhmm(flat[obi]), "terrain", hhmm(terr[obi]), "taken", round(taken[obi], 1))
        for (key, *_), i in zip(TOWNS, town_ix):
            town_rows[key][dkey] = {"flat": round(float(flat[i]), 1), "terrain": round(float(terr[i]), 1),
                                    "taken": round(float(taken[i]), 1), "flag": int(flag[i])}
    meta["towns"] = list(town_rows.values())

    # hillshade
    hs = dem[r0:r1, c0:c1].reshape(nrow * OBS_STEP // HS_STEP, HS_STEP, ncol * OBS_STEP // HS_STEP, HS_STEP).mean((1, 3))
    hsea = sea[r0:r1, c0:c1].reshape(hs.shape[0], HS_STEP, hs.shape[1], HS_STEP).mean((1, 3)) > 0.5
    pix = eqpx * math.cos(math.radians(42.8)) * HS_STEP
    gy, gx = np.gradient(hs, pix)
    slope = np.arctan(1.5 * np.hypot(gx, gy))
    aspect = np.arctan2(-gx, gy)
    azl, alt = math.radians(250), math.radians(30)
    shade = np.sin(alt) * np.cos(slope) + np.cos(alt) * np.sin(slope) * np.cos(azl - aspect + math.pi)
    shade = np.clip(shade, 0, 1)
    light = np.array([0xf3, 0xe4, 0xc7], float); dark = np.array([0x6d, 0x5e, 0x55], float)
    img = dark + (light - dark) * shade[..., None] ** 1.2
    img[hsea] = [0x1d, 0x22, 0x2e]
    Image.fromarray(img.astype(np.uint8), "RGB").quantize(64, dither=Image.Dither.NONE).save(
        SITE_DATA / "hillshade.png", optimize=True)
    meta["hillshade"]["size"] = list(hs.shape)

    with open(SITE_DATA / "meta.json", "w") as f:
        json.dump(meta, f, ensure_ascii=False, separators=(",", ":"))
    print(json.dumps({t["en"]: t["winter"]["taken"] for t in meta["towns"]}, ensure_ascii=False))
    print({k: v["max_point"] for k, v in meta["dates"].items()})


if __name__ == "__main__":
    main()
