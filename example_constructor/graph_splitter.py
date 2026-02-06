"""Module to split a build graph into different pieces"""

from random import randint

# pylint: disable=import-error
from graph_constructor import Graph, build_hop_graph


def split_graph_into_pods(
    og_graph: Graph, amount: int
) -> list[Graph]:
    """Splits the graph into the given amount of Graphs

    Args:
        og_graph (Graph): Original Graph
        amount (int): Amount to split into

    Returns:
        list[Graph]: List with the og_graph split into multiple
            graphs.
    """
    triple_list = og_graph.graph_to_triple_list(
        "http://example.org/node/",
        "http://example.org/edge/",
    )

    split_list: list[Graph] = []
    seen_vertices: list[set[str]] = [
        set() for _ in range(amount)
    ]
    split_triples: list[list[tuple[str, str, str]]] = [
        [] for _ in range(amount)
    ]

    for triple in triple_list:
        index = randint(0, amount - 1)
        seen_vertices[index].add(triple[0])
        seen_vertices[index].add(triple[2])
        split_triples[index].append(
            (triple[0], triple[1], triple[2])
        )

    for index in range(amount):
        split_list.append(
            Graph(
                list(seen_vertices[index]),
                split_triples[index],
            )
        )

    return split_list


if __name__ == "__main__":
    og_graph: Graph = build_hop_graph(1000, 1000, 4)
    print(og_graph)
    split_graphs = split_graph_into_pods(og_graph, 3)
    for graph in split_graphs:
        print(graph)
