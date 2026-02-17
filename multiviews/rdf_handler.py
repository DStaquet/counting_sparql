"""
Submodule of multiviews that handles the logic of reading RDF data.
"""

from rdflib import Graph

from example_constructor.graph_constructor import (
    Graph as custom_Graph,
)


def parse_pod_data(
    pod_data: str,
) -> list[tuple[str, str, str, str]]:
    """Parses RDF data from a pod and returns it as a list of tuples.

    Args:
        pod_data (str): The RDF data in string format.
    Returns:
        list[tuple[str, str, str, str]]: A list of tuples
            containing pod_id, subject, predicate, and object.
    """
    g = Graph()
    g.parse(data=pod_data, format="turtle")
    pod_id = "pod_example"  # This should be derived from the pod data or URL
    triples = []
    for subj, pred, obj in g:
        triples.append(
            (pod_id, str(subj), str(pred), str(obj))
        )
    return triples


def _read_ttl_data(
    data_file: str,
) -> custom_Graph:
    vertices: set[str] = set()
    edges: set[tuple[str, str, str]] = set()
    with open(data_file, "r", encoding="utf-8") as handle:
        g: Graph = Graph().parse(data=handle.read())
        for s, p, o in g:
            vertices.add(f"'{s}'")
            edges.add((f"'{s}'", f"'{p}'", f"'{o}'"))

    return custom_Graph(list(vertices), list(edges))
