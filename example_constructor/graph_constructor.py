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

    def diff(self, other):
        """Returns the difference between two graphs.

        Args:
            other (Graph): The graph to compare with.
        """
        vertices_diff = list(
            set(self.vertices).difference(
                set(other.vertices)
            )
        )
        edges_diff = list(
            set(self.edges).difference(set(other.edges))
        )

        return Graph(vertices_diff, edges_diff)

    def get_vertices(self) -> list[str]:
        """Get the vertices of the graph.

        Returns:
            list[str]: List of all vertices of the graph.
        """
        return self.vertices

    def get_edges(self) -> list[tuple[str, str, str]]:
        """Gets the edges of the graph.

        Returns:
            list[tuple[str, str, str, str]]: List of all edges.
        """
        return self.edges

    def union(self, other):
        """Returns the union of two graphs.

        Args:
            other (Graph): The graph to compare with.
        """
        vertices_union = list(
            set(self.vertices).union(set(other.vertices))
        )
        edges_union = list(
            set(self.edges).union(set(other.edges))
        )

        return Graph(vertices_union, edges_union)

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

    def graph_to_delta_turtle(
        self,
        vertices_uri: str,
        edges_uri: str,
        swap_int: int = 1,
    ) -> str:
        """Delta version of the graph to turtle.

        Args:
            vertices_uri (str): Vertices uri to use.
            edges_uri (str): edges uri to use.

        Returns:
            str: String with the turtle that is written
        """
        # Prefixes
        turtle_string = f"@prefix : <{vertices_uri}> .\n"
        turtle_string += (
            f"@prefix edge: <{edges_uri}> .\n\n"
        )

        # Edges per vertex
        for vertex in self.vertices:
            for edge in self.edges:
                if edge[0] == vertex:
                    turtle_string += f":{vertex}\n\t edge:{edge[1]} :{edge[2]} .\n\n"

        return turtle_string

    def graph_to_triple_list_delta(
        self,
        vertices_uri: str,
        edges_uri: str,
        swap_int: int = 1,
        nu_bool: bool = False,
        no_overlap: bool = False,
    ) -> list[tuple[str, str, str, str]]:
        """Converts the graph to a list of triples.

        Returns:
            list[tuple[str, str, str]]: List of triples.
        """
        triples: list[tuple[str, str, str, str]] = []

        # Triples per vertex
        known_vertices = set()
        for edge in self.edges:
            vertex = edge[0]
            triples.append(
                (
                    f"'{vertices_uri}{vertex}'",
                    f"'{edges_uri}{edge[1]}'",
                    f"'{vertices_uri}{edge[2]}'",
                    str(swap_int * 1),
                )
            )
            if (
                vertex not in known_vertices
                and swap_int > 0
            ):
                if nu_bool:
                    write_vertex = edge[2]
                else:
                    write_vertex = vertex
                triples.append(
                    (
                        f"'{vertices_uri}{write_vertex}'",
                        "'https://www.w3.org/1999/02/22-rdf-syntax-ns#type'",
                        f"'{vertices_uri}Node'",
                        str(swap_int * 1),
                    )
                )
                if no_overlap:
                    triples.append(
                        (
                            f"'{vertices_uri}{vertex}'",
                            "'https://www.w3.org/1999/02/22-rdf-syntax-ns#type'",
                            f"'{vertices_uri}Node'",
                            str(swap_int * 1),
                        )
                    )
                known_vertices.add(vertex)

        return triples

    def graph_to_triple_list(
        self, vertices_uri: str, edges_uri: str
    ) -> list[tuple[str, str, str, str]]:
        """Converts the graph to a list of triples.

        Returns:
            list[tuple[str, str, str]]: List of triples.
        """
        triples: list[tuple[str, str, str, str]] = []

        # Triples per vertex
        for vertex in self.vertices:
            triples.append(
                (
                    f"'{vertices_uri}{vertex}'",
                    "'https://www.w3.org/1999/02/22-rdf-syntax-ns#type'",
                    f"'{vertices_uri}Node'",
                    "1",
                )
            )
            for edge in self.edges:
                if edge[0] == vertex:
                    triples.append(
                        (
                            f"'{vertices_uri}{vertex}'",
                            f"'{edges_uri}{edge[1]}'",
                            f"'{vertices_uri}{edge[2]}'",
                            "1",
                        )
                    )

        return triples


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
            (temp_vertices[j], "link", bottleneck_left)
            for j in range(many_vertices)
        ]
        # Bottleneck edge
        temp_bottleneck_edge: tuple[str, str, str] = (
            bottleneck_left,
            "link",
            bottleneck_right,
        )
        # Edges from bottleneck
        second_temp_edges: list[tuple[str, str, str]] = [
            (bottleneck_right, "link", str(i + 1) + str(j))
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
    bottleneck_left: str,
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
        (bottleneck_right, "link", temp_vertices[k])
        for k in range(many_vertices)
    ]
    # Edges to bottleneck
    second_temp_edges: list[tuple[str, str, str]] = [
        (
            str(many_to_one_index)
            + str(bottleneck_index + 1)
            + str(k),
            "link",
            bottleneck_left,
        )
        for k in range(many_vertices)
    ]

    left_vertices = temp_vertices
    left_edges = first_temp_edges + second_temp_edges

    return left_vertices, left_edges


def __build_right_side(
    many_to_one_index: int,
    bottleneck_index: int,
    bottleneck_left: str,
    bottleneck_right: str,
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
    # Edges to bottleneck
    first_temp_edges: list[tuple[str, str, str]] = [
        (temp_vertices[k], "link", bottleneck_left)
        for k in range(many_vertices)
    ]
    # Edges from bottleneck
    second_temp_edges: list[tuple[str, str, str]] = [
        (
            bottleneck_right,
            "link",
            str(many_to_one_index)
            + str(bottleneck_index + 1)
            + str(k),
        )
        for k in range(many_vertices)
    ]

    right_vertices = temp_vertices
    right_edges = first_temp_edges + second_temp_edges

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
        for j in range(bottlenecks):
            bottleneck_right: str = str(i) + str(j) + "br"
            bottleneck_left: str = str(i) + str(j) + "bl"
            vertices.extend(
                [bottleneck_left, bottleneck_right]
            )
            # Bottleneck edge
            temp_bottleneck_edge: tuple[str, str, str] = (
                bottleneck_left,
                "link",
                bottleneck_right,
            )
            edges.append(temp_bottleneck_edge)

            left_vertices, left_edges = __build_left_side(
                i, j, bottleneck_right, bottleneck_left
            )
            vertices.extend(left_vertices)
            edges.extend(left_edges)

        # Last left vertices
        last_left_vertices: list[str] = [
            str(i) + str(j + 1) + str(k)
            for k in range(many_vertices)
        ]
        """# Edges to bottleneck
        last_left_edges: list[tuple[str, str, str]] = [
            (last_left_vertices[k], "link", bottleneck_left)
            for k in range(many_vertices)
        ]"""

        vertices.extend(last_left_vertices)
        # edges.extend(last_left_edges)

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
                    "link",
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
                    "link",
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
        "link",
        bottleneck_right,
    )
    main_edges.append(main_bottleneck_edge)
    vertices.extend(main_vertices)
    edges.extend(main_edges)

    # Right side
    for i in range(many_to_one, many_to_one * 2):
        for j in range(bottlenecks):
            bottleneck_right: str = str(i) + str(j) + "br"
            bottleneck_left: str = str(i) + str(j) + "bl"
            vertices.extend(
                [bottleneck_left, bottleneck_right]
            )
            # Bottleneck edge
            temp_bottleneck_edge: tuple[str, str, str] = (
                bottleneck_left,
                "link",
                bottleneck_right,
            )
            edges.append(temp_bottleneck_edge)

            right_vertices, right_edges = (
                __build_right_side(
                    i, j, bottleneck_left, bottleneck_right
                )
            )

            vertices.extend(right_vertices)
            edges.extend(right_edges)

        last_right_vertices: list[str] = [
            str(i) + str(j + 1) + str(k)
            for k in range(many_vertices)
        ]

        vertices.extend(last_right_vertices)
        # edges.extend(last_right_edges)

    return Graph(
        vertices,
        edges,
    )


def build_hop_graph(
    fraction: int, N: int, groups: int
) -> Graph:
    """Builds a hop graph.

    Args:
        fraction (int): Fraction of how much vertices need to connect groups.
        N (int): Amount of vertices in a group.
        groups (int): Amount of groups.

    Returns:
        Graph: Graph object.
    """
    from random import sample, seed

    seed(13)
    from itertools import product

    vertices: list[list[str]] = []
    edges: list[tuple[str, str, str]] = []

    for i in range(groups):
        # Build vertices
        temp_vertices: list[str] = []
        for j in range(N):
            temp_vertices.append(f"{str(i)}_{str(j)}")
        vertices.append(temp_vertices)

    # Build edges
    if fraction == 0:
        amount_of_edges = 0
    else:
        amount_of_edges = int((N**2) / fraction)
    for i in range(0, groups - 1):
        all_temp_vertices = list(
            product(vertices[i], vertices[i + 1])
        )
        temp_edges = sample(
            all_temp_vertices, amount_of_edges
        )
        for j in range(amount_of_edges):
            edges.append(
                (
                    temp_edges[j][0],
                    "link",
                    temp_edges[j][1],
                )
            )

    nodes: list[str] = []
    for vertice_group in vertices:
        for node in vertice_group:
            nodes.append(node)

    return Graph(nodes, edges)


def build_disjunct_insert_edges(
    k_value: int, base_graph: Graph
) -> tuple[Graph, Graph, Graph]:
    """Builds the disjunct insert edges.

    Args:
        k_value (int): Amount of edges to insert.

    Returns:
        Graph: Graph object.
    """

    vertices: list[str] = []
    edges: list[tuple[str, str, str]] = []

    for i in range(0, k_value, 2):
        vertices.append(f"k{i}")
        vertices.append(f"k{i + 1}")
        edges.append((f"k{i}", "link", f"k{i + 1}"))

    g = Graph(vertices, edges)

    nu_graph = base_graph.union(g)

    return Graph([], []), g, nu_graph


def __create_last_vertices(
    groups: int,
    many_vertices: int,
    amount: int,
    edges: list[tuple[str, str, str]],
) -> tuple[
    list[tuple[str, str, str]], list[str], list[str]
]:
    """Generates the insert vertices for the hop graph.

    Args:
        groups (int): Amount of node groups
        many_vertices (int): How many nodes in one group

    Returns:
        list[str]: List of edges
    """
    from random import choice

    first_chosen_nodes: list[str] = list()
    last_chosen_nodes: list[str] = list()
    last_vertices: list[tuple[str, str, str]] = list()
    found_amount = 0
    while found_amount < amount:
        chosen_group = choice(range(groups - 1))
        first_node = (
            f"{chosen_group}_{choice(range(many_vertices))}"
        )
        first_chosen_nodes.append(first_node)
        second_node = f"{chosen_group + 1}_{choice(range(many_vertices))}"
        last_chosen_nodes.append(second_node)
        if (first_node, "link", second_node) in edges:
            continue
        else:
            last_vertices.append(
                (first_node, "link", second_node)
            )
            found_amount += 1

    return (
        last_vertices,
        first_chosen_nodes,
        last_chosen_nodes,
    )


def select_delta_edges_hop_graph(
    g: Graph, k_value: int, groups: int, many_vertices: int
) -> tuple[Graph, Graph, Graph]:
    """Selects and constructs the delta edges that need to be deleted from the graph.

    Args:
        g (Graph): The graph to select the edges from.
        k_value (int): How much edges should be inserted/deleted.

    Returns:
        Graph: Graph containing the edges that need to be deleted.
    """
    from random import sample, seed

    seed(13)

    # select k edges
    edges = g.edges
    selected_edges = sample(edges, k_value // 2)
    selected_vertices = [node[0] for node in selected_edges]
    """ last_vertices = [
        f"{groups}_{i}" for i in range(k_value // 2)
    ]"""

    """ second_to_last_group = [
        f"{groups - 1}_{i}" for i in range(many_vertices)
    ]

    chosen_second_to_last_vertices = sample(
        second_to_last_group, k_value // 2
    ) """

    (
        selected_ins_edges,
        first_chosen_nodes,
        last_chosen_nodes,
    ) = __create_last_vertices(
        groups, many_vertices, k_value // 2, edges
    )
    """ for i in range(k_value // 2):
        selected_ins_edges.append(
            (
                chosen_second_to_last_vertices[i],
                "link",
                last_vertices[i],
            )
        ) """

    delta_del_graph = Graph(
        selected_vertices, selected_edges
    )
    delta_ins_graph = Graph(
        first_chosen_nodes + last_chosen_nodes,
        selected_ins_edges,
    )

    # Construct the nu graphs
    nu_graph = g.diff(Graph([], selected_edges))
    nu_graph = nu_graph.union(Graph([], selected_ins_edges))

    return delta_del_graph, delta_ins_graph, nu_graph


def __replaceSingleQuote(filename: str) -> None:
    """Replaces the single quote in the file with a double quote.

    Args:
        filename (str): Filename to replace the single quotes in.
    """
    with open(filename, "r+") as f:
        text = f.read()
        text = text.replace("'", '"')
        f.seek(0)
        f.write(text)
        f.truncate()


if __name__ == "__main__":
    import argparse

    from save_graph import (
        save_graph_to_file,
    )

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
    parser.add_argument(
        "-t",
        "--type",
        default="parallel",
        help="Type of graph to construct",
        choices=["parallel", "serial", "hop"],
    )
    parser.add_argument(
        "-fr",
        "--fraction",
        type=int,
        default=1,
        help="Fraction of how much vertices need to connect groups",
    )
    parser.add_argument(
        "-csv",
        "--csv",
        type=str,
        default=None,
        help="CSV file to save the graph",
    )
    parser.add_argument(
        "-k",
        "--k_value",
        type=int,
        default=1,
        help="Amount of edges to delete",
    )
    parser.add_argument(
        "-dc",
        "--delta_csv",
        type=str,
        default=None,
        help="CSV file to save the delta graph",
    )
    parser.add_argument(
        "-nc",
        "--nu_csv",
        type=str,
        default=None,
        help="CSV file to save the new graph",
    )
    parser.add_argument(
        "-no",
        "--no-overlap",
        dest="no_overlap",
        action="store_true",
        default=False,
        help="No joining of the delta graphs",
    )

    args = parser.parse_args()

    bottlenecks: int = args.bottlenecks
    many_vertices: int = args.many_vertices
    many_to_one: int = args.many_to_one

    if args.type == "serial":
        graph = construct_serial(bottlenecks, many_vertices)
    elif args.type == "parallel":
        graph = construct_parallel(
            bottlenecks,
            many_vertices,
            many_to_one,
        )

    if args.type == "hop":
        graph = build_hop_graph(
            args.fraction,
            many_vertices,
            bottlenecks,
        )
        if args.no_overlap:
            delta_graph_del, delta_graph_ins, nu_graph = (
                build_disjunct_insert_edges(
                    args.k_value,
                    graph,
                )
            )
        else:
            delta_graph_del, delta_graph_ins, nu_graph = (
                select_delta_edges_hop_graph(
                    graph,
                    args.k_value,
                    bottlenecks,
                    many_vertices,
                )
            )

    if args.file:
        save_graph_to_file(
            graph,
            args.file,
        )
    if args.csv:
        save_graph_to_file(
            graph,
            args.csv,
            csv=True,
        )
    if args.delta_csv:
        save_graph_to_file(
            delta_graph_ins,
            args.delta_csv,
            csv=True,
            delta=True,
            nu=True,
            swap=1,
            no_overlap=args.no_overlap,
        )
        save_graph_to_file(
            delta_graph_del,
            args.delta_csv,
            csv=True,
            delta=True,
            swap=-1,
            append=True,
        )
        __replaceSingleQuote(args.delta_csv)
    if args.nu_csv:
        save_graph_to_file(
            nu_graph,
            args.nu_csv,
            csv=True,
        )
