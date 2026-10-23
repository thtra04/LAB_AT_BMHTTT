// Bản rút gọn 10 slide (thuyết trình ~5 phút có demo) – chạy: node report/build_deck_10.js
// Dùng chung theme/layout/số liệu với build_deck.js (bản 17 slide giữ làm bản đầy đủ để trả lời câu hỏi).
const path = require("path");
const fs = require("fs");
const pptxgen = require("pptxgenjs");
const React = require("react");
const ReactDOMServer = require("react-dom/server");
const sharp = require("sharp");
const fa = require("react-icons/fa6");
const { applyTheme } = require("./apply_theme.js");

const HERE = __dirname;
const ROOT = path.resolve(HERE, "..");
const FIG = path.join(ROOT, "results", "figures");
const D = JSON.parse(fs.readFileSync(path.join(HERE, "deck_data.json"), "utf8"));
const OUT = path.join(HERE, "SlideThuyetTrinh_DT043_10slide_1150080120_HoangThanhTra.pptx");
const TAB = path.join(ROOT, "results", "tables");
function csv(name) {
  // đọc CSV chuẩn (có trường đặt trong ngoặc kép chứa dấu phẩy)
  const raw = fs.readFileSync(path.join(TAB, name), "utf8").replace(String.fromCharCode(0xFEFF), "");
  const NL = String.fromCharCode(10), CR = String.fromCharCode(13);
  const rows = [];
  let row = [], cur = "", inQ = false;
  for (let i = 0; i < raw.length; i++) {
    const ch = raw[i];
    if (inQ) {
      if (ch === '"' && raw[i + 1] === '"') { cur += '"'; i++; }
      else if (ch === '"') inQ = false;
      else cur += ch;
    } else if (ch === '"') inQ = true;
    else if (ch === ",") { row.push(cur); cur = ""; }
    else if (ch === NL || ch === CR) {
      if (ch === CR && raw[i + 1] === NL) i++;
      row.push(cur); cur = ""; if (row.some((v) => v !== "")) rows.push(row); row = [];
    } else cur += ch;
  }
  if (cur !== "" || row.length) { row.push(cur); rows.push(row); }
  const head = rows[0];
  return rows.slice(1).map((r) => Object.fromEntries(r.map((v, i) => [head[i], v])));
}

const THEME = {
  name: "DT043 Edge Defense",
  headFontFace: "Cambria",
  bodyFontFace: "Calibri",
  colors: {
    dk1: "1B2430", lt1: "FFFFFF", dk2: "0B1F33", lt2: "EAF2F5",
    accent1: "0E9F8E", accent2: "F2A541", accent3: "D64545", accent4: "5B6B7C",
    accent5: "2E6FB0", accent6: "3A9D5D", hlink: "2E6FB0", folHlink: "5B6B7C",
  },
};
const HEX = THEME.colors;

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE"; // 13.33 x 7.5 in
pres.title = "DT043 – Phát hiện botnet IoT bằng autoencoder nhẹ";
pres.author = "Hoàng Thanh Trà";
pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
const C = pres.SchemeColor;

// ------------------------------------------------------------------ layouts
pres.defineSlideMaster({
  title: "DARK",
  background: { color: HEX.dk2 },
  objects: [
    { placeholder: { options: { name: "title", type: "title", x: 0.8, y: 2.0, w: 11.7, h: 1.9, fontSize: 40, bold: true,
      color: C.background1, fontFace: THEME.headFontFace, valign: "bottom", align: "left", margin: 0 }, text: "" } },
    { placeholder: { options: { name: "body", type: "body", x: 0.8, y: 4.1, w: 11.7, h: 1.6, fontSize: 18,
      color: C.background2, valign: "top", margin: 0 }, text: "" } },
  ],
});
pres.defineSlideMaster({
  title: "DARK_CONTENT",
  background: { color: HEX.dk2 },
  objects: [
    { placeholder: { options: { name: "title", type: "title", x: 0.8, y: 0.5, w: 11.7, h: 1.0, fontSize: 36, bold: true,
      color: C.background1, fontFace: THEME.headFontFace, valign: "middle", align: "left", margin: 0 }, text: "" } },
    { placeholder: { options: { name: "body", type: "body", x: 0.8, y: 1.8, w: 11.7, h: 4.9, fontSize: 19,
      color: C.background2, valign: "top", margin: 0 }, text: "" } },
  ],
});
pres.defineSlideMaster({
  title: "CONTENT",
  background: { color: HEX.lt1 },
  margin: [0.5, 0.6, 0.6, 0.6],
  objects: [
    { placeholder: { options: { name: "title", type: "title", x: 0.6, y: 0.35, w: 12.1, h: 0.85, fontSize: 32, bold: true,
      color: C.text2, fontFace: THEME.headFontFace, valign: "middle", margin: 0 }, text: "" } },
    { text: { text: "DT043 · Hoàng Thanh Trà · 1150080120", options: { x: 0.6, y: 7.0, w: 6, h: 0.3, fontSize: 10,
      color: C.accent4, margin: 0 } } },
  ],
  slideNumber: { x: 12.2, y: 7.0, w: 0.5, h: 0.3, fontSize: 10, color: HEX.accent4, align: "right" },
});

// ------------------------------------------------------------------ helpers
async function icon(Comp, color, px = 256) {
  const svg = ReactDOMServer.renderToStaticMarkup(React.createElement(Comp, { color: "#" + color, size: px }));
  const buf = await sharp(Buffer.from(svg)).png().toBuffer();
  return "image/png;base64," + buf.toString("base64");
}
async function iconCircle(slide, Comp, x, y, d, fill, name) {
  slide.addShape(pres.shapes.OVAL, { x, y, w: d, h: d, fill: { color: fill }, line: { color: fill }, objectName: name + "-circle" });
  const pad = d * 0.25;
  slide.addImage({ data: await icon(Comp, HEX.lt1), x: x + pad, y: y + pad, w: d - 2 * pad, h: d - 2 * pad, objectName: name + "-icon" });
}
function text(slide, t, opts) {
  slide.addText(t, { isTextBox: true, margin: 0, fontSize: 15, color: C.text1, valign: "top", ...opts });
}
function card(slide, x, y, w, h, fill, name) {
  slide.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h, rectRadius: 0.12, fill: { color: fill }, line: { color: fill },
    shadow: { type: "outer", color: "000000", opacity: 0.12, blur: 6, offset: 2, angle: 90 }, objectName: name });
}
function stat(slide, x, y, w, big, label, color, name) {
  text(slide, big, { x, y, w, h: 0.95, fontSize: 40, bold: true, color, fontFace: THEME.headFontFace, objectName: name + "-num" });
  text(slide, label, { x, y: y + 0.95, w, h: 0.7, fontSize: 13, color: C.accent4, objectName: name + "-label" });
}
const f = (v, d = 3) => (v === null || v === undefined ? "–" : Number(v).toFixed(d));
const pct = (v, d = 0) => (Number(v) * 100).toFixed(d) + "%";
const nf = (v) => Number(v).toLocaleString("en-US");
const content = (section) => pres.addSlide({ masterName: "CONTENT", sectionTitle: section });
const chartText = { catAxisLabelFontFace: "+mn-lt", valAxisLabelFontFace: "+mn-lt", dataLabelFontFace: "+mn-lt",
  titleFontFace: "+mn-lt", legendFontFace: "+mn-lt", catAxisLabelColor: HEX.dk1, valAxisLabelColor: HEX.accent4,
  catAxisLabelFontSize: 12, valAxisLabelFontSize: 11, dataLabelFontSize: 11, dataLabelColor: HEX.dk1,
  valGridLine: { color: "D9E1E7", size: 0.5 }, catGridLine: { style: "none" } };

async function main() {
  const cf = D.configs, q = D.quant, e = D.edge;
  const lbl = { E1_baseline: "B0 AE", E2_global: "B1 global", E2_shared_pdnorm: "B1 chung+pdnorm", E3_iforest: "B2 IForest", E4_light: "V1 AE nhẹ" };
  let s;

  // ================================================================ 1. Tiêu đề
  pres.addSection({ title: "Mở đầu" });
  s = pres.addSlide({ masterName: "DARK", sectionTitle: "Mở đầu" });
  s.addText("Phát hiện botnet IoT bằng autoencoder nhẹ", { placeholder: "title" });
  s.addText([
    { text: "Đề tài DT043 · Bài giữa kỳ An toàn Bảo mật Hệ thống thông tin", options: { breakLine: true } },
    { text: "Hoàng Thanh Trà · MSSV 1150080120 · Lớp 11CNPM2", options: { breakLine: true } },
    { text: "Per-device AE · lượng tử hóa int8 · edge benchmark · MTD lai · tái lập 3-layer THARM", options: { italic: true, color: C.accent2 } },
  ], { placeholder: "body" });
  await iconCircle(s, fa.FaShieldHalved, 0.8, 0.7, 1.0, HEX.accent1, "logo");
  s.addNotes("Em chào thầy và các bạn. Đề tài DT043: phát hiện thiết bị IoT bị nhiễm botnet ngay tại thiết bị biên bằng autoencoder huấn luyện "
    + "riêng cho từng thiết bị, thu nhỏ và lượng tử hóa int8, và nối với hướng Moving Target Defence của paper chính.");

  // ================================================================ 2. Bài toán & RQ
  s = content("Mở đầu");
  s.addText("Bài toán: phát hiện botnet ngay tại edge", { placeholder: "title" });
  const probs = [
    [fa.FaVideo, HEX.accent3, "Thiết bị IoT dễ bị chiếm", "Mật khẩu mặc định, ít vá – Mirai, BASHLITE chiếm hàng loạt để DDoS"],
    [fa.FaMicrochip, HEX.accent5, "Edge có tài nguyên hạn chế", "Bộ phát hiện phải nhỏ (KB), nhanh (µs), ít RAM và năng lượng"],
    [fa.FaFingerprint, HEX.accent1, "Mỗi thiết bị một hành vi", "Học benign riêng từng thiết bị, cảnh báo khi lỗi tái tạo tăng"],
  ];
  for (let i = 0; i < probs.length; i++) {
    const y = 1.55 + i * 1.6;
    await iconCircle(s, probs[i][0], 0.7, y, 0.9, probs[i][1], "prob" + i);
    text(s, probs[i][2], { x: 1.85, y, w: 5.0, h: 0.45, fontSize: 19, bold: true, color: C.text2 });
    text(s, probs[i][3], { x: 1.85, y: y + 0.48, w: 5.0, h: 0.9, fontSize: 15 });
  }
  card(s, 7.3, 1.45, 5.4, 5.2, HEX.lt2, "rq-card");
  text(s, "Câu hỏi nghiên cứu", { x: 7.6, y: 1.65, w: 4.8, h: 0.45, fontSize: 19, bold: true, color: C.text2 });
  const rqs = ["RQ1 Tái lập baseline Meidan 2018", "RQ2 Per-device có hơn model chung?", "RQ3 AE nhẹ giữ chất lượng?",
    "RQ4 int8 + hiệu chỉnh ngưỡng", "RQ5 Chạy được trên edge?", "RQ6 AE kích hoạt MTD lai"];
  s.addText(rqs.map((r, i) => ({ text: r, options: { bullet: true, breakLine: i < rqs.length - 1 } })),
    { x: 7.6, y: 2.2, w: 4.9, h: 3.6, fontSize: 16, color: C.text1, paraSpaceAfter: 8, valign: "top", margin: 0, isTextBox: true });
  text(s, "Tiêu chí thành công chốt trước khi chạy (SHA-256 ghi trong nhật ký)", { x: 7.6, y: 5.85, w: 4.9, h: 0.6, fontSize: 12, italic: true, color: C.accent4 });
  s.addNotes("Thiết bị IoT dễ bị chiếm, edge có tài nguyên hạn chế, mỗi thiết bị một hành vi. Sáu câu hỏi nghiên cứu, tiêu chí định lượng chốt "
    + "và lưu checksum trước khi chạy để không chỉnh theo kết quả.");

  // ================================================================ 3. Hai track
  s = content("Mở đầu");
  s.addText("Paper chính nói về MTD → chiến lược hai track", { placeholder: "title" });
  text(s, "Masud et al. (2025, Computers & Security 153:104380) – hybrid Moving Target Defence trên mô hình 3-layer THARM; "
    + "không dùng autoencoder, N-BaIoT hay edge.", { x: 0.6, y: 1.35, w: 12.1, h: 0.7, fontSize: 15, color: C.accent4 });
  const tracks = [
    ["Track A · phát hiện", fa.FaBrain, HEX.accent1, ["Per-device AE trên N-BaIoT, baseline Meidan 2018", "Model nhẹ + int8 + hiệu chỉnh ngưỡng", "Edge benchmark trên 1 lõi E-core"]],
    ["Track B · MTD", fa.FaShuffle, HEX.accent2, ["Tái lập 3-layer THARM bằng đúng CVE/topology của paper (E11)", "Shuffle / diversity / redundancy và tổ hợp", "MTD lai: cảnh báo AE kích hoạt move"]],
  ];
  for (let i = 0; i < 2; i++) {
    const x = 0.6 + i * 6.35;
    card(s, x, 2.25, 5.75, 3.4, HEX.lt2, "track" + i);
    await iconCircle(s, tracks[i][1], x + 0.3, 2.5, 0.8, tracks[i][2], "trackicon" + i);
    text(s, tracks[i][0], { x: x + 1.3, y: 2.65, w: 4.2, h: 0.5, fontSize: 20, bold: true, color: C.text2 });
    s.addText(tracks[i][3].map((t, j) => ({ text: t, options: { bullet: true, breakLine: j < tracks[i][3].length - 1 } })),
      { x: x + 0.4, y: 3.55, w: 5.0, h: 1.95, fontSize: 16, color: C.text1, paraSpaceAfter: 8, valign: "top", margin: 0, isTextBox: true });
  }
  s.addShape(pres.shapes.RIGHT_ARROW, { x: 6.12, y: 3.7, w: 0.6, h: 0.5, fill: { color: HEX.accent3 }, line: { color: HEX.accent3 }, objectName: "track-arrow" });
  text(s, "Cầu nối: cửa sổ cảnh báo của AE (Track A) là sự kiện kích hoạt MTD event-based (Track B)",
    { x: 0.6, y: 5.95, w: 12.1, h: 0.5, fontSize: 16, bold: true, color: C.accent3, align: "center" });
  s.addNotes("Paper chính nói về MTD, không dùng autoencoder. Em chia hai track: A phát hiện bằng AE theo Meidan; B tái lập 3-layer THARM "
    + "bằng đúng dữ liệu của paper và dùng cảnh báo AE để kích hoạt MTD lai.");

  // ================================================================ 4. Dữ liệu & chống rò rỉ
  pres.addSection({ title: "Dữ liệu & phương pháp" });
  s = content("Dữ liệu & phương pháp");
  s.addText("Dữ liệu N-BaIoT và chống rò rỉ train/test", { placeholder: "title" });
  const st = [[(D.data.rows_raw / 1e6).toFixed(2) + "M", "dòng · UCI, CC BY 4.0 · 107 file khớp SHA-256"],
    [nf(D.data.dups), "dòng trùng lặp bị loại (2.2%)"], [D.data.ratio_min + "–" + D.data.ratio_max + "×", "attack nhiều hơn benign → dùng macro-F1, FPR"]];
  st.forEach((v, i) => stat(s, 0.6 + i * 4.1, 1.45, 3.8, v[0], v[1], i === 1 ? HEX.accent3 : HEX.dk2, "stat" + i));
  const parts = [["DStrn · train AE + fit scaler", HEX.accent1], ["DSopt · ngưỡng tr*, cửa sổ ws*", HEX.accent5], ["Test benign + mọi tấn công", HEX.accent3]];
  parts.forEach((p, i) => {
    const x = 0.6 + i * 4.1;
    s.addShape(pres.shapes.RECTANGLE, { x, y: 3.35, w: 3.7, h: 0.8, fill: { color: p[1] }, line: { color: p[1] }, objectName: "split" + i });
    text(s, p[0], { x: x + 0.15, y: 3.35, w: 3.4, h: 0.8, fontSize: 15, bold: true, color: C.background1, valign: "middle", align: "center" });
  });
  text(s, "← chia benign theo thời gian 1/3 · 1/3 · 1/3; khoảng trắng giữa các khối = 500 dòng đệm bị bỏ →", { x: 0.6, y: 4.25, w: 12.1, h: 0.4, fontSize: 13, color: C.accent4, align: "center" });
  const chk = ["Khử trùng lặp trong từng file; loại dòng test trùng hash với train", "Scaler fit chỉ trên DStrn; ngưỡng/cửa sổ chỉ từ DSopt",
    "Đối chứng E6 cố tình chia ngẫu nhiên: FPR \"đẹp giả\" 0.0006 so với 0.0025"];
  s.addText(chk.map((t, i) => ({ text: t, options: { bullet: true, breakLine: i < chk.length - 1 } })),
    { x: 0.6, y: 4.85, w: 12.1, h: 1.8, fontSize: 16, color: C.text1, paraSpaceAfter: 8, valign: "top", margin: 0, isTextBox: true });
  s.addNotes("7,06 triệu dòng, 115 đặc trưng, 9 thiết bị; khử 157.779 dòng trùng, dữ liệu mất cân bằng nên không dùng Accuracy. Dòng liền kề "
    + "gần giống nhau nên chia theo thời gian có vùng đệm 500 dòng; mỗi biện pháp chống rò rỉ đều có unit test.");

  // ================================================================ 5. Mô hình & hệ thống
  s = content("Dữ liệu & phương pháp");
  s.addText("Pipeline, mô hình so sánh và hệ thống 4 tầng", { placeholder: "title" });
  const steps = ["z-score\nper-device", "Autoencoder\n(benign)", "MSE tái tạo", "tr* = mean+std\nws* vote", "TFLite int8\n+ hiệu chỉnh"];
  steps.forEach((t, i) => {
    const x = 0.6 + i * 2.5;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y: 1.45, w: 2.1, h: 1.0, rectRadius: 0.1, fill: { color: i === 4 ? HEX.accent2 : HEX.dk2 }, line: { color: i === 4 ? HEX.accent2 : HEX.dk2 }, objectName: "step" + i });
    text(s, t, { x, y: 1.45, w: 2.1, h: 1.0, fontSize: 14, bold: true, color: i === 4 ? C.text1 : C.background1, align: "center", valign: "middle" });
    if (i < 4) s.addShape(pres.shapes.RIGHT_ARROW, { x: x + 2.13, y: 1.78, w: 0.34, h: 0.34, fill: { color: HEX.accent4 }, line: { color: HEX.accent4 }, objectName: "arrow" + i });
  });
  const rows = [["Mô hình", "Kiến trúc", "Tham số"], ["B0 Meidan", "115-86-58-38-29-…", "36,876"], ["B1 chung", "B0 dùng chung 9 thiết bị", "36,876"],
    ["B2", "Isolation Forest", "–"], ["V1 nhẹ", "115-32-8-32-115", "8,059"]];
  s.addTable(rows.map((r, i) => r.map((c) => ({ text: c, options: { bold: i === 0, color: i === 0 ? HEX.lt1 : HEX.dk1, fill: { color: i === 0 ? HEX.accent1 : (i % 2 ? "FFFFFF" : HEX.lt2) } } }))),
    { x: 0.6, y: 2.85, w: 6.6, colW: [1.6, 3.4, 1.6], fontSize: 14, border: { type: "solid", pt: 0.5, color: "D0DAE0" }, rowH: 0.5, valign: "middle", objectName: "model-table" });
  const tiers = [[fa.FaBrain, "AI", "huấn luyện, int8, xuất gói có SHA-256", HEX.accent1], [fa.FaServer, "Backend", "FastAPI, TFLite 1 luồng, từ chối gói bị sửa", HEX.accent5],
    [fa.FaDatabase, "Database", "SQLite: cảnh báo, hành động MTD", HEX.accent2], [fa.FaDisplay, "Frontend", "dashboard phát lại, biểu đồ MSE", HEX.accent3]];
  for (let i = 0; i < 4; i++) {
    const y = 2.85 + i * 0.85;
    await iconCircle(s, tiers[i][0], 7.6, y, 0.65, tiers[i][3], "tier" + i);
    text(s, tiers[i][1], { x: 8.45, y: y - 0.04, w: 4.2, h: 0.35, fontSize: 16, bold: true, color: C.text2 });
    text(s, tiers[i][2], { x: 8.45, y: y + 0.3, w: 4.2, h: 0.4, fontSize: 13 });
  }
  text(s, "54 test tự động: unit · integration · negative (gói bị sửa 1 byte, path traversal, sai số chiều)", { x: 0.6, y: 6.3, w: 12.1, h: 0.4, fontSize: 13, italic: true, color: C.accent4 });
  s.addNotes("Pipeline theo Meidan: chuẩn hóa per-device, AE học benign, ngưỡng mean + std, vote cửa sổ; cải tiến là V1 chỉ 8 nghìn tham số, "
    + "int8 rồi hiệu chỉnh ngưỡng. Hệ thống tách 4 tầng, AI và backend chỉ nói chuyện qua gói có checksum. Tiếp theo em demo.");

  // ================================================================ 6. Demo
  s = content("Dữ liệu & phương pháp");
  s.addText("Demo: phát hiện + cảnh báo + MTD trên dashboard", { placeholder: "title" });
  s.addImage({ path: path.join(FIG, "demo_dashboard_crop.png"), x: 0.6, y: 1.35, w: 6.35, h: 5.49, objectName: "demo-img",
    shadow: { type: "outer", color: "000000", opacity: 0.18, blur: 6, offset: 2, angle: 90 } });
  const demo = [
    [fa.FaBug, HEX.accent3, "mirai/syn (Danmini)", "1989/1989 cửa sổ cảnh báo → cảnh báo high + shuffle IP + đổi firmware"],
    [fa.FaCircleCheck, HEX.accent6, "benign (Ennio, phần test)", "0 cảnh báo – không báo động giả"],
    [fa.FaTriangleExclamation, HEX.accent2, "gafgyt/tcp (Ennio)", "0 cảnh báo – đúng lỗi bỏ sót đã phân tích"],
    [fa.FaClock, HEX.accent5, "MTD time-based", "Lưới an toàn cho tấn công AE bỏ sót"],
  ];
  for (let i = 0; i < demo.length; i++) {
    const y = 1.45 + i * 1.3;
    await iconCircle(s, demo[i][0], 7.3, y, 0.75, demo[i][1], "demo" + i);
    text(s, demo[i][2], { x: 8.25, y: y - 0.02, w: 4.45, h: 0.4, fontSize: 17, bold: true, color: C.text2 });
    text(s, demo[i][3], { x: 8.25, y: y + 0.4, w: 4.45, h: 0.8, fontSize: 14 });
  }
  text(s, "Chạy: uvicorn backend.app.main:app → http://127.0.0.1:8000/", { x: 7.3, y: 6.45, w: 5.4, h: 0.4, fontSize: 12, italic: true, color: C.accent4 });
  s.addNotes("Demo trực tiếp (90 giây): 9 model đã nạp; phát lại mirai/syn → 1989/1989 cửa sổ cảnh báo, cảnh báo high và 2 hành động MTD ghi vào CSDL; "
    + "benign không cảnh báo; gafgyt/tcp bị bỏ sót – em không che giấu điểm yếu; cuối cùng chạy MTD time-based làm lưới an toàn.");

  // ================================================================ 7. Kết quả & lỗi chính
  pres.addSection({ title: "Kết quả" });
  s = content("Kết quả");
  s.addText("Kết quả: FPR rất thấp, lỗi tập trung ở flood tcp/udp", { placeholder: "title" });
  const order = ["E1_baseline", "E2_shared_pdnorm", "E3_iforest", "E4_light"].filter((k) => cf[k]);
  s.addChart(pres.charts.BAR, [{ name: "macro-F1", labels: order.map((k) => lbl[k]), values: order.map((k) => cf[k].macro_f1) }],
    { x: 0.6, y: 1.4, w: 4.6, h: 4.0, barDir: "col", chartColors: [HEX.dk2], showValue: true, dataLabelPosition: "outEnd", dataLabelFormatCode: "0.00",
      valAxisMinVal: 0, valAxisMaxVal: 1, showLegend: false, showTitle: true, title: "macro-F1 (9 thiết bị × 5 seed)", titleFontSize: 14, titleColor: HEX.dk2, ...chartText, objectName: "f1-chart" });
  const rg = D.recall_groups;
  const gk = ["E1_baseline", "E4_light", "E3_iforest"].filter((k) => rg[k]);
  s.addChart(pres.charts.BAR, [
    { name: "tcp/udp", labels: gk.map((k) => lbl[k]), values: gk.map((k) => rg[k].tcp_udp) },
    { name: "8 loại còn lại", labels: gk.map((k) => lbl[k]), values: gk.map((k) => rg[k].others) },
  ], { x: 5.4, y: 1.4, w: 4.2, h: 4.0, barDir: "bar", barGrouping: "clustered", chartColors: [HEX.accent3, HEX.accent1],
    showValue: true, dataLabelPosition: "outEnd", dataLabelFormatCode: "0.00", valAxisMinVal: 0, valAxisMaxVal: 1.2,
    showLegend: true, legendPos: "b", legendFontSize: 12, showTitle: true, title: "Recall theo nhóm tấn công", titleFontSize: 14, titleColor: HEX.dk2, ...chartText, objectName: "recall-chart" });
  const b0 = cf.E1_baseline;
  stat(s, 9.9, 1.5, 2.8, f(b0.fpr, 4), "FPR của B0 (Meidan: 0.007)", HEX.accent1, "fpr");
  stat(s, 9.9, 3.3, 2.8, f(b0.tpr, 3), "TPR của B0 (Meidan: 100%)", HEX.accent3, "tpr");
  text(s, "Nguồn bị giả mạo liên tục → mỗi gói như \"luồng mới\" (weight = 1, variance = 0), MSE nằm dưới ngưỡng mean+std. "
    + "Tám loại tấn công còn lại recall ≈ 1.0.", { x: 0.6, y: 5.6, w: 12.1, h: 1.0, fontSize: 15 });
  s.addNotes("Trên 468 lần chạy, FPR chỉ 0,0025, thấp hơn Meidan, nhưng TPR 0,822. Toàn bộ suy giảm đến từ flood tcp/udp của BASHLITE: nguồn giả mạo "
    + "nên mỗi gói giống luồng mới, giống benign. Isolation Forest tốt hơn về chất lượng, em báo cáo trung thực.");

  // ================================================================ 8. int8 & edge
  s = content("Kết quả");
  s.addText("Lượng tử hóa int8 và edge benchmark", { placeholder: "title" });
  const modes = ["fp32", "fp16", "dyn", "int8"];
  s.addChart(pres.charts.BAR, [{ name: "KB", labels: modes.map((m) => "V1 " + m), values: modes.map((m) => q[`V1_${m}_keep`].kb) }],
    { x: 0.6, y: 1.4, w: 5.4, h: 4.4, barDir: "col", chartColors: [HEX.accent1, HEX.accent1, HEX.accent1, HEX.accent2],
      showValue: true, dataLabelPosition: "outEnd", dataLabelFormatCode: "0.0", showLegend: false, showTitle: true,
      title: "Kích thước file TFLite (KB)", titleFontSize: 14, titleColor: HEX.dk2, valAxisMinVal: 0, ...chartText, objectName: "quant-chart" });
  const v = e["V1_int8_P1_edge"];
  const es = [[f(v.p95_us, 1) + " µs", "p95 / mẫu (tiêu chí ≤ 1000 µs)"], [f(v.size_kb, 1) + " KB", "model (tiêu chí ≤ 50 KB)"],
    [f(v.rss_delta_mb, 1) + " MB", "RAM tăng thêm"], [nf(Math.round(v.throughput_samples_s)), "mẫu/giây trên 1 lõi E-core"]];
  es.forEach((x, i) => stat(s, 6.5 + (i % 2) * 3.15, 1.45 + Math.floor(i / 2) * 1.85, 2.95, x[0], x[1], i < 3 ? HEX.accent1 : HEX.dk2, "edge" + i));
  const k = q.V1_int8_keep, r2 = q.V1_int8_recal;
  text(s, `Hiệu chỉnh ngưỡng trên DSopt bằng chính model int8: FPR ${f(k.fpr, 4)} → ${f(r2.fpr, 4)}, cửa sổ ${k.ws} → ${r2.ws} mẫu. `
    + `Energy proxy ≈ ${f(v.energy_proxy_uJ, 1)} µJ/mẫu. RQ5 đạt với biên rất lớn.`, { x: 6.5, y: 5.2, w: 6.2, h: 1.5, fontSize: 14 });
  s.addNotes("Bản int8 chỉ 15,3 KB; giữ ngưỡng fp32 thì lệch nên em hiệu chỉnh lại trên DSopt. Trên một lõi E-core p95 chỉ 10,8 micro-giây mỗi mẫu, "
    + "khoảng 103 nghìn mẫu mỗi giây, RAM tăng 4,6 MB. Kích thước chỉ còn 45% bản fp32 do khung flatbuffer nên RQ4 không đạt.");

  // ================================================================ 9. MTD & tái lập paper chính
  s = content("Kết quả");
  s.addText("MTD: tái lập paper chính bằng đúng dữ liệu của paper", { placeholder: "title" });
  const paths = csv("tharm_paths_vs_paper.csv");
  const pathName = { shuffle: "Đường shuffle", diversity: "Đường diversity", redundancy: "Đường redundancy" };
  const prow = [["Rủi ro", "Paper", "Tái lập"], ["R_V5 (Windows 11)", "12.58", "12.578"], ["R_V7 · R_V8", "8.67 · 5.62", "8.667 · 5.625"]]
    .concat(paths.map((p) => [pathName[p["đường (ví dụ của paper)"].split(" ")[0]] || p["đường (ví dụ của paper)"],
      Number(p.R_paper).toFixed(2), Number(p.R_ours).toFixed(2) + " (" + Number(p["lệch %"]).toFixed(1) + "%)"]));
  s.addTable(prow.map((r, i) => r.map((c) => ({ text: c, options: { bold: i === 0, color: i === 0 ? HEX.lt1 : HEX.dk1, fill: { color: i === 0 ? HEX.dk2 : (i % 2 ? "FFFFFF" : HEX.lt2) } } }))),
    { x: 0.6, y: 1.4, w: 6.3, colW: [2.9, 1.5, 1.9], fontSize: 14, border: { type: "solid", pt: 0.5, color: "D0DAE0" }, rowH: 0.45, valign: "middle", objectName: "tharm-table" });
  const tr = csv("tharm_trends.csv");
  const nFig3 = tr.filter((t) => t.topology !== "Definition 2" && t["tái lập"] === "True").length;
  const nDef2 = tr.filter((t) => t.topology === "Definition 2" && t["tái lập"] === "True").length;
  stat(s, 7.3, 1.4, 2.6, nFig3 + "/7", "kết luận tái lập được (topology Hình 3)", HEX.accent1, "trend-fig3");
  stat(s, 10.1, 1.4, 2.6, nDef2 + "/7", "nếu dùng đúng Definition 2", HEX.accent3, "trend-def2");
  card(s, 7.3, 3.4, 5.4, 1.9, HEX.lt2, "tharm-note");
  text(s, "Khớp: rủi ro mức VM ±0.01, đường tấn công −0.8%. Không khớp: tổng toàn mạng – paper cắt danh sách cạnh, công thức in mâu thuẫn; "
    + "kết luận \"S+D tốt nhất\" phụ thuộc cạnh V6 → V4.", { x: 7.5, y: 3.55, w: 5.0, h: 1.65, fontSize: 14 });
  text(s, `HARM rút gọn (chu kỳ 20): ASP không MTD ${f(D.harm20.none)} → shuffle ${f(D.harm20.shuffle)} · diversity ${f(D.harm20.diversity)} · `
    + `kết hợp ${f(D.harm20.combined)}. MTD lai dùng cảnh báo AE: cùng chi phí, lộ diện ít hơn time-based.`, { x: 0.6, y: 4.4, w: 6.3, h: 1.4, fontSize: 14 });
  text(s, "Dữ liệu paper: 18 CVE OS + 14 CVE dịch vụ (Bảng 1–2), 8 VM, Definition 2; shuffle/diversity/redundancy theo mục 4.2–4.4",
    { x: 0.6, y: 6.2, w: 12.1, h: 0.5, fontSize: 12, italic: true, color: C.accent4 });
  s.addNotes("Track B: em dựng lại 3-layer THARM bằng đúng 32 CVE, 8 VM và topology của paper. Rủi ro từng VM khớp tới 0,01, ba đường tấn công lệch 0,8%; "
    + "tổng toàn mạng không ra đúng vì paper cắt danh sách cạnh và in công thức mâu thuẫn. Với topology Hình 3 tái lập 6/7 kết luận, gồm S+D tốt nhất.");

  // ================================================================ 10. Tiêu chí & kết luận
  pres.addSection({ title: "Kết luận" });
  s = content("Kết luận");
  s.addText("Đối chiếu tiêu chí và kết luận", { placeholder: "title" });
  const crit = D.criteria;
  const trows = [["RQ", "Giá trị đo", "Kết luận"]].concat(crit.map((c) => [c.RQ, c.value, c.pass ? "Đạt" : "Không đạt"]));
  s.addTable(trows.map((r, i) => r.map((c, j) => ({ text: String(c), options: {
    bold: i === 0 || j === 2, color: i === 0 ? HEX.lt1 : (j === 2 ? (c === "Đạt" ? HEX.accent6 : HEX.accent3) : HEX.dk1),
    fill: { color: i === 0 ? HEX.dk2 : (i % 2 ? "FFFFFF" : HEX.lt2) } } }))),
    { x: 0.6, y: 1.4, w: 6.4, colW: [0.9, 3.9, 1.6], fontSize: 14, rowH: 0.55, border: { type: "solid", pt: 0.5, color: "D0DAE0" }, valign: "middle", objectName: "crit-table" });
  text(s, "Không chỉnh tiêu chí sau khi có kết quả; báo cáo đủ " + D.n_runs + " lần chạy.", { x: 0.6, y: 5.1, w: 6.4, h: 0.5, fontSize: 13, italic: true, color: C.accent4 });
  card(s, 7.4, 1.4, 5.3, 5.25, HEX.dk2, "concl-card");
  const concl = ["AE per-device bắt gần tuyệt đối 8/10 loại tấn công, FPR rất thấp; bỏ sót flood tcp/udp giả mạo nguồn",
    "V1 int8 15 KB, ~10 µs/mẫu trên 1 lõi – khả thi cho edge",
    "Kết quả dao động theo seed → cần nhiều lần chạy và kiểm định",
    "Tái lập paper chính: khớp mức VM/đường, 6/7 kết luận định tính",
    "Tiếp theo: đặc trưng cho flood giả mạo · Raspberry Pi + đo điện thật"];
  s.addText(concl.map((t, i) => ({ text: t, options: { bullet: true, breakLine: i < concl.length - 1, color: i === concl.length - 1 ? C.accent2 : C.background1 } })),
    { x: 7.7, y: 1.65, w: 4.8, h: 4.8, fontSize: 16, paraSpaceAfter: 10, valign: "top", margin: 0, isTextBox: true, objectName: "concl-text" });
  s.addNotes("RQ5 về edge đạt với biên lớn, RQ1 đến RQ4 không đạt và em giữ nguyên tiêu chí. Tóm lại: AE nhẹ bắt gần tuyệt đối 8/10 loại tấn công, "
    + "chạy được trên edge, nhưng cần thêm đặc trưng cho flood giả mạo nguồn. Mã nguồn và hướng dẫn chạy lại có trên GitHub. Em cảm ơn thầy và các bạn.");

  await pres.writeFile({ fileName: OUT });
  await applyTheme(OUT, THEME);
  console.log("Đã lưu", OUT);
}

main().catch((err) => { console.error(err); process.exit(1); });
