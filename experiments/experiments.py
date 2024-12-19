from duckdb import DuckDBPyConnection
from rdflib.plugins.sparql import algebra, parser
from rdflib.plugins.sparql.parser import parseQuery
from rdflib.plugins.sparql.sparql import Query


def get_query_object(query: str) -> Query:
    query_tree = parseQuery(str(query))
    return algebra.translateQuery(query_tree)


def load_table_in_graph(
    table: str,
    duckdb_conn: DuckDBPyConnection,
) -> None:
    """Loads the table into the graph.

    Args:
        table (str): The given table.
        duckdb_conn (DuckDBPyConnection): Connection to the database.
    """
    # DROP THE TABLES BEFORE MAKING THEM ANEW
    duckdb_conn.execute(f"DROP TABLE IF EXISTS G;")

    # CREATE THE TABLES
    duckdb_conn.execute(
        f"CREATE TABLE G AS FROM '{table}';"
    )


def load_delta_table_in_graph(
    delta_table: str,
    duckdb_conn: DuckDBPyConnection,
    nu_table: str,
    nu_table_name: str = "nu_G",
) -> None:
    """Loads the delta table into the graph.

    Args:
        delta_table (str): The given delta table.
        duckdb_conn (DuckDBPyConnection): Connection to the database.
        nu_table (str): The given nu table.
    """
    # DROP THE TABLES BEFORE MAKING THEM ANEW
    duckdb_conn.execute(f"DROP TABLE IF EXISTS delta_G;")
    duckdb_conn.execute(
        f"DROP TABLE IF EXISTS {nu_table_name};"
    )

    # CREATE THE TABLES
    duckdb_conn.execute(
        f"CREATE TABLE {nu_table_name} AS FROM '{nu_table}';"
    )
    duckdb_conn.execute(
        f"CREATE TABLE delta_G AS FROM '{delta_table}';"
    )


if __name__ == "__main__":
    import argparse

    # from experiments import duckdb_conn
    import duckdb
    from build_data import (
        readQueryFile,
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
