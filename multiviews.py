"""
Experiments for connecting multiple solid pods to a DuckDB database and storing them as one view.
"""

from argparse import ArgumentParser, ArgumentTypeError, Namespace
import os
import sys
from datetime import date
from time import strptime
from typing import Callable
from duckdb import DuckDBPyConnection


from multiviews.db_handler import connect_main_db
from multiviews.db_handler import create_multi_pod_view
from multiviews.db_handler import drop_aggregates_sum_count
from multiviews.thread_handler import hops_main
from multiviews.thread_handler import we_are_poc_main
from multiviews.pod_handler import construct_pod_urls


def sample_range(mini: int, maxi: int) -> Callable[[int], int]:
    """Return a function that validates an integer is within [mini, maxi]."""

    def range_checker(value: int):
        ivalue = int(value)
        if not (mini <= ivalue <= maxi):
            raise ArgumentTypeError(f"Value must be between {mini} and {maxi}")
        return ivalue

    return range_checker


def _run_queries(
    args_space: Namespace, duckdb_conn: DuckDBPyConnection, pods_list: list[str]
) -> list[float]:
    """Run the queries on the database."""
    scratch_time: float | None = None
    ivm_time: float | None = None

    if args_space.type == "hop":
        hops_main(args_space, duckdb_conn, pods_list)
    elif args_space.type == "we_are":
        scratch_time, ivm_time = we_are_poc_main(
            args_space,
            args_space.triple_amounts,
            args_space.hospital_amount,
            (
                args_space.rating_interval[0],
                args_space.rating_interval[1],
            ),
            (
                date(*strptime(args_space.date_interval[0], "%Y-%m-%d")[0:3]),
                date(*strptime(args_space.date_interval[1], "%Y-%m-%d")[0:3]),
            ),
            duckdb_conn,
            args_space.edges_to_delete,
            pods_list,
            verbose=args_space.verbose,
        )
    elif args_space.type == "reif":
        scratch_time, ivm_time = we_are_poc_main(
            args_space,
            args_space.triple_amounts,
            args_space.hospital_amount,
            (
                args_space.rating_interval[0],
                args_space.rating_interval[1],
            ),
            (
                date(*strptime(args_space.date_interval[0], "%%Y-%%m-%d")[0:3]),
                date(*strptime(args_space.date_interval[1], "%%Y-%%m-%d")[0:3]),
            ),
            duckdb_conn,
            args_space.edges_to_delete,
            pods_list,
            verbose=args_space.verbose,
            reification=True,
        )

    if scratch_time is None or ivm_time is None:
        raise RuntimeError("Scratch time or IVM time was not set.")

    return [scratch_time, ivm_time]


if __name__ == "__main__":
    hashseed = os.getenv("PYTHONHASHSEED")
    if not hashseed:
        os.environ["PYTHONHASHSEED"] = "0"
        os.execv(sys.executable, [sys.executable] + sys.argv)

    arg_parser = ArgumentParser(description="Connect to DuckDB database")
    arg_parser.add_argument(
        "-db",
        "--database",
        help="The DuckDB database file to connect to",
        default=":memory:",
    )
    arg_parser.add_argument(
        "-p",
        "--ports",
        nargs=2,
        type=int,
        metavar=("MIN_PORT", "MAX_PORT"),
        help="Interval of pod URLs ports to connect to",
        required=True,
    )
    arg_parser.add_argument(
        "-pu",
        "--pod_url",
        help="The URL of the pod to connect to",
        default="http://localhost",
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
        choices=["hop", "we_are", "reif"],
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
        help="Interval of dates to choose between in format: YY-MM-DD.",
        default=["2025-12-01", "2026-01-31"],
    )
    arg_parser.add_argument(
        "-r",
        "--runs",
        help="The amount of runs to do.",
        default=10,
        type=int,
    )
    arg_parser.add_argument(
        "-vb",
        "--verbose",
        help="Prints out more information.",
        action="store_true",
    )
    args = arg_parser.parse_args()

    # Connect to the DuckDB database
    duckdb_connection = connect_main_db(args.database)
    if args.type == "reif":
        create_multi_pod_view(duckdb_connection, "G", "delta_G", "nu_G", True)
    else:
        create_multi_pod_view(duckdb_connection, "G", "delta_G", "nu_G")

    pods = construct_pod_urls(args.pod_url, args.ports)

    total_scratch_time = 0.0
    total_ivm_time = 0.0

    for run in range(args.runs):
        print(f"Run {run + 1}/{args.runs}")

        drop_aggregates_sum_count("AggregateJoin_824796569515826316", duckdb_connection)

        scratch_t, ivm_t = _run_queries(args, duckdb_connection, pods)
        print(f"Scratch time: {scratch_t:.4f} seconds")
        print(f"IVM time: {ivm_t:.4f} seconds")

        total_scratch_time += scratch_t
        total_ivm_time += ivm_t

    avg_scratch_time = total_scratch_time / args.runs
    avg_ivm_time = total_ivm_time / args.runs

    print(f"Average Scratch time over {args.runs} runs: {avg_scratch_time:.4f} seconds")
    print(f"Average IVM time over {args.runs} runs: {avg_ivm_time:.4f} seconds")
