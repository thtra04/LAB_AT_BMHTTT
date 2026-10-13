// Sinh slide thuyết trình DT043 từ report/deck_data.json (chạy: node report/build_deck.js)
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
const OUT = path.join(HERE, "SlideThuyetTrinh_DT043_1150080120_HoangThanhTra.pptx");

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
  const cf = D.configs;
  const q = D.quant;
  const e = D.edge;

  // ================================================================ 1. Tiêu đề
  pres.addSection({ title: "Mở đầu" });
  let s = pres.addSlide({ masterName: "DARK", sectionTitle: "Mở đầu" });
  s.addText("Phát hiện botnet IoT bằng autoencoder nhẹ", { placeholder: "title" });
  s.addText([
    { text: "Đề tài DT043 · Bài giữa kỳ An toàn Bảo mật Hệ thống thông tin", options: { breakLine: true } },
    { text: "Hoàng Thanh Trà · MSSV 1150080120 · Lớp 11CNPM2", options: { breakLine: true } },
    { text: "Per-device AE · lượng tử hóa int8 · edge benchmark · MTD lai", options: { italic: true, color: C.accent2 } },
  ], { placeholder: "body" });
  await iconCircle(s, fa.FaShieldHalved, 0.8, 0.7, 1.0, HEX.accent1, "logo");
  s.addNotes("Giới thiệu đề tài: phát hiện thiết bị IoT bị nhiễm botnet ngay tại edge bằng autoencoder huấn luyện riêng "
    + "cho từng thiết bị, thu nhỏ và lượng tử hóa để chạy trên thiết bị yếu, và nối với hướng Moving Target Defence của paper chính.");

  // ================================================================ 2. Bài toán
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
    text(s, probs[i][2], { x: 1.85, y: y, w: 5.0, h: 0.45, fontSize: 19, bold: true, color: C.text2 });
    text(s, probs[i][3], { x: 1.85, y: y + 0.48, w: 5.0, h: 0.9, fontSize: 15 });
  }
  card(s, 7.3, 1.45, 5.4, 5.2, HEX.lt2, "rq-card");
  text(s, "Câu hỏi nghiên cứu", { x: 7.6, y: 1.65, w: 4.8, h: 0.45, fontSize: 19, bold: true, color: C.text2 });
  const rqs = ["RQ1 Tái lập baseline Meidan 2018", "RQ2 Per-device có hơn model chung?", "RQ3 AE nhẹ giữ chất lượng?",
    "RQ4 int8 + hiệu chỉnh ngưỡng", "RQ5 Chạy được trên edge?", "RQ6 AE kích hoạt MTD lai"];
  s.addText(rqs.map((r, i) => ({ text: r, options: { bullet: true, breakLine: i < rqs.length - 1 } })),
    { x: 7.6, y: 2.2, w: 4.9, h: 3.6, fontSize: 16, color: C.text1, paraSpaceAfter: 8, valign: "top", margin: 0, isTextBox: true });
  text(s, "Tiêu chí thành công chốt trước khi chạy (SHA-256 ghi trong nhật ký)", { x: 7.6, y: 5.85, w: 4.9, h: 0.6, fontSize: 12, italic: true, color: C.accent4 });
  s.addNotes("Ba lý do của bài toán. Sáu câu hỏi nghiên cứu, mỗi câu có tiêu chí định lượng được chốt và lưu checksum trước khi chạy để không chỉnh tiêu chí theo kết quả.");

  // ================================================================ 3. Hai track
  s = content("Mở đầu");
  s.addText("Paper chính nói về MTD → chiến lược hai track", { placeholder: "title" });
  text(s, "Masud et al. (2025, Computers & Security) – hybrid Moving Target Defence + mô hình đồ thị tấn công 3-layer THARM; "
    + "không dùng autoencoder, N-BaIoT hay edge.", { x: 0.6, y: 1.35, w: 12.1, h: 0.7, fontSize: 15, color: C.accent4 });
  const tracks = [
    ["Track A · lõi · ~70%", fa.FaBrain, HEX.accent1, ["Per-device AE trên N-BaIoT", "Baseline: Meidan 2018", "Model nhẹ + int8 + hiệu chỉnh ngưỡng", "Edge benchmark"]],
    ["Track B · cầu nối · ~30%", fa.FaShuffle, HEX.accent2, ["Tái lập xu hướng MTD: shuffle / diversity / kết hợp", "Mô hình HARM rút gọn", "MTD lai: cảnh báo AE kích hoạt move"]],
  ];
  for (let i = 0; i < 2; i++) {
    const x = 0.6 + i * 6.35;
    card(s, x, 2.25, 5.75, 3.4, HEX.lt2, "track" + i);
    await iconCircle(s, tracks[i][1], x + 0.3, 2.5, 0.8, tracks[i][2], "trackicon" + i);
    text(s, tracks[i][0], { x: x + 1.3, y: 2.65, w: 4.2, h: 0.5, fontSize: 20, bold: true, color: C.text2 });
    s.addText(tracks[i][3].map((t, j) => ({ text: t, options: { bullet: true, breakLine: j < tracks[i][3].length - 1 } })),
      { x: x + 0.4, y: 3.55, w: 5.0, h: 1.95, fontSize: 16, color: C.text1, paraSpaceAfter: 8, valign: "top", margin: 0, isTextBox: true });
  }
  text(s, "Cầu nối: cửa sổ cảnh báo của AE (Track A) là sự kiện kích hoạt MTD event-based (Track B)",
    { x: 0.6, y: 5.95, w: 12.1, h: 0.5, fontSize: 16, bold: true, color: C.accent3, align: "center" });
  s.addShape(pres.shapes.RIGHT_ARROW, { x: 6.12, y: 3.7, w: 0.6, h: 0.5, fill: { color: HEX.accent3 }, line: { color: HEX.accent3 }, objectName: "track-arrow" });
  s.addNotes("Phát hiện quan trọng khi đọc paper: paper chính lệch chủ đề. Em không gượng ép tái lập số liệu MTD bằng autoencoder mà chia hai track; "
    + "track B nối hai mảng bằng cách dùng cảnh báo AE làm bộ kích hoạt event-based cho MTD lai.");

  // ================================================================ 4. Dữ liệu
  pres.addSection({ title: "Dữ liệu & phương pháp" });
  s = content("Dữ liệu & phương pháp");
  s.addText("Dữ liệu N-BaIoT: lớn, trùng lặp và mất cân bằng", { placeholder: "title" });
  const st = [[(D.data.rows_raw / 1e6).toFixed(2) + "M", "dòng (UCI, CC BY 4.0)", HEX.dk2],
    ["115", "đặc trưng = 23 thống kê × 5 cửa sổ", HEX.dk2], ["9", "thiết bị IoT thương mại", HEX.dk2],
    ["10", "kiểu tấn công Mirai + BASHLITE", HEX.dk2]];
  st.forEach((v, i) => stat(s, 0.6 + i * 3.1, 1.5, 2.8, v[0], v[1], v[2], "stat" + i));
  card(s, 0.6, 3.75, 5.85, 2.4, HEX.lt2, "dup-card");
  text(s, nf(D.data.dups), { x: 0.9, y: 3.95, w: 5.3, h: 0.9, fontSize: 36, bold: true, color: C.accent3, fontFace: THEME.headFontFace });
  text(s, "dòng trùng lặp chính xác bị loại (benign Danmini 18.5%; gafgyt tcp/udp). Còn " + nf(D.data.rows_dedup) + " dòng; "
    + "manifest SHA-256 cho 107 file.", { x: 0.9, y: 4.85, w: 5.3, h: 1.6, fontSize: 15 });
  card(s, 6.85, 3.75, 5.85, 2.4, HEX.lt2, "imb-card");
  text(s, D.data.ratio_min + "–" + D.data.ratio_max + "×", { x: 7.15, y: 3.95, w: 5.3, h: 0.9, fontSize: 36, bold: true, color: C.accent2, fontFace: THEME.headFontFace });
  text(s, "attack nhiều hơn benign → Accuracy vô nghĩa; metric chính là macro-F1 và FPR mức cửa sổ, kèm F1 khi test cân bằng.",
    { x: 7.15, y: 4.85, w: 5.3, h: 1.6, fontSize: 15 });
  s.addNotes("Dữ liệu ghi rõ nguồn, giấy phép, ngày tải, checksum. Hai vấn đề chất lượng: trùng lặp và mất cân bằng nặng – quyết định cách chọn metric.");

  // ================================================================ 5. Chống rò rỉ
  s = content("Dữ liệu & phương pháp");
  s.addText("Chống rò rỉ: chia theo thời gian, có vùng đệm", { placeholder: "title" });
  const parts = [["DStrn · train AE + fit scaler", HEX.accent1], ["DSopt · ngưỡng tr*, cửa sổ ws*", HEX.accent5], ["Test benign + mọi tấn công", HEX.accent3]];
  parts.forEach((p, i) => {
    const x = 0.6 + i * 4.1;
    s.addShape(pres.shapes.RECTANGLE, { x, y: 1.6, w: 3.7, h: 0.9, fill: { color: p[1] }, line: { color: p[1] }, objectName: "split" + i });
    text(s, p[0], { x: x + 0.15, y: 1.6, w: 3.4, h: 0.9, fontSize: 15, bold: true, color: C.background1, valign: "middle", align: "center" });
  });
  text(s, "← thứ tự thời gian của benign (1/3 · 1/3 · 1/3 như Meidan); khoảng trắng giữa các khối = 500 dòng đệm bị bỏ →", { x: 0.6, y: 2.65, w: 12.1, h: 0.4, fontSize: 13, color: C.accent4, align: "center" });
  stat(s, 0.6, 3.35, 5.6, D.data.ac_min.toFixed(2) + "–" + D.data.ac_max.toFixed(2), "tự tương quan bậc 1 của benign theo thứ tự gốc (xáo trộn: ≈ 0.00) → chia ngẫu nhiên sẽ rò rỉ", HEX.accent2, "ac");
  const chk = ["Khử trùng lặp trong từng file", "Scaler fit chỉ trên DStrn, gắn tên thiết bị", "Ngưỡng/cửa sổ chỉ từ DSopt benign",
    "Vote không vượt ranh giới file", "Đối chứng E6: cố tình làm sai để đo sai lệch"];
  s.addText(chk.map((t, i) => ({ text: t, options: { bullet: true, breakLine: i < chk.length - 1 } })),
    { x: 6.7, y: 3.35, w: 6.0, h: 3.2, fontSize: 16, color: C.text1, paraSpaceAfter: 8, valign: "top", margin: 0, isTextBox: true });
  s.addNotes("EDA cho thấy các dòng liền kề gần giống nhau, nên chia ngẫu nhiên là rò rỉ. Mỗi biện pháp chống rò rỉ đều có unit test.");

  // ================================================================ 6. Pipeline & mô hình
  s = content("Dữ liệu & phương pháp");
  s.addText("Pipeline và các mô hình so sánh", { placeholder: "title" });
  const steps = ["z-score\nper-device", "Autoencoder\n(benign)", "MSE tái tạo", "tr* = mean+std\nws* vote", "TFLite int8\n+ hiệu chỉnh"];
  steps.forEach((t, i) => {
    const x = 0.6 + i * 2.5;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y: 1.5, w: 2.1, h: 1.1, rectRadius: 0.1, fill: { color: i === 4 ? HEX.accent2 : HEX.dk2 }, line: { color: i === 4 ? HEX.accent2 : HEX.dk2 }, objectName: "step" + i });
    text(s, t, { x, y: 1.5, w: 2.1, h: 1.1, fontSize: 14, bold: true, color: i === 4 ? C.text1 : C.background1, align: "center", valign: "middle" });
    if (i < 4) s.addShape(pres.shapes.RIGHT_ARROW, { x: x + 2.13, y: 1.88, w: 0.34, h: 0.34, fill: { color: HEX.accent4 }, line: { color: HEX.accent4 }, objectName: "arrow" + i });
  });
  const rows = [["Mô hình", "Kiến trúc", "Tham số", "Vai trò"],
    ["B0", "115-86-58-38-29-…-115", "36,876", "Baseline Meidan, per-device"],
    ["B1", "B0 dùng chung 9 thiết bị", "36,876", "Kiểm tra giả thuyết per-device"],
    ["B2", "Isolation Forest", "–", "Baseline không phải NN"],
    ["V1", "115-32-8-32-115", "8,059", "AE nhẹ (21.9% tham số)"],
    ["V2", "23-12-4-12-23 × 5 cửa sổ", "~700", "Bớt cả đặc trưng"]];
  s.addTable(rows.map((r, i) => r.map((c) => ({ text: c, options: { bold: i === 0, color: i === 0 ? HEX.lt1 : HEX.dk1, fill: { color: i === 0 ? HEX.accent1 : (i % 2 ? "FFFFFF" : HEX.lt2) } } }))),
    { x: 0.6, y: 3.05, w: 12.1, colW: [1.3, 4.0, 1.8, 5.0], fontSize: 14, border: { type: "solid", pt: 0.5, color: "D0DAE0" }, rowH: 0.5, valign: "middle", objectName: "model-table" });
  s.addNotes("Pipeline giống Meidan nhưng thống nhất tối ưu bằng Adam + early stopping, 5 seed. Cải tiến chính là V1 lượng tử hóa int8 rồi tính lại ngưỡng trên DSopt bằng chính model int8.");

  // ================================================================ 7. Kiến trúc hệ thống
  s = content("Dữ liệu & phương pháp");
  s.addText("Hệ thống demo tách 4 tầng: AI · BE · DB · FE", { placeholder: "title" });
  const tiers = [[fa.FaBrain, "AI", "ai/ – huấn luyện, đánh giá, lượng tử hóa, benchmark, xuất gói triển khai", HEX.accent1],
    [fa.FaServer, "Backend", "FastAPI – nạp gói (kiểm SHA-256), suy luận TFLite 1 luồng, API detect/replay/alerts/MTD", HEX.accent5],
    [fa.FaDatabase, "Database", "SQLite – devices, models, detection_batches, alerts, mtd_actions, experiment_results", HEX.accent2],
    [fa.FaDisplay, "Frontend", "Dashboard HTML/JS – thiết bị, phát lại lưu lượng, biểu đồ MSE, cảnh báo, nhật ký MTD", HEX.accent3]];
  for (let i = 0; i < 4; i++) {
    const x = 0.6 + i * 3.1;
    card(s, x, 1.55, 2.8, 3.6, HEX.lt2, "tier" + i);
    await iconCircle(s, tiers[i][0], x + 0.9, 1.8, 1.0, tiers[i][3], "tiericon" + i);
    text(s, tiers[i][1], { x: x + 0.2, y: 2.95, w: 2.4, h: 0.5, fontSize: 20, bold: true, color: C.text2, align: "center" });
    text(s, tiers[i][2], { x: x + 0.25, y: 3.5, w: 2.3, h: 2.0, fontSize: 13 });
  }
  text(s, "Hợp đồng AI → BE: artifacts/deploy/<thiết bị>/{model.tflite, scaler.json, meta.json} · 42 test tự động (30 AI + 12 BE/DB)",
    { x: 0.6, y: 5.5, w: 12.1, h: 0.6, fontSize: 14, italic: true, color: C.accent4 });
  s.addNotes("Tầng AI và BE chỉ nói chuyện qua gói triển khai có checksum, nên thay model không phải sửa backend. Có test từ chối gói bị sửa 1 byte và chặn path traversal.");

  // ================================================================ 7b. Demo
  s = content("Dữ liệu & phương pháp");
  s.addText("Demo: phát hiện + cảnh báo + MTD trên dashboard", { placeholder: "title" });
  s.addImage({ path: path.join(FIG, "demo_dashboard_crop.png"), x: 0.6, y: 1.35, w: 6.35, h: 5.49, objectName: "demo-img",
    shadow: { type: "outer", color: "000000", opacity: 0.18, blur: 6, offset: 2, angle: 90 } });
  const demo = [
    [fa.FaBug, HEX.accent3, "mirai/syn (Danmini)", "100% cửa sổ cảnh báo → cảnh báo mức high + shuffle IP + đổi firmware (event-based)"],
    [fa.FaCircleCheck, HEX.accent6, "benign (phần test)", "Không cảnh báo, không move vô ích"],
    [fa.FaTriangleExclamation, HEX.accent2, "gafgyt/tcp (Ennio)", "Không vượt ngưỡng – đúng lỗi bỏ sót đã phân tích"],
    [fa.FaGaugeHigh, HEX.accent5, "Suy luận V1 int8", "Vài µs/mẫu, 1 luồng; mọi lô ghi vào SQLite"],
  ];
  for (let i = 0; i < demo.length; i++) {
    const y = 1.45 + i * 1.3;
    await iconCircle(s, demo[i][0], 7.3, y, 0.75, demo[i][1], "demo" + i);
    text(s, demo[i][2], { x: 8.25, y: y - 0.02, w: 4.45, h: 0.4, fontSize: 17, bold: true, color: C.text2 });
    text(s, demo[i][3], { x: 8.25, y: y + 0.4, w: 4.45, h: 0.8, fontSize: 14 });
  }
  text(s, "Mở: http://127.0.0.1:8000/?replay=Danmini_Doorbell:mirai/syn", { x: 7.3, y: 6.45, w: 5.4, h: 0.4, fontSize: 12, italic: true, color: C.accent4 });
  s.addNotes("Demo trực tiếp: phát lại dữ liệu test công khai qua API. Tấn công Mirai sinh cảnh báo và hai hành động MTD được ghi vào CSDL; "
    + "benign không cảnh báo; tcp của Ennio bị bỏ sót đúng như phân tích – demo không che giấu điểm yếu.");

  // ================================================================ 8. Kết quả tổng quan
  pres.addSection({ title: "Kết quả" });
  s = content("Kết quả");
  s.addText("Kết quả tổng quan (mức cửa sổ, 9 thiết bị × seed)", { placeholder: "title" });
  const order = ["E1_baseline", "E2_global", "E2_shared_pdnorm", "E3_iforest", "E4_light"].filter((k) => cf[k]);
  const lbl = { E1_baseline: "B0 AE", E2_global: "B1 global", E2_shared_pdnorm: "B1 chung+pdnorm", E3_iforest: "B2 IForest", E4_light: "V1 AE nhẹ" };
  s.addChart(pres.charts.BAR, [
    { name: "macro-F1", labels: order.map((k) => lbl[k]), values: order.map((k) => cf[k].macro_f1) },
    { name: "F1 cân bằng", labels: order.map((k) => lbl[k]), values: order.map((k) => cf[k].f1_bal) },
  ], { x: 0.6, y: 1.4, w: 7.6, h: 5.3, barDir: "col", barGrouping: "clustered", chartColors: [HEX.dk2, HEX.accent1],
    showValue: true, dataLabelPosition: "outEnd", dataLabelFormatCode: "0.00", valAxisMinVal: 0, valAxisMaxVal: 1,
    showLegend: true, legendPos: "b", legendFontSize: 12, ...chartText, objectName: "overview-chart" });
  const b0 = cf.E1_baseline;
  stat(s, 8.7, 1.5, 4.0, f(b0.fpr, 4), "FPR của B0 – thấp hơn Meidan (0.007)", HEX.accent1, "fpr");
  stat(s, 8.7, 3.35, 4.0, f(b0.tpr, 3), "TPR của B0 – không đạt 100% như paper", HEX.accent3, "tpr");
  text(s, "ROC-AUC mức mẫu vẫn > 0.99: điểm MSE phân tách tốt, vấn đề nằm ở ngưỡng.", { x: 8.7, y: 5.3, w: 4.0, h: 1.2, fontSize: 14, italic: true, color: C.accent4 });
  s.addNotes("Báo cáo trung thực: FPR rất thấp nhưng TPR không đạt 100% như Meidan. F1 cân bằng phản ánh tốt hơn macro-F1 khi test mất cân bằng.");

  // ================================================================ 9. Lỗi tcp/udp
  s = content("Kết quả");
  s.addText("Lỗi chính: flood BASHLITE tcp/udp trông giống benign", { placeholder: "title" });
  s.addImage({ path: path.join(FIG, "fig_error_mse_hist.png"), x: 0.6, y: 1.45, w: 7.4, h: 3.37, objectName: "err-fig" });
  text(s, "Nguồn bị giả mạo liên tục → mỗi gói như \"luồng mới\": weight = 1, variance = 0, 60 byte. MSE ≈ 0.17 – trên phần lớn benign "
    + "nhưng dưới ngưỡng mean+std bị đuôi phân phối kéo lên.", { x: 0.6, y: 5.0, w: 7.4, h: 1.6, fontSize: 15 });
  const rg = D.recall_groups;
  const gk = ["E1_baseline", "E4_light", "E2_global", "E3_iforest"].filter((k) => rg[k]);
  s.addChart(pres.charts.BAR, [
    { name: "tcp/udp", labels: gk.map((k) => lbl[k]), values: gk.map((k) => rg[k].tcp_udp) },
    { name: "8 loại còn lại", labels: gk.map((k) => lbl[k]), values: gk.map((k) => rg[k].others) },
  ], { x: 8.3, y: 1.45, w: 4.4, h: 5.2, barDir: "bar", barGrouping: "clustered", chartColors: [HEX.accent3, HEX.accent1],
    showValue: true, dataLabelPosition: "outEnd", dataLabelFormatCode: "0.00", valAxisMinVal: 0, valAxisMaxVal: 1.15,
    showLegend: true, legendPos: "b", legendFontSize: 12, showTitle: true, title: "Recall theo nhóm tấn công", titleFontSize: 14,
    titleColor: HEX.dk2, ...chartText, objectName: "recall-chart" });
  s.addNotes("Toàn bộ suy giảm đến từ hai file gafgyt tcp và udp; tám loại tấn công còn lại recall gần 1. Đã kiểm tra trên dữ liệu thô để giải thích nguyên nhân.");

  // ================================================================ 10. Hậu kiểm ngưỡng
  s = content("Kết quả");
  s.addText("Hậu kiểm: hạ ngưỡng bắt được tcp/udp nhưng phải trả giá", { placeholder: "title" });
  const ph = D.posthoc.filter((r) => r.exp === "E4_light");
  const orig = ph.find((r) => r.rule.startsWith("mean"));
  const p75 = ph.find((r) => r.rule === "p75");
  const cols = [["Ngưỡng mean+std (gốc)", orig, HEX.dk2], ["Ngưỡng p75 của DSopt", p75, HEX.accent2]];
  cols.forEach((cdef, i) => {
    const x = 0.6 + i * 6.25;
    card(s, x, 1.5, 5.85, 4.4, HEX.lt2, "ph" + i);
    text(s, cdef[0], { x: x + 0.3, y: 1.7, w: 5.3, h: 0.5, fontSize: 20, bold: true, color: C.text2 });
    const r = cdef[1];
    const items = [["macro-F1", f(r.macro_f1)], ["Recall tcp/udp", f(r.recall_tcp_udp, 2)], ["FPR test", f(r.fpr, 4)], ["Cửa sổ ws*", Math.round(r.ws) + " mẫu"]];
    items.forEach((it, j) => {
      const yy = 2.4 + j * 0.85;
      text(s, it[0], { x: x + 0.3, y: yy, w: 2.6, h: 0.7, fontSize: 16, color: C.accent4, valign: "middle" });
      text(s, it[1], { x: x + 2.9, y: yy, w: 2.7, h: 0.7, fontSize: 26, bold: true, color: cdef[2], fontFace: THEME.headFontFace, valign: "middle" });
    });
  });
  text(s, "Phân tích khám phá làm SAU khi xem test (V1, seed 42) → chỉ để giải thích, không tuyên bố cải tiến. FPR = 0 trên DSopt nhưng tăng trên test: benign trôi theo thời gian.",
    { x: 0.6, y: 6.1, w: 12.1, h: 0.7, fontSize: 14, italic: true, color: C.accent4 });
  s.addNotes("Trade-off rõ ràng: bắt được tấn công giống benign thì phải chấp nhận cửa sổ dài (phát hiện chậm) và FPR cao hơn. Em ghi rõ đây là hậu kiểm.");

  // ================================================================ 11. Lượng tử hóa
  s = content("Kết quả");
  s.addText("Lượng tử hóa: nhỏ hơn, và cần hiệu chỉnh lại ngưỡng", { placeholder: "title" });
  const modes = ["fp32", "fp16", "dyn", "int8"];
  s.addChart(pres.charts.BAR, [{ name: "KB", labels: modes.map((m) => "V1 " + m), values: modes.map((m) => q[`V1_${m}_keep`].kb) }],
    { x: 0.6, y: 1.45, w: 6.0, h: 5.2, barDir: "col", chartColors: [HEX.accent1, HEX.accent1, HEX.accent1, HEX.accent2],
      showValue: true, dataLabelPosition: "outEnd", dataLabelFormatCode: "0.0", showLegend: false, showTitle: true,
      title: "Kích thước file TFLite (KB)", titleFontSize: 14, titleColor: HEX.dk2, valAxisMinVal: 0, ...chartText, objectName: "quant-chart" });
  const k = q.V1_int8_keep, r2 = q.V1_int8_recal;
  card(s, 7.0, 1.45, 5.7, 5.2, HEX.lt2, "recal-card");
  text(s, "int8: giữ ngưỡng fp32 → hiệu chỉnh trên DSopt", { x: 7.3, y: 1.65, w: 5.1, h: 0.5, fontSize: 17, bold: true, color: C.text2 });
  const rr = [["FPR", f(k.fpr, 4), f(r2.fpr, 4)], ["Cửa sổ ws*", String(k.ws), String(r2.ws)], ["macro-F1", f(k.macro_f1), f(r2.macro_f1)]];
  rr.forEach((it, j) => {
    const yy = 2.35 + j * 1.15;
    text(s, it[0], { x: 7.3, y: yy, w: 1.7, h: 0.8, fontSize: 15, color: C.accent4, valign: "middle" });
    text(s, it[1] + "  →  " + it[2], { x: 9.0, y: yy, w: 3.5, h: 0.8, fontSize: 24, bold: true, color: j < 2 ? C.accent1 : C.accent3, fontFace: THEME.headFontFace, valign: "middle" });
  });
  text(s, "Hiệu chỉnh giảm FPR và độ trễ, nhưng macro-F1 giảm: khi giữ ngưỡng cũ, nhiễu int8 \"vô tình\" đẩy tcp/udp vượt ngưỡng.",
    { x: 7.3, y: 5.55, w: 5.1, h: 1.0, fontSize: 13, italic: true, color: C.accent4 });
  s.addNotes("Trọng số giảm 4 lần nhưng file chỉ còn khoảng 45% vì khung flatbuffer chiếm tỷ trọng lớn ở model nhỏ, nên không đạt tiêu chí 30%. Hiệu chỉnh ngưỡng là cải tiến về FPR và độ trễ, không phải macro-F1.");

  // ================================================================ 12. Edge
  s = content("Kết quả");
  s.addText("Edge benchmark: V1 int8 trên một lõi E-core", { placeholder: "title" });
  const v = e["V1_int8_P1_edge"];
  const es = [[f(v.p95_us, 1) + " µs", "p95 latency / mẫu (ngưỡng 1000 µs)", HEX.accent1], [f(v.size_kb, 1) + " KB", "file model (ngưỡng 50 KB)", HEX.accent1],
    [f(v.rss_delta_mb, 1) + " MB", "RAM tăng thêm khi nạp + chạy", HEX.accent1], [nf(Math.round(v.throughput_samples_s)), "mẫu/giây trên 1 lõi", HEX.dk2]];
  es.forEach((x, i) => stat(s, 0.6 + i * 3.1, 1.6, 2.9, x[0], x[1], x[2], "edge" + i));
  const p0 = e["V1_int8_P0_b1"];
  card(s, 0.6, 3.9, 5.85, 2.1, HEX.lt2, "thread-card");
  text(s, "Đa luồng làm chậm model nhỏ", { x: 0.9, y: 4.1, w: 5.3, h: 0.5, fontSize: 18, bold: true, color: C.text2 });
  text(s, `Batch 1 với 20 luồng: p50 ${f(p0.p50_us, 0)} µs, so với ${f(v.p50_us, 1)} µs khi 1 luồng ghim E-core → trên edge nên chạy đơn luồng.`,
    { x: 0.9, y: 4.7, w: 5.3, h: 1.2, fontSize: 15 });
  card(s, 6.85, 3.9, 5.85, 2.1, HEX.lt2, "energy-card");
  text(s, "Energy proxy & giới hạn", { x: 7.15, y: 4.1, w: 5.3, h: 0.5, fontSize: 18, bold: true, color: C.text2 });
  text(s, `≈ ${f(v.energy_proxy_uJ, 1)} µJ/mẫu (CPU-time × 55 W/14 lõi), ${nf(v.macs)} MAC/mẫu. Không có Raspberry Pi: lõi E-core laptop mạnh hơn CPU edge thật.`,
    { x: 7.15, y: 4.7, w: 5.3, h: 1.2, fontSize: 15 });
  s.addNotes("Mỗi cấu hình đo trong process riêng: 10.000 lần × 5 lượt, báo cáo p50/p95/p99. Phần lớn thời gian mỗi lần gọi là overhead Python; invoke() chỉ vài µs.");

  // ================================================================ 13. Ổn định & robustness
  s = content("Kết quả");
  s.addText("Độ ổn định theo seed và robustness", { placeholder: "title" });
  s.addImage({ path: path.join(FIG, "fig_seed_stability.png"), x: 0.6, y: 1.45, w: 7.6, h: 2.85, objectName: "seed-fig" });
  text(s, `${D.unstable_pairs} cặp (model, thiết bị) có TPR dao động > 0.05 chỉ vì đổi seed – một lần chạy như Meidan là không đủ.`,
    { x: 0.6, y: 4.4, w: 7.4, h: 1.0, fontSize: 16 });
  s.addImage({ path: path.join(FIG, "fig_evasion.png"), x: 8.4, y: 1.45, w: 4.3, h: 2.87, objectName: "evasion-fig" });
  text(s, "Né tránh: kéo mẫu tấn công về tâm benign; phải bắt chước rất sát (α lớn) mới né được – tức là phải giảm cường độ tấn công.",
    { x: 8.4, y: 4.4, w: 4.3, h: 1.6, fontSize: 14 });
  text(s, "Báo cáo mean ± std, KTC95 và Wilcoxon thay vì con số tốt nhất.", { x: 0.6, y: 5.6, w: 7.4, h: 0.6, fontSize: 14, italic: true, color: C.accent4 });
  s.addNotes("Ổn định: cùng cấu hình, đổi seed có thể lật kết quả phát hiện tcp/udp. Robustness: thử offline né tránh, nhiễu và đầu độc dữ liệu huấn luyện.");

  // ================================================================ 14. MTD
  s = content("Kết quả");
  s.addText("MTD: tái lập xu hướng và MTD lai kích hoạt bởi AE", { placeholder: "title" });
  const h = D.harm20;
  const pol = [["none", "Không MTD"], ["shuffle", "Shuffle"], ["diversity", "Diversity"], ["combined", "Kết hợp"]];
  s.addChart(pres.charts.BAR, [{ name: "ASP", labels: pol.map((p) => p[1]), values: pol.map((p) => h[p[0]]) }],
    { x: 0.6, y: 1.45, w: 5.6, h: 4.6, barDir: "col", chartColors: [HEX.accent4, HEX.accent5, HEX.accent2, HEX.accent1],
      showValue: true, dataLabelPosition: "outEnd", dataLabelFormatCode: "0.00", showLegend: false, valAxisMinVal: 0, valAxisMaxVal: 0.6,
      showTitle: true, title: "Xác suất tấn công thành công (chu kỳ 20 bước)", titleFontSize: 14, titleColor: HEX.dk2, ...chartText, objectName: "harm-chart" });
  text(s, "Khớp xu hướng paper chính: kết hợp shuffle + diversity thấp nhất.", { x: 0.6, y: 6.15, w: 5.6, h: 0.6, fontSize: 14, italic: true, color: C.accent4 });
  s.addImage({ path: path.join(FIG, "fig_mtd_hybrid_tradeoff.png"), x: 6.6, y: 1.45, w: 6.1, h: 3.77, objectName: "hybrid-fig" });
  text(s, `Cùng chi phí, hybrid lộ diện ít hơn time-based. Chỉ event-based: lộ diện TB ${nf(Math.round(D.hybrid.event_exposure))} mẫu vì tấn công AE bỏ sót không kích hoạt move → time-based là lưới an toàn.`,
    { x: 6.6, y: 5.35, w: 6.1, h: 1.4, fontSize: 14 });
  s.addNotes("Track B: mô hình HARM rút gọn với tham số giả định, chỉ so xu hướng. MTD lai dùng chuỗi cảnh báo thật của V1 trên luồng test.");

  // ================================================================ 15. Tiêu chí
  pres.addSection({ title: "Kết luận" });
  s = content("Kết luận");
  s.addText("Đối chiếu tiêu chí đã chốt trước", { placeholder: "title" });
  const crit = D.criteria;
  const trows = [["RQ", "Tiêu chí", "Giá trị đo", "Kết luận"]].concat(crit.map((c) => [c.RQ, c.criterion, c.value, c.pass ? "Đạt" : "Không đạt"]));
  s.addTable(trows.map((r, i) => r.map((c, j) => ({ text: String(c), options: {
    bold: i === 0 || j === 3, color: i === 0 ? HEX.lt1 : (j === 3 ? (c === "Đạt" ? HEX.accent6 : HEX.accent3) : HEX.dk1),
    fill: { color: i === 0 ? HEX.dk2 : (i % 2 ? "FFFFFF" : HEX.lt2) } } }))),
    { x: 0.6, y: 1.45, w: 12.1, colW: [0.9, 5.0, 4.4, 1.8], fontSize: 14, rowH: 0.62, border: { type: "solid", pt: 0.5, color: "D0DAE0" }, valign: "middle", objectName: "crit-table" });
  text(s, "Không chỉnh tiêu chí sau khi có kết quả; mọi lần chạy (" + D.n_runs + ") đều được báo cáo.", { x: 0.6, y: 6.25, w: 12.1, h: 0.5, fontSize: 14, italic: true, color: C.accent4 });
  s.addNotes("Nhiều tiêu chí không đạt và em giữ nguyên, giải thích nguyên nhân ở các slide trước. Riêng edge đạt với biên rất lớn.");

  // ================================================================ 16. Kết luận
  s = pres.addSlide({ masterName: "DARK_CONTENT", sectionTitle: "Kết luận" });
  s.addText("Kết luận & hướng phát triển", { placeholder: "title" });
  s.addText([
    { text: "AE per-device bắt gần tuyệt đối 8/10 loại tấn công với FPR rất thấp; bỏ sót flood tcp/udp giả mạo nguồn", options: { bullet: true, breakLine: true } },
    { text: "V1 int8 < 20 KB, vài µs/mẫu trên 1 lõi E-core – khả thi cho edge", options: { bullet: true, breakLine: true } },
    { text: "Kết quả dao động theo seed → cần nhiều lần chạy và kiểm định", options: { bullet: true, breakLine: true } },
    { text: "MTD: kết hợp shuffle + diversity tốt nhất; MTD lai dùng cảnh báo AE giảm thời gian lộ diện", options: { bullet: true, breakLine: true } },
    { text: "Tiếp theo: chọn ngưỡng có kiểm định trên dữ liệu mới · Raspberry Pi + đo điện thật · đặc trưng cho flood giả mạo", options: { bullet: true, color: C.accent2 } },
  ], { placeholder: "body", fontSize: 20, paraSpaceAfter: 14 });
  s.addNotes("Tóm tắt năm ý chính và hướng phát triển. Mã nguồn, cấu hình, log, manifest và hướng dẫn chạy lại ở thư mục DT043 trên GitHub.");

  await pres.writeFile({ fileName: OUT });
  await applyTheme(OUT, THEME);
  console.log("Đã lưu", OUT);
}

main().catch((err) => { console.error(err); process.exit(1); });
