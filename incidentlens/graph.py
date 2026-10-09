import re

import networkx as nx

from incidentlens.models import Chunk, GraphEdge

RELATION = re.compile(
    r"^([A-Z][A-Za-z0-9 -]{1,60})\s+(depends on|is owned by)\s+"
    r"([A-Z][A-Za-z0-9 -]{1,60})\.$",
    re.M,
)


class KnowledgeGraph:
    """Conservative domain extraction: only explicit dependency and ownership sentences."""

    def __init__(self, chunks: list[Chunk]):
        self.graph = nx.MultiDiGraph()
        self.edges: list[GraphEdge] = []
        for chunk in chunks:
            for match in RELATION.finditer(chunk.text):
                source, relation, target = (x.strip() for x in match.groups())
                edge = GraphEdge(
                    source=source,
                    target=target,
                    relation=relation,
                    chunk_id=chunk.id,
                    document=chunk.document,
                    page=chunk.page,
                    evidence=match.group(),
                )
                self.edges.append(edge)
                self.graph.add_edge(source, target, evidence=edge)
        for chunk in chunks:
            chunk.entities = [n for n in self.graph.nodes if n.lower() in chunk.text.lower()]

    def related(self, query: str, max_depth: int = 2) -> list[GraphEdge]:
        aliases = {
            "checkout": "Checkout Service",
            "payments": "Payments API",
            "ledger": "Ledger Database",
            "inventory": "Inventory API",
        }
        seeds = [n for n in self.graph.nodes if n.lower() in query.lower()]
        seeds += [v for k, v in aliases.items() if re.search(rf"\b{k}\b", query, re.I)]
        reached = set()
        for seed in set(seeds):
            if seed not in self.graph:
                continue
            reached.update(
                nx.single_source_shortest_path_length(self.graph, seed, cutoff=max_depth - 1).keys()
            )
        return [e for e in self.edges if e.source in reached]
