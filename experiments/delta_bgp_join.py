from SQL_Constructor.SQL_Constructor import get_table_name
from rdflib.plugins.sparql.parserutils import CompValue
from duckdb import DuckDBPyConnection
from os.path import join
from numpy import ndarray


def go_through_algebra_for_test(
    part: CompValue,
    output_dir: str,
    runs: int,
    table_args: str,
    delta_tables: list[str],
    nu_tables: list[str],
    duckdb_conn: DuckDBPyConnection,
) -> None:
    """Goes through the algebra and does the test for BGP's.

    Args:
        part (CompValue): Current part of the query.
        output_dir (str): The output directory.
        duckdb_conn (DuckDBPyConnection): Connection to the database.
    """
    from plots.build_compare_plot import compare_times_plot
    from SQL_Constructor.SQL_Constructor import (
        get_table_name,
    )

    if part.name == "BGP":
        table_file_names, to_drop_table_names = (
            get_bgp_delta_table_names(part)
        )
        # Run the test
        (
            avg_groupby_time,
            avg_join_time,
            avg_long_join_time,
        ) = join_delta_rules_bgp_test(
            join(output_dir, table_file_names[0]),
            join(output_dir, table_file_names[1]),
            join(output_dir, table_file_names[2]),
            join(output_dir, table_file_names[3]),
            join(output_dir, table_file_names[4]),
            to_drop_table_names[0],
            runs,
            table_args,
            delta_tables,
            nu_tables,
            duckdb_conn,
            to_drop_table_names[1],
        )

        # Plot the results
        compare_times_plot(
            avg_join_time,
            avg_groupby_time,
            "Full outer join",
            "Group by",
            ["50", "100", "200", "1000"],
            f"delta_{get_table_name(part)}",
            name_three="Long join",
            cmp_arr_three=avg_long_join_time,
        )
    else:
        if "p" in part:
            go_through_algebra_for_test(
                part.p,
                output_dir,
                runs,
                table_args,
                delta_tables,
                nu_tables,
                duckdb_conn,
            )
        elif "p1" in part and "p2" in part:
            go_through_algebra_for_test(
                part.p1,
                output_dir,
                runs,
                table_args,
                delta_tables,
                nu_tables,
                duckdb_conn,
            )
            go_through_algebra_for_test(
                part.p2,
                output_dir,
                runs,
                table_args,
                delta_tables,
                nu_tables,
                duckdb_conn,
            )
        else:
            return


def get_bgp_delta_table_names(
    part: CompValue,
) -> tuple[
    tuple[str, str, str, str, str],
    tuple[list[str], list[str]],
]:
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
    delta_table_long_join_name: str = (
        f"delta_{table_name}_long_join.sql"
    )
    prep_table_name: str = f"delta_prep_{table_name}"
    delta_table_tables: str = (
        f"delta_{table_name}_tables.sql"
    )
    delta_table_sum: str = f"delta_{table_name}_sum.sql"

    delta_table_names.append(delta_table_name)
    # delta_table_names.append(prep_table_name)

    delta_table_name += ".sql"

    # Build to drop table names for join
    delta_delete_table_names: list[str] = []
    for i in range(2, len(part.triples)):
        delta_delete_table_names.append(
            f"delta_{table_name}_{i}"
        )

    return (
        delta_table_name,
        delta_table_join_name,
        delta_table_long_join_name,
        delta_table_tables,
        delta_table_sum,
    ), (delta_table_names, delta_delete_table_names)


def run_query_time(
    query: str,
    runs: int,
    tables_to_drop: list[str],
    duckdb_conn: DuckDBPyConnection,
    tables_to_delete: list[str] = [],
) -> float:
    import time as t

    avg_time: float | None = None

    duckdb_conn.execute("SELECT * FROM G LIMIT 1;")

    for i in range(runs):
        print(f"Run {i + 1} of {runs}")

        print("Dropping tables")
        for table_name in tables_to_drop:
            print(f"Dropping table {table_name}")
            duckdb_conn.execute(
                f"DROP TABLE IF EXISTS {table_name};"
            )
        for table_name in tables_to_delete:
            print(f"Deleting data from table {table_name}")
            duckdb_conn.execute(
                f"DELETE FROM {table_name};"
            )

        start_time: float = t.time()
        duckdb_conn.execute(query)
        end_time: float = t.time()

        measured_time: float = (
            end_time - start_time
        ) * 1000
        if avg_time is None:
            avg_time = measured_time
        else:
            avg_time = (avg_time + measured_time) / 2

        print(f"Measured time: {measured_time}")
        print(f"Average time: {avg_time}")

    if avg_time is None:
        raise ValueError("No time was measured.")

    return avg_time


def load_delta_table_in_graph(
    delta_table: str,
    duckdb_conn: DuckDBPyConnection,
    nu_table: str,
) -> None:
    """Loads the delta table into the graph.

    Args:
        delta_table (str): The given delta table.
        duckdb_conn (DuckDBPyConnection): Connection to the database.
        nu_table (str): The given nu table.
    """
    # DROP THE TABLES BEFORE MAKING THEM ANEW
    duckdb_conn.execute(f"DROP TABLE IF EXISTS delta_G;")
    duckdb_conn.execute(f"DROP TABLE IF EXISTS nu_G;")

    # CREATE THE TABLES
    duckdb_conn.execute(
        f"CREATE TABLE delta_G AS FROM '{delta_table}';"
    )
    duckdb_conn.execute(
        f"CREATE TABLE nu_G AS FROM '{nu_table}';"
    )


def load_table_in_graph(
    table: str,
    duckdb_conn: DuckDBPyConnection,
) -> None:
    """Loads the table into the graph.

    Args:
        table (str): The given table.
        duckdb_conn (DuckDBPyConnection): Connection to the database.
    """
    # DROP THE TABLES BEFORE MAKING THEM ANEW
    duckdb_conn.execute(f"DROP TABLE IF EXISTS G;")

    # CREATE THE TABLES
    duckdb_conn.execute(
        f"CREATE TABLE G AS FROM '{table}';"
    )


def join_delta_rules_bgp_test(
    group_by_filename: str,
    join_filename: str,
    long_join_filename: str,
    delta_tables_tables: str,
    delta_tables_sum: str,
    tables_to_drop: list[str],
    runs: int,
    table_args: str,
    delta_tables: list[str],
    nu_tables: list[str],
    duckdb_conn: DuckDBPyConnection,
    tables_to_delete: list[str],
) -> tuple[ndarray, ndarray, ndarray]:
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
    from numpy import append, array

    # Read the query file
    group_by_query: str = iqp.readQueryFile(
        group_by_filename
    )

    # Read the join query file
    join_query: str = iqp.readQueryFile(join_filename)

    avg_group_by_time: ndarray = array([])
    avg_join_time: ndarray = array([])
    avg_long_join_time: ndarray = array([])

    print(f"Loading the table {table_args}")
    load_table_in_graph(table_args, duckdb_conn)

    print(f"Loading the delta tables")
    duckdb_conn.execute(
        iqp.readQueryFile(delta_tables_tables)
    )

    print(f"Inserting the prep tables.")
    duckdb_conn.execute(group_by_query)
    sum_query: str = iqp.readQueryFile(delta_tables_sum)

    for index in range(0, len(delta_tables)):
        if len(delta_tables) != len(nu_tables):
            raise ValueError(
                "The number of delta tables and nu tables must be the same."
            )

        print(
            f"Running with delta table {delta_tables[index]} and nu table {nu_tables[index]}"
        )

        # Load the delta table into the graph
        load_delta_table_in_graph(
            delta_tables[index],
            duckdb_conn,
            nu_tables[index],
        )

        # Run the group by query
        print(f"Running the group by query")
        group_by_time: float = run_query_time(
            sum_query,
            runs,
            tables_to_drop,
            duckdb_conn,
        )
        avg_group_by_time = append(
            avg_group_by_time, group_by_time
        )

        # Run the join query
        print(f"Running the join query")
        join_time: float = run_query_time(
            join_query,
            runs,
            tables_to_drop,
            duckdb_conn,
            tables_to_delete,
        )
        avg_join_time = append(avg_join_time, join_time)

        # Run the long join query
        print(f"Running the long join query")
        long_join_time: float = run_query_time(
            iqp.readQueryFile(long_join_filename),
            runs,
            tables_to_drop,
            duckdb_conn,
        )
        avg_long_join_time = append(
            avg_long_join_time, long_join_time
        )

    print(f"Group by average time: {avg_group_by_time}")
    print(f"Join average time: {avg_join_time}")
    print(f"Long join average time: {avg_long_join_time}")

    return (
        avg_group_by_time,
        avg_join_time,
        avg_long_join_time,
    )
