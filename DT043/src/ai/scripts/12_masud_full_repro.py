"""E12 – Tái hiện đầy đủ nhất có thể phần kết quả của Masud et al. (2025): tổng mạng, Hình 5, 6, 7, 8.

Không chỉnh số cho khớp. Mọi giá trị "bài báo" của hình là đọc bằng mắt (sai số ≈ ±5 với AR, ±15 với AC, ±0.03 với RoC, ASP).
Phần suy ra thêm so với E11 (bài không in rõ):
- AC theo VM = Σ CVSS BS × attack cost (khớp 3/4 số AC bài in; V2 không khớp).
- ASP theo VM = Eq. 1 đúng nguyên văn bản in, ASP đường = tích ASP các VM trên đường.
- IPV (Hình 5a): m IP đổi mỗi chu kỳ, m ∈ {8, 9, 10} SUY RA TỪ CHÍNH HÌNH nên hình này chỉ kiểm tra công thức, không độc lập.
- Hình 8: bài không mô tả cách sinh mạng 400 VM; bộ sinh ở đây là giả định nên chỉ so tỷ lệ so với "trước MTD".
Hình 9 không chạy: bài không nêu mô hình theo thời gian, và trục ASP 200–400 trái định nghĩa ASP ∈ [0, 1].

Chạy:  python ai/scripts/12_masud_full_repro.py
Đầu ra: results/tables/e12_*.csv, results/figures/fig_e12_*.png
"""
from __future__ import annotations

import itertools
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import networkx as nx  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "ai" / "src"))

from nbaiot.mtd import tharm as T  # noqa: E402

TAB, FIG = ROOT / "results" / "tables", ROOT / "results" / "figures"
ORDER = ["V5", "V4", "V7", "V2", "V1", "V3", "V6"]
DST = {"V2": "H3"}
MTDS = ["s", "d", "r", "s+d", "s+d+r"]
# Đọc bằng mắt từ Hình 6 của bài, theo thứ tự ORDER
PAPER_FIG6 = {
    "AR": {"s": [167, 171, 184, 188, 203, 203, 209], "d": [203, 222, 232, 203, 221, 205, 210],
           "r": [261, 263, 258, 252, 266, 263, 265], "s+d": [165, 179, 193, 182, 205, 194, 205],
           "s+d+r": [173, 196, 211, 195, 222, 206, 218]},
    "AC": {"s": [660, 665, 710, 760, 730, 745, 825], "d": [625, 605, 690, 720, 700, 710, 790],
           "r": [878, 880, 875, 868, 882, 880, 882], "s+d": [635, 620, 695, 725, 705, 715, 800],
           "s+d+r": [640, 620, 700, 730, 715, 720, 810]},
    "RoC": {"s": [1.01, 1.04, 1.01, 0.99, 1.09, 1.07, 1.26], "d": [1.04, 1.21, 1.11, 1.02, 1.16, 1.08, 1.32],
            "r": [1.46, 1.48, 1.45, 1.43, 1.48, 1.47, 1.48], "s+d": [1.04, 1.21, 1.11, 1.02, 1.16, 1.08, 1.32],
            "s+d+r": [1.09, 1.28, 1.20, 1.07, 1.25, 1.14, 1.37]},
}
PAPER_FIG7_BEFORE = [.285, .265, .435, .42, .35, .435, .265, .215]
PAPER_FIG7_AFTER = [.275, .275, .41, .405, .36, .40, .26, .205]
PAPER_FIG5B = {10: [.5, .5, 1, 1, .75, 1, .75, .5], 15: [.67, .67, 1, 1, .83, 1, .67, .5],
               20: [.62, .67, .65, 1, .82, 1, .52, .22]}
PAPER_FIG8_400 = {"AR": {"before": 1.3, "S": 1.3, "D": .85, "R": 3.7, "S+D": .8, "S+D+R": 1.2},
                  "AC": {"before": 2.9, "S": 2.8, "D": 4.0, "R": 4.4, "S+D": 4.0, "S+D+R": 6.0},
                  "RoA": {"before": 430, "S": 420, "D": 205, "R": 430, "S+D": 205, "S+D+R": 200}}


def states(base: T.Tharm, vm: str) -> dict[str, T.Tharm]:
    s = T.shuffle(base, vm, DST.get(vm, "H4"))
    sd = T.diversity(s, vm)
    return {"s": s, "d": T.diversity(base, vm), "r": T.redundancy(base, vm), "s+d": sd, "s+d+r": T.redundancy(sd, vm)}


def network_totals() -> pd.DataFrame:
    rows = []
    for name, fig3 in (("Definition 2", False), ("Hình 3", True)):
        sc = T.scenarios(with_fig3_edge=fig3)
        for key, label in (("S", "shuffle"), ("D", "diversity"), ("R", "redundancy")):
            pap = T.PAPER_NETWORK[label]
            old = sc[key].network_metrics()
            for variant, printed in (("Σ BS×cost", False), ("Σ BS×cost + số bài in", True)):
                m = sc[key].network_metrics_weighted(printed)
                for k in ("R", "AC", "RoC"):
                    rows.append({"topology": name, "MTD": label, "biến thể": variant, "chỉ số": k, "bài báo": pap[k],
                                 "E11 cũ": old[k], "E12": m[k], "lệch E11 %": 100 * (old[k] / pap[k] - 1),
                                 "lệch E12 %": 100 * (m[k] / pap[k] - 1), "n_paths": m["n_paths"]})
    df = pd.DataFrame(rows)
    df.to_csv(TAB / "e12_network_totals.csv", index=False)
    return df


def vm_ac_check() -> pd.DataFrame:
    b = T.build()
    df = pd.DataFrame([{"VM": v, "AC bài in (mục 4.2)": p, "Σ cost (E11)": b.cost(v), "Σ BS×cost (E12)": b.cost_weighted(v),
                        "lệch E12 %": 100 * (b.cost_weighted(v) / p - 1)} for v, p in T.PAPER_VM_AC.items()])
    df.to_csv(TAB / "e12_vm_ac.csv", index=False)
    return df


def path_set_search() -> pd.DataFrame:
    """Có tập 4 đường nào cho đúng R_s = 167.38 và AC_s = 666.2 không? (dùng số bài in; có đường ví dụ của bài)."""
    b = T.build()
    vms = [v for v in T.VM_OS if v != "V8"]
    allp = [list(c) + ["V8"] for n in range(1, 5) for c in itertools.permutations(vms, n)]
    rv = {v: b.risk_printed(v) for v in T.VM_OS}
    cv = {v: b.cost_weighted(v, True) for v in T.VM_OS}
    must = ["V2", "V7", "V5", "V8"]
    rc = [(p, sum(rv[v] for v in p), sum(cv[v] for v in p)) for p in allp if p != must]
    r0, c0 = sum(rv[v] for v in must), sum(cv[v] for v in must)
    rows = []
    # giới hạn: đường hợp lệ phải bắt đầu ở điểm vào của bài (V1 hoặc V2)
    rc = [x for x in rc if x[0][0] in ("V1", "V2")]
    for tri in itertools.combinations(rc, 3):
        r = r0 + sum(x[1] for x in tri)
        if abs(r - 167.38) > 0.05:
            continue
        c = c0 + sum(x[2] for x in tri)
        if abs(c - 666.2) <= 1.0:
            rows.append({"đường": " ; ".join("-".join(x[0]) for x in tri), "R": r, "AC": c})
    df = pd.DataFrame(rows, columns=["đường", "R", "AC"])
    df.to_csv(TAB / "e12_shuffle_path_search.csv", index=False)
    return df


def fig6() -> pd.DataFrame:
    rows = []
    for name, fig3 in (("Definition 2", False), ("Hình 3", True)):
        base = T.build(with_fig3_edge=fig3)
        for i, vm in enumerate(ORDER):
            for mtd, st in states(base, vm).items():
                m = st.network_metrics_weighted(printed=True)
                for k in ("AR", "AC", "RoC"):
                    ours = m["R" if k == "AR" else k]
                    pap = PAPER_FIG6[k][mtd][i]
                    rows.append({"topology": name, "VM": vm, "MTD": mtd, "chỉ số": k, "E12": ours, "bài báo (đọc hình)": pap,
                                 "lệch %": 100 * (ours / pap - 1)})
    df = pd.DataFrame(rows)
    df.to_csv(TAB / "e12_fig6.csv", index=False)

    fig, axes = plt.subplots(2, 3, figsize=(15, 8), sharex=True)
    color = {"s": "#3b6fc4", "d": "#e08a3c", "r": "#3a9d5d", "s+d": "#d64545", "s+d+r": "#7b1f8a"}
    for c, k in enumerate(("AR", "AC", "RoC")):
        for mtd in MTDS:
            axes[0, c].plot(ORDER, PAPER_FIG6[k][mtd], "--o", ms=4, color=color[mtd], label=mtd)
            d = df[(df.topology == "Definition 2") & (df.MTD == mtd) & (df["chỉ số"] == k)].set_index("VM").loc[ORDER]
            axes[1, c].plot(ORDER, d["E12"], "--o", ms=4, color=color[mtd], label=mtd)
        axes[0, c].set_title(f"{k} – bài báo (đọc từ Hình 6)")
        axes[1, c].set_title(f"{k} – E12, topology Definition 2")
        for r in (0, 1):
            axes[r, c].grid(alpha=.4)
            axes[r, c].legend(fontsize=7)
            axes[r, c].set_ylim(bottom=0)
    fig.tight_layout()
    fig.savefig(FIG / "fig_e12_masud_fig6.png", dpi=140)
    plt.close(fig)
    return df


def fig7() -> pd.DataFrame:
    b = T.build(with_fig3_edge=True)
    rows = []
    for p in b.paths():
        vms = p[1:]
        before = float(np.prod([b.asp_eq1(v) for v in vms]))
        d5 = T.diversity(b, "V5")
        dall = b
        for v in T.VM_OS:
            dall = T.diversity(dall, v)
        rows.append({"đường": "-".join(p), "ASP trước (Eq. 1)": before,
                     "ASP sau diversity V5": float(np.prod([d5.asp_eq1(v) for v in vms])),
                     "ASP sau diversity mọi VM": float(np.prod([dall.asp_eq1(v) for v in vms])),
                     "ASP cũ (OR độc lập)": b.path_metrics(p)["ASP"]})
    df = pd.DataFrame(rows)
    df.to_csv(TAB / "e12_fig7.csv", index=False)

    fig, (a, c) = plt.subplots(1, 2, figsize=(13, 4.6), sharey=True)
    x = np.arange(8)
    a.bar(x - .18, PAPER_FIG7_BEFORE, .36, color="#1f5f7a", label="Before")
    a.bar(x + .18, PAPER_FIG7_AFTER, .36, color="#ed7d31", label="After")
    a.set_xticks(x, [f"Path {i + 1}" for i in x])
    a.set_title("Bài báo (đọc từ Hình 7) – 8 đường không nêu chuỗi VM")
    x = np.arange(len(df))
    c.bar(x - .18, df["ASP trước (Eq. 1)"], .36, color="#1f5f7a", label="Before")
    c.bar(x + .18, df["ASP sau diversity V5"], .36, color="#ed7d31", label="After (V5 → Linux)")
    c.set_xticks(x, [s.replace("A-", "").replace("-", "→") for s in df["đường"]], fontsize=7)
    c.set_title("E12 – Eq. 1 nguyên văn, 5 đường của topology Hình 3")
    for ax in (a, c):
        ax.grid(axis="y", alpha=.4)
        ax.legend()
    fig.tight_layout()
    fig.savefig(FIG / "fig_e12_masud_fig7.png", dpi=140)
    plt.close(fig)
    return df


def psv_of(before: T.Tharm, after: T.Tharm) -> float:
    return T.path_shuffle_variation([before, after])


def random_edges(n_edges: int, rng: np.random.Generator) -> T.Tharm:
    """Đồ thị n_edges cạnh trên 8 VM, luôn giữ Definition 2 làm lõi nếu n_edges ≥ 11 (giả định, bài không nêu)."""
    edges = list(T.EDGES_DEF2)
    nodes = list(T.VM_OS)
    cand = [(u, v) for u in nodes[:-1] for v in nodes if u != v and (u, v) not in edges and nodes.index(u) < nodes.index(v)]
    if n_edges < len(edges):
        keep = [i for i in range(len(edges))]
        rng.shuffle(keep)
        g = None
        for size in (n_edges,):
            for _ in range(500):
                pick = rng.choice(len(edges), size, replace=False)
                g = nx.DiGraph([edges[i] for i in pick])
                if "A" in g and "V8" in g and nx.has_path(g, "A", "V8"):
                    break
        edges = list(g.edges)
    else:
        idx = rng.choice(len(cand), n_edges - len(edges), replace=False)
        edges += [cand[i] for i in idx]
    gg = nx.DiGraph(edges)
    gg.add_nodes_from(T.VM_OS)
    return T.Tharm(gg, dict(T.VM_OS), {k: list(v) for k, v in T.VM_SERVICES.items()})


def fig5(seeds: int = 200) -> tuple[pd.DataFrame, pd.DataFrame]:
    # (a) IPV đúng công thức mục 3.6.1, k = 1
    rng = np.random.default_rng(42)
    t = np.arange(10, 150, 20)
    rows = []
    for n in (10, 20, 50, 100, 200):
        ips = set(range(n))
        nxt = n
        for tt in t:
            m = int(rng.integers(8, 11))
            old = rng.choice(sorted(ips), min(m, n), replace=False)
            new = set(range(nxt, nxt + len(old)))
            nxt += len(old)
            cur = (ips - set(old.tolist())) | new
            rows.append({"n": n, "t": int(tt), "IPV": len(cur - ips) / len(cur)})
            ips = cur
    ipv = pd.DataFrame(rows)
    ipv.to_csv(TAB / "e12_fig5a_ipv.csv", index=False)

    # (b) PSV khi shuffle từng VM, trung bình trên các đồ thị n cạnh
    rows = []
    for n_edges in ("Definition 2", 10, 15, 20):
        for vm in list(T.VM_OS):
            vals = []
            for s in range(1 if n_edges == "Definition 2" else seeds):
                base = T.build() if n_edges == "Definition 2" else random_edges(int(n_edges), np.random.default_rng(s))
                if vm not in base.graph or not base.paths():
                    continue
                dst = DST.get(vm, "H4" if T.HOSTS[vm] != "H4" else "H3")
                after = T.shuffle(base, vm, dst)
                if after.paths():
                    vals.append(psv_of(base, after))
            pap = PAPER_FIG5B[n_edges][list(T.VM_OS).index(vm)] if n_edges in PAPER_FIG5B else np.nan
            rows.append({"Edge set": n_edges, "VM": vm, "PSV": float(np.mean(vals)) if vals else np.nan, "bài báo": pap})
    psv = pd.DataFrame(rows)
    psv.to_csv(TAB / "e12_fig5b_psv.csv", index=False)

    fig, (a, b) = plt.subplots(1, 2, figsize=(12, 4.4))
    for n, g in ipv.groupby("n"):
        a.plot(g.t, g.IPV, "-o", ms=4, label=f"n={n}")
    a.set_xlabel("Time (s)"), a.set_ylabel("IPV"), a.set_title("Hình 5(a) chạy lại: IPV ≈ m/n"), a.legend(), a.grid(alpha=.4)
    for n, g in psv.groupby("Edge set", sort=False):
        b.plot(g.VM, g.PSV, "-o", ms=4, label=str(n))
    b.set_ylim(0, 1.05), b.set_title("Hình 5(b) chạy lại: PSV theo VM (đồ thị n cạnh là giả định)"), b.legend(), b.grid(alpha=.4)
    fig.tight_layout()
    fig.savefig(FIG / "fig_e12_masud_fig5.png", dpi=140)
    plt.close(fig)
    return ipv, psv


def layered_cloud(n: int, rng: np.random.Generator) -> nx.DiGraph:
    """GIẢ ĐỊNH: mạng phân lớp, vài VM cửa vào, một nút đích, mỗi VM nối tới 2 VM lớp sau."""
    layers = np.array_split(np.arange(n), 5)
    g = nx.DiGraph()
    g.add_nodes_from(range(n))
    g.add_nodes_from(["A", "T"])
    for v in rng.choice(layers[0], max(2, n // 100), replace=False):
        g.add_edge("A", int(v))
    for a, b in zip(layers, layers[1:]):
        for v in a:
            for w in rng.choice(b, 2, replace=False):
                g.add_edge(int(v), int(w))
    for v in layers[-1]:
        g.add_edge(int(v), "T")
    return g


def cloud_metrics(g: nx.DiGraph, os_of: dict) -> dict:
    """Tổng theo đường bằng quy hoạch động (số đường rất lớn nên không liệt kê)."""
    order = list(nx.topological_sort(g))
    fw = {v: 0.0 for v in g}
    fw["A"] = 1.0
    for v in order:
        for w in g.successors(v):
            fw[w] += fw[v]
    bw = {v: 0.0 for v in g}
    bw["T"] = 1.0
    for v in reversed(order):
        for w in g.successors(v):
            bw[v] += bw[w]
    r = c = 0.0
    for v in g:
        if v in ("A", "T"):
            continue
        vul = T.OS_VULNS[os_of[v]]
        through = fw[v] * bw[v]
        r += through * sum(x[4] * x[3] for x in vul)
        c += through * sum(x[2] * x[5] for x in vul)
    paths = fw["T"]
    return {"AR": r, "AC": c, "RoA": paths * r / c if c else 0.0, "paths": paths}


def fig8(seeds: int = 5) -> pd.DataFrame:
    rows = []
    for n in (50, 100, 200, 400):
        for seed in range(seeds):
            rng = np.random.default_rng(seed)
            g = layered_cloud(n, rng)
            vms = [v for v in g if v not in ("A", "T")]
            win = {v: "Windows 11" for v in vms}
            lin = {v: "Linux" for v in vms}
            # shuffle: 10% VM đổi nút ở lớp kế cận (giữ số cạnh)
            s = g.copy()
            for v in rng.choice(vms, max(1, n // 10), replace=False):
                v = int(v)
                succ = [w for w in s.successors(v) if w != "T"]
                if succ:
                    alts = [w for w in vms if w not in succ and w != v and nx.has_path(g, v, w)]
                    if alts:
                        s.remove_edge(v, succ[0])
                        s.add_edge(v, int(rng.choice(alts)))

            def redund(h: nx.DiGraph) -> tuple[nx.DiGraph, dict]:
                r = h.copy()
                extra = {}
                for i, v in enumerate(rng.choice(vms, max(1, n // 10), replace=False)):
                    v, new = int(v), 10 ** 6 + i
                    extra[new] = v
                    for u in list(h.predecessors(v)):
                        r.add_edge(u, new)
                    for w in list(h.successors(v)):
                        r.add_edge(new, w)
                return r, extra

            rr, ex = redund(g)
            srr, ex2 = redund(s)
            cases = {"before": (g, win), "S": (s, win), "D": (g, lin), "S+D": (s, lin),
                     "R": (rr, {**win, **{k: "Linux" for k in ex}}),
                     "S+D+R": (srr, {**lin, **{k: "Linux" for k in ex2}})}
            base = cloud_metrics(g, win)
            for name, (h, os_of) in cases.items():
                m = cloud_metrics(h, os_of)
                rows.append({"n": n, "seed": seed, "MTD": name, **m,
                             **{f"tỷ lệ {k}": m[k] / base[k] for k in ("AR", "AC", "RoA")}})
    df = pd.DataFrame(rows)
    df.to_csv(TAB / "e12_fig8_runs.csv", index=False)
    agg = df[df.n == 400].groupby("MTD")[["tỷ lệ AR", "tỷ lệ AC", "tỷ lệ RoA"]].mean()
    for k in ("AR", "AC", "RoA"):
        agg[f"bài {k}"] = [PAPER_FIG8_400[k][m] / PAPER_FIG8_400[k]["before"] for m in agg.index]
    agg.to_csv(TAB / "e12_fig8_vs_paper.csv")
    return agg


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    pd.set_option("display.width", 200, "display.max_columns", 30)
    print("== AC theo VM\n", vm_ac_check().round(2).to_string(index=False))
    net = network_totals()
    print("== Tổng mạng\n", net.round(2).to_string(index=False))
    found = path_set_search()
    print(f"== Tập 4 đường khớp đồng thời R_s, AC_s: {len(found)}\n", found.head(10).to_string(index=False))
    f6 = fig6()
    f6["ok"] = f6["lệch %"].abs() <= 5
    print("== Hình 6, số điểm lệch ≤ 5%\n", f6.groupby(["topology", "chỉ số", "MTD"]).ok.sum().unstack().to_string())
    print(f6.groupby(["topology", "chỉ số"])[["ok"]].sum().assign(tong=35).to_string())
    print("== Hình 7\n", fig7().round(3).to_string(index=False))
    ipv, psv = fig5()
    print("== Hình 5a IPV\n", ipv.groupby("n").IPV.mean().round(3).to_string())
    print("== Hình 5b PSV\n", psv.pivot(index="VM", columns="Edge set", values="PSV").round(2).to_string())
    print("== Hình 8 (n = 400, tỷ lệ so với trước MTD)\n", fig8().round(2).to_string())


if __name__ == "__main__":
    main()
