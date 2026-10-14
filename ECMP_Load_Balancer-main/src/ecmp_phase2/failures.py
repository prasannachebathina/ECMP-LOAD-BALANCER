import time
from .models import FailureEvent
from .ecmp import assign_all
from .metrics import collect_link_metrics, flow_rows


def run_failure_scenario(topology, flows, baseline_assignments, failure_type, target):
    """Inject one logical failure, reassign affected flows, and return measurements.

    recovery_time_ms is the measured Python wall-clock time spent recomputing
    assignments; it is not real network convergence time.
    """
    if failure_type not in {"link", "spine"}:
        raise ValueError("failure_type must be 'link' or 'spine'")
    failed_links, failed_spines = set(), set()
    if failure_type == "link":
        if target not in topology.links:
            raise ValueError(f"Unknown link: {target}")
        failed_links.add(target)
        description = f"Link {target} disabled"
    else:
        if target not in topology.spines:
            raise ValueError(f"Unknown spine: {target}")
        failed_spines.add(target)
        description = f"Spine {target} disabled"

    affected = []
    for assignment in baseline_assignments:
        if not assignment.path:
            continue
        if failure_type == "link" and target in topology.path_links(assignment.path):
            affected.append(assignment.flow.flow_id)
        elif failure_type == "spine" and target in assignment.path:
            affected.append(assignment.flow.flow_id)

    start = time.perf_counter()
    after = assign_all(flows, topology, failed_links, failed_spines)
    recovery_time_ms = (time.perf_counter() - start) * 1000.0
    rerouted = sum(a.flow.flow_id in set(affected) and a.status == "connected"
                   for a in after)
    disconnected_affected = sum(a.flow.flow_id in set(affected) and a.status == "disconnected"
                                for a in after)
    link_rows, summary = collect_link_metrics(topology, after)
    for row in link_rows:
        row["failed"] = row["link_id"] in failed_links
        if failure_type == "spine":
            row["failed"] = target in (row["node_a"], row["node_b"])
    summary.update({
        "scenario": f"{failure_type}_failure_{target}",
        "failure_type": failure_type,
        "failure_target": target,
        "affected_flows": len(affected),
        "rerouted_affected_flows": rerouted,
        "disconnected_affected_flows": disconnected_affected,
        "recovery_time_ms": round(recovery_time_ms, 6),
        "recovery_time_definition": "wall-clock time for simulator reassignment only",
    })
    event = FailureEvent(failure_type, target, description)
    return {
        "event": event, "assignments": after, "link_rows": link_rows,
        "flow_rows": flow_rows(after, topology), "summary": summary,
        "affected_flow_ids": affected,
    }
