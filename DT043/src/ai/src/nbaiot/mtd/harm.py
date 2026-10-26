"""Mô hình tấn công phân cấp có thời gian (rút gọn, lấy cảm hứng từ 3-layer THARM của Masud et al. 2025).

Lớp 1 (trên)  : đồ thị khả năng tiếp cận giữa các node (internet → gateway → thiết bị IoT → cloud).
Lớp 2 (dưới)  : mỗi node có tập lỗ hổng (OR) với xác suất khai thác p, chi phí c, tác động i.
Lớp 3 (thời gian): mạng thay đổi theo thời gian do MTD (shuffle: đổi địa chỉ → kẻ tấn công mất vị trí/thông tin
                 trinh sát; diversity: đổi biến thể firmware → exploit đã chuẩn bị kém hiệu quả).

Mọi tham số là GIẢ ĐỊNH MINH HỌA (không phải số liệu của paper), dùng để so sánh tương đối các chiến lược MTD.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import networkx as nx
import numpy as np


@dataclass
class Vuln:
    name: str
    p: float        # xác suất khai thác thành công mỗi lần thử
    cost: float     # công sức kẻ tấn công cho mỗi lần thử
    impact: float   # tác động khi node bị chiếm (0–10)


@dataclass
class Network:
    graph: nx.DiGraph
    vulns: dict[str, list[Vuln]]
    entry: str = "internet"
    targets: list[str] = field(default_factory=lambda: ["cloud"])


def iot_network(devices: list[str]) -> Network:
    """Mạng IoT minh họa: 9 thiết bị N-BaIoT sau 1 gateway; thiết bị tới được cloud server."""
    g = nx.DiGraph()
    g.add_edge("internet", "gateway")
    vulns = {"gateway": [Vuln("dịch vụ quản trị lộ ra WAN", 0.35, 3.0, 8.0)],
             "cloud": [Vuln("API dùng chung khóa thiết bị", 0.30, 4.0, 10.0)]}
    for d in devices:
        g.add_edge("gateway", d)
        g.add_edge(d, "cloud")
        vulns[d] = [Vuln("Telnet mật khẩu mặc định (kiểu Mirai)", 0.60, 1.0, 6.0),
                    Vuln("lỗi firmware chưa vá", 0.25, 2.5, 7.0)]
        if "Camera" in d or "Webcam" in d or "Monitor" in d:
            vulns[d].append(Vuln("lộ thông tin xác thực qua web UI camera", 0.40, 1.5, 7.0))
    return Network(g, vulns)


def node_p(vs: list[Vuln], factor: float = 1.0) -> float:
    """OR các lỗ hổng: 1 − Π(1 − p_i·factor)."""
    return 1.0 - float(np.prod([1.0 - v.p * factor for v in vs]))


def static_metrics(net: Network) -> dict:
    """Metric tĩnh của HARM: số đường tấn công, ASP (đường tốt nhất), chi phí nhỏ nhất, rủi ro."""
    paths = [p for t in net.targets for p in nx.all_simple_paths(net.graph, net.entry, t)]
    best_asp, min_cost = 0.0, np.inf
    for path in paths:
        nodes = path[1:]
        asp = float(np.prod([node_p(net.vulns[n]) for n in nodes]))
        cost = float(sum(min(v.cost for v in net.vulns[n]) for n in nodes))
        best_asp, min_cost = max(best_asp, asp), min(min_cost, cost)
    risk = sum(node_p(vs) * max(v.impact for v in vs) for n, vs in net.vulns.items())
    return {"n_paths": len(paths), "asp_best_path": best_asp, "min_attack_cost": min_cost, "risk_sum": risk}


def simulate(net: Network, policy: str, horizon: int = 20, period: int = 10, runs: int = 2000,
             diversity_factor: float = 0.3, seed: int = 0) -> dict:
    """Mô phỏng Monte Carlo theo thời gian.

    Mỗi bước kẻ tấn công thử khai thác 1 node kế tiếp (chọn node dễ nhất trong các node tiếp cận được).
    - shuffle  : mỗi `period` bước, các node IoT/gateway đổi địa chỉ → kẻ tấn công mất các vị trí đã chiếm
                 (trừ điểm vào) và phải trinh sát lại 1 bước.
    - diversity: mỗi `period` bước đổi biến thể firmware → exploit đã chuẩn bị cho biến thể cũ chỉ còn
                 hiệu quả `diversity_factor` cho đến khi kẻ tấn công thích nghi (1 lần thử thất bại).
    - combined : cả hai, lệch pha nửa chu kỳ.
    `horizon` = ngân sách thời gian của một đợt tấn công. Trả về: ASP trong `horizon`, chi phí kỳ vọng (tổng cost các lần thử), thời gian đến khi thành công, số lần MTD.
    """
    rng = np.random.default_rng(seed)
    succ, costs, ttc = 0, [], []
    moves = 0
    for _ in range(runs):
        owned = {net.entry}
        adapted = True
        recon_wait = 0
        spent = 0.0
        done_at = None
        for t in range(1, horizon + 1):
            shuffle_now = policy in ("shuffle", "combined") and t % period == 0
            div_now = (policy == "diversity" and t % period == 0) or \
                      (policy == "combined" and (t + period // 2) % period == 0)
            if shuffle_now:
                owned = {net.entry}
                recon_wait = 1
                moves += 1
            if div_now:
                adapted = False
                moves += 1
            if recon_wait:
                recon_wait -= 1
                continue
            frontier = {v for u in owned for v in net.graph.successors(u)} - owned
            if not frontier:
                continue
            factor = 1.0 if adapted else diversity_factor
            node = max(frontier, key=lambda n: node_p(net.vulns[n], factor))
            v = max(net.vulns[node], key=lambda x: x.p)
            spent += v.cost
            if rng.random() < v.p * factor:
                owned.add(node)
                if node in net.targets:
                    done_at = t
                    break
            elif not adapted:
                adapted = True  # kẻ tấn công thích nghi với biến thể mới sau 1 lần thất bại
        succ += done_at is not None
        costs.append(spent)
        ttc.append(done_at if done_at is not None else np.nan)
    return {"policy": policy, "asp": succ / runs, "attack_cost_mean": float(np.mean(costs)),
            "time_to_compromise_mean": float(np.nanmean(ttc)) if succ else float("nan"),
            "mtd_moves_per_run": moves / runs, "risk": succ / runs * 10.0}
