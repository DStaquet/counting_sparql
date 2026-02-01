"""
Experiments for connecting multiple solid pods to a DuckDB database and storing them as one view.
"""

from argparse import ArgumentParser
from threading import Thread, Lock

from requests import get, RequestException
from duckdb import DuckDBPyConnection, connect
from rdflib import Graph


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


def __create_multi_pod_view(
    conn: DuckDBPyConnection,
    view_name: str,
) -> None:
    """Creates a view in the DuckDB database to combine data from multiple pods."""
    # Create mutex lock for thread safety if needed
    conn.execute(
        f"CREATE OR REPLACE TABLE {view_name}"
        + " (pod_id STRING,subject STRING, predicate STRING, object STRING);"
    )


def __parse_pod_data(
    pod_data: str,
) -> list[tuple[str, str, str, str]]:
    """Parses RDF data from a pod and returns it as a list of tuples.

    Args:
        pod_data (str): The RDF data in string format.
    Returns:
        list[tuple[str, str, str, str]]: A list of tuples
            containing pod_id, subject, predicate, and object.
    """
    g = Graph()
    g.parse(data=pod_data, format="turtle")
    pod_id = "pod_example"  # This should be derived from the pod data or URL
    triples = []
    for subj, pred, obj in g:
        triples.append(
            (pod_id, str(subj), str(pred), str(obj))
        )
    return triples


def __put_pod_data(
    conn: DuckDBPyConnection,
    pod_name: str,
    triples: list[tuple[str, str, str, str]],
    db_lock: Lock,
):
    """Inserts pod data into the multi-pod view in the DuckDB database."""
    # Create mutex lock for thread safety if needed
    with db_lock:
        for triple in triples:
            conn.execute(
                "INSERT INTO multi_pod_view (pod_id, subject, predicate, object)"
                + f" VALUES ('{pod_name}', '{triple[1]}', '{triple[2]}', '{triple[3]}');",
            )


def __get_pod_data(pod_url: str) -> str:
    """Fetches data from the specified pod URL.

    Args:
        pod_url (str): The URL of the pod to fetch data from.

    Returns:
        str: The text content retrieved from the pod.
    """
    try:
        response = get(pod_url, timeout=10)
    except RequestException:
        return f"Error fetching data from pod {pod_url}"
    finally:
        print(
            f"Data fetched from pod {pod_url}: {response.text}"
        )
    return response.text


def handle_pod_connection(
    conn: DuckDBPyConnection, pod_url: str, db_lock: Lock
):
    """Handles the connection to a pod and stores its data in the DuckDB database.

    Args:
        conn (DuckDBPyConnection): The DuckDB connection object.
        pod_url (str): The URL of the pod to connect to.
    """
    pod_data = __get_pod_data(pod_url)
    triples = __parse_pod_data(pod_data)
    __put_pod_data(conn, pod_url, triples, db_lock)
    print(f"Data from pod {pod_url} stored in database.")


if __name__ == "__main__":
    arg_parser = ArgumentParser(
        description="Connect to DuckDB database"
    )
    arg_parser.add_argument(
        "-db",
        "--database",
        help="The DuckDB database file to connect to",
        default=":memory:",
    )
    arg_parser.add_argument(
        "-p",
        "--pods",
        nargs="+",
        help="List of pod URLs to connect to",
        required=True,
    )
    args = arg_parser.parse_args()

    # Connect to the DuckDB database
    duckdb_connection = connect_main_db(args.database)
    __create_multi_pod_view(
        duckdb_connection, "multi_pod_view"
    )

    # We will connect to three pods multithreadedly
    threads = []
    lock = Lock()
    for pod in args.pods:
        thread = Thread(
            target=handle_pod_connection,
            args=(duckdb_connection, pod, lock),
        )
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()
