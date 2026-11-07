(() => {
  "use strict";

  const T = {
    en: {
      kicker: "#30DayMapChallenge · Day 17 · Light & dark",
      title: "The Hidaka shadow clock",
      headline: (n) => `On the winter solstice, the Hidaka Mountains take <b>${n} minutes</b> of sunset from Obihiro.`,
      dates: { winter: "Winter solstice", equinox: "Equinox", summer: "Summer solstice", today: "Nov 7" },
      viewShadow: "Shadow", viewTaken: "Minutes taken",
      before: (m) => m === 0 ? "sunset in Obihiro<br>(flat horizon)" : `${m} min before sunset<br>in Obihiro (flat horizon)`,
      sunline: (e, a, s) => `Sun ${e.toFixed(1)}° high, azimuth ${a.toFixed(0)}° · ${s}% of land in shadow`,
      legendShadow: [["#121222", "In the shadow of the mountains (or after sunset)"], ["#f3e4c7", "Still in the sun"]],
      legendTaken: "Minutes of sunset taken by the terrain",
      legendTakenNote: "60 or more shown darkest.",
      hint: "Tap or click the map to read the sunset at any point.",
      pt: "This point", flat: "Sunset, flat horizon", terr: "Sunset behind terrain", taken: "Minutes taken",
      noSun: "No direct sun after 11:30 on this date", sea: "Sea", outside: "Outside the calculated area",
      takenBig: (m) => `${m} min taken`,
      townsTitle: "Sunset taken, by town", thTown: "Town", thFlat: "Flat", thTerrain: "Terrain", thTaken: "Taken",
      townsNote: "Values at the point nearest each town office. Times in JST.",
      notesTitle: "About the calculation",
      note1: "Terrain only. Clouds, buildings and trees are not considered.",
      cond: (c) => [
        `Elevation: GSI DEM10B elevation tiles at zoom 12 (about ${c.dem_spacing_m} m spacing), used for the horizon search over ${c.dem_bounds[0]}–${c.dem_bounds[2]}°E, ${c.dem_bounds[1]}–${c.dem_bounds[3]}°N. Results on a ${c.observer_spacing_m} m grid; shaded relief at about 85 m.`,
        `Horizon: azimuths ${c.azimuth[0]}–${c.azimuth[1]}° every 1°, up to ${c.max_distance_km} km, with Earth curvature and atmospheric refraction (coefficient ${c.refraction_k}) corrected. Observer ${c.eye_height_m} m above ground.`,
        "Sun position: pvlib (NREL SPA), apparent elevation including refraction for standard conditions.",
        "Flat-horizon sunset: true elevation of the sun's centre −0.833°. Terrain sunset: the last moment the sun's upper limb is above the terrain horizon. The difference is the minutes taken.",
        "Shadow frames: every minute for the 90 minutes before the flat-horizon sunset in Obihiro.",
      ],
      credit: "Elevation: Geospatial Information Authority of Japan (GSI), elevation tiles (DEM10B). Sun position: pvlib.",
      source: "Source code and method",
      min: "min",
      lang: "日本語",
      attrib: "Elevation: <a href=\"https://maps.gsi.go.jp/development/ichiran.html\">GSI Japan</a>",
    },
    ja: {
      kicker: "#30DayMapChallenge · Day 17 · Light & dark",
      title: "日高山脈の影の時計",
      headline: (n) => `冬至の日、日高山脈は帯広から日没を<b>${n}分</b>奪う。`,
      dates: { winter: "冬至", equinox: "春分", summer: "夏至", today: "11月7日" },
      viewShadow: "影", viewTaken: "奪われた分数",
      before: (m) => m === 0 ? "帯広の日没<br>（平らな地平線）" : `帯広の日没の${m}分前<br>（平らな地平線）`,
      sunline: (e, a, s) => `太陽の高さ ${e.toFixed(1)}°・方位 ${a.toFixed(0)}°・陸地の${s}%が影`,
      legendShadow: [["#121222", "山の影（または日没後）"], ["#f3e4c7", "まだ日が当たる"]],
      legendTaken: "地形に奪われた日没の分数",
      legendTakenNote: "60分以上は最も暗い色。",
      hint: "地図をタップ・クリックすると、その地点の日没を表示します。",
      pt: "この地点", flat: "平らな地平線での日没", terr: "地形による日没", taken: "奪われた分数",
      noSun: "この日は11:30以降に直射日光が当たらない", sea: "海", outside: "計算範囲の外",
      takenBig: (m) => `${m}分 奪われる`,
      townsTitle: "町ごとの奪われた日没", thTown: "町", thFlat: "平らな地平線", thTerrain: "地形", thTaken: "奪われた分",
      townsNote: "各役場に最も近い計算点の値。時刻は日本時間。",
      notesTitle: "計算について",
      note1: "地形だけで計算しています。雲、建物、木は考慮していません。",
      cond: (c) => [
        `標高：国土地理院 標高タイル DEM10B（ズーム12、約${c.dem_spacing_m}m間隔）。地平線の計算には東経${c.dem_bounds[0]}〜${c.dem_bounds[2]}度、北緯${c.dem_bounds[1]}〜${c.dem_bounds[3]}度の範囲を使用。結果は約${c.observer_spacing_m}m間隔、陰影図は約85m間隔。`,
        `地平線：方位${c.azimuth[0]}〜${c.azimuth[1]}度を1度ごと、最大${c.max_distance_km}kmまで。地球の丸みと大気差（屈折係数${c.refraction_k}）を補正。視点の高さは地上${c.eye_height_m}m。`,
        "太陽の位置：pvlib（NREL SPA）。見かけの高さは標準大気での大気差を含む。",
        "平らな地平線での日没：太陽の中心の高さが −0.833度になる時刻。地形による日没：太陽の上端が地形の地平線より上にある最後の時刻。その差を「奪われた分数」とする。",
        "影の画像：帯広の平らな地平線での日没前90分を1分ごと。",
      ],
      credit: "出典：国土地理院 標高タイル（DEM10B）。太陽の位置：pvlib。",
      source: "ソースコードと計算方法",
      min: "分",
      lang: "English",
      attrib: "標高：<a href=\"https://maps.gsi.go.jp/development/ichiran.html\">国土地理院</a>",
    },
  };

  const LEFT = new Set(["memuro", "toyokoro", "kamishihoro", "shintoku"]);
  const MINOR = new Set(["makubetsu", "ikeda", "urahoro", "shihoro", "nakasatsunai", "shikaoi", "honbetsu", "otofuke"]);
  const DATE_KEYS = ["winter", "equinox", "summer", "today"];
  const params = new URLSearchParams(location.search);
  const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const state = {
    lang: params.get("lang") === "ja" ? "ja" : "en",
    date: DATE_KEYS.includes(params.get("date")) ? params.get("date") : "winter",
    view: params.get("view") === "taken" ? "taken" : "shadow",
    frame: 0,
    playing: false,
    picked: null,
  };
  let meta, map, canvas, ctx;
  const frames = {};       // date -> Image[]
  const takenData = {};    // date -> Uint8ClampedArray (RGBA)
  const markers = [];
  let timer = null;

  const $ = (id) => document.getElementById(id);
  const t = () => T[state.lang];

  // --- geometry -----------------------------------------------------------
  const mercX = (lon) => (lon + 180) / 360;
  const mercY = (lat) => { const s = Math.sin(lat * Math.PI / 180); return 0.5 - Math.log((1 + s) / (1 - s)) / (4 * Math.PI); };
  function gridIndex(lon, lat) {
    const c = meta.grid.coords;
    const fx = (mercX(lon) - mercX(c[0][0])) / (mercX(c[1][0]) - mercX(c[0][0]));
    const fy = (mercY(lat) - mercY(c[0][1])) / (mercY(c[3][1]) - mercY(c[0][1]));
    if (fx < 0 || fy < 0 || fx >= 1 || fy >= 1) return -1;
    return Math.floor(fy * meta.grid.rows) * meta.grid.cols + Math.floor(fx * meta.grid.cols);
  }
  function flatSunset(date, lon, lat) {
    const { lons, lats } = meta.nodes, nl = lons.length;
    const v = meta.dates[date].flat_nodes;
    const clamp = (x, n) => Math.min(Math.max(x, 0), n - 1 - 1e-9);
    const fx = clamp((lon - lons[0]) / (lons[1] - lons[0]), nl), fy = clamp((lat - lats[0]) / (lats[1] - lats[0]), lats.length);
    const ix = Math.floor(fx), iy = Math.floor(fy), ax = fx - ix, ay = fy - iy;
    const g = (y, x) => v[y * nl + x];
    return g(iy, ix) * (1 - ax) * (1 - ay) + g(iy, ix + 1) * ax * (1 - ay) + g(iy + 1, ix) * (1 - ax) * ay + g(iy + 1, ix + 1) * ax * ay;
  }
  const fmt = (sec, withSec) => {
    const s = Math.round(sec);
    const h = Math.floor(s / 3600), m = Math.floor((s % 3600) / 60), ss = s % 60;
    return `${String(h).padStart(2, "0")}:${String(m).padStart(2, "0")}` + (withSec ? `:${String(ss).padStart(2, "0")}` : "");
  };
  const fmtMin = (m) => (m >= 100 ? m.toFixed(0) : m.toFixed(1));

  // --- loading ------------------------------------------------------------
  const loadImage = (src) => new Promise((res, rej) => { const im = new Image(); im.onload = () => res(im); im.onerror = rej; im.src = src; });
  function loadFrames(date) {
    if (frames[date]) return frames[date].ready;
    const n = meta.dates[date].frames.count;
    const arr = new Array(n);
    const ready = Promise.all(Array.from({ length: n }, (_, i) =>
      loadImage(`data/frames/${date}/${String(i).padStart(2, "0")}.png`).then((im) => { arr[i] = im; if (date === state.date && i === state.frame) drawFrame(); })));
    frames[date] = { arr, ready };
    return ready;
  }
  async function loadTaken(date) {
    if (takenData[date]) return takenData[date];
    const im = await loadImage(`data/taken_${date}.png`);
    const c = document.createElement("canvas");
    c.width = im.width; c.height = im.height;
    const cx = c.getContext("2d", { willReadFrequently: true });
    cx.drawImage(im, 0, 0);
    takenData[date] = cx.getImageData(0, 0, im.width, im.height).data;
    return takenData[date];
  }

  // --- rendering ----------------------------------------------------------
  function drawFrame() {
    const f = frames[state.date];
    const im = f && f.arr[state.frame];
    if (!ctx) return;
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    if (im) ctx.drawImage(im, 0, 0);
    const src = map && map.getSource("shadow");
    if (src) { src.play(); requestAnimationFrame(() => src.pause()); }
  }

  function renderTime() {
    const d = meta.dates[state.date];
    const sec = d.frames.start + state.frame * d.frames.step;
    $("clock").textContent = fmt(sec);
    const before = d.frames.count - 1 - state.frame;
    $("rel").innerHTML = t().before(before);
    const [e, a] = d.frames.sun[state.frame];
    $("sunline").textContent = t().sunline(e, a, Math.round(d.frames.shade_share[state.frame] * 100));
    $("slider").value = state.frame;
    $("slider").setAttribute("aria-valuetext", `${fmt(sec)} JST`);
  }

  function renderLegend() {
    const L = t();
    if (state.view === "shadow") {
      $("legend").innerHTML = L.legendShadow.map(([c, s]) => `<div class="lg-row"><span class="sw" style="background:${c}"></span>${s}</div>`).join("");
    } else {
      $("legend").innerHTML = `<div>${L.legendTaken}</div><div class="ramp"></div>
        <div class="ramp-labels"><span>0</span><span>5</span><span>15</span><span>30</span><span>60+ ${L.min}</span></div>
        <div>${L.legendTakenNote}</div>`;
    }
  }

  function renderTowns() {
    const L = t();
    const rows = meta.towns.map((tw) => ({ tw, v: tw[state.date] })).sort((a, b) => b.v.taken - a.v.taken);
    const max = Math.max(...rows.map((r) => r.v.taken), 1);
    $("towns").querySelector("tbody").innerHTML = rows.map(({ tw, v }) =>
      `<tr data-key="${tw.key}"><td>${state.lang === "ja" ? tw.ja : tw.en}</td><td>${fmt(v.flat)}</td><td>${v.flag ? "—" : fmt(v.terrain)}</td>
       <td class="tk"><span class="bar" style="width:${Math.round(30 * v.taken / max)}px"></span>${fmtMin(v.taken)}</td></tr>`).join("");
  }

  function renderMarkers() {
    for (const m of markers) {
      const tw = m._town;
      const v = tw[state.date];
      const el = m.getElement();
      const nm = state.lang === "ja" ? tw.ja : tw.en;
      el.querySelector(".lbl").innerHTML = state.view === "taken" ? `${nm} <i>${Math.round(v.taken)}${state.lang === "ja" ? "分" : " min"}</i>` : nm;
      el.classList.toggle("dark", state.view === "taken" && v.taken > 12);
    }
  }

  async function renderInfo() {
    const L = t();
    const box = $("info");
    if (!state.picked) { box.innerHTML = `<span class="hint">${L.hint}</span>`; return; }
    const { lon, lat, tw } = state.picked;
    const name = tw ? (state.lang === "ja" ? tw.ja : tw.en) : null;
    const data = await loadTaken(state.date);
    const i = gridIndex(lon, lat);
    const head = `<div><b>${name || L.pt}</b> <span class="small">${lat.toFixed(3)}°N ${lon.toFixed(3)}°E</span></div>`;
    if (i < 0) { box.innerHTML = head + `<div>${L.outside}</div>`; return; }
    const r = data[i * 4], g = data[i * 4 + 1], b = data[i * 4 + 2];
    if (b === 2) { box.innerHTML = head + `<div>${L.sea}</div>`; return; }
    const taken = (r * 256 + g) / 10;
    const flat = flatSunset(state.date, lon, lat);
    box.innerHTML = head + (b === 1
      ? `<div class="big">${L.noSun}</div><dl><dt>${L.flat}</dt><dd>${fmt(flat, true)}</dd></dl>`
      : `<div class="big">${L.takenBig(fmtMin(taken))}</div>
         <dl><dt>${L.flat}</dt><dd>${fmt(flat, true)}</dd><dt>${L.terr}</dt><dd>${fmt(flat - taken * 60, true)}</dd>
         <dt>${L.taken}</dt><dd>${fmtMin(taken)} ${L.min}</dd></dl>`);
  }

  function renderStatic() {
    const L = t();
    document.documentElement.lang = state.lang;
    document.title = L.title;
    document.querySelectorAll("[data-i18n]").forEach((el) => { const v = L[el.dataset.i18n]; if (typeof v === "string") el.textContent = v; });
    $("lang").textContent = L.lang;
    $("headline").innerHTML = L.headline(Math.round(meta.towns[0].winter.taken));
    $("dates").innerHTML = DATE_KEYS.map((k) =>
      `<button type="button" role="radio" data-date="${k}" aria-checked="${k === state.date}">${L.dates[k]}<small>${meta.dates[k].date.slice(5).replace("-", "/")}</small></button>`).join("");
    document.querySelectorAll("#views button").forEach((b) => { b.setAttribute("role", "radio"); b.setAttribute("aria-checked", b.dataset.view === state.view); });
    $("conditions").innerHTML = L.cond(meta.conditions).map((s) => `<li>${s}</li>`).join("");
    $("timebox").style.display = state.view === "shadow" ? "" : "none";
    const attr = document.querySelector(".maplibregl-ctrl-attrib-inner");
    if (attr) attr.innerHTML = L.attrib;
    renderLegend(); renderTowns(); renderMarkers(); renderTime(); renderInfo();
  }

  function applyView() {
    if (!map) return;
    map.setLayoutProperty("shadow", "visibility", state.view === "shadow" ? "visible" : "none");
    map.setLayoutProperty("taken", "visibility", state.view === "taken" ? "visible" : "none");
    if (state.view !== "shadow") stop();
  }

  // --- playback -----------------------------------------------------------
  function setPlayIcon() {
    $("playicon").setAttribute("d", state.playing ? "M4 2.5h3v11H4zM9 2.5h3v11H9z" : "M4 2.5v11l9-5.5z");
    $("play").setAttribute("aria-label", state.playing ? "Pause" : "Play");
  }
  function stop() { state.playing = false; clearTimeout(timer); setPlayIcon(); }
  async function play() {
    if (state.view !== "shadow") return;
    state.playing = true; setPlayIcon();
    await loadFrames(state.date);
    const n = meta.dates[state.date].frames.count;
    if (state.frame >= n - 1) state.frame = 0;
    const tick = () => {
      if (!state.playing) return;
      if (state.frame >= n - 1) { stop(); return; }
      state.frame += 1; drawFrame(); renderTime();
      timer = setTimeout(tick, state.frame >= n - 8 ? 220 : 110);
    };
    timer = setTimeout(tick, 110);
  }

  // --- setup --------------------------------------------------------------
  async function init() {
    meta = await (await fetch("data/meta.json")).json();
    const n = meta.dates[state.date].frames.count;
    const tp = parseInt(params.get("t"), 10);
    state.frame = Number.isFinite(tp) ? Math.min(Math.max(tp, 0), n - 1) : 0;
    $("slider").max = n - 1;

    canvas = document.createElement("canvas");
    canvas.width = meta.grid.cols; canvas.height = meta.grid.rows;
    ctx = canvas.getContext("2d");

    const c = meta.grid.coords;
    const small = window.innerWidth <= 760;
    map = new maplibregl.Map({
      container: "map",
      style: { version: 8, sources: {}, layers: [{ id: "bg", type: "background", paint: { "background-color": "#0f1019" } }] },
      bounds: small ? [[142.75, 42.45], [143.55, 43.2]] : [[142.55, 42.25], [143.75, 43.35]],
      fitBoundsOptions: { padding: small ? { top: 10, bottom: window.innerHeight * 0.46 + 10, left: 10, right: 10 } : { top: 30, bottom: 30, left: 410, right: 30 } },
      maxBounds: [[141.9, 41.8], [144.3, 43.8]],
      minZoom: 7, maxZoom: 13,
      attributionControl: false,
      dragRotate: false, pitchWithRotate: false,
    });
    map.touchZoomRotate.disableRotation();
    map.addControl(new maplibregl.NavigationControl({ showCompass: false }), "top-right");
    map.addControl(new maplibregl.AttributionControl({ compact: false, customAttribution: T[state.lang].attrib }), small ? "top-left" : "bottom-right");

    map.on("load", () => {
      map.addSource("hillshade", { type: "image", url: "data/hillshade.png", coordinates: c });
      map.addLayer({ id: "hillshade", type: "raster", source: "hillshade", paint: { "raster-fade-duration": 0 } });
      map.addSource("shadow", { type: "canvas", canvas, coordinates: c, animate: false });
      map.addLayer({ id: "shadow", type: "raster", source: "shadow", paint: { "raster-opacity": 0.86, "raster-fade-duration": 0 } });
      map.addSource("taken", { type: "image", url: `data/takenmap_${state.date}.png`, coordinates: c });
      map.addLayer({ id: "taken", type: "raster", source: "taken", paint: { "raster-opacity": 0.92, "raster-fade-duration": 0 } });
      applyView();
      drawFrame();

      for (const tw of meta.towns) {
        const el = document.createElement("div");
        const left = LEFT.has(tw.key);
        el.className = "town-marker" + (MINOR.has(tw.key) ? " minor" : "") + (left ? " left" : "");
        el.innerHTML = left ? `<span class="lbl"></span><span class="dot"></span>` : `<span class="dot"></span><span class="lbl"></span>`;
        el.addEventListener("click", (ev) => { ev.stopPropagation(); pick(tw.lon, tw.lat, tw); });
        const m = new maplibregl.Marker({ element: el, anchor: left ? "right" : "left", offset: [left ? 4 : -4, 0] }).setLngLat([tw.lon, tw.lat]).addTo(map);
        m._town = tw;
        markers.push(m);
      }
      renderMarkers();
      const zoomClass = () => document.body.classList.toggle("zoomed-out", map.getZoom() < 8.3);
      map.on("zoom", zoomClass); zoomClass();
      map.on("click", (e) => pick(e.lngLat.lng, e.lngLat.lat));

      loadFrames(state.date).then(() => {
        drawFrame();
        if (!reduceMotion && !Number.isFinite(tp) && state.view === "shadow") play();
      });
    });

    renderStatic();

    $("lang").addEventListener("click", () => { state.lang = state.lang === "en" ? "ja" : "en"; renderStatic(); });
    $("dates").addEventListener("click", (e) => {
      const b = e.target.closest("button"); if (!b) return;
      const was = state.playing;
      stop();
      state.date = b.dataset.date;
      const nn = meta.dates[state.date].frames.count;
      state.frame = Math.min(state.frame, nn - 1);
      $("slider").max = nn - 1;
      map.getSource("taken").updateImage({ url: `data/takenmap_${state.date}.png`, coordinates: c });
      loadFrames(state.date).then(() => { drawFrame(); if (was) play(); });
      drawFrame();
      renderStatic();
    });
    $("views").addEventListener("click", (e) => {
      const b = e.target.closest("button"); if (!b) return;
      state.view = b.dataset.view;
      applyView(); renderStatic();
    });
    $("play").addEventListener("click", () => (state.playing ? stop() : play()));
    $("slider").addEventListener("input", (e) => { stop(); state.frame = +e.target.value; drawFrame(); renderTime(); });
    $("towns").addEventListener("click", (e) => {
      const tr = e.target.closest("tr[data-key]"); if (!tr) return;
      const tw = meta.towns.find((x) => x.key === tr.dataset.key);
      pick(tw.lon, tw.lat, tw);
      map.easeTo({ center: [tw.lon, tw.lat], duration: reduceMotion ? 0 : 600 });
    });
    document.addEventListener("keydown", (e) => {
      if (e.target.tagName === "INPUT" || state.view !== "shadow") return;
      if (e.key === " ") { e.preventDefault(); state.playing ? stop() : play(); }
    });
  }

  function pick(lon, lat, tw) {
    state.picked = { lon, lat, tw };
    renderInfo();
  }

  init().catch((err) => { console.error(err); });
})();
