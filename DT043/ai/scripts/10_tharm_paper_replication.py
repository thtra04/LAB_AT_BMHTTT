"""E11 – Tái lập paper chính (Masud et al. 2025) bằng 3-layer THARM với ĐÚNG số liệu của paper (Bảng 1, 2, Hình 1, 3,
Definition 2) và đối chiếu từng con số paper công bố (Bảng 4, mục 4.2–4.4).

Chạy:  python ai/scripts/10_tharm_paper_replication.py
Đầu ra: results/tables/tharm_vm_vs_paper.csv, tharm_paths_vs_paper.csv, tharm_scenarios.csv, tharm_network_vs_paper.csv,
        tharm_centrality.csv, results/figures/fig_tharm_scenarios.png, results/tharm_replication.log
"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "ai" / "src"))

from nbaiot.mtd import tharm as T  # noqa: E402

TAB, FIG = ROOT / "results" / "tables", ROOT / "results" / "figures"
VMS = [f"V{i}" for i in range(1, 9)]


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    TAB.mkdir(parents=True, exist_ok=True)
    FIG.mkdir(parents=True, exist_ok=True)
    out = []

    # 1. Chỉ số từng VM so với Bảng 4 và các giá trị R_v paper dùng trong mục 4.2–4.3
    b = T.build()
    rows = []
    for i, v in enumerate(VMS):
        rows.append({"VM": v, "OS": b.os[v], "dịch vụ": ",".join(f"s{s}" for s in b.services[v]) or "–",
                     "ASP_ours": b.asp(v), "ASP_paper": T.PAPER_TABLE4["ASP"][i],
                     "AC_ours": b.cost(v), "AC_paper": T.PAPER_TABLE4["AC"][i],
                     "AR_ours(ASP_paper×ΣBS)": T.PAPER_TABLE4["ASP"][i] * b.base_score(v), "AR_paper": T.PAPER_TABLE4["AR"][i],
                     "R_ours(ΣE·I)": b.risk(v), "R_paper(mục 4.2–4.3)": T.PAPER_VM_RISK.get(v)})
    vm = pd.DataFrame(rows)
    vm.to_csv(TAB / "tharm_vm_vs_paper.csv", index=False)
    out.append("== Chỉ số VM so với paper\n" + vm.round(4).to_string(index=False))
    d5 = T.diversity(b, "V5")
    out.append(f"R_V5 sau diversity (Linux): ours {d5.risk('V5'):.3f} – paper {T.PAPER_VM_RISK['V5_linux']}")

    # 2. Rủi ro theo đường tấn công paper nêu làm ví dụ
    sc = T.scenarios()
    s, d, r = sc["S"], sc["D"], sc["R"]
    pmap = {"shuffle A-V2-V7-V5-V8": s.path_metrics(["A", "V2", "V7", "V5", "V8"]),
            "diversity A-V2-V4-V5(Linux)-V8": d.path_metrics(["A", "V2", "V4", "V5", "V8"]),
            "redundancy A-V2-V4-V5'-V8": r.path_metrics(["A", "V2", "V4", "V5'", "V8"])}
    paths = pd.DataFrame([{"đường (ví dụ của paper)": k, "R_ours": v["R"], "R_paper": T.PAPER_PATHS[k],
                           "lệch %": 100 * (v["R"] - T.PAPER_PATHS[k]) / T.PAPER_PATHS[k]} for k, v in pmap.items()])
    paths.to_csv(TAB / "tharm_paths_vs_paper.csv", index=False)
    out.append("== Rủi ro đường tấn công\n" + paths.round(3).to_string(index=False))

    # 3. Kịch bản MTD (V5 như paper): theo Def. 2 và theo Hình 3 (thêm V6→V4)
    srows = []
    for fig3 in (False, True):
        for name, st in T.scenarios(with_fig3_edge=fig3).items():
            m = st.network_metrics()
            srows.append({"topology": "Hình 3 (+V6→V4)" if fig3 else "Definition 2", "MTD": name, **m,
                          "đường": " | ".join("-".join(p) for p in st.paths())})
    scen = pd.DataFrame(srows)
    scen.to_csv(TAB / "tharm_scenarios.csv", index=False)
    out.append("== Kịch bản MTD\n" + scen.drop(columns="đường").round(3).to_string(index=False))

    # 4. Tổng toàn mạng so với paper
    base = scen[(scen.topology == "Definition 2")].set_index("MTD")
    fig3 = scen[(scen.topology != "Definition 2")].set_index("MTD")
    nrows = []
    for key, mtd in (("shuffle", "S"), ("diversity", "D"), ("redundancy", "R")):
        for k in ("R", "AC", "RoC"):
            nrows.append({"MTD": key, "chỉ số": k, "ours": base.loc[mtd, k], "paper": T.PAPER_NETWORK[key][k]})
    net = pd.DataFrame(nrows)
    net.to_csv(TAB / "tharm_network_vs_paper.csv", index=False)
    out.append("== Tổng toàn mạng\n" + net.round(3).to_string(index=False))

    # 5. Xu hướng định tính paper kết luận – kiểm tra trên cả hai topology
    trows = []
    for topo in ("Definition 2", "Hình 3 (+V6→V4)"):
        t = scen[scen.topology == topo].set_index("MTD")
        n0 = t.loc["none"]
        checks = [("Shuffle làm giảm rủi ro mạng so với không MTD", t.loc["S", "R"] < n0["R"]),
                  ("Diversity làm giảm rủi ro mạng so với không MTD", t.loc["D", "R"] < n0["R"]),
                  ("Redundancy làm tăng rủi ro (thêm VM, thêm lỗ hổng)", t.loc["R", "R"] > n0["R"]),
                  ("Rủi ro diversity < redundancy (paper: 163.73 < 260.84)", t.loc["D", "R"] < t.loc["R", "R"]),
                  ("S+D có rủi ro mạng thấp nhất trong các phương án", t.loc["S+D", "R"] == t["R"].min()),
                  ("S+D có ASP trung bình các đường thấp hơn S và D riêng",
                   t.loc["S+D", "ASP_mean_path"] < min(t.loc["S", "ASP_mean_path"], t.loc["D", "ASP_mean_path"])),
                  ("S+D+R giảm rủi ro so với chỉ R", t.loc["S+D+R", "R"] < t.loc["R", "R"])]
        trows += [{"topology": topo, "kết luận của paper": c, "tái lập": bool(ok)} for c, ok in checks]
    tr = pd.DataFrame(trows)
    tr.to_csv(TAB / "tharm_trends.csv", index=False)
    out.append("== Xu hướng định tính\n" + "\n".join(f"[{'ĐÚNG' if r['tái lập'] else 'KHÔNG'}] {r['topology']}: "
                                                    f"{r['kết luận của paper']}" for r in trows))

    # 6. Độ trung tâm và lựa chọn V* (Eq. 8)
    cen = pd.DataFrame(b.centrality()).T
    cen.to_csv(TAB / "tharm_centrality.csv")
    out.append(f"== Độ trung tâm (Eq. 5–7), V* = {b.select_vm()} (paper: V5)\n" + cen.round(3).to_string())
    out.append(f"PSV giữa không MTD → shuffle V5: {T.path_shuffle_variation([b, s]):.3f}")

    # Hình
    fig, axes = plt.subplots(1, 3, figsize=(13, 3.8))
    order = ["none", "S", "D", "R", "S+D", "S+D+R"]
    import numpy as np
    x = np.arange(len(order))
    for ax, (k, lab) in zip(axes, [("R", "Attack risk (tổng các đường)"), ("AC", "Attack cost (tổng các đường)"),
                                   ("ASP_mean_path", "ASP trung bình các đường")]):
        ax.bar(x - 0.2, base.loc[order, k], 0.4, label="Definition 2", color="#3b82f6")
        ax.bar(x + 0.2, fig3.loc[order, k], 0.4, label="Hình 3 (+V6→V4)", color="#f59e0b")
        ax.set_xticks(x, order, fontsize=9)
        ax.set_title(lab, fontsize=10)
    axes[0].legend(fontsize=8)
    fig.suptitle("Tái lập 3-layer THARM (Masud et al. 2025) – MTD áp lên V5 như ví dụ của paper", fontsize=11)
    fig.tight_layout()
    fig.savefig(FIG / "fig_tharm_scenarios.png", dpi=150)

    text = "\n\n".join(out)
    (ROOT / "results" / "tharm_replication.log").write_text(text, encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
