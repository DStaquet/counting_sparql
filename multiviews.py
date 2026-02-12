"""
Experiments for connecting multiple solid pods to a DuckDB database and storing them as one view.
"""

from argparse import ArgumentParser, Namespace
from threading import Thread, Lock
import os
import sys
from os.path import join
from typing import Iterable, Any
from datetime import date
from time import strptime

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
from example_constructor.we_are_poc_constructor import (
    generate_random_ratings,
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


def _put_pod_data_in_database(
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
                f"INSERT INTO {table_name} (pod_id, s, p, o, k_count) VALUES "
                + f"('{pod_name}', '{triple[1]}', '{triple[2]}', '{triple[3]}', {ins_or_del});",
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
    pod_url: str,
    filename: str,
    data: custom_Graph | None = None,
    turtle_to_insert: str | None = None,
) -> None:
    if not turtle_to_insert and data:
        turtle_to_insert = data.graph_to_turtle(
            "http://example.org/node/",
            "http://example.org/edges/",
        )

    put(
        pod_url + filename,
        data=turtle_to_insert,
        headers={"Content-Type": "text/turtle"},
        timeout=10,
    )

    print(
        f"Put data for hospitals in pod {pod_url} in file {filename}."
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
    _put_data_in_pod(pod_url, delta_filenames[0], delta_del)
    # Insert the insertions
    _put_data_in_pod(pod_url, delta_filenames[1], delta_ins)

    # Insert the nu graph
    _put_data_in_pod(pod_url, nu_filename, nu_graph)


def _handle_delta_pod_connection(
    conn: DuckDBPyConnection,
    pod_url: str,
    filename: str,
    db_lock: Lock,
    table_names: tuple[str, str],
) -> None:
    # Get the delta data
    ins_data = __get_pod_data(
        join(pod_url, "delta_ins_" + filename)
    )
    del_data = __get_pod_data(
        join(pod_url, "delta_del_" + filename)
    )
    ins_triples = __parse_pod_data(ins_data)
    del_triples = __parse_pod_data(del_data)
    _put_pod_data_in_database(
        conn, pod_url, ins_triples, db_lock, table_names[0]
    )
    _put_pod_data_in_database(
        conn,
        pod_url,
        del_triples,
        db_lock,
        table_names[0],
        -1,
    )
    # Get the nu data
    nu_data = __get_pod_data(
        join(pod_url, "nu_" + filename)
    )
    nu_triples = __parse_pod_data(nu_data)
    _put_pod_data_in_database(
        conn, pod_url, nu_triples, db_lock, table_names[1]
    )


def handle_pod_connection(
    conn: DuckDBPyConnection,
    pod_url: str,
    filename: str,
    db_lock: Lock,
    graphs_and_deltas: tuple[
        custom_Graph,
        tuple[custom_Graph, custom_Graph, custom_Graph],
    ],
    table_name: str,
) -> None:
    """Handles the connection to a pod and stores its data in the DuckDB database.

    Args:
        conn (DuckDBPyConnection): The DuckDB connection object.
        pod_url (str): The URL of the pod to connect to.
    """
    data, deltas = graphs_and_deltas
    _put_data_in_pod(pod_url, filename, data)
    _put_delta_in_pod(
        deltas,
        pod_url,
        ("delta_ins_" + filename, "delta_del_" + filename),
        "nu_" + filename,
    )
    # Get the normal data
    pod_data = __get_pod_data(join(pod_url, filename))
    triples = __parse_pod_data(pod_data)
    _put_pod_data_in_database(
        conn, pod_url, triples, db_lock, table_name
    )
    print(f"Data from pod {pod_url} stored in database.")


def handle_pod_connection_we_are(
    pod_url: str,
    filename: str,
    triple_amount: int,
    hospital_amount: int,
    rating_interval: tuple[int, int],
    dates: tuple[date, date],
    duckdb_conn: DuckDBPyConnection,
    lock: Lock,
    table_name: str,
    delta_amount: int,
) -> None:
    """Handles the we are POC connection cases.

    Args:
        pod_url (str): URL to each pod.
        filename (str): Filename to store the data in.
        triple_amount (int): Amount of triples to generate.
        hospital_amount (int): Amount of possible hospitals.
        rating_interval (tuple[int, int]): Rating interval.
        dates (tuple[date, date]): Interval of dates to choose.
    """
    # Put the normal data.
    (
        turtle_to_insert,
        delete_delta,
        insert_delta,
        nu_to_insert,
    ) = generate_random_ratings(
        "http://example.org/we_are/",
        triple_amount,
        hospital_amount,
        rating_interval,
        dates,
        delta_amount,
    )

    _put_data_in_pod(
        pod_url, filename, turtle_to_insert=turtle_to_insert
    )
    pod_data = __get_pod_data(join(pod_url, filename))
    triples = __parse_pod_data(pod_data)
    _put_pod_data_in_database(
        duckdb_conn, pod_url, triples, lock, table_name
    )

    # Put down delta data
    _put_data_in_pod(
        pod_url,
        "delta_del_" + filename,
        turtle_to_insert=delete_delta,
    )
    _put_data_in_pod(
        pod_url,
        "delta_ins_" + filename,
        turtle_to_insert=insert_delta,
    )

    # Put down the nu graph
    _put_data_in_pod(
        pod_url,
        "nu_" + filename,
        turtle_to_insert=nu_to_insert,
    )


def sql_query(
    output_dir: str,
    aggregator_db: DuckDBPyConnection,
    query_to_execute: str,
    drop: bool = False,
) -> None:
    """Executes a given sql query in the given directory.

    Args:
        output_dir (str): Directory where the query is located.
        aggregator_db (DuckDBPyConnection): Connection to the database.
        query_to_execute (str): Query to execute.
        drop (bool, optional): Drops all tables if True. Defaults to False.
    """
    if drop:
        _drop_tables(output_dir, aggregator_db)
        print("Dropping the tables.")
    # Execute the from SQL queries
    with open(
        join(output_dir, query_to_execute),
        "r",
        encoding="utf-8",
    ) as handle:
        aggregator_db.execute(handle.read())


def _drop_tables(
    output_dir: str, aggregator_db: DuckDBPyConnection
) -> None:
    with open(
        join(output_dir, "drop_tables.sql"),
        encoding="utf-8",
    ) as drop_handle:
        aggregator_db.execute(drop_handle.read())
    with open(
        join(output_dir, "drop_delta_tables.sql"),
        encoding="utf-8",
    ) as drop_handle:
        aggregator_db.execute(drop_handle.read())


def _setup_queries(query_file: str, query_dir: str) -> str:
    # Put ready the query files
    output_dir = setup_query_files(query_file, query_dir)
    set_entire_query(query_file, query_dir)

    return output_dir


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


def _thread_per_pod(
    given_function,
    arguments: list[Iterable[Any]],
    passed_args: Namespace,
) -> None:
    # We will connect to three pods multithreadedly
    threads = []
    for i, _ in enumerate(passed_args.pods):
        thread = Thread(
            target=given_function,
            args=arguments[i],
        )
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()


def hops_main(
    given_args: Namespace,
    duckdb_conn: DuckDBPyConnection,
) -> None:
    """Main function for the hop scenario POC.

    Args:
        given_args (Namespace): Namespace with arguments.
    """
    og_graph = build_hop_graph(
        given_args.edges,
        given_args.vertices,
        given_args.bottlenecks,
    )
    split_graphs = split_graph_into_pods(
        og_graph, len(given_args.pods)
    )
    split_deltas = _deltas_per_pod(
        split_graphs,
        given_args.edges_to_delete,
        given_args.bottlenecks,
        given_args.edges,
    )
    # custom_graph = _read_ttl_data(args.data_file)

    # Put the data for the non IVM part ready
    lock = Lock()
    _thread_per_pod(
        handle_pod_connection,
        [
            (
                duckdb_conn,
                pod,
                given_args.filename,
                lock,
                (split_graphs[i], split_deltas[i]),
                "G",
            )
            for i, pod in enumerate(given_args.pods)
        ],
        given_args,
    )
    print("Finished putting all the data in the database.")
    query_output_dir = _setup_queries(
        given_args.query_file, given_args.query_dir
    )
    # Execute the scratch query
    sql_query(
        query_output_dir,
        duckdb_conn,
        "scratch_query.sql",
        drop=True,
    )
    print("Run from scratch.")

    # Get the delta values
    _thread_per_pod(
        _handle_delta_pod_connection,
        [
            (
                duckdb_conn,
                pod,
                given_args.filename,
                lock,
                ("delta_G", "nu_G"),
            )
            for pod in given_args.pods
        ],
        given_args,
    )
    # Execute the IVM query
    sql_query(
        query_output_dir,
        duckdb_conn,
        "incremental_query.sql",
    )
    print("Finished the incremental queries.")


def we_are_poc_main(
    given_args: Namespace,
    triple_amount: int,
    hospital_amount: int,
    rating_interval: tuple[int, int],
    dates: tuple[date, date],
    duckdb_conn: DuckDBPyConnection,
    delta_amount: int,
) -> None:
    """Main function for the We Are POC.

    Args:
        args (Namespace): Given arguments.
        triple_amount (int): Amount of triples.
        hospital_amount (int): Amount of hospitals to choose.
        rating_interval (tuple[int, int]): Rating interval.
        dates (tuple[date, date]): Dates to choose between.
    """
    # Generate and put all the different data in the pods.
    lock = Lock()
    _thread_per_pod(
        handle_pod_connection_we_are,
        [
            (
                pod,
                given_args.filename,
                triple_amount,
                hospital_amount,
                rating_interval,
                dates,
                duckdb_conn,
                lock,
                "G",
                delta_amount,
            )
            for pod in given_args.pods
        ],
        given_args,
    )
    query_output_dir = _setup_queries(
        given_args.query_file, given_args.query_dir
    )
    # Execute the scratch query
    sql_query(
        query_output_dir,
        duckdb_conn,
        "scratch_query.sql",
        drop=True,
    )
    print("Run from scratch.")

    _thread_per_pod(
        _handle_delta_pod_connection,
        [
            (
                duckdb_conn,
                pod,
                given_args.filename,
                lock,
                ("delta_G", "nu_G"),
            )
            for pod in given_args.pods
        ],
        given_args,
    )
    # Execute the IVM query
    sql_query(
        query_output_dir,
        duckdb_conn,
        "incremental_query.sql",
    )
    print("Finished the incremental queries.")


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
        help="The amount of edges to delete or insert/In the We Are POC, the delta amount.",
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
    arg_parser.add_argument(
        "-t",
        "--type",
        help="Type of multiview to do.",
        choices=["hop", "we_are"],
        required=True,
    )
    arg_parser.add_argument(
        "-tr",
        "--triple_amounts",
        help="Amount of triples to construct for the we are POC.",
        default=10,
        type=int,
    )
    arg_parser.add_argument(
        "-ho",
        "--hospital_amount",
        help="Amount of possible hospitals.",
        default=3,
        type=int,
    )
    arg_parser.add_argument(
        "-ri",
        "--rating_interval",
        help="Interval to put the ratings between.",
        default=[1, 10],
        nargs=2,
        type=int,
    )
    arg_parser.add_argument(
        "-di",
        "--date_interval",
        nargs=2,
        help="Interval of dates to choose between in format: %Y-%m-%d",
        default=["2025-12-01", "2026-01-31"],
    )
    args = arg_parser.parse_args()

    # Connect to the DuckDB database
    duckdb_connection = connect_main_db(args.database)
    __create_multi_pod_view(
        duckdb_connection, "G", "delta_G", "nu_G"
    )

    if args.type == "hop":
        hops_main(args, duckdb_connection)
    elif args.type == "we_are":
        we_are_poc_main(
            args,
            args.triple_amounts,
            args.hospital_amount,
            (
                args.rating_interval[0],
                args.rating_interval[1],
            ),
            (
                date(
                    *strptime(
                        args.date_interval[0], "%Y-%m-%d"
                    )[0:3]
                ),
                date(
                    *strptime(
                        args.date_interval[1], "%Y-%m-%d"
                    )[0:3]
                ),
            ),
            duckdb_connection,
            args.edges_to_delete,
        )

    """ with open(
        args.data_file, encoding="utf-8"
    ) as data_handle:
        _put_data_in_pod(
            custom_graph,
            args.pods[0],
            args.filename,
            data_handle.read(),
        ) """
