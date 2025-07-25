"""Module providing timers for running benchmarks"""

from time import time
from os.path import join

from duckdb import DuckDBPyConnection
from rdflib import Graph
from rdflib.plugins.sparql.parserutils import CompValue

from benchmarker.benchmark import (
    run_query,
    load_delta_table_in_graph,
    load_table_in_graph,
    entire_run_query,
)
from benchmarker.dict_maker import constructDictFromTree
from build_data import (
    get_query_object,
    readQueryFile,
    get_query_input,
)
from SQL_Constructor.table_constructor import get_table_name


def construct_g_table(
    table_name: str,
    g: Graph,
    duckdb_conn: DuckDBPyConnection,
    swap: int = 1,
    drop: bool = True,
) -> None:
    """Constructs a DuckDB table from an RDF graph.

    Args:
        table_name (str): Name of the table to create.
        g (Graph): The RDF graph to convert into a table.
        duckdb_conn (DuckDBPyConnection): Connection to the DuckDB database.
        swap (int, optional): Indicator for swapping an integer. Defaults to 1.
        drop (bool, optional): Bool to indicate a drop is necessary. Defaults to True.
    """
    if drop:
        duckdb_conn.execute(
            f"DROP TABLE IF EXISTS {table_name};"
            + f"CREATE TABLE IF NOT EXISTS {table_name} (s TEXT, p TEXT, o TEXT, k_count INT);"
        )
    else:
        duckdb_conn.execute(
            f"CREATE TABLE IF NOT EXISTS {table_name} (s TEXT, p TEXT, o TEXT, k_count INT);"
        )

    known_tuples: dict[tuple[str, str, str], int] = dict()
    for s, p, o in g:
        if (s, p, o) in known_tuples:
            known_tuples[(str(s), str(p), str(o))] += 1
        else:
            known_tuples[(str(s), str(p), str(o))] = 1

    rdf_input_data = ""
    for s, p, o in known_tuples:
        rdf_input_data += f"('{s}', '{p}', '{o}', {swap * known_tuples[(s, p, o)]}),\n"
    insert_str = (
        f"INSERT INTO {table_name} VALUES {rdf_input_data};"
    )

    duckdb_conn.execute(insert_str)


def setup_nus(
    part: CompValue, duckdb_conn: DuckDBPyConnection
) -> None:
    """Sets up the nu_G table.

    Args:
        part (CompValue): Part of the query algebra to process.
        duckdb_conn (DuckDBPyConnection): Connection to the database.
    """
    if "p" in part:
        setup_nus(part.p, duckdb_conn)
    elif "p1" in part and "p2" in part:
        setup_nus(part.p1, duckdb_conn)
        setup_nus(part.p2, duckdb_conn)

    setup_nu_g_to_g(
        duckdb_conn,
        "nu_" + get_table_name(part),
        get_table_name(part),
    )


def setup_nu_g_to_g(
    duckdb_conn: DuckDBPyConnection,
    to_insert_from_table: str = "nu_G",
    to_insert_to_table: str = "G",
) -> None:
    """Sets up the G table from the previous nu_G table.

    Args:
        duckdb_conn (DuckDBPyConnection): Connection to the database.
    """
    duckdb_conn.execute(
        f"DROP TABLE IF EXISTS {to_insert_to_table};"
    )
    duckdb_conn.execute(
        f"ALTER TABLE {to_insert_from_table} RENAME TO {to_insert_to_table};"
    )


def run_chain_constructing(
    part: CompValue,
    delta_and_nu_files: list[
        tuple[str | tuple[str, str], str]
    ],
    duckdb_conn: DuckDBPyConnection,
    drop_tables: str,
    drop_delta_table: str,
    sql_queries: dict[str, str] | dict[str, list[str]],
    sql_delta_queries: (
        dict[str, str] | dict[str, list[str]]
    ),
    data_file: str = "",
) -> tuple[float, float]:
    """Runs the chain of benchmarks by constructing the G table and running the queries.

    Args:
        part (CompValue): CompValue part of the query algebra to process.
        delta_and_nu_files (list[ tuple[str  |  tuple[str, str], str] ]):
            Delta and nu files to process.
        duckdb_conn (DuckDBPyConnection): Connection to the DuckDB database.
        drop_tables (str): SQL command to drop tables.
        drop_delta_table (str): SQL command to drop delta tables.
        sql_queries (dict[str, str] | dict[str, list[str]]): Dictionary of SQL queries.
        sql_delta_queries (dict[str, list[str]] | dict[str, list[str]]):
            Dictionary of SQL delta queries.
        data_file (str, optional): File with data. Defaults to "".

    Raises:
        ValueError: If delta_file is not a string or tuple.
        ValueError: If delta_file should be in CSV format and is not.

    Returns:
        tuple[float, float]: Average scratch and incremental times in milliseconds.
    """

    part = part.p

    total_scratch_time: float = 0.0
    total_increm_time: float = 0.0

    duckdb_conn.execute(drop_tables)
    # Initialize base relations for incremental
    run_query(part, sql_queries, duckdb_conn)

    # nu_graph = deepcopy(base_g)
    # constructGTable("nu_G", nu_graph, duckdb_conn)

    print("Running the benchmark incrementally")
    # Read delta and nu files
    counter = 0
    previous_delta_file = data_file

    entire_run_query_str_delta = entire_run_query(
        part, sql_delta_queries
    )
    for delta_file, nu_file in delta_and_nu_files:
        counter += 1
        print(
            f"Delta {counter} of {len(delta_and_nu_files)}"
        )

        if isinstance(delta_file, tuple):
            raise ValueError(
                "Delta file should be a string, not a tuple."
            )
        elif isinstance(delta_file, str):
            load_table_in_graph(
                previous_delta_file, duckdb_conn
            )
            duckdb_conn.execute(drop_tables)
            duckdb_conn.execute(drop_delta_table)

            run_query(part, sql_queries, duckdb_conn)
            load_delta_table_in_graph(
                delta_file, duckdb_conn, nu_file
            )
            previous_delta_file = delta_file

        # Drop the tables if necessary
        duckdb_conn.execute(drop_delta_table)

        # Time counter
        start_increm_time: float = time()

        # Run the query
        duckdb_conn.execute(entire_run_query_str_delta)
        # run_query(part, SQL_delta_queries, duckdb_conn)

        # End time counter
        end_increm_time: float = time()
        curr_increm_time = (
            end_increm_time - start_increm_time
        ) * 1000
        total_increm_time += curr_increm_time

    load_table_in_graph(
        delta_and_nu_files[-2][1], duckdb_conn
    )
    last_delta_file, last_nu_file = delta_and_nu_files[-1]
    if (
        last_delta_file is not None
        and last_nu_file is not None
    ):
        load_delta_table_in_graph(
            str(last_delta_file), duckdb_conn, last_nu_file
        )
    duckdb_conn.execute(drop_delta_table)
    run_query(part, sql_delta_queries, duckdb_conn)

    print("Running the benchmark from scratch")
    counter = 0
    for delta_file, nu_file in delta_and_nu_files:
        counter += 1
        print(
            f"Delta {counter} of {len(delta_and_nu_files)}"
        )

        if isinstance(delta_file, str):
            load_delta_table_in_graph(
                delta_file,
                duckdb_conn,
                nu_file,
                nu_table_name="G",
            )
        else:
            raise ValueError(
                "Delta file should be a string in CSV format, not a tuple."
            )

        # Drop the tables if necessary
        duckdb_conn.execute(drop_tables)

        # Time counter
        start_scratch_time: float = time()

        # Run the query
        # duckdb_conn.execute(entire_run_query_str)
        run_query(part, sql_queries, duckdb_conn)

        # End time counter
        end_scratch_time: float = time()
        curr_scratch_time = (
            end_scratch_time - start_scratch_time
        ) * 1000
        total_scratch_time += curr_scratch_time

    return (
        total_scratch_time,
        total_increm_time,
    )


def run_chain_benchmark(
    query: str,
    query_files_dir: str,
    runs: int,
    duckdb_conn: DuckDBPyConnection,
    data_file: str,
    delta_and_nu_files: list[
        tuple[str | tuple[str, str], str]
    ],
) -> tuple[float, float]:
    """Runs the chain benchmark by constructing the G table and running the queries.

    Args:
        query (str): The query to run.
        query_files_dir (str): The directory containing query files.
        runs (int): The number of runs to perform.
        duckdb_conn (DuckDBPyConnection): Connection to the DuckDB database.
        data_file (str): File with data to load into the graph.
        delta_and_nu_files (list[ tuple[str  |  tuple[str, str], str] ]):
            Files with delta and nu data.

    Returns:
        tuple[float, float]: Average scratch and incremental times in milliseconds.
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
    drop_delta_tables = readQueryFile(
        join(query_input_dir, "drop_delta_tables.sql")
    )
    sql_delta_queries = constructDictFromTree(
        q_query_object.algebra, query_input_dir, True
    )

    total_scratch_time: float = 0.0
    total_increm_time: float = 0.0

    for run in range(runs):
        print(f"Run: {run + 1} of {runs}")

        print("Loading base graph data")
        load_table_in_graph(data_file, duckdb_conn)

        (
            scratch_time,
            increm_time,
        ) = run_chain_constructing(
            q_query_object.algebra,
            delta_and_nu_files,
            duckdb_conn,
            drop_tables,
            drop_delta_tables,
            sql_queries,
            sql_delta_queries,
            data_file=data_file,
        )

        total_scratch_time += scratch_time
        total_increm_time += increm_time
        print(f"Scratch time: {scratch_time} ms")
        print(
            f"Average: {total_scratch_time / (run + 1)} ms"
        )
        print(f"Incremental time: {increm_time} ms")
        print(
            f"Average: {total_increm_time / (run + 1)} ms"
        )
        print()

    print(
        f"Average scratch time: {total_scratch_time / runs} ms"
    )
    print(
        f"Average incremental time: {total_increm_time / runs} ms"
    )

    return (
        total_scratch_time / runs,
        total_increm_time / runs,
    )
