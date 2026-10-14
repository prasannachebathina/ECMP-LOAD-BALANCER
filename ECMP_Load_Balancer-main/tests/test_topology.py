import pytest
from ecmp_phase2.topology import LeafSpineTopology


def test_topology_builds_expected_links():
    t = LeafSpineTopology(3, 2, 2, 1000)
    assert len(t.leaves) == 3
    assert len(t.spines) == 2
    assert len(t.all_hosts()) == 6
    assert "L1-S1" in t.links
    assert len(t.valid_paths("H1_1", "H2_1")) == 2


def test_same_leaf_has_no_interleaf_path():
    t = LeafSpineTopology(2, 2, 1)
    assert t.valid_paths("H1_1", "H1_2") == []


def test_invalid_topology_rejected():
    with pytest.raises(ValueError):
        LeafSpineTopology(num_leaves=1)
