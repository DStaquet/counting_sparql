import duckdb
from rdflib.graph import Graph
from pandas import DataFrame
import sqlparse


def build_query_string_for_data(
    g: Graph, table_name: str, delete_count: int = 1
) -> str:
    """Builds the string for the insertion"""
    rdf_input_data = ""
    known_tuples: dict[tuple[str, str, str], int] = dict()
    for s, p, o in g:
        if (s, p, o) in known_tuples:
            known_tuples[
                (str(s), str(p), str(o))
            ] += delete_count
        else:
            known_tuples[(str(s), str(p), str(o))] = (
                delete_count
            )
    for s, p, o in known_tuples:
        rdf_input_data += f"('{s}', '{p}', '{o}', {known_tuples[(s, p, o)]}),\n"
    insert_str = (
        f"INSERT INTO {table_name} VALUES {rdf_input_data};"
    )
    return insert_str


def drop_delta_table(
    db_conn: duckdb.DuckDBPyConnection, table_name: str
) -> None:
    """Drops the delta table.

    Args:
        db_conn (duckdb.DuckDBPyConnection): Connection with the database.
        table_name (str): Name of the table to drop.
    """
    db_conn.execute(f"DELETE FROM {table_name};")


def create_delta_table(
    db_conn: duckdb.DuckDBPyConnection, table_name: str
) -> None:
    """Creates the delta table.

    Args:
        db_conn (duckdb.DuckDBPyConnection): Connection with the database.
        table_name (str): Name of the table to create.
    """
    db_conn.execute(
        f"CREATE TABLE IF NOT EXISTS {table_name} (s TEXT, p TEXT, o TEXT, k_count INT);"
    )


def insert_delete_delta_data(
    db_conn: duckdb.DuckDBPyConnection,
    data: str,
    table_name: str = "delta_G",
) -> None:
    """Builds up the data that gets changed in the table.

    Args:
        db_conn (duckdb.DuckDBPyConnection): Connection with the database.
        data (str): The data that gets changed
    """
    # table_name: str = "delta_G"
    g: Graph = Graph().parse(data=data)
    insert_data_query: str = build_query_string_for_data(
        g, table_name, -1
    )

    db_conn.execute(
        f"CREATE TABLE IF NOT EXISTS {table_name} (s TEXT, p TEXT, o TEXT, k_count INT);"
    )
    db_conn.execute(insert_data_query)


def insert_insert_delta_data(
    db_conn: duckdb.DuckDBPyConnection,
    data: str,
    table_name: str = "delta_G",
) -> None:
    """Builds up the data that gets added to the table.

    Args:
        db_conn (duckdb.DuckDBPyConnection): Connection to the database
        data (str): The given data
    """
    # table_name: str = "delta_G"
    g: Graph = Graph().parse(data=data)
    insert_data_query: str = build_query_string_for_data(
        g, table_name, 1
    )

    db_conn.execute(
        f"CREATE TABLE IF NOT EXISTS {table_name} (s TEXT, p TEXT, o TEXT, k_count INT);"
    )
    db_conn.execute(insert_data_query)

    df: DataFrame = db_conn.sql(
        f"SELECT * FROM {table_name};"
    ).df()


def insert_nu_data(
    db_conn: duckdb.DuckDBPyConnection,
) -> None:
    """Takes the delta and original and combines them to the new version.

    Args:
        db_conn (duckdb.DuckDBPyConnection): Connection with the database.
    """
    table_name: str = "nu_G"
    og_name: str = "G"
    delta_table_name: str = "delta_G"

    # Create the nu_G table
    db_conn.execute(
        f"CREATE TABLE IF NOT EXISTS {table_name} (s TEXT, p TEXT, o TEXT, k_count INT);"
    )
    db_conn.execute(f"DELETE FROM {table_name};")
    # Create the prep_nu_G table
    db_conn.execute(
        f"CREATE TABLE IF NOT EXISTS prep_{table_name} (s TEXT, p TEXT, o TEXT, k_count INT);"
    )
    db_conn.execute(f"DELETE FROM prep_{table_name};")

    '''original full outer join: f"insert into prep_{table_name} (s, p, o, k_count) select coalesce(r1.s, r2.s) as s, coalesce(r1.p, r2.p) as p, coalesce(r1.o, r2.o) as o, coalesce(r1.k_count, 0) + coalesce(r2.k_count, 0) as k_count from {og_name} as r1 FULL OUTER JOIN {delta_table_name} as r2 ON r1.s = r2.s and r1.p = r2.p and r1.o = r2.o where (coalesce(r1.k_count, 0) + coalesce(r2.k_count, 0)) > 0;"'''
    import time as t

    insert_nu_query: str = (
        f"insert into prep_{table_name} (s, p, o, k_count) select s, p, o, k_count from {og_name};"
        + f"insert into prep_{table_name} (s, p, o, k_count) select s, p, o, k_count from {delta_table_name};"
        + f"insert into {table_name} (s, p, o, k_count) select s, p, o, sum(k_count) from prep_{table_name} group by s, p, o;"
    )
    start = t.time()
    db_conn.execute(insert_nu_query)
    end = t.time()
    print(f"Time to insert nu data: {end - start}")

    df: DataFrame = db_conn.sql(
        f"SELECT * FROM {table_name};"
    ).df()


def insert_data(
    db_conn: duckdb.DuckDBPyConnection, data: str
) -> None:
    """Build up a query string and inserts data into a table.


    Args:
        db_conn (duckdb.DuckDBPyConnection): Database connection object.
        data (str): Given data to insert into the table.
    """
    table_name: str = "G"
    g: Graph = Graph().parse(data=data)
    insert_data_query: str = build_query_string_for_data(
        g, table_name
    )

    """db_conn.execute(
        f"CREATE TABLE IF NOT EXISTS {table_name} (s TEXT, p TEXT, o TEXT, k_count INT);"
    )
    db_conn.execute(f"DELETE FROM {table_name};")"""
    db_conn.execute(insert_data_query)


if __name__ == "__main__":
    from eval_incremental import duckdb_conn
    import sys

    if len(sys.argv) < 2:
        print("Usage: python setup_data.py <data_file>")
        sys.exit(1)

    data_file = sys.argv[1]
    with open(data_file, "r") as f:
        data = f.read()
    insert_data(duckdb_conn, data)
