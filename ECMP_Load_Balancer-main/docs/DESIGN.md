# System and Research Design

## 1. Architecture

```text
JSON configuration
       |
       v
Topology builder ---- Traffic generator
       |                      |
       +----------+-----------+
                  v
           ECMP path selector
                  |
                  v
         Baseline flow assignment
                  |
                  v
           Link metric analyser
                  |
        +---------+----------+
        |                    |
        v                    v
   Link failure         Spine failure
        |                    |
        +---------+----------+
                  v
         Reassignment/recovery
                  |
                  v
       CSV + JSON + PNG outputs
                  |
                  v
        Automated test suite
```

## 2. Topology model
Every host is connected to exactly one leaf. Each leaf is connected to every spine. A path between hosts on different leaves has the form `source host -> source leaf -> spine -> destination leaf -> destination host`. All such paths have equal hop count.

## 3. ECMP selection
For each flow, SHA-256 is calculated from a fixed salt, flow ID, endpoints and seed. The resulting integer modulo the ordered list of currently available paths chooses the path. SHA-256 is used instead of Python's built-in `hash()` because Python may randomise its hash between processes. The model is deterministic but is not a vendor switch implementation.

## 4. Traffic model
Flows are logical demands in Mbps. A seeded pseudo-random generator selects endpoints on different leaves and demands within the configured range. The demand is counted on each link along the flow's route.

## 5. Failure and recovery
A link failure removes every candidate path using that link. A spine failure removes every candidate path through that spine. Assignments are recomputed for the traffic set, and the simulator counts baseline flows affected by the event, those still connected, and those disconnected.

## 6. Performance metrics
Utilisation is `100 × assigned traffic / link capacity`. Mean, minimum, maximum and population standard deviation are calculated across all links, including zero-load links. Imbalance is max utilisation divided by mean utilisation, or zero if the mean is zero. Recovery time is the local wall-clock duration of assignment recomputation only.

## 7. Research positioning
The Phase I survey discusses static ECMP's potential for uneven flow placement and cites adaptive or congestion-aware approaches including PLB and REPS. Phase 2 implements baseline deterministic flow hashing and failure rerouting; it does not implement PLB, REPS, packet spraying, or vendor-specific hash behaviour.

## 8. Limitations
- Logical simulation, not packet-level or hardware experiment.
- No queue, packet loss, latency, or TCP/RDMA modelling.
- Demand is aggregated as a static Mbps load.
- Recovery time depends on local machine/runtime conditions.
- Hash selection is an educational approximation.
