from graph_constructor import Graph


def save_graph_to_file(
    graph: Graph,
    filename: str,
    vertices_uri: str = "http://example.org/",
    edges_uri: str = "http://example.org/edges/",
) -> None:
    """Saves the graph to a file.

    Args:
        graph (Graph): Given graph.
        filename (str): File name.
        vertices_uri (str, optional): URI of the vertices. Defaults to "http://example.org/".
        edges_uri (str, optional): URI of the edges. Defaults to "http://example.org/edges/".
    """
    with open(filename, "w") as file:
        file.write(
            graph.graph_to_turtle(vertices_uri, edges_uri)
        )
