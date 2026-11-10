// Bản rút gọn 10 slide (thuyết trình ~5 phút có demo) – chạy: node report/build_deck_10.js
// Bản 4'30 không demo trực tiếp, theo 5 phần: phân tích bài báo → các bước làm bài → kết quả → so sánh với bài báo
// → dự định làm tiếp (slide 8 là ảnh dashboard chạy thật): node report/build_deck_10.js --4p30
// Thêm --mau2: cùng nội dung bản 4'30 nhưng trình bày giản dị kiểu sinh viên tự làm (nền trắng, không thẻ, không icon), ghi ra file riêng.
// Dùng chung theme/layout/số liệu với build_deck.js (bản 17 slide giữ làm bản đầy đủ để trả lời câu hỏi).
const path = require("path");
const fs = require("fs");
const pptxgen = require("pptxgenjs");
const React = require("react");
const ReactDOMServer = require("react-dom/server");
const sharp = require("sharp");
const fa = require("react-icons/fa6");
const { applyTheme } = require("./apply_theme.js");
const { paperSlides, fig6Slide, appendixSlides, helpers, csv } = require("./deck_paper.js");

const HERE = __dirname;
const ROOT = path.resolve(HERE, "..");
const FIG = path.join(ROOT, "results", "figures");
const D = JSON.parse(fs.readFileSync(path.join(HERE, "deck_data.json"), "utf8"));
const NO_DEMO = process.argv.includes("--4p30");
const MAU2 = process.argv.includes("--mau2");
const OUT = process.argv.includes("--out") ? path.resolve(process.argv[process.argv.indexOf("--out") + 1])
  : path.join(ROOT, "..", "tailieu", "thuyet_trinh", `SlideThuyetTrinh_DT043_${NO_DEMO ? "4p30" : "10slide"}${MAU2 ? "_mau2" : ""}_1150080120_HoangThanhTra.pptx`);
const THEME = MAU2 ? {
  name: "DT043 Mau 2",
  headFontFace: "Calibri",
  bodyFontFace: "Calibri",
  colors: {
    dk1: "222222", lt1: "FFFFFF", dk2: "1F3864", lt2: "F2F2F2",
    accent1: "2F5597", accent2: "BF8F00", accent3: "C00000", accent4: "595959",
    accent5: "2F5597", accent6: "548235", hlink: "2F5597", folHlink: "595959",
  },
} : {
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
  background: { color: MAU2 ? HEX.lt1 : HEX.dk2 },
  objects: [
    { placeholder: { options: { name: "title", type: "title", x: 0.8, y: MAU2 ? 1.5 : 2.0, w: 11.7, h: MAU2 ? 1.3 : 0.88, fontSize: 40, bold: true,
      color: MAU2 ? C.text2 : C.background1, fontFace: THEME.headFontFace, valign: "bottom", align: MAU2 ? "center" : "left", margin: 0 }, text: "" } },
    { placeholder: { options: { name: "body", type: "body", x: 0.8, y: 3.17, w: 11.7, h: 2.6, fontSize: MAU2 ? 24 : 32,
      color: MAU2 ? C.text1 : C.background2, valign: "top", align: MAU2 ? "center" : "left", margin: 0 }, text: "" } },
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
    { placeholder: { options: { name: "title", type: "title", x: 0.6, y: 0.35, w: 12.1, h: 0.85, fontSize: MAU2 ? 30 : 32, bold: true,
      color: C.text2, fontFace: THEME.headFontFace, valign: "middle", align: MAU2 ? "left" : undefined, margin: 0 }, text: "" } },
    { text: { text: MAU2 ? "Hoàng Thanh Trà – 1150080120" : "DT043 · Hoàng Thanh Trà · 1150080120", options: { x: 0.6, y: 7.0, w: 6, h: 0.3, fontSize: 10,
      color: C.accent4, margin: 0 } } },
  ],
  slideNumber: { x: 12.2, y: 7.0, w: 0.5, h: 0.3, fontSize: 10, color: HEX.accent4, align: "right" },
});

// ------------------------------------------------------------------ mẫu 2: bỏ trang trí ở một chỗ, nội dung giữ nguyên
if (MAU2) {
  const addSlide = pres.addSlide.bind(pres);
  pres.addSlide = (o) => {
    const sl = addSlide(o);
    const addShape = sl.addShape.bind(sl), addTable = sl.addTable.bind(sl);
    sl.addShape = (type, opt) => {
      if (/bar/.test(opt.objectName || "")) return sl;           // bỏ sọc màu cạnh khối
      const { rectRadius, shadow, ...rest } = opt;
      return addShape(type === pres.shapes.ROUNDED_RECTANGLE ? pres.shapes.RECTANGLE : type, rest);
    };
    sl.addTable = (rows, opt) => addTable(rows.map((r, i) => r.map((c) => ({ ...c, options: { ...c.options,
      color: i === 0 ? HEX.dk1 : (c.options && c.options.color), fill: { color: i === 0 ? "DCE6F1" : "FFFFFF" } } }))),
    { ...opt, border: { type: "solid", pt: 0.75, color: "A6A6A6" } });
    return sl;
  };
}

// ------------------------------------------------------------------ helpers
async function icon(Comp, color, px = 256) {
  const svg = ReactDOMServer.renderToStaticMarkup(React.createElement(Comp, { color: "#" + color, size: px }));
  const buf = await sharp(Buffer.from(svg)).png().toBuffer();
  return "image/png;base64," + buf.toString("base64");
}
async function iconCircle(slide, Comp, x, y, d, fill, name) {
  if (MAU2) return;
  slide.addShape(pres.shapes.OVAL, { x, y, w: d, h: d, fill: { color: fill }, line: { color: fill }, objectName: name + "-circle" });
  const pad = d * 0.25;
  slide.addImage({ data: await icon(Comp, HEX.lt1), x: x + pad, y: y + pad, w: d - 2 * pad, h: d - 2 * pad, objectName: name + "-icon" });
}
function text(slide, t, opts) {
  slide.addText(t, { isTextBox: true, margin: 0, fontSize: 15, color: C.text1, valign: "top", ...opts });
}
function card(slide, x, y, w, h, fill, name) {
  if (MAU2 && fill !== HEX.dk2) return;                          // nền trắng, chữ đứng trực tiếp trên slide
  slide.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h, rectRadius: 0.12, fill: { color: fill }, line: { color: fill },
    shadow: { type: "outer", color: "000000", opacity: 0.12, blur: 6, offset: 2, angle: 90 }, objectName: name });
}
function stat(slide, x, y, w, big, label, color, name) {
  text(slide, big, { x, y, w, h: 0.95, fontSize: MAU2 ? 34 : 40, bold: true, color, fontFace: THEME.headFontFace, objectName: name + "-num" });
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
  const ctx = { pres, D, FIG, HEX, C, fa, text, card, iconCircle, stat, content, f, nf, MAU2 };
  const H = helpers(ctx);
  const kick = (s, k) => k && H.kicker(s, k);
  const b0 = cf.E1_baseline, v = e["V1_int8_P1_edge"];
  // MTD lai (T = 2000) so với time-based (T = 500): lộ diện tương đương, số lần đổi ít hơn
  const hyb = (p, T) => D.hybrid.series.find((r) => r.policy === p && r.period === T);
  const hy = hyb("hybrid", 2000), tm = hyb("time", 500);
  const saving = Math.floor((1 - hy.moves_per_10k / tm.moves_per_10k) * 100);
  let s;

  // ================================================================ Tiêu đề
  async function titleSlide(section) {
    s = pres.addSlide({ masterName: "DARK", sectionTitle: section });
    // bìa theo bản sinh viên chỉnh trong PowerPoint (27/10): tên, MSSV, lớp mỗi thứ một dòng, cỡ 32
    s.addText("Phát hiện botnet IoT bằng autoencoder nhẹ", { placeholder: "title" });
    s.addText([
      { text: "Đề tài DT043 · Bài giữa kỳ An toàn Bảo mật Hệ thống thông tin", options: { breakLine: true } },
      { text: "Tên: Hoàng Thanh Trà", options: { breakLine: true } },
      { text: "MSSV: 1150080120", options: { breakLine: true } },
      { text: "Lớp: 11CNPM2" },
    ], { placeholder: "body" });
    await iconCircle(s, fa.FaShieldHalved, 0.8, 0.7, 1.0, HEX.accent1, "logo");
    if (NO_DEMO) {
      const parts = ["Phân tích bài báo", "Các bước làm bài", "Kết quả", "So sánh với bài báo", "Dự định làm tiếp"];
      text(s, parts.map((p, i) => `${i + 1}. ${p}`).join("   ·   "), { x: 0.8, y: 6.35, w: 11.7, h: 0.45, fontSize: 16,
        color: MAU2 ? HEX.accent4 : HEX.accent2, align: MAU2 ? "center" : "left", objectName: "agenda" });
    }
    s.addNotes("Em chào thầy và các bạn. Đề tài DT043: phát hiện thiết bị IoT bị nhiễm botnet ngay tại thiết bị biên bằng autoencoder huấn luyện "
      + "riêng cho từng thiết bị, thu nhỏ và lượng tử hóa int8, và nối với hướng Moving Target Defence của paper chính."
      + (NO_DEMO ? " Em trình bày năm phần: phân tích bài báo, các bước làm bài, kết quả, so sánh với bài báo và dự định làm tiếp." : ""));
  }

  // ================================================================ Bài toán & RQ
  async function problemSlide(section) {
    s = content(section);
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
  }

  // ================================================================ Dữ liệu & chống rò rỉ
  function dataSlide(section, k) {
    s = content(section);
    kick(s, k);
    s.addText("Dữ liệu N-BaIoT và chống rò rỉ train/test", { placeholder: "title" });
    const st = [[(D.data.rows_raw / 1e6).toFixed(2) + "M", "dòng · UCI, CC BY 4.0 · 107 file khớp SHA-256"],
      [nf(D.data.dups), "dòng trùng lặp bị loại (2.2%)"], [D.data.ratio_min + "–" + D.data.ratio_max + "×", "attack nhiều hơn benign → dùng macro-F1, FPR"]];
    st.forEach((x, i) => stat(s, 0.6 + i * 4.1, 1.45, 3.8, x[0], x[1], i === 1 ? HEX.accent3 : HEX.dk2, "stat" + i));
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
  }

  // ================================================================ Mô hình & hệ thống
  async function modelSlide(section, k) {
    s = content(section);
    kick(s, k);
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
    text(s, "56 test tự động: unit · integration · negative (gói bị sửa 1 byte, path traversal, sai số chiều)", { x: 0.6, y: 6.3, w: 12.1, h: 0.4, fontSize: 13, italic: true, color: C.accent4 });
    s.addNotes("Pipeline theo Meidan: chuẩn hóa per-device, AE học benign, ngưỡng mean + std, vote cửa sổ; cải tiến là V1 chỉ 8 nghìn tham số, "
      + "int8 rồi hiệu chỉnh ngưỡng. Hệ thống tách 4 tầng, AI và backend chỉ nói chuyện qua gói có checksum. "
      + (NO_DEMO ? "Tiếp theo là kết quả." : "Tiếp theo em demo."));
  }

  // ================================================================ Demo (bản 4'30: kết quả chạy hệ thống, không demo trực tiếp)
  async function demoSlide(section, k) {
    s = content(section);
    kick(s, k);
    s.addText(NO_DEMO ? "Kết quả chạy hệ thống: phát hiện → cảnh báo → MTD" : "Demo: phát hiện + cảnh báo + MTD trên dashboard",
      { placeholder: "title" });
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
    text(s, NO_DEMO ? "Ảnh chụp dashboard khi phát lại tập test · 9 model V1 int8 đã nạp"
      : "Chạy: uvicorn backend.app.main:app → http://127.0.0.1:8000/", { x: 7.3, y: 6.45, w: 5.4, h: 0.4, fontSize: 12, italic: true, color: C.accent4 });
    s.addNotes(NO_DEMO
      ? "Kết quả chạy thật trên dashboard: 9 model V1 int8 đã nạp; phát lại mirai/syn của Danmini → 1989/1989 cửa sổ cảnh báo, cảnh báo high "
        + "và 2 hành động MTD (xáo trộn IP, đổi firmware) ghi vào CSDL; benign của Ennio không cảnh báo; gafgyt/tcp bị bỏ sót – phân tích ở slide sau."
      : "Demo trực tiếp (90 giây): 9 model đã nạp; phát lại mirai/syn → 1989/1989 cửa sổ cảnh báo, cảnh báo high và 2 hành động MTD ghi vào CSDL; "
        + "benign không cảnh báo; gafgyt/tcp bị bỏ sót – em không che giấu điểm yếu; cuối cùng chạy MTD time-based làm lưới an toàn.");
  }

  // ================================================================ Kết quả & lỗi chính
  function resultSlide(section, k) {
    s = content(section);
    kick(s, k);
    s.addText("Kết quả: FPR rất thấp, lỗi tập trung ở flood tcp/udp", { placeholder: "title" });
    const order = ["E1_baseline", "E2_shared_pdnorm", "E3_iforest", "E4_light"].filter((x) => cf[x]);
    s.addChart(pres.charts.BAR, [{ name: "macro-F1", labels: order.map((x) => lbl[x]), values: order.map((x) => cf[x].macro_f1) }],
      { x: 0.6, y: 1.4, w: 4.6, h: 4.0, barDir: "col", chartColors: [HEX.dk2], showValue: true, dataLabelPosition: "outEnd", dataLabelFormatCode: "0.00",
        valAxisMinVal: 0, valAxisMaxVal: 1, showLegend: false, showTitle: true, title: "macro-F1 (9 thiết bị × 5 seed)", titleFontSize: 14, titleColor: HEX.dk2, ...chartText, objectName: "f1-chart" });
    const rg = D.recall_groups;
    const gk = ["E1_baseline", "E4_light", "E3_iforest"].filter((x) => rg[x]);
    s.addChart(pres.charts.BAR, [
      { name: "tcp/udp", labels: gk.map((x) => lbl[x]), values: gk.map((x) => rg[x].tcp_udp) },
      { name: "8 loại còn lại", labels: gk.map((x) => lbl[x]), values: gk.map((x) => rg[x].others) },
    ], { x: 5.4, y: 1.4, w: 4.2, h: 4.0, barDir: "bar", barGrouping: "clustered", chartColors: [HEX.accent3, HEX.accent1],
      showValue: true, dataLabelPosition: "outEnd", dataLabelFormatCode: "0.00", valAxisMinVal: 0, valAxisMaxVal: 1.2,
      showLegend: true, legendPos: "b", legendFontSize: 12, showTitle: true, title: "Recall theo nhóm tấn công", titleFontSize: 14, titleColor: HEX.dk2, ...chartText, objectName: "recall-chart" });
    stat(s, 9.9, 1.5, 2.8, f(b0.fpr, 4), "FPR của B0 (Meidan: 0.007)", HEX.accent1, "fpr");
    stat(s, 9.9, 3.3, 2.8, f(b0.tpr, 3), "TPR của B0 (Meidan: 100%)", HEX.accent3, "tpr");
    text(s, "Nguồn bị giả mạo liên tục → mỗi gói như \"luồng mới\" (weight = 1, variance = 0), MSE nằm dưới ngưỡng mean+std. "
      + "Tám loại tấn công còn lại recall ≈ 1.0.", { x: 0.6, y: 5.6, w: 12.1, h: 1.0, fontSize: 15 });
    s.addNotes("Trên 468 lần chạy, FPR chỉ 0,0025, thấp hơn Meidan, nhưng TPR 0,822. Toàn bộ suy giảm đến từ flood tcp/udp của BASHLITE: nguồn giả mạo "
      + "nên mỗi gói giống luồng mới, giống benign. Isolation Forest tốt hơn về chất lượng, em báo cáo trung thực.");
  }

  // ================================================================ int8 & edge
  function edgeSlide(section, k) {
    s = content(section);
    kick(s, k);
    s.addText("Lượng tử hóa int8 và edge benchmark", { placeholder: "title" });
    const modes = ["fp32", "fp16", "dyn", "int8"];
    s.addChart(pres.charts.BAR, [{ name: "KB", labels: modes.map((m) => "V1 " + m), values: modes.map((m) => q[`V1_${m}_keep`].kb) }],
      { x: 0.6, y: 1.4, w: 5.4, h: 4.4, barDir: "col", chartColors: [HEX.accent1, HEX.accent1, HEX.accent1, HEX.accent2],
        showValue: true, dataLabelPosition: "outEnd", dataLabelFormatCode: "0.0", showLegend: false, showTitle: true,
        title: "Kích thước file TFLite (KB)", titleFontSize: 14, titleColor: HEX.dk2, valAxisMinVal: 0, ...chartText, objectName: "quant-chart" });
    const es = [[f(v.p95_us, 1) + " µs", "p95 / mẫu (tiêu chí ≤ 1000 µs)"], [f(v.size_kb, 1) + " KB", "model (tiêu chí ≤ 50 KB)"],
      [f(v.rss_delta_mb, 1) + " MB", "RAM tăng thêm"], [nf(Math.round(v.throughput_samples_s)), "mẫu/giây trên 1 lõi E-core"]];
    es.forEach((x, i) => stat(s, 6.5 + (i % 2) * 3.15, 1.45 + Math.floor(i / 2) * 1.85, 2.95, x[0], x[1], i < 3 ? HEX.accent1 : HEX.dk2, "edge" + i));
    const kq = q.V1_int8_keep, r2 = q.V1_int8_recal;
    text(s, `Hiệu chỉnh ngưỡng trên DSopt bằng chính model int8: FPR ${f(kq.fpr, 4)} → ${f(r2.fpr, 4)}, cửa sổ ${kq.ws} → ${r2.ws} mẫu. `
      + `Energy proxy ≈ ${f(v.energy_proxy_uJ, 1)} µJ/mẫu. RQ5 đạt với biên rất lớn.`, { x: 6.5, y: 5.2, w: 6.2, h: 1.5, fontSize: 14 });
    s.addNotes("Bản int8 chỉ 15,3 KB; giữ ngưỡng fp32 thì lệch nên em hiệu chỉnh lại trên DSopt. Trên một lõi E-core p95 chỉ 10,8 micro-giây mỗi mẫu, "
      + "khoảng 103 nghìn mẫu mỗi giây, RAM tăng 4,6 MB. Kích thước chỉ còn 45% bản fp32 do khung flatbuffer nên RQ4 không đạt.");
  }

  // ================================================================ MTD & tái lập paper chính
  function mtdSlide(section, k, title) {
    s = content(section);
    kick(s, k);
    s.addText(title, { placeholder: "title" });
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
    text(s, "Khớp: rủi ro VM ±0.01, đường −0.8%. Gần khớp (E12, công thức AC suy ra): tổng AC ≤ 3.4%, RoC ≤ 8.4%. Chưa khớp: tổng R của D, R (−13%, −17%), "
      + "Hình 5(b), 6, 7, 9. \"S+D tốt nhất\" chỉ đạt ở ví dụ V5, topology Hình 3.", { x: 7.5, y: 3.5, w: 5.0, h: 1.75, fontSize: 14.5 });
    text(s, `HARM rút gọn (chu kỳ 20): ASP không MTD ${f(D.harm20.none)} → shuffle ${f(D.harm20.shuffle)} · diversity ${f(D.harm20.diversity)} · `
      + `kết hợp ${f(D.harm20.combined)}. MTD lai dùng cảnh báo AE: cùng chi phí, lộ diện ít hơn time-based.`, { x: 0.6, y: 4.4, w: 6.3, h: 1.4, fontSize: 14 });
    text(s, "Dữ liệu paper: 18 CVE OS + 14 CVE dịch vụ (Bảng 1–2), 8 VM, Definition 2; shuffle/diversity/redundancy theo mục 4.2–4.4",
      { x: 0.6, y: 6.2, w: 12.1, h: 0.5, fontSize: 12, italic: true, color: C.accent4 });
    s.addNotes("Track B: em dựng lại 3-layer THARM bằng đúng 32 CVE, 8 VM và topology của paper. Rủi ro từng VM khớp tới 0,01, ba đường tấn công lệch 0,8%; "
      + "tổng AC và RoC gần khớp với công thức em suy ra, đây là giả thuyết và chưa giải thích được V2. Tổng R của diversity, redundancy và nhiều hình vẫn chưa khớp vì bài thiếu công thức và có chỗ không nhất quán. Với topology Hình 3 tái lập 6/7 kết luận, nhưng S+D chỉ tốt nhất ở ví dụ V5.");
  }

  // ================================================================ Tiêu chí & kết luận (bộ 10 slide)
  function criteriaConclSlide(section) {
    s = content(section);
    s.addText("Đối chiếu tiêu chí và kết luận", { placeholder: "title" });
    const trows = [["RQ", "Giá trị đo", "Kết luận"]].concat(D.criteria.map((c) => [c.RQ, c.value, c.pass ? "Đạt" : "Không đạt"]));
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
  }

  // ================================================================ Các bước làm bài: mỗi bước một slide, hình lấy từ notebook (bản 4'30)
  // hình: report/nb_figs/ (sinh bằng extract_nb_figs.py từ DT043_walkthrough.ipynb)
  async function stepsSlides(section, k) {
    const NB = path.join(HERE, "nb_figs");
    const L = { x: 0.6, y: 1.35, w: 7.4, h: 5.15 };  // vùng hình bên trái
    const steps = [
      { n: "1–2", name: "Đọc bài báo, lập kế hoạch", figs: [],
        doing: ["Đọc Masud 2025 (MTD, mô hình THARM) và Meidan 2018 (autoencoder trên N-BaIoT)",
          "Viết phiếu tái lập: liệt kê ≥ 5 hạn chế của bài, đặt câu hỏi nghiên cứu"],
        result: ["Bài chính không có bộ phát hiện → chia 2 track: A phát hiện bằng AE, B tái lập THARM + MTD lai",
          "6 câu hỏi nghiên cứu RQ1–RQ6, ma trận 11 thí nghiệm E1–E11"] },
      { n: "3–4", name: "Tải dữ liệu, làm sạch, EDA", sec: "mục 1–2",
        figs: [["eda_dedup_counts.png", { ...L, h: 2.3 }], ["eda_pca_danmini.png", { ...L, y: 3.75, h: 2.75 }]],
        doing: ["Tải N-BaIoT 1.77 GB, kiểm SHA-256 từng file", "Kiểm schema 115 cột, khử trùng lặp, đo mất cân bằng, PCA"],
        result: [`107 file khớp SHA-256 · ${(D.data.rows_raw / 1e6).toFixed(2)} triệu dòng · 9 thiết bị`,
          `Loại ${nf(D.data.dups)} dòng trùng; attack nhiều hơn benign ${D.data.ratio_min}–${D.data.ratio_max}× → dùng macro-F1, FPR`] },
      { n: "5", name: "Chia chống rò rỉ, huấn luyện AE, chọn ngưỡng", sec: "mục 3–4",
        figs: [["v1_mse_hist_ennio.png", L]],
        doing: ["Chia benign theo thời gian 1/3 · 1/3 · 1/3, đệm 500 dòng; scaler fit trên train",
          "AE V1 115-32-8-32-115 học benign; ngưỡng tr* = mean + std của MSE"],
        result: ["Benign nằm dưới ngưỡng – không báo động giả; 30 test chống rò rỉ",
          "Flood gafgyt tcp/udp cũng nằm dưới tr* → nguyên nhân bỏ sót chính"] },
      { n: "6–7", name: "Chốt tiêu chí, chạy 468 lần", sec: "mục 7",
        figs: [["recall_per_attack.png", { ...L, h: 2.55 }], ["seed_stability.png", { ...L, y: 4.0, h: 2.5 }]],
        doing: ["Chốt tiêu chí thành công, lưu SHA-256 trước khi chạy", `Chạy ${D.n_runs} lần: cấu hình × 9 thiết bị × 5 seed`],
        result: [`B0: FPR ${f(b0.fpr, 4)}, TPR ${f(b0.tpr, 3)}; 8/10 loại tấn công recall ≈ 1, chỉ tcp/udp thấp`,
          "Kết quả dao động theo seed → phải chạy nhiều lần"] },
      { n: "7", name: "Lượng tử hóa int8, đo trên edge", sec: "mục 5–7",
        figs: [["quant_tradeoff.png", L]],
        doing: ["Chuyển TFLite fp32 / fp16 / dynamic / int8, hiệu chỉnh lại ngưỡng", "Đo trên 1 lõi E-core: độ trễ, RAM, thông lượng"],
        result: [`V1 int8 ${f(v.size_kb, 1)} KB (45.5% bản fp32), macro-F1 giảm 0.028 – RQ4 không đạt`,
          `p95 ${f(v.p95_us, 1)} µs/mẫu · ~${nf(Math.round(v.throughput_samples_s / 1000))} nghìn mẫu/s · RAM +${f(v.rss_delta_mb, 1)} MB`] },
      { n: "8–9", name: "Dựng hệ thống 4 tầng, MTD lai", sec: "mục 8, 10",
        figs: [[path.join(FIG, "demo_dashboard_crop.png"), { ...L, w: 3.75 }], ["mtd_hybrid.png", { ...L, x: 4.5, w: 3.5 }]],
        doing: ["AI xuất gói có SHA-256 → FastAPI → SQLite → dashboard", "Mô phỏng MTD theo thời gian, theo cảnh báo và lai"],
        result: ["mirai/syn: 1989/1989 cửa sổ cảnh báo → tự kích hoạt 2 hành động MTD",
          `MTD lai: cùng mức lộ diện, số lần đổi ít hơn ≈ ${saving}%`] },
      { n: "10", name: "Tái lập bài báo chính (E11, E12)", sec: "mục 9",
        figs: [["masud_fig6_rerun.png", L]],
        doing: ["Dựng 3-layer THARM bằng đúng 32 CVE, 8 VM, topology của bài", "Vẽ lại Hình 6, 7; dò công thức AC, ASP mà bài không in rõ"],
        result: ["Rủi ro VM khớp ±0.01, đường tấn công −0.8%", "Tổng AC lệch ≤ 3.4%, RoC ≤ 8.4% với công thức suy ra; tổng R của D, R vẫn lệch 13–17%", "Hình 6(a): 11/35 điểm lệch ≤ 5%"] },
    ];
    for (const st of steps) {
      s = content(section);
      kick(s, `${k} · BƯỚC ${st.n}`);
      s.addText(`Bước ${st.n}: ${st.name}`, { placeholder: "title" });
      if (st.figs.length) {
        for (const [file, b] of st.figs) {
          await H.image(s, path.isAbsolute(file) ? file : path.join(NB, file), b.x, b.y, b.w, b.h, "fig-" + path.basename(file));
        }
        H.caption(s, `Hình chạy trong notebook src/DT043_walkthrough.ipynb (${st.sec})`, L.x, 6.55, L.w);
      } else {
        // bước 1–2 không có hình: hai track của đề tài
        const tracks = [["Track A – Phát hiện", "Theo Meidan 2018: AE per-device trên N-BaIoT, thu nhỏ, int8, chạy trên edge (RQ1–RQ5)", HEX.accent1],
          ["Track B – MTD", "Theo Masud 2025: tái lập THARM bằng đúng dữ liệu bài, cảnh báo AE kích hoạt MTD lai (RQ6, E11)", HEX.accent5]];
        tracks.forEach(([h, b, c], i) => {
          const y = 1.5 + i * 2.5;
          card(s, L.x, y, L.w, 2.2, HEX.lt2, "track" + i);
          s.addShape(pres.shapes.RECTANGLE, { x: L.x, y, w: 0.12, h: 2.2, fill: { color: c }, line: { color: c }, objectName: "track-bar" + i });
          text(s, h, { x: L.x + 0.35, y: y + 0.2, w: L.w - 0.6, h: 0.45, fontSize: 20, bold: true, color: C.text2 });
          text(s, b, { x: L.x + 0.35, y: y + 0.8, w: L.w - 0.6, h: 1.2, fontSize: 16 });
        });
      }
      card(s, 8.3, 1.35, 4.4, 2.45, HEX.lt2, "doing");
      text(s, "Làm gì", { x: 8.5, y: 1.45, w: 4.0, h: 0.4, fontSize: 16, bold: true, color: C.accent4 });
      s.addText(st.doing.map((t, i) => ({ text: t, options: { bullet: true, breakLine: i < st.doing.length - 1 } })),
        { x: 8.5, y: 1.9, w: 4.05, h: 1.8, fontSize: MAU2 ? 15 : 13.5, color: C.text1, paraSpaceAfter: 6, valign: "top", margin: 0, isTextBox: true });
      card(s, 8.3, 4.0, 4.4, 2.75, "E3F4F1", "result");
      text(s, "Kết quả", { x: 8.5, y: 4.1, w: 4.0, h: 0.4, fontSize: 16, bold: true, color: C.accent1 });
      s.addText(st.result.map((t, i) => ({ text: t, options: { bullet: true, breakLine: i < st.result.length - 1 } })),
        { x: 8.5, y: 4.55, w: 4.05, h: 2.1, fontSize: MAU2 ? 15 : 13.5, bold: !MAU2, color: C.text2, paraSpaceAfter: 6, valign: "top", margin: 0, isTextBox: true });
      s.addNotes(`Bước ${st.n} – ${st.name}. Làm gì: ${st.doing.join("; ")}. Kết quả: ${st.result.join("; ")}.`);
    }
  }

  // ================================================================ Đối chiếu tiêu chí 6 RQ (bản 4'30)
  function criteriaSlide(section, k) {
    s = content(section);
    kick(s, k);
    s.addText("Đối chiếu 6 câu hỏi nghiên cứu với tiêu chí chốt trước", { placeholder: "title" });
    const ask = { RQ1: "Tái lập baseline Meidan 2018", RQ2: "Per-device hơn model chung?", RQ3: "AE nhẹ giữ chất lượng?",
      RQ4: "int8 + hiệu chỉnh ngưỡng", RQ5: "Chạy được trên edge?" };
    const rows = D.criteria.map((c) => [c.RQ, ask[c.RQ], c.value, c.pass ? "Đạt" : "Không đạt"])
      .concat([["RQ6", "AE kích hoạt MTD lai", `lộ diện ${f(hy.exposure_mean, 0)} vs ${f(tm.exposure_mean, 0)} mẫu; `
        + `đổi ${f(hy.moves_per_10k, 1)} vs ${f(tm.moves_per_10k, 1)} lần/10k (so với time-based)`, "Ủng hộ H6"]]);
    H.table(s, [["RQ", "Câu hỏi", "Giá trị đo", "Kết luận"]].concat(rows), { fontSize: 14, head: HEX.dk2,
      colorCol: { j: 3, fn: (c) => (c === "Không đạt" ? HEX.accent3 : HEX.accent6) },
      box: { x: 0.6, y: 1.4, w: 12.1, colW: [0.9, 3.6, 5.7, 1.9], rowH: 0.58, objectName: "crit6-table" } });
    card(s, 0.6, 5.7, 12.1, 0.95, HEX.lt2, "crit-note");
    text(s, "Tiêu chí chốt và lưu SHA-256 trước khi chạy, không chỉnh sau khi có kết quả. RQ1 hụt vì flood tcp/udp; RQ2–RQ4 sát ngưỡng; "
      + `RQ5 đạt với biên rất lớn; MTD lai đổi ít hơn ≈ ${saving}% ở cùng mức lộ diện.`, { x: 0.85, y: 5.7, w: 11.6, h: 0.95, fontSize: 15, valign: "middle" });
    s.addNotes("Đối chiếu tiêu chí chốt trước: RQ5 về edge đạt; RQ1 đến RQ4 không đạt và em giữ nguyên tiêu chí. Với RQ6, MTD lai dùng cảnh báo "
      + `autoencoder có thời gian lộ diện tương đương MTD theo thời gian nhưng số lần đổi ít hơn khoảng ${saving}%.`);
  }

  // ================================================================ So sánh với Meidan 2018 (bản 4'30)
  function meidanSlide(section, k) {
    s = content(section);
    kick(s, k);
    s.addText("So sánh với Meidan 2018: FPR khớp, TPR thấp hơn", { placeholder: "title" });
    const rows = [["Tiêu chí", "Meidan 2018", "DT043"],
      ["FPR", "0.007 ± 0.01", f(b0.fpr, 4) + " (thấp hơn, chưa kiểm định)"],
      ["TPR", "100%", f(b0.tpr, 3)],
      ["Chia dữ liệu", "1 lần, không khử trùng lặp", `theo thời gian, đệm 500 dòng, khử ${nf(D.data.dups)} dòng trùng`],
      ["Số lần chạy", "1", `${D.n_runs} lần, 5 seed`],
      ["Thời gian phát hiện", "174 ± 212 ms", "theo số mẫu (CSV không có timestamp)"],
      ["Chạy trên edge", "không đo", `int8 ${f(v.size_kb, 1)} KB, ${f(v.p95_us, 1)} µs/mẫu`]];
    H.table(s, rows, { fontSize: 14, head: HEX.dk2, box: { x: 0.6, y: 1.4, w: 7.3, colW: [2.0, 2.3, 3.0], rowH: 0.62, objectName: "meidan-table" } });
    card(s, 8.2, 1.4, 4.5, 4.35, HEX.lt2, "why-card");
    text(s, "Vì sao TPR thấp hơn?", { x: 8.45, y: 1.55, w: 4.0, h: 0.45, fontSize: 18, bold: true, color: C.text2 });
    const why = ["Phần bỏ sót nằm ở flood tcp/udp BASHLITE giả mạo nguồn – mỗi gói như luồng mới, giống benign; 8 loại còn lại recall ≈ 1.0",
      "Ngưỡng mean + std bị đuôi MSE kéo cao; bài cũng tối ưu η, epochs riêng từng thiết bị",
      "Rò rỉ không giải thích được: chia ngẫu nhiên (E6) có TPR 0.804, FPR 0.0006. Chưa tách được nguyên nhân duy nhất"];
    s.addText(why.map((t, i) => ({ text: t, options: { bullet: { type: "number" }, breakLine: i < why.length - 1 } })),
      { x: 8.45, y: 2.1, w: 4.05, h: 3.5, fontSize: 15, color: C.text1, paraSpaceAfter: 8, valign: "top", margin: 0, isTextBox: true, objectName: "why-text" });
    text(s, "Phương pháp giữ đúng Meidan: AE 75-50-33-25% số chiều, tr* = mean + std trên DSopt, vote cửa sổ ws*; khác biệt có chủ đích "
      + "ghi trong phiếu tái lập.", { x: 0.6, y: 6.0, w: 12.1, h: 0.7, fontSize: 13, italic: true, color: C.accent4 });
    s.addNotes("So với Meidan: FPR của em 0,0025, thấp hơn 0,007 của bài nhưng chưa kiểm định, còn TPR 0,822 thay vì 100%. Phần bỏ sót nằm ở flood tcp/udp "
      + "giả mạo nguồn, trông giống lưu lượng bình thường. Chia ngẫu nhiên ở E6 không làm TPR tăng, nên rò rỉ không phải lý do; em chưa tách được nguyên nhân duy nhất.");
  }

  // ================================================================ Kết luận & dự định làm tiếp (bản 4'30)
  async function finalSlide(section, k) {
    s = content(section);
    kick(s, k);
    s.addText("Kết luận và dự định làm tiếp", { placeholder: "title" });
    card(s, 0.6, 1.4, 5.5, 5.2, HEX.dk2, "concl-card");
    text(s, "Kết luận", { x: 0.9, y: 1.6, w: 5.0, h: 0.45, fontSize: 19, bold: true, color: HEX.accent2 });
    const concl = ["AE per-device bắt gần tuyệt đối 8/10 loại tấn công, FPR " + f(b0.fpr, 4) + "; bỏ sót flood tcp/udp giả mạo nguồn",
      `V1 int8 ${f(v.size_kb, 1)} KB, ~${Math.round(v.p95_us)} µs/mẫu trên 1 lõi – khả thi cho edge`,
      `MTD lai do AE kích hoạt: cùng mức lộ diện, đổi ít hơn ≈ ${saving}%`,
      "Tái lập Masud: khớp mức VM/đường, tổng AC và RoC gần khớp; tổng R, Hình 5–9 chưa khớp vì bài thiếu thông tin"];
    s.addText(concl.map((t, i) => ({ text: t, options: { bullet: true, breakLine: i < concl.length - 1 } })),
      { x: 0.9, y: 2.15, w: 5.0, h: 4.3, fontSize: 15, color: C.background1, paraSpaceAfter: 10, valign: "top", margin: 0, isTextBox: true, objectName: "concl-text" });
    text(s, "Dự định làm tiếp", { x: 6.5, y: 1.45, w: 6.2, h: 0.45, fontSize: 19, bold: true, color: C.text2 });
    const next = [
      [fa.FaFilter, HEX.accent3, "Bắt flood giả mạo nguồn", "đặc trưng tốc độ luồng mới, entropy IP nguồn; luật chạy song song AE"],
      [fa.FaMicrochip, HEX.accent5, "Chạy trên Raspberry Pi", "đo độ trễ và điện năng thật, tính cả bước trích đặc trưng"],
      [fa.FaNetworkWired, HEX.accent1, "MTD trên mạng giả lập", "Mininet / SDN, đo gián đoạn dịch vụ khi đổi IP, firmware"],
      [fa.FaDatabase, HEX.accent2, "Thử dữ liệu mới", "CICIoT2023, IoT-23 – kiểm tra khả năng tổng quát"],
      [fa.FaEnvelope, HEX.accent4, "Hoàn thiện tái lập", "xin tác giả công thức AC, chuỗi 8 đường Hình 7, mô hình Hình 8–9"],
    ];
    for (let i = 0; i < next.length; i++) {
      const y = 2.0 + i * 0.9;
      await iconCircle(s, next[i][0], 6.5, y, 0.62, next[i][1], "next" + i);
      const nx = MAU2 ? 6.5 : 7.3, nw = MAU2 ? 6.2 : 5.4;
      text(s, next[i][2], { x: nx, y: y - 0.04, w: nw, h: 0.35, fontSize: MAU2 ? 16 : 15, bold: true, color: C.text2 });
      text(s, next[i][3], { x: nx, y: y + 0.3, w: nw, h: 0.4, fontSize: MAU2 ? 14 : 13 });
    }
    text(s, "Mã nguồn: github.com/thtra04/LAB_AT_BMHTTT (thư mục DT043) · Em cảm ơn thầy và các bạn!", { x: 6.5, y: 6.35, w: 6.2, h: 0.35,
      fontSize: 13, italic: true, color: C.accent4 });
    s.addNotes("Tóm lại: autoencoder nhẹ bắt gần tuyệt đối 8/10 loại tấn công, báo động giả thấp, chạy được ở edge. Dự định tiếp theo: thêm đặc trưng "
      + "cho flood giả mạo nguồn, chạy trên Raspberry Pi có đo điện, đưa MTD lai lên mạng giả lập và thử trên bộ dữ liệu mới. Em cảm ơn thầy và các bạn.");
  }

  // ================================================================ thứ tự slide
  const sec = (title) => { pres.addSection({ title }); return title; };
  let t;
  if (!NO_DEMO) {
    t = sec("Mở đầu");
    await titleSlide(t);
    await problemSlide(t);
    t = sec("Bài báo tham khảo");
    await paperSlides(ctx, t);
    t = sec("Dữ liệu & phương pháp");
    dataSlide(t);
    await modelSlide(t);
    await demoSlide(t);
    t = sec("Kết quả");
    resultSlide(t);
    edgeSlide(t);
    mtdSlide(t, null, "MTD: tái lập paper chính bằng đúng dữ liệu của paper");
    await fig6Slide(ctx, t);
    t = sec("Kết luận");
    criteriaConclSlide(t);
    await appendixSlides(ctx);
  } else {
    // 5 phần theo yêu cầu: phân tích bài báo → các bước làm bài → kết quả → so sánh với bài báo → dự định làm tiếp
    await titleSlide(sec("Mở đầu"));
    t = sec("1. Phân tích bài báo");
    await paperSlides(ctx, t, "PHẦN 1 · PHÂN TÍCH BÀI BÁO · MASUD ET AL. (2025)");
    t = sec("2. Các bước làm bài");
    await stepsSlides(t, "PHẦN 2 · CÁC BƯỚC LÀM BÀI");
    t = sec("3. Kết quả");
    resultSlide(t, "PHẦN 3 · KẾT QUẢ");
    criteriaSlide(t, "PHẦN 3 · KẾT QUẢ");
    t = sec("4. So sánh với bài báo");
    meidanSlide(t, "PHẦN 4 · SO SÁNH BÀI LÀM VÀ BÀI BÁO");
    mtdSlide(t, "PHẦN 4 · SO SÁNH BÀI LÀM VÀ BÀI BÁO", "So sánh với Masud 2025: tái lập bằng đúng dữ liệu bài");
    t = sec("5. Dự định làm tiếp");
    await finalSlide(t, "PHẦN 5 · DỰ ĐỊNH LÀM TIẾP");
    await appendixSlides(ctx, { skipProcess: true, e12: true });
  }

  await pres.writeFile({ fileName: OUT });
  await applyTheme(OUT, THEME);
  console.log("Đã lưu", OUT);
}

main().catch((err) => { console.error(err); process.exit(1); });
