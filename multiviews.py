"""
Experiments for connecting multiple solid pods to a DuckDB database and storing them as one view.
"""

from argparse import ArgumentParser
from threading import Thread, Lock
import os
import sys
from os.path import join

from requests import get, RequestException, put
from duckdb import DuckDBPyConnection, connect
from rdflib import Graph

from example_constructor.graph_constructor import (
    build_hop_graph,
    Graph as custom_Graph,
    select_delta_edges_hop_graph,
)
from example_constructor.graph_splitter import (
    split_graph_into_pods,
)
from build_data import setup_query_files
from benchmarker.benchmark import set_entire_query


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


def _create_table(
    table_name: str, conn: DuckDBPyConnection
) -> None:
    conn.execute(
        f"CREATE OR REPLACE TABLE {table_name}"
        + " (pod_id STRING, s STRING, p STRING, o STRING, k_count INT);"
    )


def __create_multi_pod_view(
    conn: DuckDBPyConnection,
    view_name: str,
    delta_view_name: str,
    nu_view_name: str,
) -> None:
    """Creates a view in the DuckDB database to combine data from multiple pods."""
    # Create mutex lock for thread safety if needed
    _create_table(view_name, conn)
    # Create the delta
    _create_table(delta_view_name, conn)
    # Create the nu_table
    _create_table(nu_view_name, conn)


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
    table_name: str,
    ins_or_del: int = 1,
):
    """Inserts pod data into the multi-pod view in the DuckDB database."""
    # Create mutex lock for thread safety if needed
    with db_lock:
        for triple in triples:
            conn.execute(
                f"INSERT INTO {table_name} (pod_id, s, p, o, k_count)"
                + f" VALUES ('{pod_name}', '{triple[1]}', '{triple[2]}', '{triple[3]}', {ins_or_del});",
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
        print(f"Data fetched from pod {pod_url}.")
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

    # print(turtle_to_insert)


def _put_delta_in_pod(
    deltas: tuple[custom_Graph, custom_Graph, custom_Graph],
    pod_url: str,
    delta_filenames: tuple[str, str],
    nu_filename: str,
) -> None:
    delta_del, delta_ins, nu_graph = deltas

    # Insert the deletions
    _put_data_in_pod(delta_del, pod_url, delta_filenames[0])
    # Insert the insertions
    _put_data_in_pod(delta_ins, pod_url, delta_filenames[1])

    # Insert the nu graph
    _put_data_in_pod(nu_graph, pod_url, nu_filename)


def handle_pod_connection(
    conn: DuckDBPyConnection,
    pod_url: str,
    filename: str,
    db_lock: Lock,
    graphs_and_deltas: tuple[
        custom_Graph,
        tuple[custom_Graph, custom_Graph, custom_Graph],
    ],
    table_names: tuple[str, str, str],
) -> None:
    """Handles the connection to a pod and stores its data in the DuckDB database.

    Args:
        conn (DuckDBPyConnection): The DuckDB connection object.
        pod_url (str): The URL of the pod to connect to.
    """
    data, deltas = graphs_and_deltas
    _put_data_in_pod(data, pod_url, filename)
    _put_delta_in_pod(
        deltas,
        pod_url,
        ("delta_ins_" + filename, "delta_del_" + filename),
        "nu_" + filename,
    )
    # Get the normal data
    pod_data = __get_pod_data(join(pod_url, filename))
    triples = __parse_pod_data(pod_data)
    __put_pod_data(
        conn, pod_url, triples, db_lock, table_names[0]
    )
    # Get the delta data
    ins_data = __get_pod_data(
        join(pod_url, "delta_ins_" + filename)
    )
    del_data = __get_pod_data(
        join(pod_url, "delta_del_" + filename)
    )
    ins_triples = __parse_pod_data(ins_data)
    del_triples = __parse_pod_data(del_data)
    __put_pod_data(
        conn, pod_url, ins_triples, db_lock, table_names[1]
    )
    __put_pod_data(
        conn,
        pod_url,
        del_triples,
        db_lock,
        table_names[1],
        -1,
    )
    # Get the nu data
    nu_data = __get_pod_data(
        join(pod_url, "nu_" + filename)
    )
    nu_triples = __parse_pod_data(nu_data)
    __put_pod_data(
        conn, pod_url, nu_triples, db_lock, table_names[2]
    )
    print(f"Data from pod {pod_url} stored in database.")


def _sql_query(
    query_output_dir: str,
    aggregator_db: DuckDBPyConnection,
    query_to_execute: str,
) -> None:
    # Execute the from SQL queries
    with open(
        join(query_output_dir, query_to_execute),
        "r",
        encoding="utf-8",
    ) as handle:
        aggregator_db.execute(handle.read())


def _drop_tables(
    query_output_dir: str, aggregator_db: DuckDBPyConnection
) -> None:
    with open(
        join(query_output_dir, "drop_tables.sql"),
        encoding="utf-8",
    ) as drop_handle:
        aggregator_db.execute(drop_handle.read())
    with open(
        join(query_output_dir, "drop_delta_tables.sql"),
        encoding="utf-8",
    ) as drop_handle:
        aggregator_db.execute(drop_handle.read())


def ivm(
    query_file: str,
    query_dir: str,
    aggregator_db: DuckDBPyConnection,
) -> None:

    # Put ready the query files
    query_output_dir = setup_query_files(
        query_file, query_dir
    )
    set_entire_query(query_file, query_dir)

    _drop_tables(query_output_dir, aggregator_db)
    # Execute the scratch query
    _sql_query(
        query_output_dir, aggregator_db, "scratch_query.sql"
    )
    # Execute the IVM query
    _sql_query(
        query_output_dir,
        aggregator_db,
        "incremental_query.sql",
    )


def _deltas_per_pod(
    split_g: list[custom_Graph],
    edges_to_delete: int,
    bottlenecks: int,
    many_vertices: int,
) -> list[tuple[custom_Graph, custom_Graph, custom_Graph]]:
    return_list: list[
        tuple[custom_Graph, custom_Graph, custom_Graph]
    ] = []
    for _, graph in enumerate(split_g):
        current = select_delta_edges_hop_graph(
            graph,
            edges_to_delete,
            bottlenecks,
            many_vertices,
        )
        return_list.append(current)
    return return_list


if __name__ == "__main__":
    hashseed = os.getenv("PYTHONHASHSEED")
    if not hashseed:
        os.environ["PYTHONHASHSEED"] = "0"
        os.execv(
            sys.executable, [sys.executable] + sys.argv
        )
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
        help="The fraction for the edges to build between bottlenecks",
        default=10,
        type=int,
    )
    arg_parser.add_argument(
        "-b",
        "--bottlenecks",
        help="The amount of bottlenecks",
        default=4,
        type=int,
    )
    arg_parser.add_argument(
        "-v",
        "--vertices",
        help="The amount of vertices per bottleneck",
        default=10,
        type=int,
    )
    arg_parser.add_argument(
        "-ed",
        "--edges_to_delete",
        help="The amount of edges to delete",
        default=1,
        type=int,
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
    split_deltas = _deltas_per_pod(
        split_graphs,
        args.edges_to_delete,
        args.bottlenecks,
        args.edges,
    )
    """ custom_graph = _read_ttl_data(args.data_file) """

    # Connect to the DuckDB database
    duckdb_connection = connect_main_db(args.database)
    __create_multi_pod_view(
        duckdb_connection, "G", "delta_G", "nu_G"
    )

    # We will connect to three pods multithreadedly
    threads = []
    lock = Lock()
    hop_filename = args.filename
    multiview_table_names = ("G", "delta_G", "nu_G")
    for i, pod in enumerate(args.pods):
        thread = Thread(
            target=handle_pod_connection,
            args=(
                duckdb_connection,
                pod,
                hop_filename,
                lock,
                (split_graphs[i], split_deltas[i]),
                multiview_table_names,
            ),
        )
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    ivm(args.query_file, args.query_dir, duckdb_connection)

    """ with open(
        args.data_file, encoding="utf-8"
    ) as data_handle:
        _put_data_in_pod(
            custom_graph,
            args.pods[0],
            args.filename,
            data_handle.read(),
        ) """
