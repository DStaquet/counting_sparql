from duckdb import DuckDBPyConnection

from rdflib.plugins.sparql.parserutils import CompValue

import build_data


def run_queries(
    part: CompValue,
    output_dir: str,
    part_name: str,
    duckdb_conn: DuckDBPyConnection,
    incremental: bool = False,
) -> None:
    """Execute the BGP queries recursively.

    Args:
        part (CompValue): Current part of the query
        output_dir (str): Directory to write the output to
        duckdb_conn (DuckDBPyConnection): Connection to the database
    """
    from eval_incremental.eval_incremental import (
        get_query_string,
    )

    if part.name == part_name:
        query_file: str = get_query_string(part, output_dir)
        print(query_file)
        duckdb_conn.sql(query_file)
        if incremental:
            query_file_delta: str = get_query_string(
                part, output_dir, "delta_"
            )
            duckdb_conn.sql(query_file_delta)
            query_file_nu: str = get_query_string(
                part, output_dir, "nu_"
            )
            duckdb_conn.sql(query_file_nu)
    if "p" in part:
        run_queries(
            part.p, output_dir, part_name, duckdb_conn
        )
    elif "p1" in part and "p2" in part:
        run_queries(
            part.p1, output_dir, part_name, duckdb_conn
        )
        run_queries(
            part.p2, output_dir, part_name, duckdb_conn
        )


def run_bgps(
    query_str: str,
    output_dir: str,
    duckdb_conn: DuckDBPyConnection,
    incremental: bool = False,
) -> None:
    """Run the BGP queries.

    Args:
        query_str (str): The query string to construct the BGP queries
        output_dir (str): The output directory to write the BGP queries to
        duckdb_con (DuckDBPyConnection): Connection to the database.
    """
    import incremental_query_parser as iqp
    from setup_queries import get_query_output_dir

    q_query_object: iqp.Query = build_data.get_query_object(
        build_data.readQueryFile(query_str)
    )
    output: str = get_query_output_dir(
        output_dir, q_query_object
    )
    run_queries(
        q_query_object.algebra, output, "BGP", duckdb_conn
    )


def run_filter(
    query_str: str,
    output_dir: str,
    duckdb_conn: DuckDBPyConnection,
    incremental: bool = False,
) -> None:
    """Run the filter part of the query

    Args:
        query_str (str): Query
        output_dir (str): Output directory
        duckdb_conn (DuckDBPyConnection): Connection to the database
    """
    import incremental_query_parser as iqp
    from setup_queries import get_query_output_dir

    q_query_object: iqp.Query = build_data.get_query_object(
        build_data.readQueryFile(query_str)
    )
    output: str = get_query_output_dir(
        output_dir, q_query_object
    )
    run_queries(
        q_query_object.algebra,
        output,
        "Filter",
        duckdb_conn,
    )


def run_project(
    query_str: str,
    output_dir: str,
    duckdb_conn: DuckDBPyConnection,
    incremental: bool = False,
) -> None:
    """Run the project part of the query

    Args:
        query_str (str): Query
        output_dir (str): Output directory
        duckdb_conn (DuckDBPyConnection): Connection to the database
    """
    import incremental_query_parser as iqp
    from setup_queries import get_query_output_dir

    q_query_object: iqp.Query = build_data.get_query_object(
        build_data.readQueryFile(query_str)
    )
    output: str = get_query_output_dir(
        output_dir, q_query_object
    )
    run_queries(
        q_query_object.algebra,
        output,
        "Project",
        duckdb_conn,
    )


def run_minus(
    query_str: str,
    output_dir: str,
    duckdb_conn: DuckDBPyConnection,
    incremental: bool = False,
) -> None:
    """Run the minus part of the query

    Args:
        query_str (str): Query
        output_dir (str): Output directory
        duckdb_conn (DuckDBPyConnection): Connection to the database
    """
    import incremental_query_parser as iqp
    from setup_queries import get_query_output_dir

    q_query_object: iqp.Query = build_data.get_query_object(
        build_data.readQueryFile(query_str)
    )
    output: str = get_query_output_dir(
        output_dir, q_query_object
    )
    run_queries(
        q_query_object.algebra,
        output,
        "Minus",
        duckdb_conn,
    )


if __name__ == "__main__":
    import sys, os
    import argparse

    from build_data import build_data
    from duckdb import connect
    from experiments import (
        load_table_in_graph,
    )

    hashseed = os.getenv("PYTHONHASHSEED")
    if not hashseed:
        os.environ["PYTHONHASHSEED"] = "0"
        os.execv(
            sys.executable, [sys.executable] + sys.argv
        )

    # Connection to database
    # from eval_incremental import duckdb_conn

    # Parse the arguments
    parser = argparse.ArgumentParser(
        description="Test the kcounts modularly.",
        prog="kcount_tester.py",
        epilog="The program needs a query, output directory, data file, and deletions file to run properly.",
    )
    parser.add_argument("query", help="The query to test")
    parser.add_argument(
        "query_dir",
        help="The directory to read the query files from",
    )
    parser.add_argument("data", help="The data file")
    parser.add_argument(
        "--delf",
        dest="deletion_file",
        help="The file containing deletions",
    )
    parser.add_argument(
        "--insf",
        dest="insert_file",
        help="The file containing insertions",
    )
    parser.add_argument(
        "-i",
        "--incremental",
        action="store_true",
        help="Run the incremental version of the query",
        default=False,
    )
    parser.add_argument(
        "-db",
        "--database",
        dest="db",
        default="./database/k_tester.db",
        help="The database to connect to",
    )

    args = parser.parse_args()

    # Connection to database
    duckdb_conn = connect(args.db)

    build_data(
        args.query_dir,
        args.query,
        duckdb_conn,
        args.data,
        args.insert_file,
        args.deletion_file,
        True,
    )

    run_bgps(
        args.query,
        args.query_dir,
        duckdb_conn,
        args.incremental,
    )
    run_filter(
        args.query,
        args.query_dir,
        duckdb_conn,
        args.incremental,
    )
    run_minus(
        args.query,
        args.query_dir,
        duckdb_conn,
        args.incremental,
    )
    run_project(
        args.query,
        args.query_dir,
        duckdb_conn,
        args.incremental,
    )
