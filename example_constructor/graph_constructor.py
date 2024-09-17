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

    def graph_to_turtle(self) -> str:  # type: ignore
        """Converts the graph to a turtle string.

        Returns:
            str: Turtle string.
        """
        pass


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
    left_vertices: list[str] = []
    right_vertices: list[str] = []
    left_edges: list[tuple[str, str, str]] = []
    right_edges: list[tuple[str, str, str]] = []
    # Left side
    for i in range(many_to_one):
        for j in range(bottlenecks):
            temp_vertices: list[str] = [
                str(i) + str(j) + str(k)
                for k in range(many_vertices)
            ]
            bottleneck_right: str = str(i) + str(j) + "br"
            bottleneck_left: str = str(i) + str(j) + "bl"
            # Edges from bottleneck
            first_temp_edges: list[tuple[str, str, str]] = [
                (bottleneck_right, "hop", temp_vertices[k])
                for k in range(many_vertices)
            ]
            # Bottleneck edge
            temp_bottleneck_edge: tuple[str, str, str] = (
                bottleneck_left,
                "hop",
                bottleneck_right,
            )
            # Edges to bottleneck
            second_temp_edges: list[
                tuple[str, str, str]
            ] = [
                (
                    str(i) + str(j + 1) + str(k),
                    "hop",
                    bottleneck_left,
                )
                for k in range(many_vertices)
            ]

            left_vertices.extend(temp_vertices)
            left_vertices.extend(
                [bottleneck_left, bottleneck_right]
            )
            left_edges.extend(first_temp_edges)
            left_edges.append(temp_bottleneck_edge)
            left_edges.extend(second_temp_edges)

    # Right side
    for i in range(i + 1, i + 1 + many_to_one):
        for j in range(bottlenecks):
            temp_vertices: list[str] = [
                str(i) + str(j) + str(k)
                for k in range(many_vertices)
            ]
            bottleneck_right: str = str(i) + str(j) + "br"
            bottleneck_left: str = str(i) + str(j) + "bl"
            # Edges from bottleneck
            first_temp_edges: list[tuple[str, str, str]] = [
                (temp_vertices[k], "hop", bottleneck_right)
                for k in range(many_vertices)
            ]
            # Bottleneck edge
            temp_bottleneck_edge: tuple[str, str, str] = (
                bottleneck_left,
                "hop",
                bottleneck_right,
            )
            # Edges to bottleneck
            second_temp_edges: list[
                tuple[str, str, str]
            ] = [
                (
                    bottleneck_left,
                    "hop",
                    str(i) + str(j + 1) + str(k),
                )
                for k in range(many_vertices)
            ]

            right_vertices.extend(temp_vertices)
            right_vertices.extend(
                [bottleneck_left, bottleneck_right]
            )
            right_edges.extend(first_temp_edges)
            right_edges.append(temp_bottleneck_edge)
            right_edges.extend(second_temp_edges)

    return Graph(
        left_vertices + right_vertices,
        left_edges + right_edges,
    )


if __name__ == "__main__":
    import argparse

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

    args = parser.parse_args()

    bottlenecks: int = args.bottlenecks
    many_vertices: int = args.many_vertices

    serial_graph = construct_serial(
        bottlenecks, many_vertices
    )
    print(serial_graph)

    parallel_graph = construct_parallel(
        bottlenecks, many_vertices, 2
    )

    print(parallel_graph)
