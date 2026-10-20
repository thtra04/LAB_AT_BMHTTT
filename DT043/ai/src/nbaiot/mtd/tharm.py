"""Tái lập 3-layer THARM của Masud et al. (2025, Computers & Security 153:104380) với SỐ LIỆU CỦA PAPER.

Nguồn từng phần (số trang/bảng của bản PDF Open Access):
- Lỗ hổng hệ điều hành w1–w6, li1–li6, f1–f6: Bảng 1 (CVSS BS, Impact, Exploitability, Attack cost).
- Lỗ hổng dịch vụ s1–s14: Bảng 2.
- VM → hệ điều hành: Hình 1 (Linux: V1, V4, V7, V8; Windows 11: V2, V5; FreeBSD: V3, V6).
- VM → dịch vụ: Hình 3 (V1: s1–s2, V2: s3–s4, …, V7: s13–s14; V8 chỉ nối tới CSDL).
- Đồ thị VM lớp trên: Definition 2 (11 cạnh); Hình 3 vẽ thêm cạnh V6 → V4 (tùy chọn `with_fig3_edge`).
- Shuffle: ví dụ mục 4.2 – V5 di trú host 2 → host 4, tạo đường A→V2→V7→V5→V8.
- Diversity: mục 4.3 – OS dự phòng: Windows 11 → Linux, FreeBSD → Windows 11, Linux → FreeBSD.
- Redundancy: mục 4.4 – nhân bản VM được chọn (V5′) với cùng kết nối; bản sao chạy OS dự phòng (paper: rủi ro
  đường A→V2→V4→V5′→V8 "giữ nguyên như diversity" = 43.31, tức V5′ mang lỗ hổng của Linux).

Công thức (Algorithm 2) – ghi rõ chỗ phải diễn giải vì bản in mâu thuẫn:
- Rủi ro VM  R_v = Σ E·I trên mọi lỗ hổng OS + dịch vụ. Bản in Eq. 2 ghi "∏"; diễn giải Σ khớp ĐÚNG các số
  của paper ở mục 4.2–4.3 (R_V4 = 12.47, R_V5 = 12.58, R_V5(Linux) = 8.9, R_V7 = 8.67, R_V8 = 5.62).
- ASP VM = 1 − Π(1 − E) (OR độc lập). Bản in Eq. 1 "1 − (Π + Π)" có thể âm nên không dùng nguyên văn;
  kết quả lệch nhẹ so với Bảng 4 (paper không công bố cách ra các số trong Bảng 4).
- Attack cost VM = Σ cost (Bảng 1 + Bảng 2): khớp Bảng 4 ở V1 (8.17) và V8 (6.27).
- Chỉ số mạng: cộng theo mọi đường tấn công đơn A → V8 (Algorithm 2: append theo từng đường).
"""
from __future__ import annotations

import copy
from dataclasses import dataclass, field

import networkx as nx
import numpy as np

# (CVE, loại, CVSS BS, Impact, Exploitability, Attack cost) – Bảng 1
OS_VULNS: dict[str, list[tuple]] = {
    "Windows 11": [("CVE-2021-38631", "RA", 2.1, 2.9, 0.39, 1.07), ("CVE-2023-40023", "RA", 7.5, 3.6, 0.39, 1.20),
                   ("CVE-2021-41338", "RA", 2.1, 3.9, 0.29, 0.27), ("CVE-2022-34709", "BP", 6.0, 5.2, 0.08, 1.47),
                   ("CVE-2022-29103", "BP", 4.6, 6.4, 0.39, 0.13), ("CVE-2022-21894", "BP", 4.9, 6.9, 0.39, 0.40)],
    "Linux": [("CVE-2023-25136", "RA", 6.5, 4.2, 0.22, 1.27), ("CVE-2022-2663", "BP", 5.3, 1.4, 0.39, 1.55),
              ("CVE-2023-38432", "RA", 9.1, 3.9, 0.52, 1.45), ("CVE-2021-4135", "BP", 5.5, 1.8, 0.36, 0.64),
              ("CVE-2022-2503", "BP", 6.9, 0.6, 0.58, 0.36), ("CVE-2021-32958", "RA", 2.1, 2.9, 0.39, 1.00)],
    "FreeBSD": [("CVE-2014-8612", "RA", 4.6, 2.9, 0.39, 1.17), ("CVE-2010-4755", "RA", 4.0, 1.4, 0.80, 0.93),
                ("CVE-2023-38432", "BP", 9.1, 3.9, 0.52, 0.99), ("CVE-2010-4754", "RA", 4.0, 2.9, 0.80, 1.25),
                ("CVE-2019-9499", "BP", 6.8, 6.4, 0.86, 0.81), ("CVE-2023-3326", "BP", 9.8, 5.9, 0.39, 0.99)],
}
# Bảng 2: s1 … s14
SERVICE_VULNS: list[tuple] = [
    ("CVE-2023-27389", "RA", 7.2, 5.9, 0.12, 1.0), ("CVE-2020-5536", "BP", 5.8, 6.4, 0.65, 0.9),
    ("CVE-2021-1540", "BP", 6.0, 6.4, 0.68, 0.2), ("CVE-2021-33215", "DT", 4.0, 2.9, 0.80, 0.1),
    ("CVE-2017-9382", "DT", 4.0, 2.9, 0.80, 0.8), ("CVE-2020-3624", "OV", 4.6, 6.4, 0.39, 0.3),
    ("CVE-2019-2341", "OV", 4.6, 6.4, 0.39, 1.1), ("CVE-2021-40831", "BP", 6.0, 6.4, 0.68, 1.2),
    ("CVE-2022-42055", "DT", 6.5, 3.6, 0.28, 1.5), ("CVE-2022-25686", "OV", 9.8, 5.9, 0.39, 1.4),
    ("CVE-2020-26079", "RA", 4.0, 2.9, 0.80, 0.5), ("CVE-2021-35097", "BP", 6.8, 5.9, 0.09, 0.2),
    ("CVE-2020-15858", "DT", 3.6, 4.9, 0.39, 0.9), ("CVE-2021-30331", "OV", 2.1, 2.9, 0.39, 1.2),
]
VM_OS = {"V1": "Linux", "V2": "Windows 11", "V3": "FreeBSD", "V4": "Linux",
         "V5": "Windows 11", "V6": "FreeBSD", "V7": "Linux", "V8": "Linux"}
VM_SERVICES = {"V1": [1, 2], "V2": [3, 4], "V3": [5, 6], "V4": [7, 8], "V5": [9, 10], "V6": [11, 12],
               "V7": [13, 14], "V8": []}
EDGES_DEF2 = [("A", "V1"), ("A", "V2"), ("V1", "V3"), ("V1", "V5"), ("V5", "V8"), ("V3", "V7"),
              ("V2", "V6"), ("V2", "V4"), ("V4", "V5"), ("V2", "V7"), ("V7", "V8")]
EDGE_FIG3 = ("V6", "V4")
BACKUP_OS = {"Windows 11": "Linux", "FreeBSD": "Windows 11", "Linux": "FreeBSD"}   # mục 4.3

# Số liệu paper dùng để đối chiếu
PAPER_TABLE4 = {"ASP": [0.975, 0.986, 0.99, 0.98, 0.9745, 0.99, 0.97, 0.95],
                "AC": [8.17, 6.54, 8.64, 9.97, 7.34, 8.84, 8.57, 6.27],
                "AR": [47.19, 36.68, 51.07, 47.64, 40.7, 52.12, 47.57, 33.73]}
PAPER_VM_RISK = {"V2": 16.28, "V4": 12.47, "V5": 12.58, "V7": 8.67, "V8": 5.62, "V5_linux": 8.9}
PAPER_PATHS = {"shuffle A-V2-V7-V5-V8": 43.15, "diversity A-V2-V4-V5(Linux)-V8": 43.31,
               "redundancy A-V2-V4-V5'-V8": 43.31}
PAPER_NETWORK = {"shuffle": {"R": 167.38, "AC": 666.2, "RoC": 1.01},
                 "diversity": {"R": 163.73, "AC": 624.73, "RoC": 1.04},
                 "redundancy": {"R": 260.84, "AC": 878.3, "RoC": 1.46}}


@dataclass
class Tharm:
    """Trạng thái mạng tại một thời điểm: lớp trên (đồ thị VM), lớp dưới (OS + dịch vụ của từng VM)."""
    graph: nx.DiGraph
    os: dict[str, str]
    services: dict[str, list[int]]
    entry: str = "A"
    target: str = "V8"
    log: list[str] = field(default_factory=list)

    def vulns(self, vm: str) -> list[tuple]:
        return OS_VULNS[self.os[vm]] + [SERVICE_VULNS[i - 1] for i in self.services.get(vm, [])]

    # ----------------------------------------------------------------- chỉ số mức VM (Algorithm 2)
    def asp(self, vm: str) -> float:
        return 1.0 - float(np.prod([1.0 - v[4] for v in self.vulns(vm)]))

    def risk(self, vm: str) -> float:
        return float(sum(v[4] * v[3] for v in self.vulns(vm)))

    def cost(self, vm: str) -> float:
        return float(sum(v[5] for v in self.vulns(vm)))

    def base_score(self, vm: str) -> float:
        return float(sum(v[2] for v in self.vulns(vm)))

    # ----------------------------------------------------------------- chỉ số mức mạng
    def paths(self) -> list[list[str]]:
        return sorted(nx.all_simple_paths(self.graph, self.entry, self.target), key=lambda p: (len(p), p))

    def path_metrics(self, path: list[str]) -> dict:
        vms = path[1:]
        r, c = sum(self.risk(v) for v in vms), sum(self.cost(v) for v in vms)
        return {"path": "-".join(path), "R": r, "AC": c, "RoC": r / c,
                "ASP": float(np.prod([self.asp(v) for v in vms]))}

    def network_metrics(self) -> dict:
        ps = [self.path_metrics(p) for p in self.paths()]
        return {"n_paths": len(ps), "R": sum(p["R"] for p in ps), "AC": sum(p["AC"] for p in ps),
                "RoC": sum(p["RoC"] for p in ps), "ASP_mean_path": float(np.mean([p["ASP"] for p in ps])),
                "ASP_max_path": max(p["ASP"] for p in ps), "AC_min_path": min(p["AC"] for p in ps)}

    def centrality(self) -> dict[str, dict]:
        """Closeness, degree, betweenness (Eq. 5–7) trên đồ thị VM; dùng để chọn V* (Eq. 8)."""
        g = self.graph.to_undirected()
        cl, dg, bt = nx.closeness_centrality(g), nx.degree_centrality(g), nx.betweenness_centrality(g)
        return {v: {"closeness": cl[v], "degree": dg[v], "betweenness": bt[v]}
                for v in self.graph.nodes if v not in (self.entry, self.target)}

    def select_vm(self) -> str:
        """Eq. 8: V* = rank(argmax(C, D, B)) – xếp hạng theo tổng ba độ đo trung tâm."""
        c = self.centrality()
        return max(c, key=lambda v: (c[v]["closeness"] + c[v]["degree"] + c[v]["betweenness"], v))


def build(with_fig3_edge: bool = False) -> Tharm:
    g = nx.DiGraph(EDGES_DEF2 + ([EDGE_FIG3] if with_fig3_edge else []))
    return Tharm(g, dict(VM_OS), {k: list(v) for k, v in VM_SERVICES.items()})


# --------------------------------------------------------------------- các phép MTD (Algorithm 3)
def shuffle_v5_host2_to_host4(h: Tharm) -> Tharm:
    """Ví dụ mục 4.2: V5 rời host 2 (mất các cạnh từ V1, V4), sang host 4 cạnh V8 và được V7 (host 3) tới được."""
    n = copy.deepcopy(h)
    for u in [u for u, _ in n.graph.in_edges("V5")]:
        n.graph.remove_edge(u, "V5")
    n.graph.add_edge("V7", "V5")
    n.log.append("shuffle V5: host2 → host4")
    return n


def diversity(h: Tharm, vm: str) -> Tharm:
    n = copy.deepcopy(h)
    old = n.os[vm]
    n.os[vm] = BACKUP_OS[old]
    n.log.append(f"diversity {vm}: {old} → {n.os[vm]}")
    return n


def redundancy(h: Tharm, vm: str, replicas: int = 1, replica_os: str = "backup") -> Tharm:
    """replica_os = "backup" (mặc định, khớp số của paper) hoặc "same" (bản sao y hệt VM gốc)."""
    n = copy.deepcopy(h)
    for r in range(1, replicas + 1):
        new = vm + "'" * r
        n.os[new] = BACKUP_OS[n.os[vm]] if replica_os == "backup" else n.os[vm]
        n.services[new] = list(n.services[vm])
        for u, _ in list(h.graph.in_edges(vm)):
            n.graph.add_edge(u, new)
        for _, w in list(h.graph.out_edges(vm)):
            n.graph.add_edge(new, w)
        n.log.append(f"redundancy {vm} → {new}")
    return n


def scenarios(with_fig3_edge: bool = False) -> dict[str, Tharm]:
    """Không MTD, S, D, R và các tổ hợp S+D, S+D+R – đều áp lên V5 như ví dụ của paper."""
    b = build(with_fig3_edge)
    s = shuffle_v5_host2_to_host4(b)
    d = diversity(b, "V5")
    r = redundancy(b, "V5")
    sd = diversity(s, "V5")
    sdr = redundancy(sd, "V5")
    return {"none": b, "S": s, "D": d, "R": r, "S+D": sd, "S+D+R": sdr}


def path_shuffle_variation(states: list[Tharm]) -> float:
    """PSV (mục 3.6.3): trung bình |AP_t − AP_{t−1}| / |AP_t| qua các trạng thái liên tiếp."""
    aps = [{"-".join(p) for p in s.paths()} for s in states]
    vals = [len(aps[i] - aps[i - 1]) / len(aps[i]) for i in range(1, len(aps)) if aps[i]]
    return float(np.mean(vals)) if vals else 0.0
