from duckdb import DuckDBPyConnection
from rdflib import Graph
from rdflib.compare import isomorphic, graph_diff
from rdflib.term import URIRef, Node
from rdflib.plugins.sparql.parserutils import CompValue
from time import time
from os.path import join
from copy import deepcopy

from benchmarker.benchmark import run_query
from build_data import (
    get_query_object,
    readQueryFile,
    get_query_input,
)
from benchmarker.dict_maker import constructDictFromTree


def constructGTable(
    table_name: str,
    g: Graph,
    duckdb_conn: DuckDBPyConnection,
    swap: int = 1,
    drop: bool = True,
) -> None:
    if drop:
        duckdb_conn.execute(
            f"DROP TABLE IF EXISTS {table_name}; CREATE TABLE IF NOT EXISTS {table_name} (s TEXT, p TEXT, o TEXT, k_count INT);"
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


def setupNuGToG(
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
        f"CREATE TABLE IF NOT EXISTS {to_insert_to_table} AS SELECT * FROM {to_insert_from_table};"
    )


def run_chain_constructing(
    part: CompValue,
    delta_and_nu_files: list[tuple[tuple[str, str], str]],
    duckdb_conn: DuckDBPyConnection,
    drop_tables: str,
    drop_delta_table: str,
    SQL_queries: dict[str, str],
    SQL_delta_queries: dict[str, list[str]],
    base_g: Graph,
) -> tuple[float, float]:
    total_scratch_time: float = 0.0
    total_increm_time: float = 0.0

    duckdb_conn.execute(drop_tables)
    # Initialize base relations for incremental
    run_query(part, SQL_queries, duckdb_conn)

    nu_graph = base_g

    counter = 1
    # Read delta and nu files
    for (ins_file, del_file), _ in delta_and_nu_files:
        delta_ins_g = Graph()
        delta_ins_g.parse(ins_file, format="nt")
        constructGTable("delta_G", delta_ins_g, duckdb_conn)

        delta_del_g = Graph()
        delta_del_g.parse(del_file, format="nt")
        constructGTable(
            "delta_G", delta_del_g, duckdb_conn, -1, False
        )

        nu_graph += delta_ins_g
        nu_graph -= delta_del_g
        constructGTable("nu_G", nu_graph, duckdb_conn)

        # Drop the tables if necessary
        duckdb_conn.execute(drop_delta_table)

        print(
            f"Part {counter} of {len(delta_and_nu_files)} of the chain"
        )
        # Time counter
        start_increm_time: float = time()
        # Run the query
        run_query(part, SQL_delta_queries, duckdb_conn)
        # Put the nu_G table into the G table
        setupNuGToG(duckdb_conn)
        # End time counter
        end_increm_time: float = time()
        curr_increm_time = (
            end_increm_time - start_increm_time
        ) * 1000
        total_increm_time += curr_increm_time

        # Drop the tables if necessary
        duckdb_conn.execute(drop_tables)

        # Time counter
        start_scratch_time: float = time()
        # Run the query
        run_query(part, SQL_queries, duckdb_conn)
        # End time counter
        end_scratch_time: float = time()
        curr_scratch_time = (
            end_scratch_time - start_scratch_time
        ) * 1000
        total_scratch_time += curr_scratch_time

        counter += 1

    return total_scratch_time, total_increm_time


def run_chain_benchmark(
    query: str,
    query_files_dir: str,
    runs: int,
    duckdb_conn: DuckDBPyConnection,
    data_file: str,
    delta_and_nu_files: list[tuple[tuple[str, str], str]],
) -> None:
    """Runs a chain of benchmarks.

    Args:
        query (str): Query to run on the database.
        query_files_dir (str): Output directory where the query files are stored.
        runs (int): Amount of runs to do for testing.
        duckdb_conn (DuckDBPyConnection): Connection to the database.
        data_file (str): Initial base data file. (In turtle format)
        delta_and_nu_files (list[tuple[str, str]]): List of tuples containing delta and nu files.
        (In NTriples and Turtle format respectively)
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
    drop_delta_tables = readQueryFile(
        join(query_input_dir, "drop_delta_tables.sql")
    )
    SQL_delta_queries = constructDictFromTree(
        q_query_object.algebra, query_input_dir, True
    )

    total_scratch_time: float = 0.0
    total_increm_time: float = 0.0

    for run in range(runs):
        print(f"Run: {run + 1} of {runs}")

        # Read initial data
        base_g = Graph()
        base_g.parse(data_file, format="ttl")

        print("Constructing base G table")
        constructGTable("G", base_g, duckdb_conn)

        scratch_time, increm_time = run_chain_constructing(
            q_query_object.algebra.p,
            delta_and_nu_files,
            duckdb_conn,
            drop_tables,
            drop_delta_tables,
            SQL_queries,  # type: ignore
            SQL_delta_queries,  # type: ignore
            base_g,
        )

        total_scratch_time += scratch_time
        total_increm_time += increm_time
        print(f"Scratch time: {scratch_time} ms")
        print(
            f"Average: {total_scratch_time / (run + 1)} ms"
        )
        print()
        print(f"Incremental time: {increm_time} ms")
        print(
            f"Average: {total_increm_time / (run + 1)} ms"
        )

    print(
        f"Average scratch time: {total_scratch_time / runs} ms"
    )
    print(
        f"Average incremental time: {total_increm_time / runs} ms"
    )
