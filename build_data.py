from duckdb import DuckDBPyConnection


def build_data(
    input_dir: str,
    query: str,
    duckdb_conn: DuckDBPyConnection,
    data_file: str | None = None,
    delf: str | None = None,
    insf: str | None = None,
    csv: bool = False,
) -> None:
    """Builds up the data from the data file.

    Args:
        data_file (str): String containing the data file.
    """
    if csv:
        from experiments.delta_bgp_join import (
            load_table_in_graph,
        )

        if data_file is None:
            raise ValueError(
                "Data file must be provided when using CSV"
            )
        load_table_in_graph(data_file, duckdb_conn)
        return

    import incremental_query_parser as iqp

    query_input_dir: str = iqp.get_query_input(
        input_dir,
        iqp.get_query_object(iqp.readQueryFile(query)),
    )

    # Set up tables in case they don't exist
    iqp.setup_tables(query_input_dir)

    # Read the data file and put original data into the database
    duckdb_conn.execute(
        f"CREATE TABLE IF NOT EXISTS G (s TEXT, p TEXT, o TEXT, k_count INT);"
    )
    duckdb_conn.execute(f"DELETE FROM G;")
    if data_file is not None:
        data: str = iqp.readQueryFile(data_file)
        iqp.insert_data(duckdb_conn, data)

    # Clear the delta G table
    iqp.create_delta_table(duckdb_conn, "delta_G")
    iqp.drop_delta_table(duckdb_conn, "delta_G")

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
    algebra.pprintAlgebra(q_query_object)

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
    import duckdb

    # Parse the arguments
    parser = argparse.ArgumentParser(
        description="Sets up the data.",
        prog="build_data.py",
        epilog="The program needs a query, data file, insertions and/or deletions file to run properly.",
    )
    parser.add_argument("query", help="The query to test")
    parser.add_argument(
        "input",
        help="The input directory to grab the tables from",
    )
    parser.add_argument(
        "-d",
        "--data",
        dest="data",
        help="The data file",
    )
    parser.add_argument(
        "-dl",
        "--delf",
        dest="deletion_file",
        help="The file containing deletions",
    )
    parser.add_argument(
        "-i",
        "--insf",
        dest="insert_file",
        help="The file containing insertions",
    )
    parser.add_argument(
        "-db",
        "--db",
        dest="db",
        help="The database to connect to",
        default="./database/k_values.db",
    )
    parser.add_argument(
        "-s",
        "--setup",
        action="store_true",
        help="Set up the base graphs",
    )

    args = parser.parse_args()

    # Connect to the database
    duckdb_conn = duckdb.connect(args.db)

    setup_query_files(args.query, args.input, duckdb_conn)

    if args.setup:
        build_data(
            args.input,
            args.query,
            duckdb_conn,
            args.data,
            args.deletion_file,
            args.insert_file,
        )
