"""Unit test: schema, chia dữ liệu chống rò rỉ, scaler, ngưỡng, majority vote, metric, model."""
import numpy as np
import pandas as pd
import pytest
from conftest import synthetic_frame

from nbaiot import data as D
from nbaiot.metrics import confusion_metrics, evaluate_segments
from nbaiot.models import count_params, layer_dims
from nbaiot.scaling import ZScaler
from nbaiot.split import chronological_split, drop_overlap, overlap_count
from nbaiot.threshold import find_ws, first_detection, threshold, window_votes


# ---------------------------------------------------------------- schema
def test_columns_115_and_window_subsets():
    assert len(D.COLUMNS) == 115
    for w in D.WINDOWS:
        cols = D.window_columns(w)
        assert len(cols) == 23
        assert all(f"_{w}_" in c for c in cols)
    # L1 không được lẫn với L0.1
    assert not any("_L0.1_" in c for c in D.window_columns("L1"))


def test_validate_frame_ok():
    D.validate_frame(synthetic_frame(10))


# ---------------------------------------------------------------- chia dữ liệu
def test_chronological_split_order_and_purge():
    s = chronological_split(3000, (1 / 3, 1 / 3, 1 / 3), purge_gap=50)
    assert s.train.max() < s.opt.min() < s.test.min()
    assert s.opt.min() - s.train.max() - 1 == 50
    assert s.test.min() - s.opt.max() - 1 == 50
    assert len(set(s.train) & set(s.opt)) == 0 and len(set(s.opt) & set(s.test)) == 0


def test_split_rejects_bad_fractions():
    with pytest.raises(ValueError):
        chronological_split(100, (0.5, 0.5, 0.5))
    with pytest.raises(ValueError):
        chronological_split(100, (1 / 3, 1 / 3, 1 / 3), purge_gap=100)


def test_drop_overlap_removes_exact_duplicates():
    a = synthetic_frame(100, seed=1)
    b = pd.concat([synthetic_frame(50, seed=2), a.iloc[:10]], ignore_index=True)
    assert overlap_count(b, a) == 10
    clean, removed = drop_overlap(b, D.row_hashes(a))
    assert removed == 10 and len(clean) == 50 and overlap_count(clean, a) == 0


# ---------------------------------------------------------------- scaler
def test_scaler_fit_only_on_train_stats():
    rng = np.random.default_rng(0)
    tr = rng.normal(5, 2, (1000, 4))
    te = rng.normal(50, 2, (100, 4))
    s = ZScaler().fit(tr, device="A")
    np.testing.assert_allclose(s.mean_, tr.mean(0))
    z = s.transform(te, device="A")
    assert z.mean() > 10  # test KHÔNG bị chuẩn hóa về 0 → scaler không nhìn thấy test


def test_scaler_constant_column_and_wrong_device():
    x = np.ones((10, 3))
    s = ZScaler().fit(x, device="A")
    assert np.isfinite(s.transform(x)).all()
    with pytest.raises(ValueError):
        s.transform(x, device="B")
    with pytest.raises(ValueError):
        s.transform(np.ones((2, 4)))


# ---------------------------------------------------------------- ngưỡng & vote
def test_threshold_mean_std():
    s = np.array([1.0, 2.0, 3.0])
    assert threshold(s, "mean_std") == pytest.approx(2.0 + 1.0)
    with pytest.raises(ValueError):
        threshold(s, "abc")


def test_window_votes_majority():
    f = np.array([1, 1, 0, 0, 0, 1, 1, 1])
    v = window_votes(f, 3)
    assert v.tolist() == [True, False, False, False, True, True]
    assert window_votes(np.array([1, 0]), 5).tolist() == [False]


def test_find_ws_zero_fpr():
    f = np.zeros(200, dtype=bool)
    f[::7] = True  # FP rải rác
    ws, fpr = find_ws(f, 50)
    assert fpr == 0.0 and ws == 2  # ws=1 có FP; ws=2 cần 2/2 → không còn FP


def test_first_detection_delay():
    f = np.array([0, 0, 0, 1, 1, 1, 1])
    assert first_detection(f, 3) == 5


def test_votes_do_not_cross_segments():
    # benign kết thúc bằng 1 cờ dương, attack bắt đầu bằng 1 dương: nếu nối lại sẽ có cửa sổ [0,1,1] dương sai
    res = evaluate_segments({"benign": np.array([0, 0, 0, 0, 1.0]), "mirai/ack": np.array([1, 0, 0, 0.0])},
                            thr=0.5, ws=3)
    assert res["fp"] == 0


# ---------------------------------------------------------------- metric
def test_confusion_metrics_known_values():
    m = confusion_metrics(tp=90, fp=10, tn=90, fn=10)
    assert m["tpr"] == pytest.approx(0.9) and m["fpr"] == pytest.approx(0.1)
    assert m["f1_attack"] == pytest.approx(0.9) and m["macro_f1"] == pytest.approx(0.9)
    assert m["mcc"] == pytest.approx(0.8)


# ---------------------------------------------------------------- model
def test_meidan_dims_and_params():
    dims = layer_dims(115, "meidan")
    assert dims == [115, 86, 58, 38, 29, 38, 58, 86, 115]
    assert count_params(dims) == 36876
    assert layer_dims(115, [32, 8]) == [115, 32, 8, 32, 115]
    assert count_params(layer_dims(115, [32, 8])) == 8059
