"""
Experiments for connecting multiple solid pods to a DuckDB database and storing them as one view.
"""

from argparse import ArgumentParser
import os
import sys
from datetime import date
from time import strptime


from multiviews.db_handler import connect_main_db
from multiviews.db_handler import create_multi_pod_view
from multiviews.thread_handler import hops_main
from multiviews.thread_handler import we_are_poc_main


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
    args = arg_parser.parse_args()

    # Connect to the DuckDB database
    duckdb_connection = connect_main_db(args.database)
    if args.type == "reif":
        create_multi_pod_view(duckdb_connection, "G", "delta_G", "nu_G", True)
    else:
        create_multi_pod_view(duckdb_connection, "G", "delta_G", "nu_G")

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
                date(*strptime(args.date_interval[0], "%%Y-%%m-%d")[0:3]),
                date(*strptime(args.date_interval[1], "%%Y-%%m-%d")[0:3]),
            ),
            duckdb_connection,
            args.edges_to_delete,
        )
    elif args.type == "reif":
        we_are_poc_main(
            args,
            args.triple_amounts,
            args.hospital_amount,
            (
                args.rating_interval[0],
                args.rating_interval[1],
            ),
            (
                date(*strptime(args.date_interval[0], "%%Y-%%m-%d")[0:3]),
                date(*strptime(args.date_interval[1], "%%Y-%%m-%d")[0:3]),
            ),
            duckdb_connection,
            args.edges_to_delete,
            reification=True,
        )
