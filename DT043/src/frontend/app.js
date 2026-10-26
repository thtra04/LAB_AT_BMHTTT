// Frontend DT043 – gọi REST API của backend, không dùng thư viện ngoài.
const $ = (s) => document.querySelector(s);
const fmt = (v, d = 4) => {
  if (v === null || v === undefined || v === "") return "–";
  const n = Number(v);
  if (Number.isInteger(n)) return n.toLocaleString("en-US");
  return Math.abs(n) >= 1000 ? n.toFixed(0) : n.toPrecision(d);
};
const esc = (s) => String(s ?? "").replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));

async function api(path, opts = {}) {
  const r = await fetch(path, { headers: { "Content-Type": "application/json" }, ...opts });
  const body = await r.json().catch(() => ({}));
  if (!r.ok) throw new Error(body.detail ? JSON.stringify(body.detail) : r.statusText);
  return body;
}

function fill(table, rows) {
  $(table + " tbody").innerHTML = rows.join("") || `<tr><td colspan="9" class="sub">Chưa có dữ liệu</td></tr>`;
}

async function loadHealth() {
  try {
    const h = await api("/api/health");
    $("#health").textContent = `API OK · ${h.models_loaded} model`;
    $("#health").className = "pill ok";
  } catch (e) {
    $("#health").textContent = "Mất kết nối API";
    $("#health").className = "pill bad";
  }
}

async function loadDevices() {
  const ds = await api("/api/devices");
  fill("#devices", ds.map((d) => `<tr><td>${esc(d.name)}</td><td>${esc(d.device_type)}</td>
    <td>${esc(d.variant ?? "–")} ${esc(d.quant_mode ?? "")}</td><td class="num">${d.size_bytes ? (d.size_bytes / 1024).toFixed(1) + " KB" : "–"}</td>
    <td class="num">${fmt(d.threshold)}</td><td class="num">${d.window_size ?? "–"}</td><td class="num">${d.open_alerts}</td></tr>`));
  const sel = $("#r-device");
  if (!sel.options.length) {
    ds.filter((d) => d.model_id).forEach((d) => sel.add(new Option(d.name, d.name)));
  }
}

async function loadAlerts() {
  const as = await api("/api/alerts?limit=50");
  fill("#alerts", as.map((a) => `<tr><td>${a.id}</td><td>${esc(a.device)}</td><td>${esc(a.source)}</td>
    <td class="sev-${a.severity}">${a.severity}</td><td class="num">${(a.alarm_ratio * 100).toFixed(1)}%</td>
    <td>${a.status === "open" ? "mở" : "đã xác nhận"}</td>
    <td>${a.status === "open" ? `<button class="link" data-ack="${a.id}">Xác nhận</button>` : ""}</td></tr>`));
}

async function loadMtd() {
  const ms = await api("/api/mtd/actions?limit=50");
  fill("#mtd", ms.map((m) => `<tr><td>${m.id}</td><td>${esc(m.device)}</td><td>${m.technique}</td>
    <td>${m.trigger_kind === "event" ? "sự kiện (AE)" : "chu kỳ"}</td><td>${esc(m.detail)}</td></tr>`));
}

async function loadExperiments() {
  const rows = await api("/api/experiments");
  if (!rows.length) return fill("#experiments", []);
  const cols = Object.keys(rows[0]);
  $("#experiments thead").innerHTML = "<tr>" + cols.map((c) => `<th>${esc(c)}</th>`).join("") + "</tr>";
  fill("#experiments", rows.map((r) => "<tr>" + cols.map((c) =>
    typeof r[c] === "number" ? `<td class="num">${fmt(r[c])}</td>` : `<td>${esc(r[c])}</td>`).join("") + "</tr>"));
}

function drawChart(res) {
  const cv = $("#chart");
  const dpr = window.devicePixelRatio || 1;
  const W = cv.clientWidth, H = 260;
  cv.width = W * dpr; cv.height = H * dpr;
  const ctx = cv.getContext("2d");
  ctx.scale(dpr, dpr);
  const css = getComputedStyle(document.documentElement);
  const pad = { l: 48, r: 10, t: 10, b: 22 };
  const vals = res.mse.map((v) => Math.log10(Math.max(v, 1e-6)));
  const thr = Math.log10(Math.max(res.threshold, 1e-6));
  const lo = Math.min(thr, ...vals) - 0.3, hi = Math.max(thr, ...vals) + 0.3;
  const x = (i) => pad.l + (i / Math.max(vals.length - 1, 1)) * (W - pad.l - pad.r);
  const y = (v) => pad.t + (1 - (v - lo) / (hi - lo)) * (H - pad.t - pad.b);
  ctx.clearRect(0, 0, W, H);
  ctx.fillStyle = css.getPropertyValue("--alarm");
  res.alarms.forEach((a, i) => { if (a) ctx.fillRect(x(i), pad.t, Math.max(1, x(1) - x(0)), H - pad.t - pad.b); });
  ctx.fillStyle = css.getPropertyValue("--muted"); ctx.font = "11px system-ui";
  for (let p = Math.ceil(lo); p <= Math.floor(hi); p++) {
    ctx.fillText("1e" + p, 6, y(p) + 4);
    ctx.strokeStyle = css.getPropertyValue("--border"); ctx.beginPath(); ctx.moveTo(pad.l, y(p)); ctx.lineTo(W - pad.r, y(p)); ctx.stroke();
  }
  ctx.strokeStyle = css.getPropertyValue("--mse"); ctx.lineWidth = 1.2; ctx.beginPath();
  vals.forEach((v, i) => (i ? ctx.lineTo(x(i), y(v)) : ctx.moveTo(x(i), y(v)))); ctx.stroke();
  ctx.strokeStyle = css.getPropertyValue("--thr"); ctx.setLineDash([6, 4]); ctx.beginPath();
  ctx.moveTo(pad.l, y(thr)); ctx.lineTo(W - pad.r, y(thr)); ctx.stroke(); ctx.setLineDash([]);
  ctx.fillText(`mẫu (bước ${res.step})`, W - 110, H - 6);
}

$("#replay-form").addEventListener("submit", async (ev) => {
  ev.preventDefault();
  const q = new URLSearchParams({ segment: $("#r-segment").value, n: $("#r-n").value, offset: $("#r-offset").value });
  $("#replay-summary").textContent = "Đang chạy…";
  try {
    const r = await api(`/api/replay/${encodeURIComponent($("#r-device").value)}?${q}`, { method: "POST" });
    const pct = (100 * r.n_alarm_windows / Math.max(r.n_windows, 1)).toFixed(1);
    $("#replay-summary").innerHTML = `<span>Mẫu: <b>${r.n_samples}</b></span><span>Mẫu vượt ngưỡng: <b>${r.n_flagged}</b></span>
      <span>Cửa sổ cảnh báo: <b>${r.n_alarm_windows}/${r.n_windows} (${pct}%)</b></span>
      <span>tr* = <b>${fmt(r.threshold)}</b>, ws* = <b>${r.window_size}</b></span>
      <span>Suy luận: <b>${r.infer_us_per_sample.toFixed(2)} µs/mẫu</b></span>
      <span>${r.alert_id ? `<b class="sev-high">Đã tạo cảnh báo #${r.alert_id} + ${r.mtd_action_ids.length} hành động MTD</b>` : "Không có cảnh báo"}</span>`;
    drawChart(r);
    await Promise.all([loadAlerts(), loadMtd(), loadDevices()]);
  } catch (e) {
    $("#replay-summary").textContent = "Lỗi: " + e.message;
  }
});

$("#alerts").addEventListener("click", async (ev) => {
  const id = ev.target.dataset.ack;
  if (!id) return;
  await api(`/api/alerts/${id}/ack`, { method: "POST" });
  await Promise.all([loadAlerts(), loadDevices()]);
});

$("#tick").addEventListener("click", async () => { await api("/api/mtd/tick", { method: "POST" }); loadMtd(); });

(async () => {
  await loadHealth();
  await Promise.all([loadDevices(), loadAlerts(), loadMtd(), loadExperiments()]);
  // ?replay=<thiết bị>:<segment>[:n] → tự phát lại khi mở trang (tiện cho demo/quay video)
  const auto = new URLSearchParams(location.search).get("replay");
  if (auto) {
    const [dev, seg, n] = auto.split(":");
    $("#r-device").value = dev;
    $("#r-segment").value = seg || "benign";
    if (n) $("#r-n").value = n;
    $("#replay-form").requestSubmit();
  }
})();
