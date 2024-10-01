from duckdb import DuckDBPyConnection
from rdflib import Graph


def build_up_group_by_sum(
    table_name_one: str,
    table_name_two: str,
    prep_table: str = "R2_prep",
) -> str:
    """Build up the group by sum query.

    Args:
        table_name_one (str): First table name.
        table_name_two (str): Second table name.

    Returns:
        str: Query string of the group by sum.
    """
    return_str: str = ""

    # INSERT INTO query
    insert_query: str = (
        f"INSERT INTO {prep_table} SELECT A, K FROM {table_name_one};\n"
    )
    insert_query += f"INSERT INTO {prep_table} SELECT A, K FROM {table_name_two};\n"

    # Sum and group by query
    return_str += insert_query
    return_str += f"SELECT A, SUM(K) AS K FROM {prep_table} GROUP BY A HAVING SUM(K) > 0;"

    return return_str


def build_up_full_outer_join(
    table_name_one: str, table_name_two: str
) -> str:
    """Build up the full outer join query.

    Args:
        table_name_one (str): The first table name.
        table_name_two (str): The second table name.

    Returns:
        str: The query string of the full outer join.
    """
    return_str: str = ""

    # select clause
    return_str += "SELECT "
    return_str += f"(CASE WHEN R1.A NOT NULL THEN R1.A ELSE R2.A END) AS A, "
    return_str += f"(CASE WHEN R1.A IS NULL THEN R2.K WHEN R2.A IS NULL THEN R1.K ELSE R1.K + R2.K END) AS K "

    # FROM clause
    return_str += f"FROM {table_name_one} AS R1 FULL OUTER JOIN {table_name_two} AS R2 ON R1.A = R2.A WHERE COALESCE(R1.K, 0) + COALESCE(R2.K, 0) > 0;"

    return return_str


def build_table(
    table_name: str, duckdb_conn: DuckDBPyConnection
) -> None:
    """Builds the table in DuckDB.

    Args:
        table_name (str): The table name.
        duckdb_conn (DuckDBPyConnection): Connection to the DB.
    """
    duckdb_conn.execute(
        f"CREATE TABLE IF NOT EXISTS {table_name} (A TEXT, K INT);"
    )
    duckdb_conn.execute(f"DELETE FROM {table_name};")


def build_query_string_for_data(
    g: Graph, table_name: str, delete_count: int = 1
) -> str:
    """Builds the string for the insertion"""
    rdf_input_data = ""
    known_tuples: dict[str, int] = dict()
    for s, p, o in g:
        if str(s) in known_tuples:
            known_tuples[str(s)] += delete_count
        else:
            known_tuples[str(s)] = delete_count
    for s in known_tuples:
        rdf_input_data += (
            f"('{s}', {known_tuples[str(s)]}),\n"
        )
    insert_str = (
        f"INSERT INTO {table_name} VALUES {rdf_input_data};"
    )
    return insert_str


def insert_data(
    db_conn: DuckDBPyConnection,
    data: str,
    table_name: str = "G",
) -> None:
    """Build up a query string and inserts data into a table.


    Args:
        db_conn (duckdb.DuckDBPyConnection): Database connection object.
        data (str): Given data to insert into the table.
    """
    # table_name: str = "G"
    g: Graph = Graph().parse(data=data)
    insert_data_query: str = build_query_string_for_data(
        g, table_name
    )

    db_conn.execute(insert_data_query)


def insert_delete_delta_data(
    db_conn: DuckDBPyConnection,
    data: str,
    table_name: str = "delta_G",
    insert: bool = True,
) -> None:
    """Builds up the data that gets changed in the table.

    Args:
        db_conn (duckdb.DuckDBPyConnection): Connection with the database.
        data (str): The data that gets changed
    """
    # table_name: str = "delta_G"
    g: Graph = Graph().parse(data=data)
    if not insert:
        insert_data_query: str = (
            build_query_string_for_data(g, table_name, -1)
        )
    else:
        insert_data_query: str = (
            build_query_string_for_data(g, table_name)
        )

    db_conn.execute(insert_data_query)


def build_up_data(
    duckdb_conn: DuckDBPyConnection,
    data_file: str,
    ins_file: str | None = None,
    del_file: str | None = None,
) -> None:
    """Builds up the data to compare in DuckDB.

    Args:
        duckdb_conn (DuckDBPyConnection): Connection to the DB.
        data_file (str): File containing the initial data.
        ins_file (str | None, optional): File regarding the insertions. Defaults to None.
        del_file (str | None, optional): File regarding the deletions. Defaults to None.
    """
    import incremental_query_parser as iqp

    # Read the data file and put original data into the database
    build_table("R1", duckdb_conn)
    if data_file is not None:
        data: str = iqp.readQueryFile(data_file)
        insert_data(duckdb_conn, data, "R1")

    build_table("R2", duckdb_conn)
    build_table("R2_prep", duckdb_conn)
    # Read the deleted data file and put deleted data into the database's delta G table.
    if del_file is not None:
        del_data: str = iqp.readQueryFile(del_file)
        insert_delete_delta_data(
            duckdb_conn, del_data, "R2", insert=False
        )

    # Read the inserted data file and put inserted data into the database's delta G table.
    if ins_file is not None:
        ins_data: str = iqp.readQueryFile(ins_file)
        insert_delete_delta_data(
            duckdb_conn, ins_data, "R2", insert=True
        )


def run_queries_time(
    query: str,
    data_file: str,
    duckdb_conn: DuckDBPyConnection,
    ins_file: str | None = None,
    del_file: str | None = None,
    runs: int = 5,
) -> float:
    """Runs the full outer join query for a given number of times.

    Args:
        query (str): Query to run.
        data_file (str): Data file to use.
        duckdb_conn (DuckDBPyConnection): Connection to the database.
        runs (int, optional): Amount of times to run the query. Defaults to 5.

    Returns:
        float: Average amount of time to run the query.
    """
    import time

    print("Building up data...")
    build_up_data(
        duckdb_conn, data_file, ins_file, del_file
    )

    avg_time: float | None = None
    for i in range(runs):
        print(f"Run {i + 1} of {runs}")
        start = time.time()
        duckdb_conn.execute(query)
        end = time.time()
        if avg_time is None:
            avg_time = end - start
        else:
            avg_time = (avg_time + (end - start)) / 2
        print(
            "Time taken: ",
            end - start,
            "\nAverage time: ",
            avg_time,
        )
        if i < runs - 1:
            print("Building up data...")
            build_up_data(
                duckdb_conn, data_file, ins_file, del_file
            )

    if avg_time is None:
        raise ValueError("Average time is None.")

    return avg_time


if __name__ == "__main__":
    from eval_incremental import duckdb_conn
    import argparse
    from numpy import array, ndarray, append
    from plots import build_compare_plot

    parser = argparse.ArgumentParser(
        description="Build up the full outer join query."
    )
    parser.add_argument(
        "-t1",
        "--table_name_one",
        type=str,
        default="R1",
        dest="t1",
        help="The first table name.",
    )
    parser.add_argument(
        "-t2",
        "--table_name_two",
        type=str,
        default="R2",
        dest="t2",
        help="The second table name.",
    )
    parser.add_argument(
        "data_file",
        type=str,
        help="The data files to run.",
        nargs="+",
    )
    parser.add_argument(
        "-r",
        "--runs",
        type=int,
        default=5,
        help="The amount of times to run the query.",
        dest="runs",
    )
    args = parser.parse_args()

    time_arr_outer_join: ndarray = array([])
    time_arr_group_by: ndarray = array([])

    query: str = build_up_full_outer_join("R1", "R2")
    query_group_by: str = build_up_group_by_sum("R1", "R2")

    for data_file in args.data_file:
        print(f"\nRunning the queries with {data_file}...")
        print("Running the full outer join query...")
        run_time_full_outer_join: float = run_queries_time(
            query,
            data_file,
            duckdb_conn,
            args.t1,
            args.t2,
            args.runs,
        )

        time_arr_outer_join = append(
            time_arr_outer_join, run_time_full_outer_join
        )

        print("\nRunning the group by sum query...")
        run_time_group_by_sum: float = run_queries_time(
            query_group_by,
            data_file,
            duckdb_conn,
            args.t1,
            args.t2,
            args.runs,
        )

        time_arr_group_by = append(
            time_arr_group_by, run_time_group_by_sum
        )

    print(
        "Time array: ",
        time_arr_outer_join,
        time_arr_group_by,
    )

    build_compare_plot.compare_times_plot(
        time_arr_outer_join,
        time_arr_group_by,
        "Full Outer Join",
        "Group By Sum",
        args.data_file,
    )

    print("Done.")
