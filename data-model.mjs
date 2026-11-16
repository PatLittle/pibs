const $ = (id) => document.getElementById(id),
  el = (tag, text) => {
    const n = document.createElement(tag);
    if (text != null) n.textContent = text;
    return n;
  };
let svg, model, view, full;
function setView(v) {
  view = v;
  svg.setAttribute("viewBox", v.join(" "));
}
function zoom(factor, cx = 0.5, cy = 0.5) {
  const [x, y, w, h] = view;
  const nw = Math.min(full[2] * 2, Math.max(180, w * factor)),
    nh = (nw * h) / w;
  setView([x + (w - nw) * cx, y + (h - nh) * cy, nw, nh]);
}
function focus(id, query = "") {
  const group = svg.querySelector('[data-table="' + CSS.escape(id) + '"]'),
    box = group.getBBox();
  const match =
    query &&
    [...group.querySelectorAll("[data-field]")].find((n) =>
      n.dataset.field.toLowerCase().includes(query),
    );
  const field = match?.getBBox();
  const ratio =
      $("schema-canvas").clientWidth / $("schema-canvas").clientHeight,
    w = Math.min(1100, $("schema-canvas").clientWidth);
  setView([box.x - 20, field ? field.y - 80 : box.y - 25, w, w / ratio]);
  $("schema-canvas").focus({ preventScroll: true });
  $("schema-canvas").scrollIntoView({ block: "nearest" });
}
function results() {
  const q = $("schema-search").value.toLowerCase().trim();
  $("schema-results").replaceChildren();
  if (!q) return;
  for (const t of model.tables.filter(
    (t) =>
      t.label.toLowerCase().includes(q) ||
      t.fields.some((f) => f.name.toLowerCase().includes(q)),
  )) {
    const b = el(
      "button",
      t.label +
        " · " +
        t.fields.filter((f) => f.name.toLowerCase().includes(q)).length +
        " matching fields",
    );
    b.type = "button";
    b.onclick = () => focus(t.id, q);
    $("schema-results").append(b);
  }
}
try {
  const [a, b] = await Promise.all([
    fetch("data/network-schema.json"),
    fetch("data/network-schema.svg"),
  ]);
  if (!a.ok || !b.ok) throw Error("Schema HTTP error");
  model = await a.json();
  const source = await b.text();
  svg = new DOMParser().parseFromString(
    source,
    "image/svg+xml",
  ).documentElement;
  $("schema-canvas").append(svg);
  full = svg.getAttribute("viewBox").split(" ").map(Number);
  setView([...full]);
  $("schema-summary").textContent =
    `${model.summary.tables} tables / record shapes · ${model.summary.fields.toLocaleString()} field paths · ${model.summary.relationships} documented joins and projections. AIA schema inspected ${model.external_source.inspected_on}.`;
  for (const t of model.tables) {
    const d = el("details"),
      s = el("summary", t.label + " · " + t.fields.length + " fields");
    d.append(
      s,
      el("p", t.layer + " · " + t.rows + " observed records"),
      el(
        "p",
        typeof t.source === "string" ? t.source : JSON.stringify(t.source),
      ),
      el(
        "p",
        "Key: " + (t.primary_key.join(" + ") || "container / parent key"),
      ),
    );
    if (t.note) d.append(el("p", t.note));
    const btn = el("button", "Locate in diagram");
    btn.onclick = () => focus(t.id);
    d.append(btn);
    const ul = el("ul");
    for (const f of t.fields)
      ul.append(
        el(
          "li",
          (t.primary_key.includes(f.name) ? "PK · " : "") +
            f.name +
            " : " +
            f.types.join(" | "),
        ),
      );
    d.append(ul);
    $("schema-tables").append(d);
  }
  $("schema-search").oninput = results;
  $("schema-in").onclick = () => zoom(0.75);
  $("schema-out").onclick = () => zoom(1.33);
  $("schema-fit").onclick = () => setView([...full]);
  svg.addEventListener(
    "wheel",
    (e) => {
      e.preventDefault();
      const r = svg.getBoundingClientRect();
      zoom(
        e.deltaY > 0 ? 1.12 : 0.89,
        (e.clientX - r.left) / r.width,
        (e.clientY - r.top) / r.height,
      );
    },
    { passive: false },
  );
  let drag;
  svg.onpointerdown = (e) => {
    drag = { x: e.clientX, y: e.clientY, view: [...view] };
    svg.setPointerCapture(e.pointerId);
  };
  svg.onpointermove = (e) => {
    if (!drag) return;
    const r = svg.getBoundingClientRect();
    setView([
      drag.view[0] - ((e.clientX - drag.x) * view[2]) / r.width,
      drag.view[1] - ((e.clientY - drag.y) * view[3]) / r.height,
      view[2],
      view[3],
    ]);
  };
  svg.onpointerup = svg.onpointercancel = () => (drag = null);
  $("schema-canvas").onkeydown = (e) => {
    if (["+", "=", "-"].includes(e.key)) {
      e.preventDefault();
      zoom(e.key === "-" ? 1.2 : 0.8);
    }
    const moves = {
      ArrowLeft: [-1, 0],
      ArrowRight: [1, 0],
      ArrowUp: [0, -1],
      ArrowDown: [0, 1],
    };
    if (moves[e.key]) {
      e.preventDefault();
      const [dx, dy] = moves[e.key];
      setView([
        view[0] + dx * view[2] * 0.1,
        view[1] + dy * view[3] * 0.1,
        view[2],
        view[3],
      ]);
    }
  };
} catch (e) {
  $("schema-summary").textContent =
    "The schema could not be loaded. Reload to retry.";
  $("schema-summary").setAttribute("role", "alert");
  console.error(e);
}
