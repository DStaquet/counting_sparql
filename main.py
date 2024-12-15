from benchmarker.benchmark import run_benchmark


if __name__ == "__main__":
    import os, sys
    import argparse
    from duckdb import DuckDBPyConnection, connect

    from build_data import setup_query_files, build_data

    hashseed = os.getenv("PYTHONHASHSEED")
    if not hashseed:
        os.environ["PYTHONHASHSEED"] = "0"
        os.execv(
            sys.executable, [sys.executable] + sys.argv
        )

    # Argument parser
    parser = argparse.ArgumentParser(
        description="Module to run SPARQL queries for benchmark with incremental view maintenance on SQL queries.",
        prog="main.py",
        epilog="Query files first need to be set up with build_data.py, can also be passed through this module as flags.",
    )
    parser.add_argument(
        "query", help="The SPARQL query to run"
    )
    parser.add_argument(
        "query_files",
        help="The directory where the query files are stored/need to be stored",
    )
    parser.add_argument(
        "-d",
        "--data",
        help="The base graph data file to use",
        required=True,
    )
    parser.add_argument(
        "-dl",
        "--delta",
        help="The delta graph data file to use",
        required=True,
    )
    parser.add_argument(
        "-nf",
        "--nu_file",
        help="The nu file to use",
        required=True,
    )
    parser.add_argument(
        "-db",
        "--database",
        dest="db",
        help="The database to connect to",
        default=":memory:",
    )
    parser.add_argument(
        "-s",
        "--setup",
        action="store_true",
        default=False,
        help="Construct the SQL queries before running the benchmark",
    )
    parser.add_argument(
        "-r",
        "--runs",
        type=int,
        default=10,
        help="The number of runs to do",
    )

    args = parser.parse_args()

    if args.setup:
        setup_query_files(args.query, args.query_files)

    # Connect to the database
    duckdb_conn = connect(args.db)

    """ # Build up the data
    build_data(
        args.query_files,
        args.query,
        duckdb_conn,
        args.data,
        delta_file=args.delta,
        nu_file=args.nu_file,
        csv=True,
    ) """

    run_benchmark(
        args.query,
        args.query_files,
        args.runs,
        duckdb_conn,
        args.db,
        args.data,
        args.nu_file,
    )
