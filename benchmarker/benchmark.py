from rdflib.plugins.sparql.parserutils import CompValue
from duckdb import DuckDBPyConnection
from os.path import join
from time import time

from build_data import (
    get_query_object,
    get_query_input,
    readQueryFile,
)
from experiments.experiments import (
    load_table_in_graph,
)
from SQL_Constructor.base_constructor import get_table_name
from benchmarker.dict_maker import constructDictFromTree


def run_file_query(
    query_to_run: str,
    duckdb_conn: DuckDBPyConnection,
) -> None:
    """Runs the given query.

    Args:
        query_file (str): The given query file.
        duckdb_conn (DuckDBPyConnection): Connection to the database.
    """
    duckdb_conn.execute(query_to_run)


def run_query(
    part: CompValue,
    queries_dict: dict[str, str] | dict[str, list[str]],
    duckdb_conn: DuckDBPyConnection,
) -> None:
    """Runs the given query.

    Args:
        part (CompValue): The given query.
        duckdb_conn (DuckDBPyConnection): Connection to the database.
    """
    if "p" in part:
        run_query(part.p, queries_dict, duckdb_conn)
    elif "p1" in part and "p2" in part:
        run_query(part.p1, queries_dict, duckdb_conn)
        run_query(part.p2, queries_dict, duckdb_conn)

    key = get_table_name(part)
    if type(queries_dict[key]) == list:
        run_file_query(
            queries_dict[key][0] + queries_dict[key][1],
            duckdb_conn,
        )
    else:
        query = queries_dict[key]
        if type(query) == str:
            run_file_query(query, duckdb_conn)
        else:
            raise ValueError("Query is not a string")


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

    drop_tables = readQueryFile(
        join(query_input_dir, "drop_tables.sql")
    )

    # Build dictionary with SQL queries
    SQL_queries = constructDictFromTree(
        q_query_object.algebra, query_input_dir
    )

    print("Running the benchmark from scratch")
    total_time: float = 0.0
    for run in range(runs):
        print(f"Run: {run + 1} of {runs}")
        # Drop the tables
        duckdb_conn.execute(drop_tables)
        # Prepare the G table
        load_table_in_graph(data_file, duckdb_conn)

        # Time counter
        start_time: float = time()
        # Run the query
        run_query(
            q_query_object.algebra.p,
            SQL_queries,
            duckdb_conn,
        )
        # End time
        end_time: float = time()
        # Calculate the time
        total_time += (end_time - start_time) * 1000
        print(f"Time: {(end_time - start_time) * 1000}ms")
        print(f"Average time: {total_time / (run + 1)}ms")
    print(
        f"Average time (from scratch): {total_time / runs}ms"
    )

    drop_delta_tables = readQueryFile(
        join(query_input_dir, "drop_delta_tables.sql")
    )
    SQL_delta_queries = constructDictFromTree(
        q_query_object.algebra, query_input_dir, True
    )

    print("Running the benchmark incrementally")
    total_time: float = 0.0
    for run in range(runs):
        print(f"Run: {run + 1} of {runs}")
        # Drop the tables
        duckdb_conn.execute(drop_delta_tables)
        # Prepare the G table
        # load_table_in_graph(data_file, duckdb_conn)

        # Time counter
        start_time: float = time()
        # Run the query
        run_query(
            q_query_object.algebra.p,
            SQL_delta_queries,
            duckdb_conn,
        )
        # End time
        end_time: float = time()
        # Calculate the time
        total_time += (end_time - start_time) * 1000
        print(f"Time: {(end_time - start_time) * 1000}ms")
        print(f"Average time: {total_time / (run + 1)}ms")
