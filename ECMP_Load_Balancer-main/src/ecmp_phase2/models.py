from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Flow:
    flow_id: str
    src_host: str
    dst_host: str
    demand_mbps: float
    seed: int = 0


@dataclass
class FlowAssignment:
    flow: Flow
    path: Optional[tuple[str, ...]]
    status: str  # connected or disconnected
    reason: str = ""


@dataclass
class FailureEvent:
    failure_type: str  # link or spine
    target: str
    description: str
