if __name__ == "__main__":
    import argparse

    # from experiments import duckdb_conn
    import duckdb
    from incremental_query_parser import (
        readQueryFile,
        get_query_object,
    )
    from setup_queries import get_query_output_dir
    from experiments.delta_bgp_join import (
        go_through_algebra_for_test,
    )
    import os, sys
    from plots import build_compare_plot

    hashseed = os.getenv("PYTHONHASHSEED")
    if not hashseed:
        os.environ["PYTHONHASHSEED"] = "0"
        os.execv(
            sys.executable, [sys.executable] + sys.argv
        )

    duckdb_conn = duckdb.connect(
        "./database/experiments_delta_bgp.db"
    )

    # Argument parser
    parser = argparse.ArgumentParser(
        description="build up the delta rules utilizing a join."
    )
    parser.add_argument(
        "query_str",
        type=str,
        help="the query file.",
    )
    parser.add_argument(
        "query_dir",
        type=str,
        help="the directory where the SQL queries are stored.",
    )
    parser.add_argument(
        "-r",
        "--runs",
        type=int,
        default=10,
        help="The number of runs to do.",
        dest="runs",
    )
    parser.add_argument(
        "-t",
        "--table",
        required=True,
        type=str,
        nargs="?",
        help="The table to store in G.",
    )
    parser.add_argument(
        "-d",
        "--delta_table",
        required=True,
        type=str,
        nargs="*",
        help="The delta tables to store in delta_G.",
    )
    parser.add_argument(
        "-n",
        "--nu",
        required=True,
        type=str,
        nargs="*",
        help="The nu tables.",
    )
    args = parser.parse_args()

    # Read the query file
    query_str = readQueryFile(args.query_str)
    # Make algebra
    query_obj = get_query_object(query_str)
    # Output directory
    query_output_dir = get_query_output_dir(
        args.query_dir, query_obj
    )

    go_through_algebra_for_test(
        query_obj.algebra,
        query_output_dir,
        args.runs,
        args.table,
        args.delta_table,
        args.nu,
        duckdb_conn,
    )
