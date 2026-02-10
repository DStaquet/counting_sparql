"""
Experiments for connecting multiple solid pods to a DuckDB database and storing them as one view.
"""

from argparse import ArgumentParser
from threading import Thread, Lock

from requests import get, RequestException, put
from duckdb import DuckDBPyConnection, connect
from rdflib import Graph

from example_constructor.graph_constructor import (
    build_hop_graph,
    Graph as custom_Graph,
)
from example_constructor.graph_splitter import (
    split_graph_into_pods,
)


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


def connect_main_db(db_path: str) -> DuckDBPyConnection:
    """Connects to a DuckDB database at the specified path.

    Args:
        db_path (str): The path to the DuckDB database file.

    Returns:
        DuckDBPyConnection: A connection object to the DuckDB database.
    """
    try:
        conn = connect(database=db_path)
    except Exception as e:
        raise ConnectionError(
            f"Failed to connect to DuckDB database at {db_path}: {e}"
        ) from e
    return conn


def __create_multi_pod_view(
    conn: DuckDBPyConnection,
    view_name: str,
) -> None:
    """Creates a view in the DuckDB database to combine data from multiple pods."""
    # Create mutex lock for thread safety if needed
    conn.execute(
        f"CREATE OR REPLACE TABLE {view_name}"
        + " (pod_id STRING,subject STRING, predicate STRING, object STRING);"
    )


def __parse_pod_data(
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


def __put_pod_data(
    conn: DuckDBPyConnection,
    pod_name: str,
    triples: list[tuple[str, str, str, str]],
    db_lock: Lock,
):
    """Inserts pod data into the multi-pod view in the DuckDB database."""
    # Create mutex lock for thread safety if needed
    with db_lock:
        for triple in triples:
            conn.execute(
                "INSERT INTO multi_pod_view (pod_id, subject, predicate, object)"
                + f" VALUES ('{pod_name}', '{triple[1]}', '{triple[2]}', '{triple[3]}');",
            )


def __get_pod_data(pod_url: str) -> str:
    """Fetches data from the specified pod URL.

    Args:
        pod_url (str): The URL of the pod to fetch data from.

    Returns:
        str: The text content retrieved from the pod.
    """
    try:
        response = get(pod_url, timeout=10)
    except RequestException:
        return f"Error fetching data from pod {pod_url}"
    finally:
        print(
            f"Data fetched from pod {pod_url}: {response.text}"
        )
    return response.text


def _put_data_in_pod(
    data: custom_Graph,
    pod_url: str,
    filename: str,
    turtle_to_insert: str | None = None,
) -> None:
    if not turtle_to_insert:
        turtle_to_insert = data.graph_to_turtle(
            "http://example.org/node",
            "http://example.org/edges",
        )

    put(
        pod_url + filename,
        data=turtle_to_insert,
        headers={"Content-Type": "text/turtle"},
        timeout=10,
    )

    print(turtle_to_insert)


def handle_pod_connection(
    conn: DuckDBPyConnection,
    pod_url: str,
    filename: str,
    db_lock: Lock,
    data: custom_Graph,
):
    """Handles the connection to a pod and stores its data in the DuckDB database.

    Args:
        conn (DuckDBPyConnection): The DuckDB connection object.
        pod_url (str): The URL of the pod to connect to.
    """
    pod_data = __get_pod_data(pod_url)
    triples = __parse_pod_data(pod_data)
    _put_data_in_pod(data, pod_url, filename)
    __put_pod_data(conn, pod_url, triples, db_lock)
    print(f"Data from pod {pod_url} stored in database.")


def ivm(query_file: str, query_dir: str) -> None:
    from build_data import setup_query_files

    # Put ready the query files
    setup_query_files(query_file, query_dir)


if __name__ == "__main__":
    arg_parser = ArgumentParser(
        description="Connect to DuckDB database"
    )
    arg_parser.add_argument(
        "-db",
        "--database",
        help="The DuckDB database file to connect to",
        default=":memory:",
    )
    arg_parser.add_argument(
        "-p",
        "--pods",
        nargs="+",
        help="List of pod URLs to connect to",
        required=True,
    )
    arg_parser.add_argument(
        "-f",
        "--filename",
        help="Filename to store the random data in.",
        default="hops.ttl",
    )
    arg_parser.add_argument(
        "-e",
        "--edges",
        help="The edges to build between bottlenecks",
        default=10,
    )
    arg_parser.add_argument(
        "-b",
        "--bottlenecks",
        help="The amount of bottlenecks",
        default=4,
    )
    arg_parser.add_argument(
        "-v",
        "--vertices",
        help="The amount of vertices per bottleneck",
        default=10,
    )
    arg_parser.add_argument(
        "-df",
        "--data_file",
        help="The data file to pull data from.",
    )
    arg_parser.add_argument(
        "-qd",
        "--query_dir",
        help="The query directory to store the ivm files.",
        required=True,
    )
    arg_parser.add_argument(
        "-q",
        "--query_file",
        help="The query file to run on the pods",
        required=True,
    )
    args = arg_parser.parse_args()

    og_graph = build_hop_graph(
        args.edges, args.vertices, args.bottlenecks
    )
    split_graphs = split_graph_into_pods(
        og_graph, len(args.pods)
    )
    """ custom_graph = _read_ttl_data(args.data_file) """

    # Connect to the DuckDB database
    duckdb_connection = connect_main_db(args.database)
    __create_multi_pod_view(
        duckdb_connection, "multi_pod_view"
    )

    # We will connect to three pods multithreadedly
    threads = []
    lock = Lock()
    hop_filename = args.filename
    for i, pod in enumerate(args.pods):
        thread = Thread(
            target=handle_pod_connection,
            args=(
                duckdb_connection,
                pod,
                hop_filename,
                lock,
                split_graphs[i],
            ),
        )
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    ivm(args.query_file, args.query_dir)

    """ with open(
        args.data_file, encoding="utf-8"
    ) as data_handle:
        _put_data_in_pod(
            custom_graph,
            args.pods[0],
            args.filename,
            data_handle.read(),
        ) """
