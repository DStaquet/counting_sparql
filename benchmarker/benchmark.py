"""Modules to run SPARQL queries for benchmark with incremental view maintenance on SQL queries."""

from os.path import join
from time import time
from rdflib.plugins.sparql.parserutils import CompValue
from duckdb import DuckDBPyConnection


from build_data import (
    get_query_object,
    get_query_input,
    readQueryFile,
)
from experiments.experiments import (
    load_table_in_graph,
    load_delta_table_in_graph,
)
from SQL_Constructor.table_constructor import get_table_name
from benchmarker.dict_maker import constructDictFromTree


def entire_run_query(
    part: CompValue,
    queries_dict: dict[str, str] | dict[str, list[str]],
) -> str:
    """Runs the given query.

    Args:
        part (CompValue): The given query.
        duckdb_conn (DuckDBPyConnection): Connection to the database.
    """
    key = get_table_name(part)
    curr_query = ""
    if isinstance(queries_dict[key], list):
        curr_query = (
            queries_dict[key][0] + queries_dict[key][1]
        )
    else:
        query = queries_dict[key]
        if isinstance(query, str):
            curr_query = query
        else:
            raise ValueError("Query is not a string")

    if "p" in part:
        return (
            entire_run_query(part.p, queries_dict)
            + curr_query
        )
    elif "p1" in part and "p2" in part:
        return (
            entire_run_query(part.p1, queries_dict)
            + entire_run_query(part.p2, queries_dict)
            + curr_query
        )
    return curr_query


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
    if isinstance(queries_dict[key], list):
        run_file_query(
            queries_dict[key][0],
            duckdb_conn,
        )
        run_file_query(
            queries_dict[key][1],
            duckdb_conn,
        )
    else:
        query = queries_dict[key]
        if isinstance(query, str):
            run_file_query(query, duckdb_conn)
        else:
            raise ValueError("Query is not a string")


def run_benchmark(
    query: str,
    query_files_dir: str,
    runs: int,
    duckdb_conn: DuckDBPyConnection,
    data_file: str,
    nu_file: str,
    delta_file: str,
) -> tuple[float, float]:
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
    sql_queries = constructDictFromTree(
        q_query_object.algebra, query_input_dir
    )

    print("Running the benchmark from scratch")
    total_time: float = 0.0
    for run in range(runs):
        print(f"Run: {run + 1} of {runs}")
        # Drop the tables
        duckdb_conn.execute(drop_tables)
        # Prepare the G table
        load_table_in_graph(nu_file, duckdb_conn)

        run_query_str = entire_run_query(
            q_query_object.algebra.p, sql_queries
        )
        # Time counter
        start_time: float = time()
        # Run the query
        duckdb_conn.execute(run_query_str)
        # End time
        end_time: float = time()
        # Calculate the time
        total_time += (end_time - start_time) * 1000
        print(f"Time: {(end_time - start_time) * 1000}ms")
        print(f"Average time: {total_time / (run + 1)}ms")

    duckdb_conn.execute(
        readQueryFile(
            join(
                query_input_dir,
                get_table_name(q_query_object.algebra)
                + ".sql",
            )
        )
    )
    scratch_time = total_time / runs

    # Amount of tuples in BGP
    tuple_amount_scratch: list[int] = list()
    for key in sql_queries:
        if "BGP" in key:
            tuple_amount_scratch.append(
                duckdb_conn.sql(
                    f"SELECT COUNT(*) FROM {key};"
                ).fetchone()[  # type: ignore
                    0
                ]
            )
        if "SelectQuery" in key:
            tuple_amount_scratch.append(
                duckdb_conn.sql(
                    f"SELECT COUNT(*) FROM {key};"
                ).fetchone()[  # type: ignore
                    0
                ]
            )

    drop_delta_tables = readQueryFile(
        join(query_input_dir, "drop_delta_tables.sql")
    )
    sql_delta_queries = constructDictFromTree(
        q_query_object.algebra, query_input_dir, True
    )

    print("Preparing the benchmark incrementally")
    # Prepare the G table
    load_table_in_graph(data_file, duckdb_conn)
    load_delta_table_in_graph(
        delta_file, duckdb_conn, nu_file
    )
    # Prepare the other tables
    duckdb_conn.execute(drop_tables)
    run_query(
        q_query_object.algebra.p,
        sql_queries,
        duckdb_conn,
    )

    print("Running the benchmark incrementally")
    total_time: float = 0.0
    for run in range(runs):
        print(f"Run: {run + 1} of {runs}")
        # Drop the tables
        duckdb_conn.execute(drop_delta_tables)

        run_query_str = entire_run_query(
            q_query_object.algebra.p, sql_delta_queries
        )
        # Time counter
        start_time: float = time()
        # Run the query
        duckdb_conn.execute(run_query_str)
        # End time
        end_time: float = time()
        # Calculate the time
        total_time += (end_time - start_time) * 1000
        print(f"Time: {(end_time - start_time) * 1000}ms")
        print(f"Average time: {total_time / (run + 1)}ms")

    duckdb_conn.execute(
        readQueryFile(
            join(
                query_input_dir,
                get_table_name(q_query_object.algebra)
                + ".sql",
            )
        )
    )
    duckdb_conn.execute(
        readQueryFile(
            join(
                query_input_dir,
                "delta_"
                + get_table_name(q_query_object.algebra)
                + ".sql",
            )
        )
    )
    duckdb_conn.execute(
        readQueryFile(
            join(
                query_input_dir,
                "nu_"
                + get_table_name(q_query_object.algebra)
                + ".sql",
            )
        )
    )

    # Amount of tuples in BGP
    tuple_amount_increm: list[int] = list()
    tuple_amount_increm_before: list[int] = list()
    tuple_amount_increm_delta: list[int] = list()
    for key in sql_delta_queries:
        if "BGP" in key:
            tuple_amount_increm.append(
                duckdb_conn.sql(
                    f"SELECT COUNT(*) FROM nu_{key};"
                ).fetchone()[  # type: ignore
                    0
                ]
            )
            tuple_amount_increm_before.append(
                duckdb_conn.sql(
                    f"SELECT COUNT(*) FROM {key};"
                ).fetchone()[  # type: ignore
                    0
                ]
            )
            tuple_amount_increm_delta.append(
                duckdb_conn.sql(
                    f"SELECT COUNT(*) FROM delta_{key};"
                ).fetchone()[  # type: ignore
                    0
                ]
            )
        if "SelectQuery" in key:
            tuple_amount_increm.append(
                duckdb_conn.sql(
                    f"SELECT COUNT(*) FROM nu_{key};"
                ).fetchone()[  # type: ignore
                    0
                ]
            )
            tuple_amount_increm_before.append(
                duckdb_conn.sql(
                    f"SELECT COUNT(*) FROM {key};"
                ).fetchone()[  # type: ignore
                    0
                ]
            )
            tuple_amount_increm_delta.append(
                duckdb_conn.sql(
                    f"SELECT COUNT(*) FROM delta_{key};"
                ).fetchone()[  # type: ignore
                    0
                ]
            )

    incremental_time = total_time / runs
    print()
    print(f"Average time from scratch: {scratch_time}ms")
    print(
        f"Average time incrementally: {incremental_time}ms"
    )

    print(
        "Amount of tuples in BGP:",
        "\nScratch:",
        tuple_amount_scratch[0],
        "\nIncremental(Previous + Delta + Nu):",
        tuple_amount_increm[0]
        + tuple_amount_increm_before[0]
        + tuple_amount_increm_delta[0],
        "Previous:",
        tuple_amount_increm_before[0],
        "Delta:",
        tuple_amount_increm_delta[0],
        "Nu:",
        tuple_amount_increm[0],
    )
    print(
        "Amount of tuples in end result:",
        "\nScratch:",
        tuple_amount_scratch[1],
        "\nIncremental (Previous + Delta + Nu):",
        tuple_amount_increm[1]
        + tuple_amount_increm_before[1]
        + tuple_amount_increm_delta[1],
        "Previous:",
        tuple_amount_increm_before[1],
        "Delta:",
        tuple_amount_increm_delta[1],
        "Nu:",
        tuple_amount_increm[1],
    )

    return scratch_time, incremental_time
