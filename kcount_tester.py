from duckdb import DuckDBPyConnection


def build_data(
    data_file: str,
    delf: str,
    input_dir: str,
    query: str,
    duckdb_conn: DuckDBPyConnection,
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

    # Read the deleted data file and put deleted data into the database's delta G table.
    del_data: str = iqp.readQueryFile(delf)
    iqp.insert_delete_delta_data(duckdb_conn, del_data)

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
    from setup_queries import get_query_output_dir

    q_query_object: iqp.Query = iqp.get_query_object(
        iqp.readQueryFile(query_str)
    )
    SQLiq.build_queries(
        q_query_object.algebra,
        get_query_output_dir(output_dir, q_query_object),
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
        "delf",
        help="The file containing deletions",
    )
    args = parser.parse_args()

    setup_query_files(args.query, args.output, duckdb_conn)

    build_data(
        args.data,
        args.delf,
        args.output,
        args.query,
        duckdb_conn,
    )
