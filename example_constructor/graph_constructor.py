class Graph:
    def __init__(
        self,
        vertices: list[str],
        edges: list[tuple[str, str, str]],
    ):
        self.vertices = vertices
        self.edges = edges

    def __str__(self):
        return f"Vertices: {self.vertices}, Edges: {self.edges}"

    def graph_to_turtle(
        self, vertices_uri: str, edges_uri: str
    ) -> str:
        """Converts the graph to a turtle string.

        Returns:
            str: Turtle string.
        """
        turtle_string: str = ""

        # Prefixes
        turtle_string += f"@prefix : <{vertices_uri}> .\n"
        turtle_string += (
            f"@prefix edge: <{edges_uri}> .\n\n"
        )

        # Triples per vertex
        for vertex in self.vertices:
            turtle_string += f":{vertex}\n    a :Node"
            for edge in self.edges:
                if edge[0] == vertex:
                    turtle_string += (
                        f" ;\n    edge:{edge[1]} :{edge[2]}"
                    )
            turtle_string += " .\n\n"

        return turtle_string


def construct_serial(
    bottlenecks: int, many_vertices: int
) -> Graph:
    """Builds a parallel network given the many_vertices and bottlenecks.

    Args:
        bottlenecks (int): Builds
        many_vertices (int): Amount of vertices between bottlenecks.
    """
    # Init
    vertices: list[str] = []
    edges: list[tuple[str, str, str]] = []

    for i in range(bottlenecks):
        # Build first set of vertices before bottleneck
        temp_vertices: list[str] = [
            str(i) + str(j) for j in range(many_vertices)
        ]
        bottleneck_left: str = str(i) + "bl"
        bottleneck_right: str = str(i) + "br"
        # Edges to bottleneck
        first_temp_edges: list[tuple[str, str, str]] = [
            (temp_vertices[j], "hop", bottleneck_left)
            for j in range(many_vertices)
        ]
        # Bottleneck edge
        temp_bottleneck_edge: tuple[str, str, str] = (
            bottleneck_left,
            "hop",
            bottleneck_right,
        )
        # Edges from bottleneck
        second_temp_edges: list[tuple[str, str, str]] = [
            (bottleneck_right, "hop", str(i + 1) + str(j))
            for j in range(many_vertices)
        ]

        vertices.extend(temp_vertices)
        vertices.extend([bottleneck_left, bottleneck_right])
        edges.extend(first_temp_edges)
        edges.append(temp_bottleneck_edge)
        edges.extend(second_temp_edges)

    last_vertices: list[str] = [
        str(i + 1) + str(j) for j in range(many_vertices)
    ]
    vertices.extend(last_vertices)

    return Graph(vertices, edges)


def __build_left_side(
    many_to_one_index: int,
    bottleneck_index: int,
    bottleneck_right: str,
) -> tuple[list[str], list[tuple[str, str, str]]]:
    """Builds left side of parallel graph bottleneck.

    Args:
        many_to_one_index (int): Index of many to one.
        bottleneck_index (int): Index of amount of bottlenecks.
        bottleneck_right (str): Right name of bottleneck.
        bottleneck_left (str): Left name of bottleneck.

    Returns:
        tuple[list[str], list[tuple[str, str, str]]]: Vertices and edges.
    """
    temp_vertices: list[str] = [
        str(many_to_one_index)
        + str(bottleneck_index)
        + str(k)
        for k in range(many_vertices)
    ]
    # Edges from bottleneck
    first_temp_edges: list[tuple[str, str, str]] = [
        (bottleneck_right, "hop", temp_vertices[k])
        for k in range(many_vertices)
    ]
    """# Edges to bottleneck
    second_temp_edges: list[tuple[str, str, str]] = [
        (
            str(many_to_one_index)
            + str(bottleneck_index + 1)
            + str(k),
            "hop",
            bottleneck_left,
        )
        for k in range(many_vertices)
    ]"""

    left_vertices = temp_vertices
    left_edges = first_temp_edges

    return left_vertices, left_edges


def __build_right_side(
    many_to_one_index: int,
    bottleneck_index: int,
    bottleneck_left: str,
) -> tuple[list[str], list[tuple[str, str, str]]]:
    """Builds right side of parallel graph.

    Args:
        many_to_one_index (int): Index of many to one.
        bottleneck_index (int): Index of amount of bottlenecks.
        bottleneck_right (str): Bottleneck right name.
        bottleneck_left (str): Bottleneck left name.

    Returns:
        tuple[list[str], list[tuple[str, str, str]]]: Vertices and edges.
    """
    temp_vertices: list[str] = [
        str(many_to_one_index)
        + str(bottleneck_index)
        + str(k)
        for k in range(many_vertices)
    ]
    # Edges from bottleneck
    first_temp_edges: list[tuple[str, str, str]] = [
        (temp_vertices[k], "hop", bottleneck_left)
        for k in range(many_vertices)
    ]
    """# Edges to bottleneck
    second_temp_edges: list[tuple[str, str, str]] = [
        (
            bottleneck_right,
            "hop",
            str(many_to_one_index)
            + str(bottleneck_index + 1)
            + str(k),
        )
        for k in range(many_vertices)
    ]"""

    right_vertices = temp_vertices
    right_edges = first_temp_edges

    return right_vertices, right_edges


def construct_parallel(
    bottlenecks: int, many_vertices: int, many_to_one: int
) -> Graph:
    """Constructs the graphs in parallel

    Args:
        bottlenecks (int): Amount of bottlenecks.
        many_vertices (int): Amount of vertices between bottlenecks.
        many_to_one (int): Amount of vertices connecting to one bottleneck.

    Returns:
        Graph: _description_
    """
    vertices: list[str] = []
    edges: list[tuple[str, str, str]] = []

    # Left side
    for i in range(many_to_one):
        bottleneck_right: str = str(i) + "br"
        bottleneck_left: str = str(i) + "bl"
        vertices.extend([bottleneck_left, bottleneck_right])
        # Bottleneck edge
        temp_bottleneck_edge: tuple[str, str, str] = (
            bottleneck_left,
            "hop",
            bottleneck_right,
        )
        edges.append(temp_bottleneck_edge)

        for j in range(bottlenecks):
            left_vertices, left_edges = __build_left_side(
                i, j, bottleneck_right
            )
        last_left_vertices, last_left_edges = (
            __build_right_side(i, j + 1, bottleneck_left)
        )

        vertices.extend(left_vertices)
        vertices.extend(last_left_vertices)
        edges.extend(left_edges)
        edges.extend(last_left_edges)

    # Main bottleneck
    bottleneck_right: str = "br"
    bottleneck_left: str = "bl"
    # Edges to bottleneck
    left_main_edges: list[tuple[str, str, str]] = []
    for i in range(many_to_one):
        for j in range(many_vertices):
            left_main_edges.append(
                (
                    str(i) + "0" + str(j),
                    "hop",
                    bottleneck_left,
                )
            )
    # Edges from bottleneck
    right_main_edges: list[tuple[str, str, str]] = []
    for i in range(i + 1, i + 1 + many_to_one):
        for j in range(many_vertices):
            right_main_edges.append(
                (
                    bottleneck_right,
                    "hop",
                    str(i) + "0" + str(j),
                )
            )
    main_edges: list[tuple[str, str, str]] = (
        left_main_edges + right_main_edges
    )
    main_vertices: list[str] = [
        bottleneck_left,
        bottleneck_right,
    ]
    main_bottleneck_edge: tuple[str, str, str] = (
        bottleneck_left,
        "hop",
        bottleneck_right,
    )
    main_edges.append(main_bottleneck_edge)
    vertices.extend(main_vertices)
    edges.extend(main_edges)

    # Right side
    for i in range(many_to_one, many_to_one * 2):
        bottleneck_right: str = str(i) + "br"
        bottleneck_left: str = str(i) + "bl"
        vertices.extend([bottleneck_left, bottleneck_right])
        # Bottleneck edge
        temp_bottleneck_edge: tuple[str, str, str] = (
            bottleneck_left,
            "hop",
            bottleneck_right,
        )
        edges.append(temp_bottleneck_edge)

        for j in range(bottlenecks):
            right_vertices, right_edges = (
                __build_right_side(i, j, bottleneck_left)
            )
        last_right_vertices, last_right_edges = (
            __build_left_side(i, j + 1, bottleneck_right)
        )

        vertices.extend(right_vertices)
        vertices.extend(last_right_vertices)
        edges.extend(right_edges)
        edges.extend(last_right_edges)

    return Graph(
        vertices,
        edges,
    )


if __name__ == "__main__":
    import argparse
    from save_graph import save_graph_to_file

    parser = argparse.ArgumentParser(
        description="Construct a graph",
        prog="graph_constructor.py",
    )

    parser.add_argument(
        "-b",
        "--bottlenecks",
        type=int,
        default=1,
        help="Amount of bottlenecks",
    )
    parser.add_argument(
        "-m",
        "--many_vertices",
        type=int,
        default=3,
        help="Amount of vertices between bottlenecks",
    )
    parser.add_argument(
        "-p",
        "--many_to_one",
        type=int,
        default=2,
        help="Amount of vertices connecting to one bottleneck",
    )
    parser.add_argument(
        "-f",
        "--file",
        type=str,
        default=None,
        help="File to save the graph",
    )

    args = parser.parse_args()

    bottlenecks: int = args.bottlenecks
    many_vertices: int = args.many_vertices
    many_to_one: int = args.many_to_one

    serial_graph = construct_serial(
        bottlenecks, many_vertices
    )
    print(serial_graph)
    print(
        serial_graph.graph_to_turtle(
            "http://example.org/",
            "http://example.org/edges/",
        )
    )

    parallel_graph = construct_parallel(
        bottlenecks,
        many_vertices,
        many_to_one,
    )

    print(parallel_graph)
    print(
        parallel_graph.graph_to_turtle(
            "http://example.org/",
            "http://example.org/edges/",
        )
    )

    if args.file:
        save_graph_to_file(
            parallel_graph,
            args.file,
        )
