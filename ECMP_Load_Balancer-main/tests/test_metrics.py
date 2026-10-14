from ecmp_phase2.topology import LeafSpineTopology
from ecmp_phase2.traffic import generate_flows
from ecmp_phase2.ecmp import assign_all
from ecmp_phase2.metrics import collect_link_metrics


def test_metrics_have_expected_fields():
    t = LeafSpineTopology(2, 2, 1, 1000)
    flows = generate_flows(t, 10, 4, 10, 20)
    assignments = assign_all(flows, t)
    rows, summary = collect_link_metrics(t, assignments)
    assert len(rows) == len(t.links)
    assert 0 <= summary["min_utilization_pct"] <= summary["max_utilization_pct"]
    assert summary["connected_flows"] == 10
    assert summary["disconnected_flows"] == 0
