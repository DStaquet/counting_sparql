from duckdb import DuckDBPyConnection

from rdflib.plugins.sparql.parserutils import CompValue


def build_data(
    data_file: str,
    input_dir: str,
    query: str,
    duckdb_conn: DuckDBPyConnection,
    delf: str | None = None,
    insf: str | None = None,
) -> None:
    """Builds up the data from the data file.

    Args:
        data_file (str): String containing the data file.
    """
    import incremental_query_parser as iqp

    query_input_dir: str = iqp.get_query_input(
        input_dir,
        iqp.get_query_object(iqp.readQueryFile(query)),
    )

    # Set up tables in case they don't exist
    iqp.setup_tables(query_input_dir)

    # Read the data file and put original data into the database
    data: str = iqp.readQueryFile(data_file)
    iqp.insert_data(duckdb_conn, data)

    # Clear the delta G table
    iqp.drop_delta_table(duckdb_conn, "delta_G")
    iqp.create_delta_table(duckdb_conn, "delta_G")

    # Read the deleted data file and put deleted data into the database's delta G table.
    if delf is not None:
        del_data: str = iqp.readQueryFile(delf)
        iqp.insert_delete_delta_data(duckdb_conn, del_data)

    # Read the inserted data file and put inserted data into the database's delta G table.
    if insf is not None:
        ins_data: str = iqp.readQueryFile(insf)
        iqp.insert_insert_delta_data(duckdb_conn, ins_data)
    # Combine the original and deleted data into the new version of the data.
    iqp.insert_nu_data(duckdb_conn)


def setup_query_files(
    query_str: str,
    output_dir: str,
    duckdb_conn: DuckDBPyConnection,
) -> None:
    """Constructs the BGP queries and writes them to the output directory.

    Args:
        query_str (str): The query string to construct the BGP queries
        output_dir (str): The output directory to write the BGP queries to
        duckdb_con (DuckDBPyConnection): Connection to the database.
    """
    from SQL_Constructor import (
        SQL_initialize_queries as SQLiq,
    )
    import incremental_query_parser as iqp
    from setup_queries import (
        get_query_output_dir,
        setup_tables,
    )
    from rdflib.plugins.sparql import parser, algebra

    q_query_object: iqp.Query = iqp.get_query_object(
        iqp.readQueryFile(query_str)
    )
    # algebra.pprintAlgebra(q_query_object)

    # Output directory
    query_output_dir: str = get_query_output_dir(
        output_dir, q_query_object
    )

    setup_tables(
        q_query_object.algebra,
        query_output_dir,
    )

    SQLiq.build_queries(
        q_query_object.algebra,
        query_output_dir,
    )
    SQLiq.build_increm_queries(
        q_query_object.algebra,
        query_output_dir,
    )


def run_queries(
    part: CompValue,
    output_dir: str,
    part_name: str,
    duckdb_conn: DuckDBPyConnection,
) -> None:
    """Execute the BGP queries recursively.

    Args:
        part (CompValue): _description_
        output_dir (str): _description_
        duckdb_conn (DuckDBPyConnection): _description_
    """
    from eval_incremental.eval_incremental import (
        get_query_string,
    )

    if part.name == part_name:
        query_file: str = get_query_string(part, output_dir)
        duckdb_conn.sql(query_file)
        query_file_delta: str = get_query_string(
            part, output_dir, "delta_"
        )
        print(query_file_delta)
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
) -> None:
    """Run the BGP queries.

    Args:
        query_str (str): The query string to construct the BGP queries
        output_dir (str): The output directory to write the BGP queries to
        duckdb_con (DuckDBPyConnection): Connection to the database.
    """
    import incremental_query_parser as iqp
    from setup_queries import get_query_output_dir

    q_query_object: iqp.Query = iqp.get_query_object(
        iqp.readQueryFile(query_str)
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
) -> None:
    """Run the filter part of the query

    Args:
        query_str (str): Query
        output_dir (str): Output directory
        duckdb_conn (DuckDBPyConnection): Connection to the database
    """
    import incremental_query_parser as iqp
    from setup_queries import get_query_output_dir

    q_query_object: iqp.Query = iqp.get_query_object(
        iqp.readQueryFile(query_str)
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
) -> None:
    """Run the project part of the query

    Args:
        query_str (str): Query
        output_dir (str): Output directory
        duckdb_conn (DuckDBPyConnection): Connection to the database
    """
    import incremental_query_parser as iqp
    from setup_queries import get_query_output_dir

    q_query_object: iqp.Query = iqp.get_query_object(
        iqp.readQueryFile(query_str)
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
) -> None:
    """Run the minus part of the query

    Args:
        query_str (str): Query
        output_dir (str): Output directory
        duckdb_conn (DuckDBPyConnection): Connection to the database
    """
    import incremental_query_parser as iqp
    from setup_queries import get_query_output_dir

    q_query_object: iqp.Query = iqp.get_query_object(
        iqp.readQueryFile(query_str)
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

    hashseed = os.getenv("PYTHONHASHSEED")
    if not hashseed:
        os.environ["PYTHONHASHSEED"] = "0"
        os.execv(
            sys.executable, [sys.executable] + sys.argv
        )

    # Connection to database
    from eval_incremental import duckdb_conn

    # Parse the arguments
    parser = argparse.ArgumentParser(
        description="Test the kcounts modularly.",
        prog="kcount_tester.py",
        epilog="The program needs a query, output directory, data file, and deletions file to run properly.",
    )
    parser.add_argument("query", help="The query to test")
    parser.add_argument(
        "output", help="The output directory to write to"
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

    args = parser.parse_args()

    setup_query_files(args.query, args.output, duckdb_conn)

    build_data(
        args.data,
        args.output,
        args.query,
        duckdb_conn,
        args.deletion_file,
        args.insert_file,
    )

    run_bgps(args.query, args.output, duckdb_conn)
    run_filter(args.query, args.output, duckdb_conn)
    run_minus(args.query, args.output, duckdb_conn)
    run_project(args.query, args.output, duckdb_conn)
