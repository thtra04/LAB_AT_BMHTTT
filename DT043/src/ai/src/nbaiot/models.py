"""Kiến trúc autoencoder: B0 (Meidan 2018), V1 (nhẹ), V2 (siêu nhẹ, 23 đặc trưng)."""
from __future__ import annotations

import math


def encoder_sizes(input_dim: int, hidden) -> list[int]:
    """'meidan' → 75%, 50%, 33%, 25% của đầu vào (làm tròn .5 lên); hoặc danh sách cố định."""
    if hidden == "meidan":
        return [math.floor(input_dim * r + 0.5) for r in (0.75, 0.50, 0.33, 0.25)]
    sizes = [int(h) for h in hidden]
    if not sizes or any(h <= 0 for h in sizes):
        raise ValueError("hidden phải là 'meidan' hoặc danh sách số nguyên dương")
    return sizes


def layer_dims(input_dim: int, hidden) -> list[int]:
    """Kích thước toàn bộ các lớp: vào → encoder → decoder đối xứng → ra."""
    enc = encoder_sizes(input_dim, hidden)
    return [input_dim] + enc + enc[-2::-1] + [input_dim]


def count_params(dims: list[int]) -> int:
    return sum(a * b + b for a, b in zip(dims[:-1], dims[1:]))


def count_macs(dims: list[int]) -> int:
    """Số phép nhân-cộng cho 1 lần suy luận (proxy năng lượng độc lập phần cứng)."""
    return sum(a * b for a, b in zip(dims[:-1], dims[1:]))


def build_autoencoder(input_dim: int, hidden="meidan", activation: str = "relu"):
    import keras

    dims = layer_dims(input_dim, hidden)
    inp = keras.Input(shape=(input_dim,), name="x")
    h = inp
    for i, d in enumerate(dims[1:-1]):
        h = keras.layers.Dense(d, activation=activation, name=f"dense_{i}")(h)
    out = keras.layers.Dense(input_dim, activation=None, name="recon")(h)
    return keras.Model(inp, out, name="ae")
