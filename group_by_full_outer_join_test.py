from duckdb import DuckDBPyConnection
from rdflib import Graph
from numpy import ndarray


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


def build_table_drop(
    table_name: str, duckdb_conn: DuckDBPyConnection
) -> None:
    """Builds the table in DuckDB.

    Args:
        table_name (str): Name of the table.
        duckdb_conn (DuckDBPyConnection): Connection to the DB.
    """
    duckdb_conn.execute(
        f"DROP TABLE IF EXISTS {table_name};"
    )
    duckdb_conn.execute(
        f"CREATE TABLE IF NOT EXISTS {table_name} (A TEXT, K INT);"
    )


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
    g: Graph,
    table_name: str = "G",
) -> None:
    """Inserts the data into the table.

    Args:
        db_conn (DuckDBPyConnection): Connection to the database.
        g (Graph): Loaded graph.
        table_name (str, optional): Name of the table. Defaults to "G".
    """
    insert_data_query: str = build_query_string_for_data(
        g, table_name
    )

    db_conn.execute(insert_data_query)


def insert_delete_delta_data(
    db_conn: DuckDBPyConnection,
    g: Graph,
    table_name: str = "delta_G",
    insert: bool = True,
) -> None:
    """Builds up the data that gets changed in the table.

    Args:
        db_conn (duckdb.DuckDBPyConnection): Connection with the database.
        g (rdflib.Graph): Graph with the data.
        data (str): The data that gets changed
        insert (bool, optional): If the data is inserted or deleted. Defaults to True.
    """
    # table_name: str = "delta_G"
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
    data_graph: Graph,
    ins_graph: Graph | None = None,
    del_graph: Graph | None = None,
) -> None:
    """Builds up the data to compare in DuckDB.

    Args:
        duckdb_conn (DuckDBPyConnection): Connection to the DB.
        data_graph (Graph): Graph with the data.
        ins_graph (Graph, optional): Graph with the inserted data. Defaults to None.
        del_graph (Graph, optional): Graph with the deleted data. Defaults to None.
    """
    import incremental_query_parser as iqp

    # Read the data file and put original data into the database
    build_table("R1", duckdb_conn)
    if data_file is not None:
        insert_data(duckdb_conn, data_graph, "R1")

    build_table("R2", duckdb_conn)
    build_table("R2_prep", duckdb_conn)
    # Read the deleted data file and put deleted data into the database's delta G table.
    if del_graph is not None:
        insert_delete_delta_data(
            duckdb_conn, del_graph, "R2", insert=False
        )

    # Read the inserted data file and put inserted data into the database's delta G table.
    if ins_graph is not None:
        insert_delete_delta_data(
            duckdb_conn, ins_graph, "R2", insert=True
        )


def load_graph(data_file: str) -> Graph:
    """Loads the graphs from the data files.

    Args:
        data_files (str): Data files to load.

    Returns:
        list[Graph]: List of graphs.
    """
    import incremental_query_parser as iqp

    data: str = iqp.readQueryFile(data_file)
    return Graph().parse(data=data)


def run_queries_time(
    query: str,
    data_graph: Graph,
    duckdb_conn: DuckDBPyConnection,
    ins_graph: Graph | None = None,
    del_graph: Graph | None = None,
    runs: int = 5,
) -> float:
    """Runs the full outer join query for a given number of times.

    Args:
        query (str): Query to run.
        data_graph (Graph): Graph with the data.
        duckdb_conn (DuckDBPyConnection): Connection to the database.
        ins_graph (Graph, optional): Graph with the inserted data. Defaults to None.
        del_graph (Graph, optional): Graph with the deleted data. Defaults to None.
        runs (int, optional): Amount of times to run the query. Defaults to 5.

    Returns:
        float: Average amount of time to run the query.
    """
    import time

    print("Building up data...")
    build_up_data(
        duckdb_conn, data_graph, ins_graph, del_graph
    )

    avg_time: float | None = None
    for i in range(runs):
        print(f"Run {i + 1} of {runs}")
        start = time.time()
        duckdb_conn.execute(query)
        end = time.time()
        if avg_time is None:
            avg_time = (end - start) * 1000
        else:
            avg_time = (
                avg_time + ((end - start) * 1000)
            ) / 2
        print(
            "Time taken: ",
            end - start,
            "\nAverage time: ",
            avg_time,
        )
        if i < runs - 1:
            print("Building up data...")
            build_up_data(
                duckdb_conn,
                data_graph,
                ins_graph,
                del_graph,
            )

    if avg_time is None:
        raise ValueError("Average time is None.")

    return avg_time


def save_results_to_file(
    file_name: str,
    time_arr_outer_join: ndarray,
    time_arr_group_by: ndarray,
) -> None:
    """Save the results to a file.

    Args:
        file_name (str): The file name to save the results to.
        time_arr_outer_join (ndarray): Time array for the full outer join.
        time_arr_group_by (ndarray): Time array for the group by sum.
    """
    with open(file_name, "w") as f:
        f.write("Full Outer Join\n")
        for time in time_arr_outer_join:
            f.write(f"{time}\n")
        f.write("Group By Sum\n")
        for time in time_arr_group_by:
            f.write(f"{time}\n")


def test_drop_vs_delete(
    table_name: str,
    g: Graph,
    duckdb_conn: DuckDBPyConnection,
    amount_of_tests: int = 10,
) -> tuple[float, float]:
    """Tests the drop table vs delete from table method.

    Args:
        table_name (str): Name of the table
        g (Graph): Graph with data to be inserted.
        duckdb_conn (DuckDBPyConnection): Connection to the database
    """
    import time

    avg_time_drop: float | None = None
    avg_time_delete: float | None = None

    for i in range(amount_of_tests):
        print(f"Run {i + 1} of {amount_of_tests}")
        print("Running the drop table method...")
        start = time.time()
        build_table_drop(table_name, duckdb_conn)
        end = time.time()
        insert_data(duckdb_conn, g, table_name)
        avg_time_drop = (
            avg_time_drop + (end - start)
            if avg_time_drop is not None
            else (end - start)
        )

        print("Running the delete from table method...")
        start = time.time()
        build_table(table_name, duckdb_conn)
        end = time.time()
        insert_data(duckdb_conn, g, table_name)
        avg_time_delete = (
            avg_time_delete + (end - start)
            if avg_time_delete is not None
            else (end - start)
        )

    if avg_time_drop is None or avg_time_delete is None:
        raise ValueError("Average time is None.")

    return avg_time_drop, avg_time_delete


if __name__ == "__main__":
    import argparse

    # Argument parser
    parser = argparse.ArgumentParser(
        description="Build up the full outer join query."
    )
    parser.add_argument(
        "-i",
        "--insertion_file",
        type=str,
        dest="t1",
        help="The file of the to insert data.",
        nargs="*",
    )
    parser.add_argument(
        "-d",
        "--deletion_file",
        type=str,
        dest="t2",
        help="The file of the to delete data.",
        nargs="*",
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

    # Import the necessary modules
    from eval_incremental import duckdb_conn
    from numpy import array, ndarray, append
    from plots import build_compare_plot

    drop_arr: ndarray = array([])
    delete_arr: ndarray = array([])
    # Run the test for the drop vs delete method
    for data_file in args.data_file:
        print(
            f"\nRunning the drop vs delete test with {data_file}..."
        )
        print(f"Loading graphs from {data_file}...")
        og_graph: Graph = load_graph(data_file)

        print("Running the drop vs delete test...")
        time_drop, time_delete = test_drop_vs_delete(
            "Test_table", og_graph, duckdb_conn, args.runs
        )

        print(f"Time for drop: {time_drop}")
        print(f"Time for delete: {time_delete}")

        drop_arr = append(drop_arr, time_drop)
        delete_arr = append(delete_arr, time_delete)

    # Build the plot
    build_compare_plot.compare_times_plot(
        drop_arr,
        delete_arr,
        "Drop Table",
        "Delete From Table",
        args.data_file,
    )
    exit()

    # Initialize the time arrays
    time_arr_outer_join: ndarray = array([])
    time_arr_group_by: ndarray = array([])

    # Build up the queries
    query: str = build_up_full_outer_join("R1", "R2")
    query_group_by: str = build_up_group_by_sum("R1", "R2")

    # Initialize insertion and deletion count
    ins_count: int = 0
    del_count: int = 0

    # Run the queries for each data file
    # Next insertion and deletion file get loaded with the next data file if multiple are present
    # otherwise the last one that was loaded is used.
    for data_file in args.data_file:
        print(f"\nRunning the queries with {data_file}...")
        print(f"Loading graphs from {data_file}...")
        og_graph: Graph = load_graph(data_file)
        ins_graph: Graph | None = None
        del_graph: Graph | None = None
        if args.t1 is not None:
            if ins_count < len(args.t1):
                print(
                    f"Loading insertion graph from {args.t1[ins_count]}..."
                )
                ins_graph = load_graph(args.t1[ins_count])
                ins_count += 1
        if args.t2 is not None:
            if del_count < len(args.t2):
                print(
                    f"Loading deletion graph from {args.t2[del_count]}..."
                )
                del_graph = load_graph(args.t2[del_count])
                del_count += 1

        print("Running the full outer join query...")
        run_time_full_outer_join: float = run_queries_time(
            query,
            og_graph,
            duckdb_conn,
            ins_graph,
            del_graph,
            args.runs,
        )

        time_arr_outer_join = append(
            time_arr_outer_join, run_time_full_outer_join
        )

        print("\nRunning the group by sum query...")
        run_time_group_by_sum: float = run_queries_time(
            query_group_by,
            og_graph,
            duckdb_conn,
            ins_graph,
            del_graph,
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
    save_results_to_file(
        "group_by_full_outer_join_results_same_size.txt",
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
