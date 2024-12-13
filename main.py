if __name__ == "__main__":
    import os, sys
    import argparse
    from duckdb import DuckDBPyConnection, connect

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
        "-db",
        "--database",
        dest="db",
        help="The database to connect to",
    )
    parser.add_argument(
        "-s",
        "--setup",
        action="store_true",
        default=False,
        help="Construct the SQL queries before running the benchmark",
    )

    args = parser.parse_args()
