"""Tests a quick aggregation query with SUM in the projection."""

import argparse
import os
import sys

from time import time

from duckdb import connect, DuckDBPyConnection

from experiments.time_operators import timing_per_operator
from build_data import (
    load_delta_table_in_graph,
    load_table_in_graph,
    setup_query_files,
    readQueryFile,
    get_query_object,
)
from setup_queries import get_query_output_dir


def prep_aggregation_query(
    duckdb_conn: DuckDBPyConnection,
    args_namespace: argparse.Namespace,
) -> None:
    """Prepares and runs an aggregation query."""

    # Setup query files
    setup_query_files(
        args_namespace.query_file, args_namespace.query_dir
    )

    q_query_object = get_query_object(
        readQueryFile(args_namespace.query_file)
    )
    # algebra.pprintAlgebra(q_query_object)

    # Output directory
    query_output_dir: str = get_query_output_dir(
        args_namespace.query_dir, q_query_object
    )

    load_table_in_graph(
        args_namespace.data_file,
        duckdb_conn,
    )
    load_delta_table_in_graph(
        args_namespace.delta_file,
        duckdb_conn,
        args_namespace.nu_file,
    )

    duckdb_conn.execute(
        readQueryFile(
            os.path.join(
                query_output_dir, "drop_tables.sql"
            )
        )
    )
    duckdb_conn.execute(
        readQueryFile(
            os.path.join(
                query_output_dir,
                "drop_delta_tables.sql",
            )
        )
    )

    timing_per_operator(
        q_query_object.algebra.p,
        query_output_dir,
        duckdb_conn,
    )

    timing_per_operator(
        q_query_object.algebra.p,
        query_output_dir,
        duckdb_conn,
        increm=True,
    )


if __name__ == "__main__":
    hashseed = os.getenv("PYTHONHASHSEED")
    if not hashseed:
        os.environ["PYTHONHASHSEED"] = "0"
        os.execv(
            sys.executable, [sys.executable] + sys.argv
        )

    parser = argparse.ArgumentParser(
        description="Time aggregation query."
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
        "--runs",
        "-r",
        type=int,
        default=3,
        help="The number of runs to average over.",
    )
    parser.add_argument(
        "--db",
        type=str,
        default=":memory:",
        help="The database to connect to.",
    )
    parser.add_argument(
        "aggregation_sql_file",
        type=str,
        help="The SQL file that contains the aggregation operator.",
    )
    parser.add_argument(
        "aggregation_delta_sql_file",
        type=str,
        help="The SQL file that contains the aggregation operator for the delta.",
    )
    parser.add_argument(
        "aggregation_nu_sql_file",
        type=str,
        help="The SQL file that contains the aggregation operator for the nu.",
    )

    args = parser.parse_args()

    conn: DuckDBPyConnection = connect(
        database=args.db, read_only=False
    )

    with open(
        args.aggregation_sql_file, "r", encoding="utf-8"
    ) as f:
        aggregation_sql = f.read()
    with open(
        args.aggregation_delta_sql_file,
        "r",
        encoding="utf-8",
    ) as f:
        aggregation_delta_sql = f.read()
    with open(
        args.aggregation_nu_sql_file,
        "r",
        encoding="utf-8",
    ) as f:
        aggregation_nu_sql = f.read()

    avg_increm_time: float = 0.0
    avg_scratch_time: float = 0.0

    for run in range(args.runs):
        print(f"Run {run+1}/{args.runs}")

        prep_aggregation_query(
            conn,
            args,
        )

        print("Running aggregation incrementally...")
        conn.execute("DROP TABLE IF EXISTS Agg;")
        conn.execute("DROP TABLE IF EXISTS nu_Agg_increm;")
        conn.execute(aggregation_sql)
        conn.execute("DROP TABLE IF EXISTS delta_Agg;")
        conn.execute("DROP TABLE IF EXISTS temp_Agg;")
        start_time = time()
        conn.execute(aggregation_delta_sql)
        end_time = time()
        print(
            f"Delta aggregation completed in {(end_time - start_time)*1000} milliseconds."
        )
        avg_increm_time += (end_time - start_time) * 1000
        print(
            "Average incremental time so far: ",
            avg_increm_time / (run + 1),
        )

        conn.execute("DROP TABLE IF EXISTS nu_Agg;")
        start_time = time()
        conn.execute(aggregation_nu_sql)
        end_time = time()
        print(
            f"Scratch aggregation completed in {(end_time - start_time)*1000} milliseconds."
        )
        avg_scratch_time += (end_time - start_time) * 1000
        print(
            "Average scratch time so far: ",
            avg_scratch_time / (run + 1),
        )
        print()

    avg_increm_time /= args.runs
    avg_scratch_time /= args.runs
    print(
        f"Average incremental aggregation time: {avg_increm_time} milliseconds."
    )
    print(
        f"Average scratch aggregation time: {avg_scratch_time} milliseconds."
    )

    print("Done.")
