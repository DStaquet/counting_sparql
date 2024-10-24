from SQL_Constructor.SQL_Constructor import get_table_name
from rdflib.plugins.sparql.parserutils import CompValue
from duckdb import DuckDBPyConnection
from os.path import join


def go_through_algebra_for_test(
    part: CompValue,
    output_dir: str,
    runs: int,
    table_args: list[str],
    duckdb_conn: DuckDBPyConnection,
) -> None:
    """Goes through the algebra and does the test for BGP's.

    Args:
        part (CompValue): Current part of the query.
        output_dir (str): The output directory.
        duckdb_conn (DuckDBPyConnection): Connection to the database.
    """
    if part.name == "BGP":
        table_file_names, to_drop_table_names = (
            get_bgp_delta_table_names(part)
        )
        # Run the test
        join_delta_rules_bgp_test(
            join(output_dir, table_file_names[0]),
            join(output_dir, table_file_names[1]),
            to_drop_table_names,
            runs,
            table_args,
            duckdb_conn,
        )
    else:
        if "p" in part:
            go_through_algebra_for_test(
                part.p,
                output_dir,
                runs,
                table_args,
                duckdb_conn,
            )
        elif "p1" in part and "p2" in part:
            go_through_algebra_for_test(
                part.p1,
                output_dir,
                runs,
                table_args,
                duckdb_conn,
            )
            go_through_algebra_for_test(
                part.p2,
                output_dir,
                runs,
                table_args,
                duckdb_conn,
            )
        else:
            return


def get_bgp_delta_table_names(
    part: CompValue,
) -> tuple[tuple[str, str], list[str]]:
    """Gets the table names for the BGP's delta tables.

    Args:
        part (CompValue): The current part of the query.

    Returns:
        tuple[str, str]: Tuple of two strings containing the table names
            for the BGP's delta tables.
    """
    delta_table_names: list[str] = []
    # Get the table name
    table_name: str = get_table_name(part)
    # Get the delta table names
    delta_table_name: str = f"delta_{table_name}"

    delta_table_join_name: str = (
        f"delta_{table_name}_join.sql"
    )
    prep_table_name: str = f"delta_prep_{table_name}"

    delta_table_names.append(delta_table_name)
    delta_table_names.append(prep_table_name)

    delta_table_name += ".sql"

    return (
        delta_table_name,
        delta_table_join_name,
    ), delta_table_names


def run_query_time(
    query: str, runs: int, duckdb_conn: DuckDBPyConnection
) -> float:
    import time as t

    avg_time: float | None = None

    for _ in range(runs):
        start_time: float = t.time()
        print(query)
        duckdb_conn.execute(query)
        end_time: float = t.time()

        measured_time: float = (
            end_time - start_time
        ) * 1000
        if avg_time is None:
            avg_time = measured_time
        else:
            avg_time += measured_time / 2

    if avg_time is None:
        raise ValueError("No time was measured.")

    return avg_time


def join_delta_rules_bgp_test(
    group_by_filename: str,
    join_filename: str,
    tables_to_drop: list[str],
    runs: int,
    table_args: list[str],
    duckdb_conn: DuckDBPyConnection,
) -> tuple[list[float], list[float]]:
    """Compares the delta rules utilizing a join.

    Args:
        group_by_filename (str): The filename of the group by query.
        join_filename (str): The filename of the join query.
        tables_to_drop (list[str]): List of strings containing the table names
            to drop.
        duckdb_conn (DuckDBPyConnection): Connection to the database.

    Returns:
        tuple[list[float], list[float]]: Tuple of two lists of floats
            containing the average time to execute both the group by and
            join queries.
    """
    import incremental_query_parser as iqp
    from group_by_full_outer_join_test import (
        parse_delta_table_names,
    )

    # Read the query file
    group_by_query: str = iqp.readQueryFile(
        group_by_filename
    )

    # Read the join query file
    join_query: str = iqp.readQueryFile(join_filename)

    # Drop the prep table and nu_table in case they exist
    for table_name in tables_to_drop:
        print(f"Dropping table {table_name}")
        duckdb_conn.execute(
            f"DROP TABLE IF EXISTS {table_name};"
        )

    table_names, delta_table_names = (
        parse_delta_table_names(table_args)
    )

    # Run the group by query
    group_by_time: float = run_query_time(
        group_by_query, runs, duckdb_conn
    )

    # Run the join query
    join_time: float = run_query_time(
        join_filename, runs, duckdb_conn
    )
