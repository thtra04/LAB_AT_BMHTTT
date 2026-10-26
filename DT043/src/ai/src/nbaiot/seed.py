"""Cố định seed và tính tất định cho numpy / random / TensorFlow."""
from __future__ import annotations

import os
import random

import numpy as np


def set_seed(seed: int, threads: int | None = None) -> None:
    os.environ["PYTHONHASHSEED"] = str(seed)
    os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "2")
    random.seed(seed)
    np.random.seed(seed)
    import tensorflow as tf

    if threads:
        try:
            tf.config.threading.set_intra_op_parallelism_threads(threads)
            tf.config.threading.set_inter_op_parallelism_threads(1)
        except RuntimeError:
            pass  # đã khởi tạo runtime trong process này
    tf.keras.utils.set_random_seed(seed)
    tf.config.experimental.enable_op_determinism()
