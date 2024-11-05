from graph_constructor import Graph


def save_graph_to_file(
    graph: Graph,
    filename: str,
    vertices_uri: str = "http://example.org/",
    edges_uri: str = "http://example.org/edges/",
    csv: bool = False,
) -> None:
    """Saves the graph to a file.

    Args:
        graph (Graph): Given graph.
        filename (str): File name.
        vertices_uri (str, optional): URI of the vertices. Defaults to "http://example.org/".
        edges_uri (str, optional): URI of the edges. Defaults to "http://example.org/edges/".
        csv (bool, optional): If True, saves the graph in CSV format. Defaults to False.
    """
    with open(filename, "w") as file:
        if not csv:
            file.write(
                graph.graph_to_turtle(
                    vertices_uri, edges_uri
                )
            )
        else:
            from csv import writer

            write_handle = writer(file)
            write_handle.writerow(["s", "p", "o"])
            for triple in graph.graph_to_triple_list(
                vertices_uri, edges_uri
            ):
                write_handle.writerow(triple)
