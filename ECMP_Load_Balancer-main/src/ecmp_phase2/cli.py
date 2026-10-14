import argparse
from .experiment import run_experiment


def main():
    parser = argparse.ArgumentParser(description="Run the ECMP Phase 2 simulator.")
    parser.add_argument("--config", default="data/config.json", help="Path to JSON config")
    parser.add_argument("--output", default="results", help="CSV/JSON output directory")
    parser.add_argument("--graphs", default="graphs", help="Graph output directory")
    args = parser.parse_args()
    result = run_experiment(args.config, args.output, args.graphs)
    print("\nECMP Phase 2 simulation completed.")
    print(f"Topology: {result['topology'].num_leaves} leaves, "
          f"{result['topology'].num_spines} spines, "
          f"{result['topology'].hosts_per_leaf} hosts/leaf")
    print(f"Flows generated: {len(result['flows'])}")
    print("\nScenario summary:")
    for summary in result["summaries"]:
        print(f"- {summary['scenario']}: connected={summary['connected_flows']}, "
              f"disconnected={summary['disconnected_flows']}, "
              f"max_utilisation={summary['max_utilization_pct']:.2f}%, "
              f"affected={summary.get('affected_flows', 0)}, "
              f"rerouted={summary.get('rerouted_affected_flows', 0)}")
    print("\nFiles written to results/ and graphs/.")


if __name__ == "__main__":
    main()
