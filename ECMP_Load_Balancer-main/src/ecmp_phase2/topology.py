from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class Link:
    link_id: str
    a: str
    b: str
    capacity_mbps: float

    def other(self, node: str) -> str:
        if node == self.a:
            return self.b
        if node == self.b:
            return self.a
        raise ValueError(f"{node!r} is not on link {self.link_id!r}")


class LeafSpineTopology:
    """Logical leaf-spine fabric with hosts attached to leaves."""

    def __init__(self, num_leaves=4, num_spines=3, hosts_per_leaf=3,
                 link_capacity_mbps=10000.0):
        if num_leaves < 2:
            raise ValueError("num_leaves must be at least 2")
        if num_spines < 1:
            raise ValueError("num_spines must be at least 1")
        if hosts_per_leaf < 1:
            raise ValueError("hosts_per_leaf must be at least 1")
        if link_capacity_mbps <= 0:
            raise ValueError("link_capacity_mbps must be positive")

        self.num_leaves = num_leaves
        self.num_spines = num_spines
        self.hosts_per_leaf = hosts_per_leaf
        self.link_capacity_mbps = float(link_capacity_mbps)
        self.leaves = [f"L{i}" for i in range(1, num_leaves + 1)]
        self.spines = [f"S{i}" for i in range(1, num_spines + 1)]
        self.host_to_leaf = {}
        self.links = {}
        self.adjacency = {}
        for leaf in self.leaves:
            self.adjacency[leaf] = []
        for spine in self.spines:
            self.adjacency[spine] = []
        for li, leaf in enumerate(self.leaves, start=1):
            for hi in range(1, hosts_per_leaf + 1):
                host = f"H{li}_{hi}"
                self.host_to_leaf[host] = leaf
                self.adjacency[host] = []
                self._add_link(f"{host}-{leaf}", host, leaf, link_capacity_mbps)
        for leaf in self.leaves:
            for spine in self.spines:
                self._add_link(f"{leaf}-{spine}", leaf, spine, link_capacity_mbps)

    def _add_link(self, link_id, a, b, capacity):
        link = Link(link_id, a, b, float(capacity))
        self.links[link_id] = link
        self.adjacency.setdefault(a, []).append((b, link_id))
        self.adjacency.setdefault(b, []).append((a, link_id))

    def host_leaf(self, host: str) -> str:
        try:
            return self.host_to_leaf[host]
        except KeyError as exc:
            raise ValueError(f"Unknown host: {host}") from exc

    def all_hosts(self):
        return list(self.host_to_leaf)

    def path_for_spine(self, src_host: str, dst_host: str, spine: str):
        """Return host-leaf-spine-leaf-host path, or None if invalid."""
        if src_host not in self.host_to_leaf or dst_host not in self.host_to_leaf:
            return None
        src_leaf = self.host_to_leaf[src_host]
        dst_leaf = self.host_to_leaf[dst_host]
        if src_leaf == dst_leaf or spine not in self.spines:
            return None
        return (src_host, src_leaf, spine, dst_leaf, dst_host)

    def path_links(self, path: Iterable[str]):
        path = tuple(path)
        result = []
        for left, right in zip(path, path[1:]):
            candidates = self.adjacency.get(left, [])
            link_id = next((lid for node, lid in candidates if node == right), None)
            if link_id is None:
                raise ValueError(f"No link between {left} and {right}")
            result.append(link_id)
        return result

    def valid_paths(self, src_host, dst_host, failed_links=None, failed_spines=None):
        failed_links = failed_links or set()
        failed_spines = failed_spines or set()
        paths = []
        for spine in self.spines:
            if spine in failed_spines:
                continue
            path = self.path_for_spine(src_host, dst_host, spine)
            if path and not (set(self.path_links(path)) & failed_links):
                paths.append(path)
        return paths
