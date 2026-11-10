// Slide dùng chung cho hai bộ slide: phân tích bài báo tham khảo (3 slide trong phần trình bày)
// và phụ lục chi tiết (8 slide: Meidan 2018, quy trình, phương pháp, thực nghiệm, tái lập, nguyên mẫu).
// Hình của bài báo được cắt bằng report/extract_paper_figs.py.
const path = require("path");
const fs = require("fs");
const sharp = require("sharp");

const HERE = __dirname;
const ROOT = path.resolve(HERE, "..");
const TAB = path.join(ROOT, "results", "tables");
const PFIG = path.join(HERE, "paper_figs");

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

function helpers(ctx) {
  const { pres, HEX, C, text } = ctx;
  return {
    // nhãn nhỏ phía trên tiêu đề (giống "2. BÀI BÁO THAM KHẢO")
    kicker(s, label) {
      if (ctx.MAU2) {   // chuyển thành dòng nhỏ ở chân trang, không in hoa
        const parts = label.split(" · ");
        const low = (t) => t.charAt(0) + t.slice(1).toLocaleLowerCase("vi");
        const foot = parts[0] === "PHỤ LỤC" ? "Phụ lục" : parts.slice(0, 2).map((t, i) => (i ? t.toLocaleLowerCase("vi") : low(t))).join(" – ");
        text(s, foot, { x: 6.6, y: 7.0, w: 5.5, h: 0.3, fontSize: 10, color: C.accent4, align: "right", objectName: "section-label" });
        return;
      }
      text(s, label, { x: 0.6, y: 0.12, w: 12.1, h: 0.3, fontSize: 13, bold: true, color: C.accent5, charSpacing: 1 });
    },
    // ảnh co vừa khung, giữ tỉ lệ, căn giữa
    async image(s, file, x, y, w, h, name, align = "center") {
      const m = await sharp(file).metadata();
      const r = m.width / m.height;
      let iw = w, ih = w / r;
      if (ih > h) { ih = h; iw = h * r; }
      const ix = align === "left" ? x : x + (w - iw) / 2;
      s.addImage({ path: file, x: ix, y, w: iw, h: ih, objectName: name });
      return { x: ix, y, w: iw, h: ih };
    },
    caption(s, t, x, y, w) {
      text(s, t, { x, y, w, h: 0.35, fontSize: 11, italic: true, color: C.accent4, align: "center" });
    },
    table(s, rows, opts) {
      const { head = HEX.dk2, fontSize = 12, colorCol, boldFirst = true } = opts;
      s.addTable(rows.map((r, i) => r.map((c, j) => ({ text: String(c), options: {
        bold: i === 0 || (boldFirst && j === 0), color: i === 0 ? HEX.lt1 : (colorCol && j === colorCol.j ? colorCol.fn(c) : HEX.dk1),
        fill: { color: i === 0 ? head : (i % 2 ? "FFFFFF" : HEX.lt2) } } }))),
        { fontSize, border: { type: "solid", pt: 0.5, color: "D0DAE0" }, valign: "middle", margin: [2, 5, 2, 5], ...opts.box });
    },
    // khối "nhãn màu + nội dung" như slide phân tích bài báo
    labelRow(s, label, body, y, h, color, name) {
      if (ctx.MAU2) {
        text(s, label, { x: 0.6, y, w: 2.1, h, fontSize: 18, bold: true, color: C.text2, valign: "middle" });
        text(s, body, { x: 2.8, y, w: 9.9, h, fontSize: 17, valign: "middle", objectName: name + "-text" });
        return;
      }
      s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.6, y, w: 2.4, h, rectRadius: 0.08, fill: { color }, line: { color }, objectName: name });
      text(s, label, { x: 0.6, y, w: 2.4, h, fontSize: 17, bold: true, color: C.background1, align: "center", valign: "middle" });
      text(s, body, { x: 3.25, y, w: 9.45, h, fontSize: 16, valign: "middle", objectName: name + "-text" });
    },
    // danh sách có tiêu đề in đậm: [[tiêu đề, [ý, ...]], ...]
    groups(s, groups, box) {
      const runs = [];
      groups.forEach(([head, items], gi) => {
        runs.push({ text: head, options: { bold: true, color: C.text2, breakLine: true, paraSpaceBefore: gi ? 8 : 0 } });
        items.forEach((t, k) => runs.push({ text: t, options: { bullet: { indent: 14 }, breakLine: !(gi === groups.length - 1 && k === items.length - 1) } }));
      });
      s.addText(runs, { isTextBox: true, margin: 0, valign: "top", color: C.text1, paraSpaceAfter: 3, ...box });
    },
  };
}

// ======================================================================= phân tích bài báo (3 slide)
async function paperSlides(ctx, section, KICK = "BÀI BÁO THAM KHẢO · MASUD ET AL. (2025)") {
  const { HEX, C, text, card, content } = ctx;
  const H = helpers(ctx);
  let s;

  // ---- 1. Bài toán mà bài báo đặt ra
  s = content(section);
  H.kicker(s, KICK);
  s.addText("Bài toán mà bài báo đặt ra", { placeholder: "title" });
  H.labelRow(s, "Bối cảnh", "Tấn công mạng nhắm vào hạ tầng và thiết bị IoT ngày càng nhiều. Moving Target Defence (MTD) liên tục "
    + "thay đổi bề mặt tấn công – địa chỉ, hệ điều hành, số bản sao máy – để kẻ tấn công khó khai thác và tốn công hơn.", 1.5, 1.3, HEX.accent5, "ctx");
  H.labelRow(s, "Vấn đề cốt lõi", "Chưa có đánh giá hiệu quả khi kết hợp nhiều kỹ thuật MTD theo thời gian, chi phí và công sức tấn công. "
    + "IoT không đồng nhất, tài nguyên hạn chế, nên MTD có thể tiêu tốn quá mức tài nguyên mạng và hệ thống.", 2.95, 1.3, HEX.accent3, "core");
  H.labelRow(s, "Yêu cầu đặt ra", "Cần phương pháp định lượng mức an toàn của từng trạng thái mạng sau mỗi lần MTD, so sánh shuffle, "
    + "diversity, redundancy và tổ hợp của chúng để chọn chiến lược phòng thủ tốt nhất.", 4.4, 1.3, HEX.accent1, "req");
  card(s, 0.6, 5.95, 12.1, 0.8, HEX.lt2, "cite");
  text(s, "Masud, Keshk, Moustafa, Turnbull, Susilo – Vulnerability defence using hybrid moving target defence in Internet of Things "
    + "systems. Computers & Security 153 (2025) 104380 · DOI 10.1016/j.cose.2025.104380 · Open Access (CC BY)",
  { x: 0.85, y: 5.95, w: 11.6, h: 0.8, fontSize: 13, italic: true, color: C.accent4, valign: "middle" });
  s.addNotes("Bài báo tham khảo chính của đề tài là Masud và cộng sự, 2025. Bối cảnh: MTD liên tục thay đổi bề mặt tấn công. Vấn đề: "
    + "chưa có đánh giá khi kết hợp nhiều kỹ thuật MTD về rủi ro, chi phí và tài nguyên. Yêu cầu: định lượng an toàn từng trạng thái mạng "
    + "để chọn tổ hợp MTD tốt nhất.");

  // ---- 2. Phương pháp
  s = content(section);
  H.kicker(s, KICK);
  s.addText("Phương pháp: mô hình 3-layer THARM và ba kỹ thuật MTD", { placeholder: "title" });
  const im = await H.image(s, path.join(PFIG, "masud_fig3_tharm.png"), 0.6, 1.4, 5.9, 4.75, "paper-fig3");
  H.caption(s, "Hình 3 của bài báo: tầng trên (máy ảo, dịch vụ) và tầng dưới (cây lỗ hổng OR)", 0.6, im.y + im.h + 0.08, 5.9);
  H.groups(s, [
    ["Mô hình TH = (N, U, S, L, C)", ["N: các trạng thái mạng theo thời gian", "U: đồ thị tấn công giữa 8 máy ảo",
      "S: đồ thị tấn công giữa 14 dịch vụ", "L: cây tấn công (cổng OR) gồm lỗ hổng OS + dịch vụ của từng máy ảo"]],
    ["MTD kích hoạt theo thời gian (chu kỳ 10 phút)", ["Shuffle: di trú máy ảo, đổi IP qua SDN", "Diversity: đổi hệ điều hành",
      "Redundancy: nhân bản máy ảo"]],
    ["Chỉ số đánh giá", ["ASP (xác suất tấn công thành công), rủi ro AR, chi phí tấn công AC, RoC = R/AC",
      "Độ trung tâm của đồ thị để chọn máy ảo cần bảo vệ"]],
  ], { x: 6.9, y: 1.45, w: 5.8, h: 5.3, fontSize: 15 });
  s.addNotes("Phương pháp: mô hình đồ thị tấn công ba tầng THARM – máy ảo, dịch vụ và cây lỗ hổng – trên 8 máy ảo; áp shuffle, "
    + "diversity, redundancy theo chu kỳ 10 phút, đo xác suất tấn công thành công, rủi ro và chi phí tấn công.");

  // ---- 3. Thực nghiệm, kết quả, hạn chế
  s = content(section);
  H.kicker(s, KICK);
  s.addText("Thực nghiệm, kết quả và hạn chế của bài báo", { placeholder: "title" });
  const im6 = await H.image(s, path.join(PFIG, "masud_fig6_metrics.png"), 0.6, 1.4, 6.5, 4.05, "paper-fig6");
  H.caption(s, "Hình 6 của bài báo: AR, AC, RoC sau khi áp MTD (s, d, r, s+d, s+d+r) lên từng máy ảo", 0.6, im6.y + im6.h + 0.06, 6.5);
  const boxes = [
    ["Thực nghiệm", "Mô phỏng 4 host, 8 máy ảo (Linux, Windows 11, FreeBSD), 18 CVE hệ điều hành + 14 CVE dịch vụ kèm CVSS; không dùng dataset.", HEX.accent5],
    ["Kết quả", "Shuffle + diversity cho rủi ro thấp nhất, chi phí tấn công cao hơn. Ví dụ V5: R_s 167.38 · R_d 163.73 · R_r 260.84.", HEX.accent1],
    ["Hạn chế", "Chỉ mô phỏng; xác suất khai thác tĩnh; chỉ MTD theo thời gian, không có bộ phát hiện kích hoạt; không công bố mã.", HEX.accent3],
  ];
  boxes.forEach((b, i) => {
    const y = 1.4 + i * 1.45;
    card(s, 7.4, y, 5.3, 1.32, HEX.lt2, "res" + i);
    s.addShape(ctx.pres.shapes.RECTANGLE, { x: 7.4, y, w: 0.1, h: 1.32, fill: { color: b[2] }, line: { color: b[2] }, objectName: "res-bar" + i });
    text(s, b[0], { x: 7.65, y: y + 0.08, w: 4.9, h: 0.35, fontSize: 15, bold: true, color: C.text2 });
    text(s, b[1], { x: 7.65, y: y + 0.43, w: 4.9, h: 0.85, fontSize: 13 });
  });
  text(s, "→ Đề tài: Track A phát hiện botnet bằng autoencoder (theo Meidan 2018) · Track B tái lập THARM và MTD lai do cảnh báo AE kích hoạt",
    { x: 0.6, y: 5.95, w: 12.1, h: 0.75, fontSize: 16, bold: true, color: C.accent3, align: "center", valign: "middle" });
  s.addNotes("Kết quả của bài: kết hợp shuffle và diversity cho rủi ro thấp nhất. Hạn chế: chỉ mô phỏng, chỉ MTD theo thời gian, không có bộ "
    + "phát hiện kích hoạt MTD và không dùng autoencoder. Vì vậy em chia hai track: A phát hiện bằng autoencoder theo Meidan; B tái lập "
    + "THARM bằng đúng dữ liệu của bài và dùng cảnh báo autoencoder để kích hoạt MTD lai.");
}

// ======================================================================= chạy lại Hình 6 của bài báo (trình bày chính)
// hai ảnh đặt cạnh nhau: hình gốc (trái) và hình chạy lại cùng dạng (phải), có nhãn
async function sideBySide(ctx, s, H, left, right, y, h) {
  const { text, C } = ctx;
  for (const [i, [file, label, name]] of [left, right].entries()) {
    const x = 0.6 + i * 6.2;
    text(s, label, { x, y, w: 5.9, h: 0.32, fontSize: 13, bold: true, color: i ? C.accent1 : C.accent5, align: "center" });
    await H.image(s, file, x, y + 0.36, 5.9, h, name);
  }
}

async function fig6Slide(ctx, section, kick = "TÁI LẬP BÀI BÁO CHÍNH · CHẠY LẠI ĐÚNG DẠNG BIỂU ĐỒ") {
  const { HEX, C, text, content, FIG } = ctx;
  const H = helpers(ctx);
  const cmp = csv("paper_fig6_masud_vs_paper.csv");
  const ok = (m) => cmp.filter((r) => r.MTD === m && Math.abs(Number(r["lệch %"])) <= 5).length;
  const s = content(section);
  H.kicker(s, kick);
  s.addText("Chạy lại Hình 6 của bài báo: AR, AC, RoC theo VM", { placeholder: "title" });
  await sideBySide(ctx, s, H, [path.join(PFIG, "masud_fig6_metrics.png"), "Hình 6 – bài báo", "fig6-paper"],
    [path.join(FIG, "fig_paper_masud_fig6.png"), "Chạy lại – DT043 (dữ liệu bài báo, topology Hình 3)", "fig6-ours"], 1.3, 3.75);
  const chips = [
    [`Diversity: khớp ${ok("d")}/7 VM (lệch ≤ 5%)`, HEX.accent6],
    [`Shuffle, S+D: khớp ở V5 – VM duy nhất bài nêu host đích`, HEX.accent2],
    ["Toàn Hình 6(a): 11/35 điểm lệch ≤ 5%; redundancy, S+D+R cao hơn; AC, RoC: xem E12", HEX.accent3],
  ];
  chips.forEach((c, i) => {
    const x = 0.6 + i * 4.1;
    s.addShape(ctx.pres.shapes.ROUNDED_RECTANGLE, { x, y: 5.6, w: 3.9, h: 1.05, rectRadius: 0.08, fill: { color: c[1] }, line: { color: c[1] }, objectName: "fig6chip" + i });
    text(s, c[0], { x: x + 0.15, y: 5.6, w: 3.6, h: 1.05, fontSize: 14, bold: true, color: i === 1 ? C.text1 : C.background1, valign: "middle", align: "center" });
  });
  s.addNotes("Thầy yêu cầu chạy lại đúng biểu đồ của bài: em áp từng kỹ thuật MTD lên từng máy ảo theo thứ tự trục x của Hình 6, "
    + "dùng đúng CVE và topology của bài. Đường diversity khớp cả 7 máy ảo, lệch dưới 5%; shuffle và S+D chỉ khớp ở V5 vì bài chỉ "
    + "nêu host đích của V5; redundancy cao hơn và AC, RoC khác thang đo vì bài không nêu đủ công thức. Số liệu: "
    + "results/tables/paper_fig6_masud_vs_paper.csv.");
}

// ======================================================================= quy trình thực hiện (phụ lục, hoặc phần chính ở bản 4'30)
function processSlide(ctx, section, kick) {
  const { pres, D, HEX, C, text, card, content, nf } = ctx;
  const H = helpers(ctx);
  const s = content(section);
  H.kicker(s, kick);
  s.addText("Quy trình thực hiện: từ đọc bài báo đến báo cáo", { placeholder: "title" });
  const steps = [
    ["Đọc bài báo", "Masud 2025 lệch chủ đề (MTD, không AE) → chia 2 track; Meidan 2018 làm baseline"],
    ["Lập kế hoạch", "Phiếu tái lập, ≥ 5 hạn chế, 6 câu hỏi nghiên cứu, ma trận thí nghiệm"],
    ["Môi trường, dữ liệu", "Python 3.11 + khóa phiên bản; tải N-BaIoT 1.77 GB, manifest SHA-256 107 file"],
    ["Làm sạch, EDA", `Kiểm schema 115 cột, khử ${nf(D.data.dups)} dòng trùng, đo mất cân bằng, tự tương quan`],
    ["Pipeline + test", "Chia chống rò rỉ, scaler, AE, ngưỡng, int8; 30 test unit / integration / negative"],
    ["Chốt tiêu chí", "Smoke test 1 lần → chốt tiêu chí thành công, lưu SHA-256 trước khi chạy"],
    ["Chạy ma trận", `${D.n_runs} lần chạy (cấu hình × thiết bị × seed), mỗi lần 1 process, có resume và log`],
    ["Hệ thống 4 tầng", "Xuất gói AI → BE; FastAPI + SQLite + dashboard; 12 test BE/DB"],
    ["Tổng hợp, báo cáo", "KTC95, Wilcoxon + Holm, đối chiếu tiêu chí; Word và slide sinh từ số liệu"],
    ["Tái lập bài chính", "Có toàn văn: dựng 3-layer THARM bằng đúng CVE/topology (E11, E12), 24 test so số"],
  ];
  steps.forEach((st, i) => {
    const x = 0.6 + (i % 5) * 2.45, y = 1.45 + Math.floor(i / 5) * 2.55;
    card(s, x, y, 2.3, 2.4, HEX.lt2, "step" + i);
    s.addShape(pres.shapes.OVAL, { x: x + 0.15, y: y + 0.15, w: 0.5, h: 0.5, fill: { color: i === 5 ? HEX.accent3 : HEX.dk2 }, line: { color: i === 5 ? HEX.accent3 : HEX.dk2 }, objectName: "stepnum" + i });
    text(s, String(i + 1), { x: x + 0.15, y: y + 0.15, w: 0.5, h: 0.5, fontSize: 15, bold: true, color: C.background1, align: "center", valign: "middle" });
    text(s, st[0], { x: x + 0.75, y: y + 0.12, w: 1.45, h: 0.56, fontSize: 14, bold: true, color: C.text2, valign: "middle" });
    text(s, st[1], { x: x + 0.15, y: y + 0.8, w: 2.0, h: 1.5, fontSize: 12.5 });
    if (i % 5 < 4) s.addShape(pres.shapes.RIGHT_ARROW, { x: x + 2.31, y: y + 1.05, w: 0.13, h: 0.3, fill: { color: HEX.accent4 }, line: { color: HEX.accent4 }, objectName: "steparrow" + i });
  });
  text(s, "Mỗi bước có lệnh đã chạy, kết quả và sự cố gặp phải trong tailieu/NHAT_KY_THUC_HIEN.md; bước 6 làm trước khi có kết quả nên không thể chỉnh tiêu chí theo kết quả.",
    { x: 0.6, y: 6.55, w: 12.1, h: 0.4, fontSize: 12, italic: true, color: C.accent4 });
  s.addNotes("Quy trình: đọc bài báo và thấy bài chính lệch chủ đề nên chia hai track; lập kế hoạch, chuẩn bị môi trường và dữ liệu có checksum; "
    + "làm sạch, EDA; viết pipeline kèm test; chốt tiêu chí trước khi chạy; chạy 468 lần; dựng hệ thống 4 tầng; tổng hợp thống kê và viết báo cáo; "
    + "cuối cùng tái lập bài chính bằng toàn văn.");
}

// ======================================================================= phụ lục chi tiết
// skipProcess: bản 4'30 đã đưa slide quy trình lên phần chính
async function appendixSlides(ctx, { skipProcess = false, e12 = false } = {}) {
  const { pres, D, HEX, C, text, card, content, f, nf, FIG } = ctx;
  const H = helpers(ctx);
  const SEC = "Phụ lục";
  const cf = D.configs, q = D.quant;
  let s;
  pres.addSection({ title: SEC });

  // ---- A1. Bài báo kỹ thuật Meidan 2018
  s = content(SEC);
  H.kicker(s, "PHỤ LỤC · BÀI BÁO THAM CHIẾU KỸ THUẬT");
  s.addText("N-BaIoT (Meidan et al., 2018): bài toán, phương pháp, kết quả", { placeholder: "title" });
  const mrows = [
    ["Bài toán", "Phát hiện thiết bị IoT đã bị nhiễm botnet ngay khi bắt đầu tấn công, chỉ từ lưu lượng mạng.", HEX.accent5],
    ["Phương pháp", "Lây nhiễm Mirai, BASHLITE vào 9 thiết bị thật; 115 đặc trưng thống kê; mỗi thiết bị một deep AE học benign; "
      + "tr* = mean + std, majority vote trên cửa sổ ws*.", HEX.accent1],
    ["Kết quả", "TPR 100%, FPR 0.007 ± 0.01 – tốt hơn Isolation Forest, LOF, SVM; phát hiện trong 174 ± 212 ms.", HEX.accent6],
    ["Hạn chế", "Chia dữ liệu một lần, không khoảng tin cậy; ngưỡng/cửa sổ chọn để FPR = 0; không lượng tử hóa, không đo trên edge.", HEX.accent3],
  ];
  mrows.forEach((r, i) => {
    const y = 1.4 + i * 0.6;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.6, y, w: 1.8, h: 0.5, rectRadius: 0.06, fill: { color: r[2] }, line: { color: r[2] }, objectName: "m-label" + i });
    text(s, r[0], { x: 0.6, y, w: 1.8, h: 0.5, fontSize: 14, bold: true, color: C.background1, align: "center", valign: "middle" });
    text(s, r[1], { x: 2.6, y, w: 10.1, h: 0.5, fontSize: 13.5, valign: "middle" });
  });
  const imm = await H.image(s, path.join(PFIG, "meidan_fig2_results.png"), 0.6, 3.9, 12.1, 2.6, "meidan-fig2");
  H.caption(s, "Hình 2 (a, b) của bài báo: TPR/FPR và thời gian phát hiện của autoencoder so với Isolation Forest, LOF, SVM",
    0.6, imm.y + imm.h + 0.04, 12.1);
  s.addNotes("Bài tham chiếu kỹ thuật: Meidan 2018 tạo bộ N-BaIoT, huấn luyện mỗi thiết bị một autoencoder trên benign, ngưỡng mean + std và "
    + "vote cửa sổ, đạt TPR 100%. Hạn chế: một lần chia dữ liệu, không lượng tử hóa, không đo edge – đây là chỗ đề tài làm thêm.");

  // ---- A2. Quy trình thực hiện
  if (!skipProcess) processSlide(ctx, SEC, "PHỤ LỤC · CÁCH LÀM RA ĐỀ TÀI");

  // ---- A3. Phương pháp phát hiện chi tiết
  s = content(SEC);
  H.kicker(s, "PHỤ LỤC · PHƯƠNG PHÁP");
  s.addText("Phương pháp phát hiện: chi tiết từng bước", { placeholder: "title" });
  const mstep = [
    "Chia benign của mỗi thiết bị theo thời gian: DStrn | DSopt | test (mỗi phần 1/3), bỏ 500 dòng đệm ở mỗi ranh giới; dữ liệu tấn công chỉ ở test.",
    "Chuẩn hóa z-score, fit chỉ trên DStrn của đúng thiết bị (scaler gắn tên thiết bị).",
    "Huấn luyện AE chỉ trên benign: Adam lr 1e-3, batch 256, early stopping (patience 8) theo DSopt, tối đa 100 epoch.",
    "Điểm bất thường của mỗi mẫu = MSE tái tạo (tính bằng float64 vì có đặc trưng tới 5.9e17).",
    "Ngưỡng tr* và cửa sổ ws* chỉ lấy từ DSopt benign (công thức bên phải).",
    "Lượng tử hóa TFLite (fp16, dynamic, full-int8 với dữ liệu đại diện từ DStrn), rồi tính lại tr*, ws* bằng chính model int8.",
    "Đánh giá trên test ở mức cửa sổ: macro-F1, FPR, TPR; 5 seed, KTC95, Wilcoxon + Holm trên 9 thiết bị.",
  ];
  s.addText(mstep.map((t, i) => ({ text: t, options: { bullet: { type: "number" }, breakLine: i < mstep.length - 1 } })),
    { x: 0.6, y: 1.45, w: 7.3, h: 5.3, fontSize: 16, color: C.text1, paraSpaceAfter: 10, valign: "top", margin: 0, isTextBox: true });
  card(s, 8.3, 1.45, 4.4, 5.3, HEX.dk2, "formula-card");
  s.addText([
    { text: "Công thức", options: { bold: true, fontSize: 18, color: C.accent2, breakLine: true } },
    { text: "MSE(x) = (1/115) · Σ (xᵢ − x̂ᵢ)²", options: { breakLine: true, paraSpaceBefore: 10 } },
    { text: "tr* = mean(MSE_DSopt) + std(MSE_DSopt)", options: { breakLine: true, paraSpaceBefore: 10 } },
    { text: "Cửa sổ ws* mẫu bị cảnh báo khi hơn một nửa số mẫu có MSE > tr*", options: { breakLine: true, paraSpaceBefore: 10 } },
    { text: "ws* = cửa sổ nhỏ nhất cho FPR = 0 trên DSopt", options: { breakLine: true, paraSpaceBefore: 10 } },
    { text: "Vì sao hiệu chỉnh sau int8?", options: { bold: true, color: C.accent2, breakLine: true, paraSpaceBefore: 16 } },
    { text: "Lượng tử hóa làm lệch phân phối MSE; ngưỡng chỉ dùng DSopt benign nên tính lại được mà không chạm vào test.", options: {} },
  ], { x: 8.55, y: 1.65, w: 3.95, h: 4.95, fontSize: 14.5, color: C.background1, valign: "top", margin: 0, isTextBox: true });
  s.addNotes("Phương pháp bám theo Meidan nhưng thống nhất cách tối ưu và chặn rò rỉ: chia theo thời gian có vùng đệm, scaler fit trên train, "
    + "ngưỡng và cửa sổ chỉ từ DSopt benign; sau lượng tử hóa int8 thì tính lại ngưỡng bằng chính model int8.");

  // ---- A4. Thực nghiệm
  s = content(SEC);
  H.kicker(s, "PHỤ LỤC · THỰC NGHIỆM");
  s.addText("Thực nghiệm: ma trận E1–E11 và môi trường chạy", { placeholder: "title" });
  H.table(s, [["ID", "Nội dung", "Số lần chạy", "Phục vụ"],
    ["E1", "B0 – tái lập baseline Meidan", "9 × 5", "RQ1"],
    ["E2", "B1 global; B1 chung + chuẩn hóa riêng", "9 × 5 × 2", "RQ2"],
    ["E3", "B2 Isolation Forest", "9 × 5", "baseline"],
    ["E4", "V1 nhẹ; V2 × 5 cửa sổ", "45 + 135", "RQ3"],
    ["E5", "fp32 / fp16 / dyn / int8 × giữ / hiệu chỉnh ngưỡng", "trong E1, E4", "RQ4"],
    ["E6", "Đối chứng rò rỉ (cố tình chia ngẫu nhiên)", "9 × 3", "chống rò rỉ"],
    ["E7", "Ablation 4 quy tắc ngưỡng × 3 cửa sổ", "trong E1, E4", "ablation"],
    ["E8", "Edge benchmark P0 / P1", "3 × 4 × 3 × 5 lượt", "RQ5"],
    ["E9", "Robustness: né tránh, nhiễu, đầu độc 1% / 5%", "9 × 3 × 3", "an toàn"],
    ["E10", "MTD: HARM rút gọn + MTD lai do AE kích hoạt", "5 seed Monte Carlo", "RQ6"],
    ["E11", "Tái lập 3-layer THARM bằng dữ liệu bài báo", "tất định, 24 test", "bài chính"]],
  { fontSize: 12, box: { x: 0.6, y: 1.4, w: 8.1, colW: [0.65, 4.35, 1.95, 1.15], rowH: 0.42, objectName: "matrix-table" } });
  card(s, 9.0, 1.4, 3.7, 2.55, HEX.lt2, "env-card");
  H.groups(s, [["Môi trường", ["i7-13650HX (6 P + 8 E core), RAM 23.7 GB, Windows 11", "Python 3.11.9, TensorFlow 2.21, scikit-learn 1.9",
    "Seed 42, 1337, 2024, 7, 123"]]], { x: 9.2, y: 1.55, w: 3.35, h: 2.3, fontSize: 12.5 });
  card(s, 9.0, 4.1, 3.7, 2.6, HEX.lt2, "rule-card");
  H.groups(s, [["Nguyên tắc", ["Mỗi cấu hình là 1 file YAML; lưu config, seed, log, metric từng lần chạy",
    `Giữ cả lần chạy lỗi; tổng ${D.n_runs} kết quả, không chọn seed đẹp`, "Test chỉ dùng để đánh giá cuối cùng"]]],
  { x: 9.2, y: 4.25, w: 3.35, h: 2.35, fontSize: 12.5 });
  s.addNotes("Ma trận thí nghiệm E1 đến E11, mỗi thí nghiệm gắn với một câu hỏi nghiên cứu; chạy trên laptop i7-13650HX, 5 seed cố định, "
    + "mọi lần chạy đều được lưu kể cả lần lỗi.");

  // ---- A5. Tái lập bài báo chính – cách làm
  s = content(SEC);
  H.kicker(s, "PHỤ LỤC · TÁI LẬP BÀI BÁO CHÍNH (E11)");
  s.addText("Tái lập 3-layer THARM: lấy gì từ bài báo, tính thế nào", { placeholder: "title" });
  H.table(s, [["Lấy từ bài báo", "Nguồn"],
    ["18 CVE hệ điều hành: CVSS, exploitability E, impact I, cost", "Bảng 1"],
    ["14 CVE của dịch vụ s1–s14", "Bảng 2"],
    ["Máy ảo → hệ điều hành (Linux, Windows 11, FreeBSD)", "Hình 1"],
    ["Máy ảo → dịch vụ; V8 là CSDL đích", "Hình 3"],
    ["Đồ thị tấn công giữa máy ảo (11 cạnh)", "Definition 2"],
    ["Shuffle: V5 di trú host 2 → host 4", "Mục 4.2"],
    ["Diversity: đổi hệ điều hành dự phòng", "Mục 4.3"],
    ["Redundancy: nhân bản V5 → V5′", "Mục 4.4"]],
  { fontSize: 13, boldFirst: false, box: { x: 0.6, y: 1.4, w: 6.4, colW: [4.9, 1.5], rowH: 0.5, objectName: "tharm-input" } });
  const tsteps = [
    ["Dựng 3 tầng", "Cây tấn công OR cho từng máy ảo → đồ thị dịch vụ → đồ thị máy ảo, không tự đặt tham số."],
    ["Rủi ro máy ảo", "R_v = Σ E · I. Bản in ghi tích (∏) nhưng chỉ dạng tổng mới khớp các số bài báo dùng."],
    ["Đường tấn công", "Rủi ro đường = tổng R các máy ảo trên đường; AC = Σ cost; ASP theo OR độc lập."],
    ["So với bài báo", "Áp shuffle / diversity / redundancy và tổ hợp; so số công bố và 7 kết luận định tính trên 2 topology."],
  ];
  tsteps.forEach((t, i) => {
    const y = 1.4 + i * 1.22;
    card(s, 7.4, y, 5.3, 1.1, HEX.lt2, "ts" + i);
    s.addShape(pres.shapes.OVAL, { x: 7.55, y: y + 0.3, w: 0.5, h: 0.5, fill: { color: HEX.accent2 }, line: { color: HEX.accent2 }, objectName: "tsn" + i });
    text(s, String(i + 1), { x: 7.55, y: y + 0.3, w: 0.5, h: 0.5, fontSize: 15, bold: true, color: C.text1, align: "center", valign: "middle" });
    text(s, t[0], { x: 8.2, y: y + 0.08, w: 4.4, h: 0.35, fontSize: 14, bold: true, color: C.text2 });
    text(s, t[1], { x: 8.2, y: y + 0.42, w: 4.4, h: 0.65, fontSize: 12 });
  });
  text(s, "Mã: ai/src/nbaiot/mtd/tharm.py · script ai/scripts/10_tharm_paper_replication.py · 24 test khóa các số của bài báo · chi tiết: tailieu/docs/tai_lap_paper_chinh.md",
    { x: 0.6, y: 6.4, w: 12.1, h: 0.45, fontSize: 12, italic: true, color: C.accent4 });
  s.addNotes("E11: em dựng lại THARM chỉ bằng dữ liệu bài báo công bố – 32 CVE, 8 máy ảo, topology và các bước MTD trong mục 4. "
    + "Phát hiện quan trọng: công thức rủi ro phải là tổng mới khớp số của bài, bản in ghi tích.");

  // ---- A6. Kết quả tái lập Meidan 2018
  s = content(SEC);
  H.kicker(s, "PHỤ LỤC · KẾT QUẢ TÁI LẬP (TRACK A)");
  s.addText("Kết quả tái lập Meidan 2018 trên N-BaIoT", { placeholder: "title" });
  const b0 = cf.E1_baseline, v1 = q.V1_int8_recal;
  H.table(s, [["Chỉ số", "Meidan 2018", "DT043 B0", "V1 int8", "Nhận xét"],
    ["TPR", "100%", f(b0.tpr), f(v1.tpr), "Không đạt"],
    ["FPR", "0.007", f(b0.fpr, 4), f(v1.fpr, 4), "Thấp hơn"],
    ["ws* (mẫu)", "20–82", String(Math.round(b0.ws)), String(v1.ws), "Dài hơn"],
    ["Model", "172 kB", q.B0_fp32_keep.kb + " KB", v1.kb + " KB", "Nhỏ ~10×"],
    ["Chia dữ liệu", "1 lần", "5 seed", "5 seed", "Chặt hơn"]],
  { fontSize: 12.5, box: { x: 0.6, y: 1.4, w: 7.1, colW: [1.5, 1.45, 1.35, 1.35, 1.45], rowH: 0.42, objectName: "meidan-table" } });
  card(s, 8.0, 1.4, 4.7, 2.52, HEX.lt2, "why-card");
  H.groups(s, [["Vì sao lệch so với bài báo", ["Flood tcp/udp của BASHLITE giả mạo nguồn → giống benign, MSE dưới ngưỡng",
    "Đuôi MSE trên DSopt kéo ngưỡng mean + std lên cao", "Khử trùng lặp + vùng đệm → ws* dài hơn", "8/10 loại tấn công còn lại recall ≈ 1"]]],
  { x: 8.2, y: 1.5, w: 4.35, h: 2.35, fontSize: 12.5 });
  await H.image(s, path.join(FIG, "fig_macro_f1_per_device.png"), 0.6, 4.1, 6.9, 2.8, "fig-f1-device");
  await H.image(s, path.join(FIG, "fig_recall_per_attack.png"), 7.7, 4.1, 5.0, 2.8, "fig-recall-attack");
  s.addNotes("So với Meidan: FPR thấp hơn nhưng TPR không đạt 100%; thiết bị Ennio, SH1002, SH1003 thấp vì flood tcp/udp giả mạo nguồn. "
    + "Model int8 nhỏ hơn khoảng 10 lần.");

  // ---- A6b. Chạy lại Hình 2 của Meidan
  s = content(SEC);
  H.kicker(s, "PHỤ LỤC · CHẠY LẠI ĐÚNG DẠNG BIỂU ĐỒ (MEIDAN 2018)");
  s.addText("Chạy lại Hình 2 (a, b) của Meidan 2018", { placeholder: "title" });
  text(s, "Hình 2 – bài báo", { x: 0.6, y: 1.3, w: 7.4, h: 0.3, fontSize: 13, bold: true, color: C.accent5 });
  await H.image(s, path.join(PFIG, "meidan_fig2_results.png"), 0.6, 1.62, 7.4, 2.45, "meidan2-paper", "left");
  text(s, "Chạy lại – DT043 (468 lần chạy, trung bình theo seed)", { x: 0.6, y: 4.18, w: 7.4, h: 0.3, fontSize: 13, bold: true, color: C.accent1 });
  await H.image(s, path.join(FIG, "fig_paper_meidan_fig2.png"), 0.6, 4.5, 7.4, 2.4, "meidan2-ours", "left");
  card(s, 8.4, 1.3, 4.3, 5.5, HEX.lt2, "meidan2-card");
  H.groups(s, [
    ["(a) Độ chính xác", ["FPR gần 0 ở mọi thuật toán – khớp bài báo", "TPR của AE: bài 100%, chạy lại trung vị 0.82 do flood tcp/udp giả mạo nguồn",
      "Isolation Forest chạy lại tốt hơn AE (bài: ngược lại)"]],
    ["(b) Thời gian phát hiện", ["Bài đo giây trên lưu lượng thật; N-BaIoT không có timestamp nên đo bằng số mẫu",
      "Thiết bị 3 (Ennio) trễ lớn vì AE bỏ sót tcp/udp"]],
    ["Chưa chạy lại được", ["LOF, One-class SVM (chưa nằm trong ma trận thí nghiệm)", "Hình 2 (c, d): cần lưu lượng theo giờ – không có trong dataset"]],
  ], { x: 8.6, y: 1.45, w: 3.95, h: 5.25, fontSize: 12.5 });
  s.addNotes("Hình 2 của Meidan vẽ lại cùng dạng: boxplot TPR/FPR theo thuật toán trên 9 thiết bị và độ trễ phát hiện theo thiết bị. "
    + "FPR khớp, TPR của autoencoder thấp hơn vì flood tcp/udp. Số liệu: results/tables/paper_fig2_meidan.csv.");

  // ---- A7. Kết quả tái lập bài báo chính
  s = content(SEC);
  H.kicker(s, "PHỤ LỤC · KẾT QUẢ TÁI LẬP (TRACK B, E11)");
  s.addText("Kết quả tái lập bài báo chính (Masud 2025)", { placeholder: "title" });
  const vm = Object.fromEntries(csv("tharm_vm_vs_paper.csv").map((r) => [r.VM, r]));
  const rv = (k) => Number(vm[k]["R_ours(ΣE·I)"]).toFixed(2);
  const paths = csv("tharm_paths_vs_paper.csv");
  const net = csv("tharm_network_vs_paper.csv").filter((r) => r["chỉ số"] === "R");
  const tr = csv("tharm_trends.csv");
  const nFig3 = tr.filter((t) => t.topology !== "Definition 2" && t["tái lập"] === "True").length;
  const nDef2 = tr.filter((t) => t.topology === "Definition 2" && t["tái lập"] === "True").length;
  const good = (c) => (c.startsWith("Khớp") ? HEX.accent6 : c.startsWith("Không") ? HEX.accent3 : HEX.dk1);
  H.table(s, [["Mức so sánh", "Bài báo", "Tái lập", "Kết luận"],
    ["Rủi ro V4 · V5 · V7 · V8", "12.47 · 12.58 · 8.67 · 5.62", [rv("V4"), rv("V5"), rv("V7"), rv("V8")].join(" · "), "Khớp ±0.01"],
    ["3 đường tấn công ví dụ", "43.15 · 43.31 · 43.31", paths.map((p) => Number(p.R_ours).toFixed(2)).join(" · "), "Khớp −0.8%"],
    ["Tổng mạng R_s · R_d · R_r", net.map((r) => Number(r.paper).toFixed(0)).join(" · "), net.map((r) => Number(r.ours).toFixed(0)).join(" · "), "Không khớp"]],
  { fontSize: 12.5, colorCol: { j: 3, fn: good }, box: { x: 0.6, y: 1.4, w: 8.0, colW: [2.5, 2.2, 2.0, 1.3], rowH: 0.45, objectName: "masud-table" } });
  ctx.stat(s, 8.95, 1.3, 1.8, nFig3 + "/7", "kết luận khớp (Hình 3)", HEX.accent1, "trend3");
  ctx.stat(s, 10.9, 1.3, 1.8, nDef2 + "/7", "theo Definition 2", HEX.accent3, "trend2");
  await H.image(s, path.join(FIG, "fig_tharm_scenarios.png"), 0.6, 3.45, 12.1, 3.15, "fig-tharm");
  text(s, "Tổng R không khớp với cả hai topology; AC, RoC xem E12. Kết luận \"S + D tốt nhất\" phụ thuộc cạnh V6 → V4 và chỉ đạt ở ví dụ V5.",
    { x: 0.6, y: 6.6, w: 12.1, h: 0.35, fontSize: 12, italic: true, color: C.accent4 });
  s.addNotes("Tái lập bài chính: rủi ro mức máy ảo khớp tới 0,01, ba đường tấn công lệch 0,8%, tổng R không khớp; với topology Hình 3 "
    + "tái lập 6/7 kết luận định tính, nhưng shuffle + diversity chỉ có rủi ro thấp nhất ở ví dụ V5.");

  // ---- A7c. Chạy lại Hình 7 của bài báo chính
  s = content(SEC);
  H.kicker(s, "PHỤ LỤC · CHẠY LẠI ĐÚNG DẠNG BIỂU ĐỒ (MASUD 2025)");
  s.addText("Chạy lại Hình 7: ASP trước / sau diversity", { placeholder: "title" });
  await sideBySide(ctx, s, H, [path.join(PFIG, "masud_fig7_asp.png"), "Hình 7 – bài báo (8 đường)", "fig7-paper"],
    [path.join(FIG, "fig_paper_masud_fig7.png"), "Chạy lại – DT043 (5 đường tới V8, diversity V5)", "fig7-ours"], 1.3, 3.9);
  card(s, 0.6, 5.75, 12.1, 0.95, HEX.lt2, "fig7-note");
  text(s, "Không tái lập được từng cột: topology chỉ có 5 đường tới V8 (bài vẽ 8, không in chuỗi VM). Hình phải dùng OR độc lập (0.91–0.94); Eq. 1 nguyên văn "
    + "(E12) cho 0.24–0.48, cùng thang với bài (0.2–0.43). Đổi V5 Windows 11 → Linux làm ASP tăng ở cả hai cách, ngược lời bình của bài.",
  { x: 0.85, y: 5.75, w: 11.6, h: 0.95, fontSize: 13, valign: "middle" });
  s.addNotes("Hình 7 vẽ lại cùng dạng nhưng không khớp: số đường và cách tính ASP đường của bài không suy ra được từ dữ liệu công bố. "
    + "Em ghi rõ là không tái lập được thay vì chỉnh số cho giống. Số liệu: results/tables/paper_fig7_masud.csv.");

  // ---- A7d. E12: tổng toàn mạng và các hình còn lại (chỉ bản 4'30)
  if (e12) {
    s = content(SEC);
    H.kicker(s, "PHỤ LỤC · TÁI HIỆN THÊM BÀI BÁO CHÍNH (E12)");
    s.addText("E12: công thức AC suy ra đưa tổng AC, RoC về gần bài", { placeholder: "title" });
    const e = csv("e12_network_totals.csv").filter((r) => r.topology === "Definition 2" && r["biến thể"] === "Σ BS×cost");
    const pick = (m, k) => e.find((r) => r.MTD === m && r["chỉ số"] === k);
    const pc = (r) => `${Number(r.E12).toFixed(r["chỉ số"] === "RoC" ? 2 : 1)} (${Number(r["lệch E12 %"]) > 0 ? "+" : ""}${Number(r["lệch E12 %"]).toFixed(1)}%)`;
    H.table(s, [["MTD trên V5", "R bài", "R E12", "AC bài", "AC E11", "AC E12", "RoC bài", "RoC E12"]].concat(
      [["shuffle", "Shuffle"], ["diversity", "Diversity"], ["redundancy", "Redundancy"]].map(([m, l]) => [l,
        Number(pick(m, "R")["bài báo"]).toFixed(1), pc(pick(m, "R")), Number(pick(m, "AC")["bài báo"]).toFixed(1),
        Number(pick(m, "AC")["E11 cũ"]).toFixed(1), pc(pick(m, "AC")), Number(pick(m, "RoC")["bài báo"]).toFixed(2), pc(pick(m, "RoC"))])),
    { fontSize: 12, box: { x: 0.6, y: 1.35, w: 12.1, colW: [1.6, 0.9, 2.0, 1.0, 1.0, 2.2, 1.0, 2.4], rowH: 0.4, objectName: "e12-table" } });
    card(s, 0.6, 3.1, 5.85, 3.6, HEX.lt2, "e12-formula");
    text(s, "Cách tính suy ra", { x: 0.85, y: 3.2, w: 5.4, h: 0.4, fontSize: 15, bold: true, color: C.text2 });
    const a = ["AC theo VM = Σ CVSS BS × attack cost: khớp V5, V7, V8; V2 lệch −33.9%",
      "Là giả thuyết, dò trên 4 số bài in; tổng AC không dùng khi chọn công thức",
      "Eq. 1 nguyên văn: ASP đường 0.24–0.48, cùng thang Hình 7 (0.2–0.43)",
      "Tổng mạng lệch ≤ 5%: 5/9 (E11: 1/9)"];
    s.addText(a.map((t, i) => ({ text: t, options: { bullet: true, breakLine: i < a.length - 1 } })),
      { x: 0.85, y: 3.65, w: 5.4, h: 2.95, fontSize: 15, color: C.text1, paraSpaceAfter: 8, valign: "top", margin: 0, isTextBox: true, objectName: "e12-a" });
    card(s, 6.85, 3.1, 5.85, 3.6, HEX.lt2, "e12-gaps");
    text(s, "Vẫn chưa khớp", { x: 7.1, y: 3.2, w: 5.4, h: 0.4, fontSize: 15, bold: true, color: C.accent3 });
    const b = ["Tổng R: diversity −13.1%, redundancy −16.6%",
      "Hình 5(b), Hình 6 cùng thang nhưng khác hình dạng; Hình 7 không có chuỗi VM",
      "Hình 8: chỉ so tỷ lệ, mạng 400 VM là giả định; Hình 9: không có mô hình thời gian",
      "Bài không nhất quán: R_d = 163.73 nhưng Hình 6 vẽ ≈ 203"];
    s.addText(b.map((t, i) => ({ text: t, options: { bullet: true, breakLine: i < b.length - 1 } })),
      { x: 7.1, y: 3.65, w: 5.4, h: 2.95, fontSize: 15, color: C.text1, paraSpaceAfter: 8, valign: "top", margin: 0, isTextBox: true, objectName: "e12-b" });
    s.addNotes("E12: em dò lại công thức mà bài không in rõ. AC theo VM bằng tổng điểm CVSS nhân chi phí khớp ba trên bốn số bài in, và đưa tổng AC toàn mạng về lệch "
      + "không quá 3,4%. Đây là giả thuyết của em, không phải công thức tác giả xác nhận. Tổng R của diversity, redundancy và nhiều hình vẫn chưa khớp, em không chỉnh số cho giống.");
  }

  // ---- A8. Nguyên mẫu
  s = content(SEC);
  H.kicker(s, "PHỤ LỤC · NGUYÊN MẪU");
  s.addText("Nguyên mẫu: luồng dữ liệu, gói triển khai và API", { placeholder: "title" });
  const flow = [["N-BaIoT CSV", "107 file, SHA-256"], ["03_prepare", "parquet, khử trùng"], ["04_run_matrix", "huấn luyện, đánh giá"],
    ["08_export_deploy", "gói V1 int8"], ["Backend FastAPI", "kiểm SHA-256, TFLite"], ["SQLite + dashboard", "cảnh báo, MTD"]];
  flow.forEach((b, i) => {
    const x = 0.6 + i * 2.06, fill = i < 4 ? HEX.accent1 : HEX.dk2;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y: 1.45, w: 1.8, h: 1.05, rectRadius: 0.08, fill: { color: fill }, line: { color: fill }, objectName: "flow" + i });
    s.addText([{ text: b[0], options: { bold: true, breakLine: true } }, { text: b[1], options: { fontSize: 11 } }],
      { x, y: 1.45, w: 1.8, h: 1.05, fontSize: 13, color: C.background1, align: "center", valign: "middle", margin: 2, isTextBox: true });
    if (i < 5) s.addShape(pres.shapes.RIGHT_ARROW, { x: x + 1.82, y: 1.83, w: 0.22, h: 0.3, fill: { color: HEX.accent4 }, line: { color: HEX.accent4 }, objectName: "flowarrow" + i });
  });
  text(s, "tầng AI", { x: 0.6, y: 2.55, w: 8.0, h: 0.3, fontSize: 11, italic: true, color: C.accent1, align: "center" });
  text(s, "tầng BE · DB · FE", { x: 8.84, y: 2.55, w: 3.86, h: 0.3, fontSize: 11, italic: true, color: C.text2, align: "center" });
  card(s, 0.6, 3.0, 5.9, 3.65, HEX.lt2, "pkg-card");
  H.groups(s, [["Gói triển khai mỗi thiết bị (artifacts/deploy/<thiết bị>/)", [
    "model.tflite – V1 int8, 15,688 byte", "scaler.json – mean/std 115 cột, gắn tên thiết bị",
    "meta.json – tr*, ws*, danh sách cột, SHA-256 của model", "Backend từ chối nạp nếu checksum lệch hoặc sai thiết bị"]],
  ["Cơ sở dữ liệu (6 bảng)", ["devices, models, detection_batches, alerts, mtd_actions, experiment_results – không lưu dữ liệu thô"]]],
  { x: 0.8, y: 3.15, w: 5.5, h: 3.4, fontSize: 13 });
  H.table(s, [["API", "Chức năng"],
    ["GET /api/health, /api/devices", "trạng thái, 9 model đã nạp"],
    ["POST /api/detect", "suy luận một lô đặc trưng"],
    ["POST /api/replay/{device}", "phát lại dữ liệu test công khai"],
    ["GET /api/alerts · POST …/ack", "xem, xác nhận cảnh báo"],
    ["GET /api/mtd/actions · POST /api/mtd/tick", "nhật ký MTD, MTD theo thời gian"],
    ["GET /api/experiments", "bảng kết quả thực nghiệm"]],
  { fontSize: 12, box: { x: 6.8, y: 3.0, w: 5.9, colW: [3.3, 2.6], rowH: 0.42, objectName: "api-table" } });
  text(s, "66 test tự động: 30 AI + 24 tái lập THARM + 12 backend/CSDL (gói bị sửa 1 byte, path traversal, sai số chiều, lô quá lớn)",
    { x: 6.8, y: 6.05, w: 5.9, h: 0.6, fontSize: 12, italic: true, color: C.accent4 });
  s.addNotes("Nguyên mẫu: tầng AI xuất gói triển khai gồm model int8, scaler và meta có checksum; backend FastAPI chỉ nạp gói hợp lệ, suy luận "
    + "TFLite một luồng, ghi cảnh báo và hành động MTD vào SQLite; dashboard gọi các API này.");
}

module.exports = { paperSlides, fig6Slide, processSlide, appendixSlides, helpers, csv };
