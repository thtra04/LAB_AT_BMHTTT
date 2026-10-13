"""MTD lai (mô phỏng): event-based khi có cảnh báo AE + time-based theo chu kỳ.

Chỉ ghi nhận hành động vào DB (đổi địa chỉ IP ảo / đổi biến thể firmware ảo); KHÔNG tác động mạng thật.
"""
from __future__ import annotations

import random
import time

FIRMWARE_VARIANTS = ["fw-A", "fw-B", "fw-C"]


class HybridMTD:
    def __init__(self, repo, period_s: int = 60, seed: int = 0):
        self.repo = repo
        self.period_s = period_s
        self.rng = random.Random(seed)
        self.virtual_ip: dict[str, str] = {}
        self.firmware: dict[str, str] = {}
        self.last_move: dict[str, float] = {}

    def _new_ip(self, device: str) -> str:
        old = self.virtual_ip.get(device, f"10.0.0.{self.rng.randint(2, 254)}")
        new = old
        while new == old:
            new = f"10.0.0.{self.rng.randint(2, 254)}"
        self.virtual_ip[device] = new
        return f"IP {old} -> {new}"

    def _new_fw(self, device: str) -> str:
        old = self.firmware.get(device, FIRMWARE_VARIANTS[0])
        new = self.rng.choice([v for v in FIRMWARE_VARIANTS if v != old])
        self.firmware[device] = new
        return f"firmware {old} -> {new}"

    def on_alert(self, device: str, device_id: int, alert_id: int) -> list[int]:
        """Event-based: cảnh báo → shuffle + diversity (kết hợp 2 nhóm kỹ thuật như paper chính)."""
        ids = [self.repo.add_mtd_action(device_id, "shuffle", "event", self._new_ip(device), alert_id),
               self.repo.add_mtd_action(device_id, "diversity", "event", self._new_fw(device), alert_id)]
        self.last_move[device] = time.time()
        return ids

    def tick(self, devices: dict[str, int], now: float | None = None) -> list[int]:
        """Time-based: thiết bị nào chưa đổi trong `period_s` giây thì shuffle."""
        now = time.time() if now is None else now
        ids = []
        for name, dev_id in devices.items():
            if now - self.last_move.get(name, 0.0) >= self.period_s:
                ids.append(self.repo.add_mtd_action(dev_id, "shuffle", "time", self._new_ip(name)))
                self.last_move[name] = now
        return ids
