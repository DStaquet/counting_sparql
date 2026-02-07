"""Module to split a build graph into different pieces"""

from random import randint

# pylint: disable=import-error
from example_constructor.graph_constructor import (
    build_hop_graph,
    Graph,
)


def __remove_quotes(given_string: str) -> str:
    return given_string[1 : len(given_string) - 1]


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
        "",
        "",
    )

    split_list: list[Graph] = []
    seen_vertices: list[set[str]] = [
        set() for _ in range(amount)
    ]
    split_triples: list[list[tuple[str, str, str]]] = [
        [] for _ in range(amount)
    ]

    for triple in triple_list:
        if triple[2] == "'Node'":
            continue
        index = randint(0, amount - 1)
        seen_vertices[index].add(__remove_quotes(triple[0]))
        seen_vertices[index].add(__remove_quotes(triple[2]))
        split_triples[index].append(
            (
                __remove_quotes(triple[0]),
                __remove_quotes(triple[1]),
                __remove_quotes(triple[2]),
            )
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
    og_g: Graph = build_hop_graph(5, 5, 4)
    print(og_g)
    split_graphs = split_graph_into_pods(og_g, 3)
    for i, graph in enumerate(split_graphs):
        print("Graph:", i)
        print(graph)
