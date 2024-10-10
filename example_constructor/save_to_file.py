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


def save_table_to_file(
    table_list: list[tuple[str, int]], file_name: str
) -> None:
    """Saves the given table to the given filename.

    Args:
        table_list (list[tuple[str, int]]): List of all rows in the table
        file_name (str): Name of the file to write to.
    """
    import csv

    with open(file_name, "w", newline="") as open_file:
        wr = csv.writer(open_file)
        wr.writerow(["A", "k"])
        for row in table_list:
            wr.writerow(row)
