const catalog = JSON.parse(document.getElementById("catalog").textContent);
const caves = catalog.caves;
const $ = (id) => document.getElementById(id),
  fmt = (n) => n.toLocaleString("en-US"),
  picked = new Set(),
  markers = new Map(),
  mobile = matchMedia("(max-width:760px)");
let focused = null,
  map,
  layer,
  visible = [],
  controlsOpen = true,
  resultsOpen = false;
const el = (tag, text, cls) => {
  const n = document.createElement(tag);
  if (text !== undefined) n.textContent = text;
  if (cls) n.className = cls;
  return n;
};
const approx = (c) => [
  Math.round(c.latitude * 10) / 10,
  Math.round(c.longitude * 10) / 10,
];
const displayName = (c) =>
  c.name.replace(/\s*\[\s*[a-z]{2,3}\s*\]/g, "").trim();
const regionName = (c) => c.location.replace(/\s+,/g, ",");
for (const region of [...new Set(caves.map((c) => c.location))].sort())
  $("region").add(new Option(region.replace(/\s+,/g, ","), region));
if (window.L) {
  map = L.map("map", {
    zoomControl: false,
    scrollWheelZoom: true,
    maxZoom: 8,
    minZoom: 2,
  }).setView([30, 27], 3);
  L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
    maxZoom: 8,
    attribution:
      '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap contributors</a>',
  }).addTo(map);
  layer = L.layerGroup().addTo(map);
} else {
  $("map").append(
    el(
      "p",
      "Map unavailable. Search and comparison remain available.",
      "map-error",
    ),
  );
}
function panels() {
  if (!picked.size) resultsOpen = false;
  const hideControls = !controlsOpen || (mobile.matches && resultsOpen);
  $("controls").hidden = hideControls;
  $("browse-toggle").hidden = !hideControls;
  $("browse-toggle").setAttribute("aria-expanded", !hideControls);
  $("results").hidden = !resultsOpen;
  $("results-toggle").hidden = !picked.size || resultsOpen;
  $("results-toggle").textContent = "Selected · " + picked.size;
  $("results-toggle").setAttribute("aria-expanded", resultsOpen);
  $("selection-open").disabled = !picked.size;
  $("selection-open").textContent = picked.size
    ? picked.size + " selected ↗"
    : "No caves selected";
  $("clear").hidden = !picked.size;
}
function padding() {
  const left = $("controls").hidden
    ? 0
    : $("controls").getBoundingClientRect().right;
  const right = $("results").hidden
    ? 0
    : innerWidth - $("results").getBoundingClientRect().left;
  if (mobile.matches) {
    const sheet = $("results").hidden ? $("controls") : $("results");
    const bottom = sheet.hidden
      ? 45
      : innerHeight - sheet.getBoundingClientRect().top + 12;
    return {
      paddingTopLeft: [20, 110],
      paddingBottomRight: [20, Math.min(bottom, innerHeight - 180)],
    };
  }
  return {
    paddingTopLeft: [left + 20, 40],
    paddingBottomRight: [right + 20, 65],
  };
}
function fit(ids) {
  if (!map) return;
  const rows = ids?.length ? ids : visible;
  if (rows.length)
    map.fitBounds(
      rows.map((id) => approx(caves[id])),
      { ...padding(), maxZoom: ids?.length === 1 ? 6 : 5, animate: false },
    );
}
function highlight() {
  document.querySelectorAll(".cave").forEach((n) => {
    const id = Number(n.dataset.id);
    n.classList.toggle("selected", picked.has(id));
    n.classList.toggle("focused", focused === id);
    n.querySelector("input").checked = picked.has(id);
  });
  for (const [id, m] of markers)
    m.setStyle({
      radius: focused === id ? 9 : picked.has(id) ? 8 : 6,
      fillColor: picked.has(id) ? "#b17440" : "#315d4a",
      weight: picked.has(id) ? 2.5 : 1.5,
    });
}
function add(id) {
  picked.add(id);
  focused = id;
  resultsOpen = true;
  update();
  fit([...picked]);
  if (mobile.matches) $("close-results").focus();
  return true;
}
function remove(id) {
  picked.delete(id);
  if (focused === id) focused = [...picked].at(-1) ?? null;
  update();
}
function update() {
  panels();
  highlight();
  comparison();
  $("selection-status").textContent = picked.size + " caves selected";
}
function comparison() {
  const root = $("comparison");
  root.replaceChildren();
  $("results-title").textContent = "Comparison";
  const maxima = {
    depth_m: Math.max(1, ...[...picked].map((id) => caves[id].depth_m)),
    length_km: Math.max(1, ...[...picked].map((id) => caves[id].length_km)),
  };
  for (const id of picked) {
    const c = caves[id],
      card = el("article", undefined, "result-card");
    card.dataset.id = id;
    const names = el("div", undefined, "result-identity");
    names.append(
      el("h3", displayName(c), "result-name"),
      el("p", regionName(c), "result-region"),
    );
    const metrics = el("div", undefined, "metrics");
    for (const [field, label, unit] of [
      ["depth_m", "Depth", "m"],
      ["length_km", "Length", "km"],
    ]) {
      const track = el(
          "div",
          undefined,
          "track" + (field === "length_km" ? " length" : ""),
        ),
        bar = el("div", undefined, "bar"),
        value = el("span", undefined, "metric-value");
      bar.style.width = (c[field] / maxima[field]) * 100 + "%";
      bar.setAttribute("aria-hidden", "true");
      value.append(
        document.createTextNode(fmt(c[field]) + " "),
        el("span", unit, "unit"),
      );
      value.setAttribute(
        "aria-label",
        label + ": " + fmt(c[field]) + " " + unit,
      );
      track.append(bar, value);
      metrics.append(track);
    }
    const actions = el("div", undefined, "row-actions");
    for (const [label, symbol, url] of [
      ["Wikipedia", "W", c.wikipedia_url],
      [
        "Google",
        "G",
        "https://www.google.com/search?q=" +
          encodeURIComponent(displayName(c) + " cave " + regionName(c)),
      ],
    ]) {
      if (!url) continue;
      const a = el("a", symbol, "source-link");
      a.href = url;
      a.target = "_blank";
      a.rel = "noopener noreferrer";
      a.title = label;
      a.setAttribute("aria-label", label + ": " + displayName(c));
      actions.append(a);
    }
    const removeButton = el("button", "×", "icon-button remove");
    removeButton.setAttribute("aria-label", "Remove " + displayName(c));
    removeButton.title = "Remove from comparison";
    removeButton.onclick = () => {
      const next = [...picked].filter((x) => x !== id);
      remove(id);
      if (next.length) $("comparison").querySelector("button")?.focus();
      else if (!$("controls").hidden) $("search").focus();
      else $("browse-toggle").focus();
    };
    actions.append(removeButton);
    card.append(names, metrics, actions);
    root.append(card);
  }
}
function render() {
  let rows = caves.map((c, id) => ({ ...c, id }));
  const q = $("search").value.trim().toLocaleLowerCase(),
    region = $("region").value,
    sort = $("sort").value;
  rows = rows.filter(
    (c) =>
      (!region || c.location === region) &&
      (!q ||
        (displayName(c) + " " + regionName(c)).toLocaleLowerCase().includes(q)),
  );
  rows.sort((a, b) =>
    sort === "name"
      ? displayName(a).localeCompare(displayName(b))
      : b[sort] - a[sort],
  );
  visible = rows.map((c) => c.id);
  const count =
    rows.length === caves.length
      ? caves.length + " caves"
      : rows.length + " / " + caves.length;
  $("count").textContent = count;
  $("count").setAttribute(
    "aria-label",
    rows.length + " of " + caves.length + " caves",
  );
  $("floating-count").textContent = count;
  const list = $("list");
  list.replaceChildren();
  list.scrollTop = 0;
  if (layer) layer.clearLayers();
  markers.clear();
  if (!rows.length)
    list.append(
      el("p", "No matches. Try another search or reset the filters.", "empty"),
    );
  for (const c of rows) {
    const card = el("article", undefined, "cave");
    card.dataset.id = c.id;
    const button = el("button", undefined, "cave-name");
    const meta = el("span", undefined, "cave-meta"),
      regionText = el("span", regionName(c), "cave-region"),
      listMetrics = el("span", undefined, "list-metrics");
    regionText.title = regionName(c);
    for (const [field, label, unit] of [
      ["depth_m", "Depth", "m"],
      ["length_km", "Length", "km"],
    ]) {
      const value = el(
        "span",
        fmt(c[field]) + " " + unit,
        field === "depth_m" ? "list-depth" : "list-length",
      );
      value.title = label;
      value.setAttribute(
        "aria-label",
        label + ": " + fmt(c[field]) + " " + unit,
      );
      listMetrics.append(value);
    }
    meta.append(regionText, listMetrics);
    button.append(el("strong", displayName(c)), meta);
    button.setAttribute("aria-label", "Explore " + displayName(c));
    button.title =
      displayName(c) +
      " · " +
      regionName(c) +
      " · Depth " +
      fmt(c.depth_m) +
      " m · Length " +
      fmt(c.length_km) +
      " km";
    button.onclick = () => add(c.id);
    const label = el("label", undefined, "pick"),
      input = el("input");
    input.type = "checkbox";
    input.setAttribute("aria-label", "Compare " + displayName(c));
    input.checked = picked.has(c.id);
    input.onchange = () => {
      if (input.checked) {
        add(c.id);
      } else remove(c.id);
    };
    label.append(input);
    card.append(button, label);
    list.append(card);
    if (layer) {
      const marker = L.circleMarker(approx(c), {
        radius: 6,
        color: "#fff",
        weight: 1.5,
        fillColor: "#315d4a",
        fillOpacity: 0.92,
      }).addTo(layer);
      marker.bindTooltip(el("span", displayName(c)), { direction: "top" });
      marker.on("click", () => add(c.id));
      markers.set(c.id, marker);
    }
  }
  highlight();
  panels();
}
for (const id of ["search", "region", "sort"])
  $(id).addEventListener(id === "search" ? "input" : "change", () => {
    render();
    if (id === "region") fit();
  });
$("reset").onclick = () => {
  $("search").value = "";
  $("region").value = "";
  $("sort").value = "depth_m";
  render();
  fit();
};
$("clear").onclick = () => {
  picked.clear();
  focused = null;
  update();
};
$("close-controls").onclick = () => {
  controlsOpen = false;
  panels();
  $("browse-toggle").focus();
};
$("browse-toggle").onclick = () => {
  controlsOpen = true;
  if (mobile.matches) resultsOpen = false;
  panels();
  $("search").focus();
};
$("close-results").onclick = () => {
  resultsOpen = false;
  panels();
  $("results-toggle").focus();
};
for (const id of ["results-toggle", "selection-open"])
  $(id).onclick = () => {
    resultsOpen = true;
    panels();
    $("close-results").focus();
    fit([...picked]);
  };
$("fit").onclick = () => fit();
$("zoom-in").onclick = () => map?.zoomIn();
$("zoom-out").onclick = () => map?.zoomOut();
$("info").onclick = () => $("about").showModal();
$("close-info").onclick = () => $("about").close();
$("about").addEventListener("click", (e) => {
  if (e.target === $("about")) {
    const r = $("about").getBoundingClientRect();
    if (
      e.clientX < r.left ||
      e.clientX > r.right ||
      e.clientY < r.top ||
      e.clientY > r.bottom
    )
      $("about").close();
  }
});
document.addEventListener("keydown", (e) => {
  if (e.key === "Escape" && !$("about").open && resultsOpen) {
    resultsOpen = false;
    panels();
    $("results-toggle").focus();
  }
});
let resizeFrame;
function resizeMap() {
  cancelAnimationFrame(resizeFrame);
  resizeFrame = requestAnimationFrame(() => {
    map?.invalidateSize({ pan: false });
    fit(picked.size ? [...picked] : undefined);
  });
}
mobile.addEventListener("change", () => {
  panels();
  resizeMap();
});
window.addEventListener("resize", resizeMap);
render();
fit();
