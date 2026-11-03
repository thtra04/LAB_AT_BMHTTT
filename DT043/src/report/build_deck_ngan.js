// Bản ngắn 8 slide để báo cáo (≈ 3 phút, demo rút gọn) – chạy: node report/build_deck_ngan.js
// Dùng chung theme/layout/số liệu với build_deck.js và build_deck_10.js; hình bài báo từ report/paper_figs (cmp_masud_fig6 do build_report.py tạo).
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
const OUT = path.join(ROOT, "..", "tailieu", "thuyet_trinh", "SlideThuyetTrinh_DT043_ngan_1150080120_HoangThanhTra.pptx");
const THEME = {
  name: "DT043 Edge Defense",
  headFontFace: "Times New Roman",
  bodyFontFace: "Times New Roman",
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
    { placeholder: { options: { name: "title", type: "title", x: 0.8, y: 2.0, w: 11.7, h: 0.88, fontSize: 40, bold: true,
      color: C.background1, fontFace: THEME.headFontFace, valign: "bottom", align: "left", margin: 0 }, text: "" } },
    { placeholder: { options: { name: "body", type: "body", x: 0.8, y: 3.17, w: 11.7, h: 2.6, fontSize: 32,
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
  const PFIG = path.join(HERE, "paper_figs");
  let s;

  // ================================================================ 1. Bìa
  s = pres.addSlide({ masterName: "DARK" });
  s.addText("Phát hiện botnet IoT bằng autoencoder nhẹ", { placeholder: "title" });
  s.addText([
    { text: "Đề tài DT043 · Bài giữa kỳ An toàn Bảo mật Hệ thống thông tin", options: { breakLine: true } },
    { text: "Tên: Hoàng Thanh Trà", options: { breakLine: true } },
    { text: "MSSV: 1150080120", options: { breakLine: true } },
    { text: "Lớp: 11CNPM2" },
  ], { placeholder: "body" });
  await iconCircle(s, fa.FaShieldHalved, 0.8, 0.7, 1.0, HEX.accent1, "logo");
  s.addNotes("Em chào thầy và các bạn. Đề tài DT043: phát hiện IoT nhiễm botnet ngay tại thiết bị biên bằng autoencoder nhẹ, kết hợp MTD.");

  // ================================================================ 2. Bài toán & mục tiêu
  s = content();
  s.addText("Bài toán và mục tiêu", { placeholder: "title" });
  const probs = [
    [fa.FaVideo, HEX.accent3, "Thiết bị IoT dễ bị chiếm", "Mật khẩu mặc định, ít vá – Mirai, BASHLITE chiếm hàng loạt để DDoS"],
    [fa.FaMicrochip, HEX.accent5, "Edge có tài nguyên hạn chế", "Bộ phát hiện phải nhỏ (KB), nhanh (µs), ít RAM"],
    [fa.FaFingerprint, HEX.accent1, "Mỗi thiết bị một hành vi", "Học lưu lượng bình thường riêng từng thiết bị"],
  ];
  for (let i = 0; i < probs.length; i++) {
    const y = 1.55 + i * 1.6;
    await iconCircle(s, probs[i][0], 0.7, y, 0.9, probs[i][1], "prob" + i);
    text(s, probs[i][2], { x: 1.85, y, w: 4.9, h: 0.45, fontSize: 19, bold: true, color: C.text2 });
    text(s, probs[i][3], { x: 1.85, y: y + 0.48, w: 4.9, h: 0.9, fontSize: 15 });
  }
  card(s, 7.1, 1.45, 5.6, 5.2, HEX.dk2, "goal-card");
  text(s, "Mục tiêu đề tài", { x: 7.4, y: 1.65, w: 5.0, h: 0.5, fontSize: 20, bold: true, color: C.accent2 });
  const goals = ["Phát hiện botnet ngay tại edge bằng autoencoder nhẹ, lượng tử hóa int8",
    "Tái lập có chọn lọc bài báo chính (3-layer THARM)", "Dùng cảnh báo của AE kích hoạt Moving Target Defence lai"];
  s.addText(goals.map((g, i) => ({ text: g, options: { bullet: { type: "number" }, breakLine: i < goals.length - 1 } })),
    { x: 7.4, y: 2.3, w: 5.0, h: 2.9, fontSize: 17, color: C.background1, paraSpaceAfter: 12, valign: "top", margin: 0, isTextBox: true });
  text(s, "6 câu hỏi nghiên cứu, tiêu chí chốt trước khi chạy (SHA-256 trong nhật ký)",
    { x: 7.4, y: 5.55, w: 5.0, h: 0.8, fontSize: 13, italic: true, color: C.background2 });

  // ================================================================ 3. Bài báo tham khảo
  s = content();
  text(s, "BÀI BÁO THAM KHẢO · MASUD ET AL. (2025), COMPUTERS & SECURITY 153", { x: 0.6, y: 0.12, w: 12.1, h: 0.3, fontSize: 13, bold: true, color: C.accent5 });
  s.addText("Bài báo nói gì và thiếu gì", { placeholder: "title" });
  s.addImage({ path: path.join(PFIG, "masud_fig3_tharm.png"), x: 0.6, y: 1.45, w: 5.2, h: 3.9, objectName: "paper-fig3" });
  text(s, "Hình 3 của bài báo: mô hình 3-layer THARM", { x: 0.6, y: 5.4, w: 5.2, h: 0.35, fontSize: 11, italic: true, color: C.accent4, align: "center" });
  const rowsP = [
    ["Bài toán", "Đánh giá kết hợp MTD (shuffle, diversity, redundancy) cho IoT theo rủi ro, chi phí, tài nguyên", HEX.accent5],
    ["Phương pháp", "Đồ thị tấn công 3 tầng THARM: 8 máy ảo, 32 CVE; MTD theo chu kỳ 10 phút", HEX.accent1],
    ["Kết quả", "Shuffle + diversity cho rủi ro thấp nhất", HEX.accent6],
    ["Hạn chế", "Chỉ mô phỏng, không có bộ phát hiện kích hoạt MTD, không công bố mã", HEX.accent3],
  ];
  rowsP.forEach((r, i) => {
    const y = 1.45 + i * 1.08;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 6.2, y, w: 1.75, h: 0.92, rectRadius: 0.06, fill: { color: r[2] }, line: { color: r[2] }, objectName: "plabel" + i });
    text(s, r[0], { x: 6.2, y, w: 1.75, h: 0.92, fontSize: 14, bold: true, color: C.background1, align: "center", valign: "middle" });
    text(s, r[1], { x: 8.1, y, w: 4.6, h: 0.92, fontSize: 14, valign: "middle" });
  });
  text(s, "→ Đề tài: Track A phát hiện bằng autoencoder (Meidan 2018) · Track B tái lập THARM + MTD lai do cảnh báo AE kích hoạt",
    { x: 0.6, y: 6.0, w: 12.1, h: 0.7, fontSize: 15, bold: true, color: C.accent3, align: "center", valign: "middle" });

  // ================================================================ 4. Dữ liệu & phương pháp
  s = content();
  s.addText("Dữ liệu và phương pháp", { placeholder: "title" });
  const st = [[(D.data.rows_raw / 1e6).toFixed(2) + "M", "dòng N-BaIoT · 9 thiết bị · 107 file khớp SHA-256", HEX.dk2],
    [nf(D.data.dups), "dòng trùng lặp bị loại", HEX.accent3], [D.data.ratio_min + "–" + D.data.ratio_max + "×", "tấn công nhiều hơn benign → dùng macro-F1, FPR", HEX.dk2]];
  st.forEach((v, i) => stat(s, 0.6 + i * 4.1, 1.35, 3.8, v[0], v[1], v[2], "stat" + i));
  const parts = [["DStrn · huấn luyện", HEX.accent1], ["DSopt · chọn ngưỡng tr*, cửa sổ ws*", HEX.accent5], ["Test · benign + mọi tấn công", HEX.accent3]];
  parts.forEach((p, i) => {
    const x = 0.6 + i * 4.1;
    s.addShape(pres.shapes.RECTANGLE, { x, y: 3.25, w: 3.7, h: 0.75, fill: { color: p[1] }, line: { color: p[1] }, objectName: "split" + i });
    text(s, p[0], { x: x + 0.1, y: 3.25, w: 3.5, h: 0.75, fontSize: 14, bold: true, color: C.background1, align: "center", valign: "middle" });
  });
  text(s, "chia benign theo thời gian 1/3 · 1/3 · 1/3, đệm 500 dòng, scaler chỉ fit trên DStrn – chống rò rỉ",
    { x: 0.6, y: 4.05, w: 12.1, h: 0.4, fontSize: 13, color: C.accent4, align: "center" });
  const steps = ["z-score\ntheo thiết bị", "Autoencoder\nhọc benign", "MSE tái tạo", "tr* = mean+std\nvote cửa sổ", "TFLite int8\n+ hiệu chỉnh"];
  steps.forEach((t, i) => {
    const x = 0.6 + i * 2.5;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y: 4.7, w: 2.1, h: 1.0, rectRadius: 0.1, fill: { color: i === 4 ? HEX.accent2 : HEX.dk2 }, line: { color: i === 4 ? HEX.accent2 : HEX.dk2 }, objectName: "step" + i });
    text(s, t, { x, y: 4.7, w: 2.1, h: 1.0, fontSize: 14, bold: true, color: i === 4 ? C.text1 : C.background1, align: "center", valign: "middle" });
    if (i < 4) s.addShape(pres.shapes.RIGHT_ARROW, { x: x + 2.13, y: 5.03, w: 0.34, h: 0.34, fill: { color: HEX.accent4 }, line: { color: HEX.accent4 }, objectName: "arrow" + i });
  });
  text(s, "Baseline B0 = AE Meidan 115-86-58-38-29-… (36.876 tham số) · Biến thể V1 = 115-32-8-32-115 (8.059 tham số, 21,9%) · so sánh Isolation Forest",
    { x: 0.6, y: 5.95, w: 12.1, h: 0.6, fontSize: 14, align: "center" });

  // ================================================================ 5. Hệ thống & demo
  s = content();
  s.addText("Hệ thống 4 tầng và demo", { placeholder: "title" });
  s.addImage({ path: path.join(FIG, "demo_dashboard_crop.png"), x: 0.6, y: 1.35, w: 6.0, h: 5.19, objectName: "demo-img",
    shadow: { type: "outer", color: "000000", opacity: 0.18, blur: 6, offset: 2, angle: 90 } });
  const tiers = [[fa.FaBrain, "AI", "huấn luyện, int8, xuất gói có SHA-256", HEX.accent1], [fa.FaServer, "Backend", "FastAPI, từ chối gói model bị sửa", HEX.accent5],
    [fa.FaDatabase, "CSDL", "SQLite: cảnh báo, hành động MTD", HEX.accent2], [fa.FaDisplay, "Dashboard", "phát lại dữ liệu, biểu đồ MSE", HEX.accent3]];
  for (let i = 0; i < 4; i++) {
    const y = 1.4 + i * 0.75;
    await iconCircle(s, tiers[i][0], 7.0, y, 0.6, tiers[i][3], "tier" + i);
    text(s, tiers[i][1] + ": ", { x: 7.75, y: y + 0.1, w: 1.4, h: 0.4, fontSize: 15, bold: true, color: C.text2 });
    text(s, tiers[i][2], { x: 9.1, y: y + 0.12, w: 3.6, h: 0.4, fontSize: 13 });
  }
  card(s, 7.0, 4.5, 5.7, 2.05, HEX.lt2, "demo-res");
  s.addText([
    { text: "Kết quả demo", options: { bold: true, color: C.text2, breakLine: true } },
    { text: "mirai/syn (Danmini): 1989/1989 cửa sổ cảnh báo → shuffle IP + đổi firmware", options: { bullet: true, breakLine: true } },
    { text: "benign (Ennio): 0 cảnh báo – không báo động giả", options: { bullet: true, breakLine: true } },
    { text: "gafgyt/tcp (Ennio): 0 cảnh báo – điểm yếu đã phân tích", options: { bullet: true } },
  ], { x: 7.2, y: 4.6, w: 5.35, h: 1.9, fontSize: 13, color: C.text1, valign: "top", margin: 0, isTextBox: true, paraSpaceAfter: 4 });
  text(s, "56 test tự động · server: uvicorn backend.app.main:app → http://127.0.0.1:8000/", { x: 0.6, y: 6.6, w: 12.1, h: 0.35, fontSize: 11, italic: true, color: C.accent4 });

  // ================================================================ 6. Kết quả & edge
  s = content();
  s.addText("Kết quả phát hiện và chạy trên edge", { placeholder: "title" });
  const rg = D.recall_groups;
  const lbl = { E1_baseline: "B0 AE", E4_light: "V1 AE nhẹ", E3_iforest: "IForest" };
  const gk = ["E1_baseline", "E4_light", "E3_iforest"].filter((k) => rg[k]);
  s.addChart(pres.charts.BAR, [
    { name: "tcp/udp", labels: gk.map((k) => lbl[k]), values: gk.map((k) => rg[k].tcp_udp) },
    { name: "8 loại còn lại", labels: gk.map((k) => lbl[k]), values: gk.map((k) => rg[k].others) },
  ], { x: 0.6, y: 1.4, w: 4.6, h: 4.2, barDir: "bar", barGrouping: "clustered", chartColors: [HEX.accent3, HEX.accent1],
    showValue: true, dataLabelPosition: "outEnd", dataLabelFormatCode: "0.00", valAxisMinVal: 0, valAxisMaxVal: 1.2,
    showLegend: true, legendPos: "b", legendFontSize: 12, showTitle: true, title: "Recall theo nhóm tấn công", titleFontSize: 14, titleColor: HEX.dk2, ...chartText, objectName: "recall-chart" });
  const b0 = cf.E1_baseline, v = e["V1_int8_P1_edge"];
  stat(s, 5.6, 1.4, 3.3, f(b0.fpr, 4), "FPR của B0 (Meidan: 0.007)", HEX.accent1, "fpr");
  stat(s, 5.6, 3.1, 3.3, f(b0.tpr, 3), "TPR của B0 (Meidan: 100%)", HEX.accent3, "tpr");
  stat(s, 9.3, 1.4, 3.4, f(v.size_kb, 1) + " KB", "model V1 int8 (tiêu chí ≤ 50 KB)", HEX.accent1, "kb");
  stat(s, 9.3, 3.1, 3.4, f(v.p95_us, 1) + " µs", "p95 / mẫu trên 1 lõi E-core (≤ 1000 µs)", HEX.accent1, "us");
  text(s, `Flood tcp/udp giả mạo nguồn: mỗi gói như "luồng mới" nên giống benign, MSE nằm dưới ngưỡng. RAM tăng ${f(v.rss_delta_mb, 1)} MB, `
    + `${nf(Math.round(v.throughput_samples_s))} mẫu/giây → RQ5 (edge) đạt.`, { x: 0.6, y: 5.85, w: 12.1, h: 0.9, fontSize: 15 });

  // ================================================================ 7. Tái lập bài báo
  s = content();
  text(s, "TÁI LẬP BÀI BÁO CHÍNH BẰNG ĐÚNG DỮ LIỆU CỦA BÀI", { x: 0.6, y: 0.12, w: 12.1, h: 0.3, fontSize: 13, bold: true, color: C.accent5 });
  s.addText("Tái lập bài báo: khớp đến đâu", { placeholder: "title" });
  const chips = [["6/6", "rủi ro từng VM khớp ±0.01"], ["3/3", "đường tấn công, lệch −0.8%"], ["6/7", "kết luận định tính"], ["7/7", "VM khớp ở Hình 6 (diversity)"]];
  chips.forEach((c, i) => stat(s, 0.6 + i * 3.1, 1.3, 2.9, c[0], c[1], HEX.accent1, "chip" + i));
  text(s, "Hình 6 – bài báo (trái) · chạy lại – DT043 (phải)", { x: 0.6, y: 2.95, w: 12.1, h: 0.3, fontSize: 13, bold: true, color: C.accent5, align: "center" });
  s.addImage({ path: path.join(PFIG, "cmp_masud_fig6.png"), x: 0.75, y: 3.3, w: 11.8, h: 3.66, objectName: "fig6-cmp" });

  // ================================================================ 8. Kết luận
  s = content();
  s.addText("Kết luận và hướng tiếp theo", { placeholder: "title" });
  const crit = D.criteria;
  const trows = [["RQ", "Giá trị đo", "Kết luận"]].concat(crit.map((c) => [c.RQ, c.value, c.pass ? "Đạt" : "Không đạt"]));
  s.addTable(trows.map((r, i) => r.map((c, j) => ({ text: String(c), options: {
    bold: i === 0 || j === 2, color: i === 0 ? HEX.lt1 : (j === 2 ? (c === "Đạt" ? HEX.accent6 : HEX.accent3) : HEX.dk1),
    fill: { color: i === 0 ? HEX.dk2 : (i % 2 ? "FFFFFF" : HEX.lt2) } } }))),
    { x: 0.6, y: 1.4, w: 6.4, colW: [0.9, 3.9, 1.6], fontSize: 14, rowH: 0.55, border: { type: "solid", pt: 0.5, color: "D0DAE0" }, valign: "middle", objectName: "crit-table" });
  text(s, "Tiêu chí chốt trước, không chỉnh theo kết quả; báo cáo đủ " + D.n_runs + " lần chạy.", { x: 0.6, y: 5.0, w: 6.4, h: 0.5, fontSize: 13, italic: true, color: C.accent4 });
  card(s, 7.4, 1.4, 5.3, 5.25, HEX.dk2, "concl-card");
  const concl = ["AE bắt gần tuyệt đối 8/10 loại tấn công, FPR rất thấp; bỏ sót flood tcp/udp giả mạo nguồn",
    "V1 int8 15 KB, ~10 µs/mẫu – khả thi cho edge", "Tái lập bài chính: khớp mức VM, đường, 6/7 kết luận",
    "Tiếp theo: đặc trưng cho flood giả mạo · Raspberry Pi thật · MTD trên mạng thật"];
  s.addText(concl.map((t, i) => ({ text: t, options: { bullet: true, breakLine: i < concl.length - 1, color: i === concl.length - 1 ? C.accent2 : C.background1 } })),
    { x: 7.7, y: 1.65, w: 4.8, h: 4.8, fontSize: 17, paraSpaceAfter: 12, valign: "top", margin: 0, isTextBox: true, objectName: "concl-text" });

  await pres.writeFile({ fileName: OUT });
  await applyTheme(OUT, THEME);
  console.log("Đã lưu", OUT);
}

main().catch((err) => { console.error(err); process.exit(1); });
