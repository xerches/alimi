// Small charts as inline SVG strings, drawn at build time so the pages stay static and fast. One
// series per chart, one axis, thin marks, text in the text tokens: every color is a CSS class the
// stylesheet maps to a brand token, so no chart types a color. Hover shows the value through <title>.
const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c]);

/** Line chart of one series over evenly spaced points. series: [{ label, value }]. */
export function lineChart({ series, max, title, unit = "", tone = "primary", width = 600, height = 200, ticks }) {
  const padL = 40;
  const padR = 20;
  const padT = 20;
  const padB = 28;
  const w = width - padL - padR;
  const h = height - padT - padB;
  const n = series.length;
  const x = (i) => (padL + (n === 1 ? w / 2 : (i * w) / (n - 1))).toFixed(1);
  const y = (v) => (padT + h - (v / max) * h).toFixed(1);
  const steps = ticks ?? [0, Math.round(max / 2), max];
  const path = series.map((p, i) => `${i ? "L" : "M"}${x(i)} ${y(p.value)}`).join(" ");
  const area = `${path} L${x(n - 1)} ${y(0)} L${x(0)} ${y(0)} Z`;
  const last = series[n - 1];
  const summary = series.map((p) => `${p.label}: ${p.value}${unit}`).join(", ");
  return `<svg class="chart" viewBox="0 0 ${width} ${height}" role="img" aria-label="${esc(title)}. ${esc(summary)}">
${steps.map((t) => `<line class="grid-line" x1="${padL}" x2="${width - padR}" y1="${y(t)}" y2="${y(t)}"/><text class="axis-text" x="${padL - 8}" y="${Number(y(t)) + 4}" text-anchor="end">${t}${esc(unit)}</text>`).join("\n")}
<path class="area" data-tone="${tone}" d="${area}"/>
<path class="line" data-tone="${tone}" d="${path}"/>
${series.map((p, i) => `<circle class="dot${i === n - 1 ? " end" : ""}" data-tone="${tone}" cx="${x(i)}" cy="${y(p.value)}" r="4"><title>${esc(p.label)}: ${esc(p.value)}${esc(unit)}</title></circle>`).join("\n")}
${series.map((p, i) => `<text class="axis-text" x="${x(i)}" y="${height - 8}" text-anchor="${i === 0 ? "start" : i === n - 1 ? "end" : "middle"}">${esc(p.label)}</text>`).join("\n")}
<text class="value-text" x="${x(n - 1)}" y="${Number(y(last.value)) - 10}" text-anchor="end">${esc(last.value)}${esc(unit)}</text>
</svg>`;
}

/** A sparkline: the same series without axes, for a tile. */
export function sparkline(values, { max = 100, width = 120, height = 32, tone = "primary", label = "" } = {}) {
  const n = values.length;
  const pad = 4;
  const x = (i) => (pad + (n === 1 ? (width - 2 * pad) / 2 : (i * (width - 2 * pad)) / (n - 1))).toFixed(1);
  const y = (v) => (pad + (height - 2 * pad) - (v / max) * (height - 2 * pad)).toFixed(1);
  const path = values.map((v, i) => `${i ? "L" : "M"}${x(i)} ${y(v)}`).join(" ");
  return `<svg class="sparkline" viewBox="0 0 ${width} ${height}" role="img" aria-label="${esc(label)}">
<path class="line" data-tone="${tone}" d="${path}"/>
<circle class="dot end" data-tone="${tone}" cx="${x(n - 1)}" cy="${y(values[n - 1])}" r="3"/>
</svg>`;
}
