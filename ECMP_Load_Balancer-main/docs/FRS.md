# Functional Requirements Specification (FRS)

## 1. Purpose
Define the required behaviour of the Phase 2 ECMP leaf–spine simulator described in the Phase I proposal.

## 2. Scope
The program simulates logical flow assignments and failure recovery. Physical switches and real packet forwarding are out of scope.

## 3. Functional requirements
- **FR-01 Topology:** configure leaf count, spine count, hosts per leaf, and link capacity.
- **FR-02 Flow generation:** generate flow IDs, source/destination hosts on different leaves, and configurable demand values.
- **FR-03 Repeatability:** use explicit seeds and a stable hash implementation.
- **FR-04 ECMP:** assign each flow to one available equal-cost path.
- **FR-05 Link accounting:** aggregate each assigned flow's demand on every traversed link.
- **FR-06 Metrics:** export link utilisation, mean/min/max utilisation, standard deviation, load imbalance, and flow connectivity counts.
- **FR-07 Link failure:** disable a configured link and reassign flows using surviving paths.
- **FR-08 Spine failure:** disable a configured spine and remove paths through it.
- **FR-09 Recovery metrics:** count affected, rerouted and disconnected flows; record simulator reassignment wall-clock time.
- **FR-10 Output:** export CSV and JSON data and PNG graphs.
- **FR-11 Validation:** reject invalid topology settings and invalid failure targets.
- **FR-12 Automated tests:** test topology, flow repeatability, assignment, metrics and failures.

## 4. Non-functional requirements
- Python 3.10+
- Readable, modular source code
- Repeatable traffic generation
- No physical network equipment required
- CSV outputs readable by spreadsheet applications
- Tests runnable using `python -m pytest -v`

## 5. Acceptance criteria
1. The default configuration runs without an exception.
2. Baseline and both configured failure scenarios are exported.
3. Flow and link CSVs are created for each scenario.
4. Three graph PNGs are generated when matplotlib is installed.
5. Tests pass.
6. Reports identify recovery time as simulator recomputation time, not real network convergence.
