"""
Handles the database logic for the multiviews.
"""

from os.path import join
from duckdb import DuckDBPyConnection, connect


def connect_main_db(db_path: str) -> DuckDBPyConnection:
    """Connects to a DuckDB database at the specified path.

    Args:
        db_path (str): The path to the DuckDB database file.

    Returns:
        DuckDBPyConnection: A connection object to the DuckDB database.
    """
    try:
        conn = connect(database=db_path)
    except Exception as e:
        raise ConnectionError(
            f"Failed to connect to DuckDB database at {db_path}: {e}"
        ) from e
    return conn


def create_table(
    table_name: str, conn: DuckDBPyConnection
) -> None:
    """Creates the table to pod all the data in a relation schema.

    Args:
        table_name (str): Table name to write.
        conn (DuckDBPyConnection): Connection to the database to write it to.
    """
    conn.execute(
        f"CREATE OR REPLACE TABLE {table_name}"
        + " (pod_id STRING, s STRING, p STRING, o STRING, k_count INT);"
    )


def create_reif_table(
    table_name: str,
    conn: DuckDBPyConnection,
) -> None:
    """Creates empty table for the reification version for the database.

    Args:
        table_name (str): Table name to write.
        conn (DuckDBPyConnection): Connection to the database to write to.
    """
    conn.execute(
        f"CREATE OR REPLACE TABLE {table_name}"
        + " (s STRING, p STRING, o STRING, k_count INT);"
    )


def create_multi_pod_view(
    conn: DuckDBPyConnection,
    view_name: str,
    delta_view_name: str,
    nu_view_name: str,
    reif: bool = False,
) -> None:
    """Creates a view in the DuckDB database to combine data from multiple pods."""
    # Create mutex lock for thread safety if needed
    if not reif:
        create_table(view_name, conn)
    else:
        create_reif_table(view_name, conn)
    # Create the delta
    create_table(delta_view_name, conn)
    # Create the nu_table
    create_table(nu_view_name, conn)


# print(turtle_to_insert)


def sql_query(
    output_dir: str,
    aggregator_db: DuckDBPyConnection,
    query_to_execute: str,
    drop: bool = False,
) -> None:
    """Executes a given sql query in the given directory.

    Args:
        output_dir (str): Directory where the query is located.
        aggregator_db (DuckDBPyConnection): Connection to the database.
        query_to_execute (str): Query to execute.
        drop (bool, optional): Drops all tables if True. Defaults to False.
    """
    if drop:
        _drop_tables(output_dir, aggregator_db)
        print("Dropping the tables.")
    # Execute the from SQL queries
    with open(
        join(output_dir, query_to_execute),
        "r",
        encoding="utf-8",
    ) as handle:
        aggregator_db.execute(handle.read())


def _drop_tables(
    output_dir: str, aggregator_db: DuckDBPyConnection
) -> None:
    with open(
        join(output_dir, "drop_tables.sql"),
        encoding="utf-8",
    ) as drop_handle:
        aggregator_db.execute(drop_handle.read())
    with open(
        join(output_dir, "drop_delta_tables.sql"),
        encoding="utf-8",
    ) as drop_handle:
        aggregator_db.execute(drop_handle.read())
