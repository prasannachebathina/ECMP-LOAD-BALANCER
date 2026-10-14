import random
from .models import Flow


def generate_flows(topology, num_flows=100, seed=42,
                   min_demand_mbps=50.0, max_demand_mbps=1000.0):
    """Generate reproducible flows between hosts on different leaves."""
    if num_flows < 1:
        raise ValueError("num_flows must be at least 1")
    if min_demand_mbps <= 0 or max_demand_mbps < min_demand_mbps:
        raise ValueError("Invalid traffic demand range")
    hosts = topology.all_hosts()
    eligible = [(s, d) for s in hosts for d in hosts
                if topology.host_leaf(s) != topology.host_leaf(d)]
    if not eligible:
        raise ValueError("At least two leaves with hosts are required")
    rng = random.Random(seed)
    flows = []
    for i in range(1, num_flows + 1):
        src, dst = rng.choice(eligible)
        demand = rng.uniform(min_demand_mbps, max_demand_mbps)
        flows.append(Flow(f"F{i:04d}", src, dst, round(demand, 3), seed))
    return flows
