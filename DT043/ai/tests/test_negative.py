"""Negative test: dữ liệu hỏng/sai schema phải bị từ chối rõ ràng; manifest sai phải bị phát hiện."""
import hashlib
import importlib.util
from pathlib import Path

import numpy as np
import pytest
from conftest import ROOT, synthetic_frame

from nbaiot import data as D


def test_empty_frame_rejected():
    with pytest.raises(D.SchemaError):
        D.validate_frame(synthetic_frame(5).iloc[:0])


def test_missing_column_rejected():
    with pytest.raises(D.SchemaError):
        D.validate_frame(synthetic_frame(5).drop(columns=[D.COLUMNS[3]]))


def test_extra_column_rejected():
    df = synthetic_frame(5)
    df["label"] = 1.0
    with pytest.raises(D.SchemaError):
        D.validate_frame(df)


def test_wrong_column_order_rejected():
    df = synthetic_frame(5)
    with pytest.raises(D.SchemaError):
        D.validate_frame(df[list(reversed(D.COLUMNS))])


@pytest.mark.parametrize("bad", [np.nan, np.inf, -np.inf])
def test_nan_inf_rejected(bad):
    df = synthetic_frame(5)
    df.iloc[2, 7] = bad
    with pytest.raises(D.SchemaError):
        D.validate_frame(df)


def test_non_numeric_csv_rejected(tmp_path):
    p = tmp_path / "bad.csv"
    df = synthetic_frame(3).astype(object)
    df.iloc[1, 0] = "abc"
    df.to_csv(p, index=False)
    with pytest.raises(D.SchemaError):
        D.read_csv(p)


def test_truncated_csv_rejected(tmp_path):
    p = tmp_path / "trunc.csv"
    synthetic_frame(3).to_csv(p, index=False)
    text = p.read_text().splitlines()
    text[-1] = ",".join(text[-1].split(",")[:50])  # dòng cuối bị cắt
    p.write_text("\n".join(text))
    with pytest.raises(D.SchemaError):
        D.read_csv(p)


def test_invalid_window_rejected():
    with pytest.raises(ValueError):
        D.window_columns("L7")


def test_manifest_detects_tampering(tmp_path):
    spec = importlib.util.spec_from_file_location("vm", ROOT / "ai" / "scripts" / "02_verify_manifest.py")
    vm = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(vm)
    f = tmp_path / "raw" / "a.csv"
    f.parent.mkdir()
    f.write_text("x\n1\n")
    digest = hashlib.sha256(f.read_bytes()).hexdigest()
    (tmp_path / "MANIFEST.sha256").write_text(f"{digest}  raw/a.csv\n")
    assert vm.verify(tmp_path) == []
    f.write_text("x\n2\n")  # sửa nội dung
    assert vm.verify(tmp_path) == ["raw/a.csv"]
    f.unlink()
    assert vm.verify(tmp_path) == ["raw/a.csv"]


def test_tflite_rejects_wrong_input_dim():
    pytest.importorskip("tensorflow")
    from nbaiot.models import build_autoencoder
    from nbaiot.quantize import TFLiteRunner, to_tflite

    m = build_autoencoder(23, [8, 4])
    runner = TFLiteRunner(to_tflite(m, "fp32"), batch=16)
    with pytest.raises(ValueError):
        runner.predict(np.zeros((4, 115), np.float32))
    with pytest.raises(ValueError):
        to_tflite(m, "int8", rep_data=None)
