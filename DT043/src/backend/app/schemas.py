"""Kiểu dữ liệu vào/ra của API (Pydantic) – kiểm tra đầu vào ngay ở biên hệ thống."""
from __future__ import annotations

from pydantic import BaseModel, Field, field_validator

from .settings import MAX_SAMPLES_PER_REQUEST


class DetectRequest(BaseModel):
    device: str = Field(..., pattern=r"^[A-Za-z0-9_]+$", max_length=64)
    features: list[list[float]] = Field(..., min_length=1, max_length=MAX_SAMPLES_PER_REQUEST)

    @field_validator("features")
    @classmethod
    def same_length(cls, v):
        if len({len(r) for r in v}) != 1:
            raise ValueError("mọi dòng features phải có cùng số chiều")
        return v


class _Summary(BaseModel):
    device: str
    batch_id: int
    n_samples: int
    n_flagged: int
    n_windows: int
    n_alarm_windows: int
    threshold: float
    window_size: int
    infer_us_per_sample: float
    alert_id: int | None
    mtd_action_ids: list[int]


class DetectResponse(_Summary):
    mse: list[float]
    flags: list[bool]


class ReplayResponse(_Summary):
    segment: str
    offset: int
    step: int
    mse: list[float]
    alarms: list[int]
