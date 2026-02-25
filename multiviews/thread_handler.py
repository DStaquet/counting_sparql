"""
Module to handle the threads and related functions for the multiviews module.
"""

from argparse import Namespace
from datetime import date
from threading import Lock, Thread
from typing import Any, Iterable, Callable

from duckdb import DuckDBPyConnection  # pylint: disable=import-error
from benchmarker.benchmark import set_entire_query
from build_data import setup_query_files
from example_constructor.graph_constructor import (
    Graph as custom_Graph,
    build_hop_graph,
    select_delta_edges_hop_graph,
)
from example_constructor.graph_splitter import (
    split_graph_into_pods,
)
from multiviews.db_handler import sql_query
from multiviews.pod_handler import (
    handle_delta_pod_connection,
    handle_pod_connection,
    handle_pod_connection_we_are,
)


def _deltas_per_pod(
    split_g: list[custom_Graph],
    edges_to_delete: int,
    bottlenecks: int,
    many_vertices: int,
) -> list[tuple[custom_Graph, custom_Graph, custom_Graph]]:
    return_list: list[tuple[custom_Graph, custom_Graph, custom_Graph]] = []
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
    given_function: Callable[..., None],
    arguments: list[Iterable[Any]],
    passed_args: Namespace,
) -> None:
    # We will connect to three pods multithreadedly
    threads: list[Thread] = []
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
    split_graphs = split_graph_into_pods(og_graph, len(given_args.pods))
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
    query_output_dir = _setup_queries(given_args.query_file, given_args.query_dir)
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
        handle_delta_pod_connection,
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


def _setup_queries(query_file: str, query_dir: str) -> str:
    # Put ready the query files
    output_dir = setup_query_files(query_file, query_dir)
    print("Build files!")
    set_entire_query(query_file, query_dir)

    return output_dir


def we_are_poc_main(
    given_args: Namespace,
    triple_amount: int,
    hospital_amount: int,
    rating_interval: tuple[int, int],
    dates: tuple[date, date],
    duckdb_conn: DuckDBPyConnection,
    delta_amount: int,
    reification: bool = False,
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
    if not reification:
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
    else:
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
                    True,
                )
                for pod in given_args.pods
            ],
            given_args,
        )
    query_output_dir = _setup_queries(given_args.query_file, given_args.query_dir)
    # Execute the scratch query
    sql_query(
        query_output_dir,
        duckdb_conn,
        "scratch_query.sql",
        drop=True,
    )
    print("Run from scratch.")

    _thread_per_pod(
        handle_delta_pod_connection,
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
