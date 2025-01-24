from experiments.time_operators import timing_per_operator

if __name__ == "__main__":
    import argparse
    import os, sys
    from build_data import (
        readQueryFile,
        get_query_object,
        setup_query_files,
        load_table_in_graph,
        load_delta_table_in_graph,
    )
    from setup_queries import get_query_output_dir

    from duckdb import connect, DuckDBPyConnection
    import pprint

    hashseed = os.getenv("PYTHONHASHSEED")
    if not hashseed:
        os.environ["PYTHONHASHSEED"] = "0"
        os.execv(
            sys.executable, [sys.executable] + sys.argv
        )

    parser = argparse.ArgumentParser(
        description="Time operations."
    )
    parser.add_argument(
        "query_file",
        type=str,
        help="The query file to run.",
    )
    parser.add_argument(
        "query_dir",
        type=str,
        help="The directory where the SQL queries are stored.",
    )
    parser.add_argument(
        "data_file",
        type=str,
        help="The base graph data file to use.",
    )
    parser.add_argument(
        "delta_file",
        type=str,
        help="The delta graph data file to use.",
    )
    parser.add_argument(
        "nu_file",
        type=str,
        help="The nu file to use.",
    )
    parser.add_argument(
        "-db",
        type=str,
        help="The database to connect to.",
        default=":memory:",
    )

    args = parser.parse_args()

    # Setup query files
    setup_query_files(args.query_file, args.query_dir)

    q_query_object = get_query_object(
        readQueryFile(args.query_file)
    )
    # algebra.pprintAlgebra(q_query_object)

    # Output directory
    query_output_dir: str = get_query_output_dir(
        args.query_dir, q_query_object
    )

    duckdb_conn: DuckDBPyConnection = connect(args.db)

    load_table_in_graph(
        args.data_file,
        duckdb_conn,
    )
    load_delta_table_in_graph(
        args.delta_file,
        duckdb_conn,
        args.nu_file,
    )

    timings = timing_per_operator(
        q_query_object.algebra.p,
        query_output_dir,
        duckdb_conn,
    )

    pprint.pprint(timings)
