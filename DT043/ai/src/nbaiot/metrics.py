"""Tính metric ở mức mẫu và mức cửa sổ (sau majority vote) trên các segment test."""
from __future__ import annotations

import math

import numpy as np
from sklearn.metrics import average_precision_score, roc_auc_score

from .threshold import first_detection, window_votes


def _safe_div(a: float, b: float) -> float:
    return float(a / b) if b else 0.0


def confusion_metrics(tp: int, fp: int, tn: int, fn: int) -> dict:
    tpr = _safe_div(tp, tp + fn)
    fpr = _safe_div(fp, fp + tn)
    tnr = 1.0 - fpr if (fp + tn) else 0.0
    prec = _safe_div(tp, tp + fp)
    f1_att = _safe_div(2 * tp, 2 * tp + fp + fn)
    f1_ben = _safe_div(2 * tn, 2 * tn + fn + fp)
    denom = math.sqrt(float(tp + fp) * (tp + fn) * (tn + fp) * (tn + fn))
    mcc = _safe_div(tp * tn - fp * fn, denom)
    # F1 khi giả định test cân bằng (số benign = số attack): precision = TPR / (TPR + FPR)
    p_bal = _safe_div(tpr, tpr + fpr)
    f1_bal = _safe_div(2 * p_bal * tpr, p_bal + tpr)
    return {"tp": int(tp), "fp": int(fp), "tn": int(tn), "fn": int(fn),
            "tpr": tpr, "fpr": fpr, "precision": prec, "f1_attack": f1_att, "f1_benign": f1_ben,
            "macro_f1": (f1_att + f1_ben) / 2, "balanced_acc": (tpr + tnr) / 2, "mcc": mcc,
            "f1_balanced": f1_bal, "accuracy": _safe_div(tp + tn, tp + fp + tn + fn)}


def evaluate_segments(seg_scores: dict[str, np.ndarray], thr: float, ws: int,
                      per_attack: bool = True) -> dict:
    """seg_scores: {'benign': điểm benign test, 'mirai/ack': ..., ...}. Vote KHÔNG vượt ranh giới segment."""
    tp = fp = tn = fn = 0
    per_seg, delays = {}, []
    for seg, s in seg_scores.items():
        votes = window_votes(np.asarray(s) > thr, ws)
        pos = int(votes.sum())
        if seg == "benign":
            fp += pos
            tn += votes.size - pos
        else:
            tp += pos
            fn += votes.size - pos
            if per_attack:
                per_seg[seg] = _safe_div(pos, votes.size)
                d = first_detection(np.asarray(s) > thr, ws)
                delays.append(d if d is not None else np.nan)
    out = confusion_metrics(tp, fp, tn, fn)
    if per_attack:
        out["recall_per_attack"] = per_seg
        out["detect_delay_samples_mean"] = float(np.nanmean(delays)) if delays else float("nan")
        out["undetected_attacks"] = int(np.isnan(delays).sum()) if delays else 0
    return out


def ranking_metrics(seg_scores: dict[str, np.ndarray]) -> dict:
    """ROC-AUC và PR-AUC (attack là lớp dương) trên điểm mức mẫu."""
    s = np.concatenate([np.asarray(v, dtype=np.float64) for v in seg_scores.values()])
    y = np.concatenate([np.full(len(v), seg != "benign", dtype=bool) for seg, v in seg_scores.items()])
    if y.all() or not y.any():
        return {"roc_auc": float("nan"), "pr_auc": float("nan")}
    return {"roc_auc": float(roc_auc_score(y, s)), "pr_auc": float(average_precision_score(y, s))}
