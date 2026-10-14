import csv
import json
from pathlib import Path
from .topology import LeafSpineTopology
from .traffic import generate_flows
from .ecmp import assign_all
from .metrics import collect_link_metrics, flow_rows
from .failures import run_failure_scenario


def write_csv(path, rows):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def run_experiment(config_path="data/config.json", output_dir="results", graph_dir="graphs"):
    config_path = Path(config_path)
    config = json.loads(config_path.read_text(encoding="utf-8"))
    topology = LeafSpineTopology(
        num_leaves=config["num_leaves"],
        num_spines=config["num_spines"],
        hosts_per_leaf=config["hosts_per_leaf"],
        link_capacity_mbps=config["link_capacity_mbps"],
    )
    flows = generate_flows(
        topology, config["num_flows"], config["seed"],
        config["min_demand_mbps"], config["max_demand_mbps"],
    )
    baseline = assign_all(flows, topology)
    link_rows, baseline_summary = collect_link_metrics(topology, baseline)
    baseline_summary.update({"scenario": "baseline", "failure_type": "none",
                             "failure_target": "", "affected_flows": 0,
                             "rerouted_affected_flows": 0,
                             "disconnected_affected_flows": 0,
                             "recovery_time_ms": 0.0,
                             "recovery_time_definition": "not applicable"})
    out = Path(output_dir)
    graphs = Path(graph_dir)
    out.mkdir(parents=True, exist_ok=True)
    graphs.mkdir(parents=True, exist_ok=True)

    write_csv(out / "baseline_links.csv", link_rows)
    write_csv(out / "baseline_flows.csv", flow_rows(baseline, topology))
    summaries = [baseline_summary]
    scenarios = []
    for failure in config["failures"]:
        result = run_failure_scenario(topology, flows, baseline,
                                      failure["type"], failure["target"])
        name = result["summary"]["scenario"]
        write_csv(out / f"{name}_links.csv", result["link_rows"])
        write_csv(out / f"{name}_flows.csv", result["flow_rows"])
        summaries.append(result["summary"])
        scenarios.append({"name": name, "summary": result["summary"],
                          "affected_flow_ids": result["affected_flow_ids"]})

    write_csv(out / "scenario_summary.csv", summaries)
    (out / "experiment_metadata.json").write_text(json.dumps({
        "project": "ECMP Load Distribution and Failure Recovery in a Leaf-Spine Fabric",
        "simulation_only": True,
        "hash_method": "SHA-256 of salt, flow id, source, destination, and seed; modulo available paths",
        "traffic_seed": config["seed"],
        "topology": {k: config[k] for k in [
            "num_leaves", "num_spines", "hosts_per_leaf", "link_capacity_mbps"
        ]},
        "num_flows": len(flows),
        "demand_range_mbps": [config["min_demand_mbps"], config["max_demand_mbps"]],
        "recovery_metric": "wall-clock Python time to recompute all flow assignments; not real network convergence",
        "scenarios": [s["name"] for s in scenarios],
    }, indent=2), encoding="utf-8")
    make_graphs(link_rows, summaries, graphs)
    return {"topology": topology, "flows": flows, "baseline": baseline,
            "summaries": summaries, "scenarios": scenarios}


def make_graphs(baseline_link_rows, summaries, graph_dir):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib is not installed; CSV results were generated, graphs skipped.")
        return
    graph_dir = Path(graph_dir)
    # Baseline utilisation: top 25 links to keep the graph readable.
    ranked = sorted(baseline_link_rows, key=lambda r: r["utilization_pct"], reverse=True)[:25]
    plt.figure(figsize=(11, 5))
    plt.bar([r["link_id"] for r in ranked], [r["utilization_pct"] for r in ranked])
    plt.title("Baseline Link Utilisation (top 25 links)")
    plt.xlabel("Link")
    plt.ylabel("Utilisation (%)")
    plt.xticks(rotation=60, ha="right")
    plt.tight_layout()
    plt.savefig(graph_dir / "baseline_link_utilization.png", dpi=150)
    plt.close()

    labels = [s["scenario"] for s in summaries]
    max_util = [s["max_utilization_pct"] for s in summaries]
    plt.figure(figsize=(10, 5))
    plt.bar(labels, max_util)
    plt.title("Maximum Link Utilisation by Scenario")
    plt.xlabel("Scenario")
    plt.ylabel("Maximum utilisation (%)")
    plt.xticks(rotation=30, ha="right")
    plt.tight_layout()
    plt.savefig(graph_dir / "scenario_max_utilization.png", dpi=150)
    plt.close()

    affected = [s.get("affected_flows", 0) for s in summaries]
    rerouted = [s.get("rerouted_affected_flows", 0) for s in summaries]
    x = list(range(len(labels)))
    width = 0.38
    plt.figure(figsize=(10, 5))
    plt.bar([i - width / 2 for i in x], affected, width, label="Affected")
    plt.bar([i + width / 2 for i in x], rerouted, width, label="Rerouted")
    plt.title("Affected and Rerouted Flows")
    plt.xlabel("Scenario")
    plt.ylabel("Flow count")
    plt.xticks(x, labels, rotation=30, ha="right")
    plt.legend()
    plt.tight_layout()
    plt.savefig(graph_dir / "failure_recovery.png", dpi=150)
    plt.close()
