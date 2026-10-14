# ECMP Phase 2 — Load Distribution and Failure Recovery

## 1. Project overview

This project implements a **logical Python simulation** of Equal-Cost Multi-Path (ECMP) routing in a leaf–spine data-centre fabric. It creates traffic flows, assigns each flow to one equal-cost path using deterministic hashing, measures link load, injects link/spine failures, reroutes affected flows, and exports CSV results and PNG graphs.

This is a simulation only. It does not send packets, configure physical switches, or reproduce real switch hash functions.

## 2. Project structure

```text
ecmp_phase2/
├── .venv/                         # create locally; do not share
├── data/
│   └── config.json                # topology, traffic, failure scenarios
├── docs/
│   ├── DESIGN.md                  # system design
│   ├── FRS.md                     # functional requirements
│   ├── EXPERIMENTS.md              # setup, metrics, results interpretation
│   └── PHASE2_CHECKLIST.md         # deliverables checklist
├── graphs/                        # generated PNG graphs
├── results/                       # generated CSV/JSON data
├── src/ecmp_phase2/
│   ├── __init__.py
│   ├── models.py
│   ├── topology.py
│   ├── traffic.py
│   ├── ecmp.py
│   ├── metrics.py
│   ├── failures.py
│   ├── experiment.py
│   └── cli.py
├── tests/
│   ├── test_topology.py
│   ├── test_ecmp.py
│   ├── test_failures.py
│   └── test_metrics.py
├── pyproject.toml
├── requirements.txt
└── README.md
```

## 3. Requirements

- Python 3.10 or newer
- pip
- Internet only for installing `matplotlib` and `pytest` if they are not already installed

## 4. Run on Windows PowerShell

Open PowerShell in the `ecmp_phase2` folder.

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install -e .
python -m ecmp_phase2.cli
```

If PowerShell blocks activation, use this for the current terminal only:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

You can also run without activating the environment after dependencies are installed:

```powershell
py -m ecmp_phase2.cli
```

## 5. Run tests

```powershell
python -m pytest -v
```

Expected: all tests pass. Exact recovery-time values can differ on each run because they are measured using the local Python clock.

## 6. Configure the experiment

Edit `data/config.json`:

- `num_leaves`: number of leaf switches (at least 2)
- `num_spines`: number of spine switches (at least 1)
- `hosts_per_leaf`: hosts attached to each leaf (at least 1)
- `link_capacity_mbps`: capacity assigned to each logical link
- `num_flows`: number of logical flows to generate
- `seed`: repeatable traffic-generation seed
- `min_demand_mbps`, `max_demand_mbps`: inclusive range used for generated flow demands
- `failures`: scenarios with `type` equal to `link` or `spine` and a valid `target`

Link IDs use names such as `L1-S1`. Spine IDs use names such as `S2`. If you change the topology, make sure each failure target still exists.

## 7. Outputs

The program creates or updates:

- `results/baseline_links.csv` — every logical link, capacity, traffic, utilisation and flow-hop count
- `results/baseline_flows.csv` — flow endpoints, demand, chosen path and status
- `results/<scenario>_links.csv` — link metrics for each failure scenario
- `results/<scenario>_flows.csv` — assignments after each failure
- `results/scenario_summary.csv` — baseline and scenario metrics in one table
- `results/experiment_metadata.json` — configuration and metric definitions
- `graphs/baseline_link_utilization.png`
- `graphs/scenario_max_utilization.png`
- `graphs/failure_recovery.png`

Do not write expected numerical results into a report until you have run the program and copied the values from your own generated CSV files.

## 8. Algorithm

1. Build hosts, leaves, spines and links.
2. Generate repeatable source/destination flows between different leaves.
3. Find all available equal-cost paths for each flow.
4. Compute a stable SHA-256 hash of the flow ID, endpoints, seed and fixed salt.
5. Select `hash % number_of_available_paths`.
6. Add the flow's demand to every link on its chosen path.
7. Calculate link utilisation and summary metrics.
8. Disable the configured link or spine and recalculate assignments using only valid surviving paths.
9. Count affected, rerouted and disconnected flows.
10. Export CSV/JSON and graphs.

## 9. Metric definitions and limitations

- **Traffic (Mbps):** sum of the demands of assigned flows traversing the link.
- **Link utilisation (%):** `traffic_mbps / capacity_mbps * 100`. It may exceed 100%; this flags logical oversubscription rather than simulating packet drops.
- **Mean/min/max/std. dev.:** computed over all topology links, including zero-load links. For failure scenarios, failed links remain in the table and are marked `failed`; their measured traffic is zero because invalid paths are not assigned.
- **Load imbalance:** `maximum utilisation / mean utilisation`; set to zero if mean utilisation is zero. A value closer to 1 means a more even distribution under this definition.
- **Affected flows:** baseline-connected flows whose baseline path included the failed link or spine.
- **Rerouted affected flows:** affected flows that have a valid assignment after the failure. The simulator recomputes all flow assignments, not only affected flows.
- **Disconnected flows:** flows for which no valid path remains. With at least two spines, one spine failure usually leaves a path; a topology with one spine can lose inter-leaf connectivity after that spine fails.
- **Recovery time:** Python wall-clock time to recompute assignments. It is a simulator runtime metric, **not** real network convergence or hardware recovery time.
- **Hashing:** stable deterministic hash for reproducibility, not a vendor-specific ECMP hash.
- **Scope:** no packet-level simulation, queueing, congestion control, real switch behaviour, or physical-network control.

## 10. Research/design alignment

The uploaded Phase I proposal calls for a configurable leaf–spine topology, deterministic flow-based ECMP, configurable traffic demands, per-link utilisation/imbalance, simulated link and spine failures, rerouting/connectivity checks, CSV/graphs, tests, and documentation. This implementation covers those simulation objectives. It does not implement advanced algorithms such as PLB or REPS, consistent with the proposal's initial scope.

## 11. Suggested final Phase 2 workflow

1. Run the simulator successfully.
2. Run all automated tests.
3. Open `results/scenario_summary.csv` and inspect each scenario.
4. Inspect the three PNG files in `graphs/`.
5. Record actual findings and limitations in your report. Keep recovery time described as simulated recomputation time.
