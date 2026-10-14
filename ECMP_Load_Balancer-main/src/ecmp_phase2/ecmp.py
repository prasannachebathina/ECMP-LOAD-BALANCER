import hashlib
from .models import FlowAssignment


def stable_hash(flow, salt="ecmp-phase2-v1"):
    """Stable SHA-256-based hash; unlike Python hash(), stable across runs."""
    payload = f"{salt}|{flow.flow_id}|{flow.src_host}|{flow.dst_host}|{flow.seed}"
    return int(hashlib.sha256(payload.encode("utf-8")).hexdigest(), 16)


def assign_flow(flow, topology, failed_links=None, failed_spines=None):
    paths = topology.valid_paths(flow.src_host, flow.dst_host,
                                 failed_links, failed_spines)
    if not paths:
        return FlowAssignment(flow, None, "disconnected", "no surviving equal-cost path")
    # Path order is topology.spines order; deterministic hash selects an index.
    path = paths[stable_hash(flow) % len(paths)]
    return FlowAssignment(flow, tuple(path), "connected")


def assign_all(flows, topology, failed_links=None, failed_spines=None):
    return [assign_flow(flow, topology, failed_links, failed_spines) for flow in flows]
