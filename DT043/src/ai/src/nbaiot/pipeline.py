"""Một lần chạy thí nghiệm: nạp → chia → chuẩn hóa → huấn luyện → ngưỡng → đánh giá → lượng tử hóa → lưu."""
from __future__ import annotations

import json
import platform
import subprocess
import time
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

from . import data as D
from .config import ROOT
from .metrics import evaluate_segments, ranking_metrics
from .models import count_macs, count_params, layer_dims
from .scaling import ZScaler
from .split import chronological_split, drop_overlap, random_split
from .threshold import RULES, find_ws, threshold


# ----------------------------------------------------------------------------- dữ liệu
@dataclass
class DeviceData:
    device: str
    train: np.ndarray            # đã chuẩn hóa
    opt: np.ndarray
    test: dict[str, np.ndarray]  # {'benign': ..., 'mirai/ack': ...}
    info: dict = field(default_factory=dict)
    scaler: ZScaler | None = None
    raw_train: np.ndarray | None = None  # chưa chuẩn hóa (cho global scaler)


def load_split(cfg: dict, device: str, seed: int, scaler: ZScaler | None = None) -> DeviceData:
    proc = ROOT / cfg["paths"]["processed"]
    segs = D.load_device(proc, device)
    benign = segs.pop("benign")
    sp = cfg["split"]
    if sp["method"] == "chronological":
        idx = chronological_split(len(benign), sp["fractions"], sp["purge_gap"])
    elif sp["method"] == "random":
        idx = random_split(len(benign), sp["fractions"], seed)
    else:
        raise ValueError(sp["method"])
    b_tr = benign.iloc[idx.train].reset_index(drop=True)
    b_op = benign.iloc[idx.opt].reset_index(drop=True)
    b_te = benign.iloc[idx.test].reset_index(drop=True)
    info = {"n_benign": len(benign), "n_train": len(b_tr), "n_opt": len(b_op), "n_test_benign_before": len(b_te)}

    test = {"benign": b_te, **segs}
    if sp.get("drop_overlap", True):
        ref = np.concatenate([D.row_hashes(b_tr), D.row_hashes(b_op)])
        removed = {}
        for k in list(test):
            test[k], removed[k] = drop_overlap(test[k], ref)
        info["overlap_removed"] = removed
    # đầu độc dữ liệu train (E9) – lấy mẫu tấn công từ đầu mỗi segment rồi bỏ khỏi test
    rate = float(cfg.get("poison_rate", 0) or 0)
    if rate > 0:
        att_keys = [k for k in test if k != "benign"]
        k_each = max(1, int(round(rate * len(b_tr) / len(att_keys))))
        poison = [test[k].iloc[:k_each] for k in att_keys]
        for k in att_keys:
            test[k] = test[k].iloc[k_each:].reset_index(drop=True)
        b_tr = pd.concat([b_tr] + poison, ignore_index=True).sample(frac=1.0, random_state=seed)
        info["poison_rows"] = int(sum(len(p) for p in poison))

    cols = D.window_columns(cfg["features"]["window"])
    raw_tr = b_tr[cols].to_numpy(np.float64)
    if scaler is None and cfg["normalization"] == "per_device":
        fit_on = raw_tr if sp.get("scaler_fit_on", "train") == "train" else benign[cols].to_numpy(np.float64)
        scaler = ZScaler().fit(fit_on, device=device)
    tf_dev = device if scaler is not None and scaler.device == device else None

    def tr(df):
        return scaler.transform(df[cols].to_numpy(np.float64), device=tf_dev) if scaler is not None else None

    info["n_test"] = {k: len(v) for k, v in test.items()}
    return DeviceData(device, tr(b_tr), tr(b_op), {k: tr(v) for k, v in test.items()}, info, scaler, raw_tr)


# ----------------------------------------------------------------------------- model
def make_and_train(cfg: dict, x_train: np.ndarray, x_opt: np.ndarray, seed: int):
    """Trả về (scorer: X -> điểm bất thường, model, info)."""
    m = cfg["model"]
    t0 = time.perf_counter()
    if m["kind"] == "iforest":
        from sklearn.ensemble import IsolationForest

        clf = IsolationForest(n_estimators=100, max_samples=256, random_state=seed,
                              n_jobs=cfg.get("threads", 1)).fit(x_train)
        return (lambda x: -clf.score_samples(x)), clf, {"train_time_s": time.perf_counter() - t0}

    import keras

    from .models import build_autoencoder

    model = build_autoencoder(x_train.shape[1], m["hidden"], m.get("activation", "relu"))
    t = cfg["train"]
    model.compile(optimizer=keras.optimizers.Adam(t["lr"]), loss="mse")
    es = keras.callbacks.EarlyStopping(monitor="val_loss", patience=t["patience"], restore_best_weights=True)
    hist = model.fit(x_train, x_train, validation_data=(x_opt, x_opt), epochs=t["max_epochs"],
                     batch_size=t["batch_size"], shuffle=True, callbacks=[es], verbose=0)
    info = {"train_time_s": time.perf_counter() - t0, "epochs_run": len(hist.history["loss"]),
            "best_epoch": int(np.argmin(hist.history["val_loss"])) + 1,
            "history": {k: [float(v) for v in vs] for k, vs in hist.history.items()}}

    def scorer(x):
        rec = model.predict(x, batch_size=8192, verbose=0)
        return np.mean((rec.astype(np.float64) - x) ** 2, axis=1)  # float64: tránh tràn số

    return scorer, model, info


# ----------------------------------------------------------------------------- đánh giá
def decide(cfg: dict, opt_scores) -> tuple[float, int, float]:
    rule = cfg["threshold"]["rule"]
    opt_list = opt_scores if isinstance(opt_scores, list) else [opt_scores]
    thr = threshold(np.concatenate(opt_list), rule)
    ws, opt_fpr = find_ws([s > thr for s in opt_list], cfg["threshold"]["max_ws"])
    return thr, ws, opt_fpr


def full_eval(cfg: dict, opt_scores, test_scores: dict, thr: float, ws: int) -> dict:
    res = {"thr": thr, "ws": ws,
           "window": evaluate_segments(test_scores, thr, ws),
           "instance": evaluate_segments(test_scores, thr, 1, per_attack=False),
           **ranking_metrics(test_scores)}
    if cfg.get("ablation_grid"):
        grid = []
        opt_list = opt_scores if isinstance(opt_scores, list) else [opt_scores]
        for rule in RULES:
            t = threshold(np.concatenate(opt_list), rule)
            w, _ = find_ws([s > t for s in opt_list], cfg["threshold"]["max_ws"])
            for label, wv in (("1", 1), ("ws*", w), ("2ws*", 2 * w)):
                r = evaluate_segments(test_scores, t, wv, per_attack=False)
                grid.append({"rule": rule, "ws_kind": label, "ws": wv, "thr": t,
                             **{k: r[k] for k in ("tpr", "fpr", "macro_f1", "f1_attack", "f1_balanced", "mcc")}})
        res["ablation_grid"] = grid
    return res


def robustness(cfg: dict, dd: DeviceData, scorer, thr: float, ws: int) -> dict:
    rb = cfg.get("robustness") or {}
    out = {}
    if rb.get("evasion_alphas"):
        mu = dd.train.mean(axis=0)
        ev = []
        for a in rb["evasion_alphas"]:
            # từng segment một để giới hạn RAM (không giữ bản sao toàn bộ dữ liệu tấn công)
            sc = {k: scorer(((1 - a) * v + a * mu).astype(np.float32))
                  for k, v in dd.test.items() if k != "benign" and len(v)}
            r = evaluate_segments({"benign": np.zeros(0), **sc}, thr, ws, per_attack=False)
            ev.append({"alpha": a, "tpr": r["tpr"]})
        out["evasion"] = ev
    if rb.get("noise_sigmas"):
        rng = np.random.default_rng(0)
        nz = []
        for s in rb["noise_sigmas"]:
            xb = dd.test["benign"] + rng.normal(0, s, dd.test["benign"].shape).astype(np.float32)
            r = evaluate_segments({"benign": scorer(xb)}, thr, ws, per_attack=False)
            nz.append({"sigma": s, "fpr": r["fpr"]})
        out["noise"] = nz
    return out


def quantized_eval(cfg: dict, model, dd: DeviceData, base_thr: float, base_ws: int, seed: int,
                   save_dir: Path | None) -> dict:
    from .quantize import TFLiteRunner, to_tflite

    out = {}
    for mode in cfg.get("quantize") or []:
        t0 = time.perf_counter()
        blob = to_tflite(model, mode, rep_data=dd.train, seed=seed)
        conv_s = time.perf_counter() - t0
        runner = TFLiteRunner(blob, num_threads=cfg.get("threads", 1))
        opt_s = runner.mse(dd.opt)
        test_s = {k: runner.mse(v) for k, v in dd.test.items()}
        keep = evaluate_segments(test_s, base_thr, base_ws)
        thr, ws, _ = decide(cfg, opt_s)
        recal = evaluate_segments(test_s, thr, ws)
        out[mode] = {"size_bytes": len(blob), "convert_time_s": conv_s,
                     "keep": {"thr": base_thr, "ws": base_ws, **keep},
                     "recal": {"thr": thr, "ws": ws, **recal}, **ranking_metrics(test_s)}
        if save_dir is not None:
            save_dir.mkdir(parents=True, exist_ok=True)
            (save_dir / f"{mode}.tflite").write_bytes(blob)
    return out


# ----------------------------------------------------------------------------- lưu
def git_commit() -> str:
    try:
        return subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, capture_output=True,
                              text=True, timeout=10).stdout.strip()
    except Exception:  # noqa: BLE001
        return "unknown"


def save_run(out_dir: Path, cfg: dict, payload: dict) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "config.yaml").write_text(yaml.safe_dump(cfg, allow_unicode=True, sort_keys=False), encoding="utf-8")
    hist = payload.get("train", {}).pop("history", None)
    if hist:
        pd.DataFrame(hist).to_csv(out_dir / "train_log.csv", index_label="epoch")
    (out_dir / "metrics.json").write_text(json.dumps(payload, indent=1, ensure_ascii=False, default=float),
                                          encoding="utf-8")


def model_meta(cfg: dict, input_dim: int) -> dict:
    if cfg["model"]["kind"] != "ae":
        return {"kind": cfg["model"]["kind"]}
    dims = layer_dims(input_dim, cfg["model"]["hidden"])
    return {"kind": "ae", "dims": dims, "params": count_params(dims), "macs": count_macs(dims)}


# ----------------------------------------------------------------------------- chạy
def run_one(cfg: dict, exp: str, device: str, seed: int) -> dict:
    from .seed import set_seed

    set_seed(seed, cfg.get("threads"))
    t_start = time.time()
    dd = load_split(cfg, device, seed)
    scorer, model, tinfo = make_and_train(cfg, dd.train, dd.opt, seed)
    t0 = time.perf_counter()
    opt_s = scorer(dd.opt)
    test_s = {k: scorer(v) for k, v in dd.test.items()}
    score_time = time.perf_counter() - t0
    thr, ws, opt_fpr = decide(cfg, opt_s)
    res = full_eval(cfg, opt_s, test_s, thr, ws)
    res["opt_fpr_at_ws"] = opt_fpr

    save_models = seed == cfg.get("save_scores_seed")
    mdir = ROOT / cfg["paths"]["models"] / exp / device
    if cfg["model"]["kind"] == "ae" and (cfg.get("quantize") or save_models):
        if save_models:
            mdir.mkdir(parents=True, exist_ok=True)
            model.save(mdir / "model.keras")
            if dd.scaler is not None:
                dd.scaler.save(mdir / "scaler.json")
            (mdir / "threshold.json").write_text(json.dumps({"thr": thr, "ws": ws}), encoding="utf-8")
        if cfg.get("quantize"):
            res["quantized"] = quantized_eval(cfg, model, dd, thr, ws, seed, mdir if save_models else None)
    if cfg.get("robustness"):
        res["robustness"] = robustness(cfg, dd, scorer, thr, ws)
    if save_models:
        sdir = ROOT / cfg["paths"]["scores"] / exp / device
        sdir.mkdir(parents=True, exist_ok=True)
        np.savez_compressed(sdir / f"seed{seed}.npz", opt=opt_s.astype(np.float32),
                            **{k.replace("/", "__"): v.astype(np.float32) for k, v in test_s.items()})

    payload = {"exp": exp, "device": device, "seed": seed, "git": git_commit(),
               "python": platform.python_version(), "started": t_start, "wall_s": time.time() - t_start,
               "score_time_s": score_time, "data": dd.info, "model": model_meta(cfg, dd.train.shape[1]),
               "train": tinfo, "result": res}
    save_run(ROOT / cfg["paths"]["results"] / exp / device / f"seed={seed}", cfg, payload)
    return payload


def run_shared(cfg: dict, exp: str, seed: int) -> list[dict]:
    """Một model dùng chung cho 9 thiết bị (baseline B1). normalization: global | per_device."""
    from .seed import set_seed

    set_seed(seed, cfg.get("threads"))
    t_start = time.time()
    devs = cfg["devices"]
    glob = cfg["normalization"] == "global"

    def light(dd: DeviceData) -> DeviceData:  # chỉ giữ train/opt trong RAM, test nạp lại khi đánh giá
        dd.test, dd.raw_train = {}, (dd.raw_train if glob else None)
        return dd

    datas = {d: light(load_split({**cfg, "normalization": "none" if glob else "per_device"}, d, seed))
             for d in devs}
    if glob:  # scaler chung fit trên DStrn của mọi thiết bị
        gscaler = ZScaler().fit(np.vstack([datas[d].raw_train for d in devs]))
        datas = {d: light(load_split(cfg, d, seed, scaler=gscaler)) for d in devs}
    x_tr = np.vstack([datas[d].train for d in devs])
    x_op = np.vstack([datas[d].opt for d in devs])
    rng = np.random.default_rng(seed)
    x_tr = x_tr[rng.permutation(len(x_tr))]
    scorer, model, tinfo = make_and_train(cfg, x_tr, x_op, seed)
    opt_s = {d: scorer(datas[d].opt) for d in devs}
    shared_thr = cfg.get("shared_threshold", glob)
    if shared_thr:
        thr, ws, opt_fpr = decide(cfg, [opt_s[d] for d in devs])
    out = []
    for d in devs:
        full = load_split(cfg, d, seed, scaler=datas[d].scaler)
        test_s = {k: scorer(v) for k, v in full.test.items()}
        del full
        if not shared_thr:
            thr, ws, opt_fpr = decide(cfg, opt_s[d])
        res = full_eval(cfg, opt_s[d], test_s, thr, ws)
        res["opt_fpr_at_ws"] = opt_fpr
        payload = {"exp": exp, "device": d, "seed": seed, "git": git_commit(),
                   "python": platform.python_version(), "started": t_start, "wall_s": time.time() - t_start,
                   "data": datas[d].info, "model": model_meta(cfg, x_tr.shape[1]),
                   "train": dict(tinfo), "result": res}
        save_run(ROOT / cfg["paths"]["results"] / exp / d / f"seed={seed}", cfg, payload)
        out.append(payload)
    return out
