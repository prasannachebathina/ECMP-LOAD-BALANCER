import math
from collections import defaultdict


def collect_link_metrics(topology, assignments):
    traffic = defaultdict(float)
    flow_counts = defaultdict(int)
    for assignment in assignments:
        if assignment.path is None:
            continue
        for link_id in topology.path_links(assignment.path):
            traffic[link_id] += assignment.flow.demand_mbps
            flow_counts[link_id] += 1

    rows = []
    utilizations = []
    for link_id, link in topology.links.items():
        load = traffic[link_id]
        utilization = 100.0 * load / link.capacity_mbps
        utilizations.append(utilization)
        rows.append({
            "link_id": link_id, "node_a": link.a, "node_b": link.b,
            "capacity_mbps": link.capacity_mbps, "traffic_mbps": round(load, 6),
            "utilization_pct": round(utilization, 6),
            "assigned_flow_hops": flow_counts[link_id],
            "failed": False,
        })
    if utilizations:
        mean = sum(utilizations) / len(utilizations)
        variance = sum((x - mean) ** 2 for x in utilizations) / len(utilizations)
        stddev = math.sqrt(variance)
        maximum = max(utilizations)
        minimum = min(utilizations)
        imbalance = maximum / mean if mean > 0 else 0.0
    else:
        mean = stddev = maximum = minimum = imbalance = 0.0
    summary = {
        "mean_utilization_pct": round(mean, 6),
        "min_utilization_pct": round(minimum, 6),
        "max_utilization_pct": round(maximum, 6),
        "utilization_stddev_pct": round(stddev, 6),
        "load_imbalance_max_over_mean": round(imbalance, 6),
        "connected_flows": sum(a.status == "connected" for a in assignments),
        "disconnected_flows": sum(a.status == "disconnected" for a in assignments),
        "total_flows": len(assignments),
    }
    return rows, summary


def flow_rows(assignments, topology):
    rows = []
    for a in assignments:
        rows.append({
            "flow_id": a.flow.flow_id, "src_host": a.flow.src_host,
            "dst_host": a.flow.dst_host, "demand_mbps": a.flow.demand_mbps,
            "status": a.status, "path": " -> ".join(a.path) if a.path else "",
            "path_links": ";".join(topology.path_links(a.path)) if a.path else "",
            "reason": a.reason,
        })
    return rows
