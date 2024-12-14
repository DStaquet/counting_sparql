from rdflib.plugins.sparql.parserutils import CompValue
from duckdb import DuckDBPyConnection
from os.path import join

from build_data import (
    get_query_object,
    get_query_input,
    readQueryFile,
)
from experiments.experiments import (
    load_table_in_graph,
)
from SQL_Constructor.base_constructor import get_table_name


def run_file_query(
    query_file: str,
    duckdb_conn: DuckDBPyConnection,
) -> None:
    """Runs the given query.

    Args:
        query_file (str): The given query file.
        duckdb_conn (DuckDBPyConnection): Connection to the database.
    """
    with open(query_file, "r") as file:
        query = file.read()

        duckdb_conn.execute(query)


def run_query(
    part: CompValue,
    query_file_dir: str,
    duckdb_conn: DuckDBPyConnection,
) -> None:
    """Runs the given query.

    Args:
        part (CompValue): The given query.
        duckdb_conn (DuckDBPyConnection): Connection to the database.
    """
    if "p" in part:
        run_query(part.p, query_file_dir, duckdb_conn)
    elif "p1" in part and "p2" in part:
        run_query(part.p1, query_file_dir, duckdb_conn)
        run_query(part.p2, query_file_dir, duckdb_conn)

    run_file_query(
        join(query_file_dir, get_table_name(part)) + ".sql",
        duckdb_conn,
    )


def run_benchmark(
    query: str,
    query_files_dir: str,
    runs: int,
    duckdb_conn: DuckDBPyConnection,
    data_file: str,
) -> None:
    """Runs the given query.

    Args:
        query (str): The given query.
        duckdb_conn (DuckDBPyConnection): Connection to the database.
    """
    # Get the query object
    q_query_object = get_query_object(readQueryFile(query))

    # Get the query input
    query_input_dir = get_query_input(
        query_files_dir, q_query_object
    )

    for _ in range(runs):
        # Prepare the G table
        load_table_in_graph(data_file, duckdb_conn)

        run_query(
            q_query_object.algebra,
            query_input_dir,
            duckdb_conn,
        )
