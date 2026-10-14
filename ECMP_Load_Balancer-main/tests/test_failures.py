from ecmp_phase2.topology import LeafSpineTopology
from ecmp_phase2.traffic import generate_flows
from ecmp_phase2.ecmp import assign_all
from ecmp_phase2.failures import run_failure_scenario


def setup_case():
    topology = LeafSpineTopology(4, 3, 2, 10000)
    flows = generate_flows(topology, 60, 22)
    baseline = assign_all(flows, topology)
    return topology, flows, baseline


def test_link_failure_reroutes_affected_flows():
    topology, flows, baseline = setup_case()
    result = run_failure_scenario(topology, flows, baseline, "link", "L1-S1")
    assert result["summary"]["affected_flows"] >= 0
    assert result["summary"]["rerouted_affected_flows"] <= result["summary"]["affected_flows"]
    assert result["summary"]["disconnected_flows"] == 0


def test_spine_failure_reroutes_affected_flows():
    topology, flows, baseline = setup_case()
    result = run_failure_scenario(topology, flows, baseline, "spine", "S2")
    assert result["summary"]["rerouted_affected_flows"] <= result["summary"]["affected_flows"]
    assert result["summary"]["disconnected_flows"] == 0


def test_invalid_failure_rejected():
    topology, flows, baseline = setup_case()
    import pytest
    with pytest.raises(ValueError):
        run_failure_scenario(topology, flows, baseline, "spine", "S99")
