from ecmp_phase2.topology import LeafSpineTopology
from ecmp_phase2.traffic import generate_flows
from ecmp_phase2.ecmp import assign_all, stable_hash


def test_flow_generation_is_reproducible():
    t = LeafSpineTopology(3, 2, 2)
    assert generate_flows(t, 10, 9) == generate_flows(t, 10, 9)


def test_assignments_are_deterministic_and_valid():
    t = LeafSpineTopology(3, 3, 2)
    flows = generate_flows(t, 30, 10)
    first = assign_all(flows, t)
    second = assign_all(flows, t)
    assert [a.path for a in first] == [a.path for a in second]
    assert all(a.path is not None for a in first)
    assert all(len(a.path) == 5 for a in first)


def test_hash_is_stable_integer():
    t = LeafSpineTopology(2, 2, 1)
    flow = generate_flows(t, 1, 1)[0]
    assert stable_hash(flow) == stable_hash(flow)
