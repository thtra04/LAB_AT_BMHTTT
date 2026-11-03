"""Kiểm tra mô hình 3-layer THARM tái lập đúng các con số paper Masud et al. (2025) công bố."""
import pytest

from nbaiot.mtd import tharm as T


@pytest.fixture
def base():
    return T.build()


@pytest.mark.parametrize("vm,paper", [("V4", 12.47), ("V5", 12.58), ("V7", 8.67), ("V8", 5.62)])
def test_vm_risk_matches_paper(base, vm, paper):
    assert base.risk(vm) == pytest.approx(paper, abs=0.01)


def test_diversity_v5_to_linux_matches_paper(base):
    d = T.diversity(base, "V5")
    assert d.os["V5"] == "Linux"
    assert d.risk("V5") == pytest.approx(8.9, abs=0.05)


@pytest.mark.parametrize("vm,paper", [("V1", 8.17), ("V8", 6.27)])
def test_attack_cost_matches_table4(base, vm, paper):
    assert base.cost(vm) == pytest.approx(paper, abs=0.005)


def test_paper_example_paths_within_1_percent():
    sc = T.scenarios()
    r_s = sc["S"].path_metrics(["A", "V2", "V7", "V5", "V8"])["R"]
    r_d = sc["D"].path_metrics(["A", "V2", "V4", "V5", "V8"])["R"]
    r_r = sc["R"].path_metrics(["A", "V2", "V4", "V5'", "V8"])["R"]
    assert r_s == pytest.approx(43.15, rel=0.01)
    assert r_d == pytest.approx(43.31, rel=0.01)
    assert r_r == pytest.approx(43.31, rel=0.01)


def test_shuffle_creates_paper_path_and_keeps_vulns(base):
    s = T.shuffle_v5_host2_to_host4(base)
    assert ["A", "V2", "V7", "V5", "V8"] in s.paths()
    assert s.os == base.os and s.services == base.services   # shuffle chỉ đổi lớp trên


def test_redundancy_adds_vm_and_paths(base):
    r = T.redundancy(base, "V5")
    assert "V5'" in r.graph and len(r.paths()) > len(base.paths())


def test_fig3_topology_trend_shuffle_diversity_best():
    sc = T.scenarios(with_fig3_edge=True)
    risk = {k: v.network_metrics()["R"] for k, v in sc.items()}
    assert risk["S"] < risk["none"] and risk["D"] < risk["none"] < risk["R"]
    assert risk["S+D"] == min(risk.values())


def test_asp_is_probability(base):
    assert all(0.0 <= base.asp(v) <= 1.0 for v in T.VM_OS)


@pytest.mark.parametrize("fig3", [False, True])
def test_general_shuffle_reproduces_paper_v5_example(fig3):
    b = T.build(with_fig3_edge=fig3)
    assert set(T.shuffle(b, "V5", "H4").graph.edges) == set(T.shuffle_v5_host2_to_host4(b).graph.edges)


@pytest.mark.parametrize("fig3", [False, True])
def test_select_vm_is_v5_like_paper(fig3):
    """Eq. 8 trên đồ thị tấn công có hướng chọn V5 như mục 4.2 (cả Definition 2 và topology Hình 3)."""
    assert T.build(with_fig3_edge=fig3).select_vm() == "V5"
