"""
Submodule of multiviews that handles the logic of dealing with the pods.
"""

from datetime import date
from os.path import join
from threading import Lock
from requests import RequestException, get, put

from duckdb import DuckDBPyConnection  # pylint: disable=import-error

from example_constructor.graph_constructor import (
    Graph as custom_Graph,
)
from example_constructor.we_are_poc_constructor import (
    generate_random_ratings,
)
from multiviews.rdf_handler import parse_pod_data


def _put_pod_data_in_database_reif(
    conn: DuckDBPyConnection,
    pod_name: str,
    triples: list[tuple[str, str, str, str]],
    db_lock: Lock,
    table_name: str,
    given_uri: str,
    ins_or_del: int = 1,
) -> None:
    with db_lock:
        known_ratings: dict[str, str] = {}
        for triple in triples:
            if triple[1] not in known_ratings:
                triple_id = str(abs(hash(triple)))
                conn.execute(
                    f"INSERT INTO {table_name} (s, p, o, k_count) VALUES "
                    + f"('{pod_name}', '{given_uri}hasRating', 'triple_id_{triple_id}', 1)"
                )
                known_ratings[triple[1]] = triple_id
            else:
                triple_id = known_ratings[triple[1]]
            conn.execute(
                f"INSERT INTO {table_name} (s, p, o, k_count) VALUES "
                + f"('triple_id_{triple_id}', '{triple[2]}', '{triple[3]}', {ins_or_del})"
            )


def _put_pod_data_in_database(
    conn: DuckDBPyConnection,
    pod_name: str,
    triples: list[tuple[str, str, str, str]],
    db_lock: Lock,
    table_name: str,
    ins_or_del: int = 1,
) -> None:
    """Inserts pod data into the multi-pod view in the DuckDB database."""
    # Create mutex lock for thread safety if needed
    with db_lock:
        for triple in triples:
            conn.execute(
                f"INSERT INTO {table_name} (pod_id, s, p, o, k_count) VALUES "
                + f"('{pod_name}', '{triple[1]}', '{triple[2]}', '{triple[3]}', {ins_or_del});",
            )


def get_pod_data(pod_url: str) -> str:
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
        print(f"Data fetched from pod {pod_url}.")
    return response.text


def _put_data_in_pod(
    pod_url: str,
    filename: str,
    data: custom_Graph | None = None,
    turtle_to_insert: str | None = None,
) -> None:
    if not turtle_to_insert and data:
        turtle_to_insert = data.graph_to_turtle(
            "http://example.org/node/",
            "http://example.org/edges/",
        )

    put(
        pod_url + filename,
        data=turtle_to_insert,
        headers={"Content-Type": "text/turtle"},
        timeout=10,
    )

    print(f"Put data for hospitals in pod {pod_url} in file {filename}.")


def _put_delta_in_pod(
    deltas: tuple[custom_Graph, custom_Graph, custom_Graph],
    pod_url: str,
    delta_filenames: tuple[str, str],
    nu_filename: str,
) -> None:
    delta_del, delta_ins, nu_graph = deltas

    # Insert the deletions
    _put_data_in_pod(pod_url, delta_filenames[0], delta_del)
    # Insert the insertions
    _put_data_in_pod(pod_url, delta_filenames[1], delta_ins)

    # Insert the nu graph
    _put_data_in_pod(pod_url, nu_filename, nu_graph)


def handle_delta_pod_connection(
    conn: DuckDBPyConnection,
    pod_url: str,
    filename: str,
    db_lock: Lock,
    table_names: tuple[str, str],
) -> None:
    """Handles the delta pod connection

    Args:
        conn (DuckDBPyConnection): Connection to the database.
        pod_url (str): URL to the current pod.
        filename (str): Filename to write the data in.
        db_lock (Lock): Lock to use for concurrency.
        table_names (tuple[str, str]): Table names to write in the database.
    """
    # Get the delta data
    ins_data = get_pod_data(join(pod_url, "delta_ins_" + filename))
    del_data = get_pod_data(join(pod_url, "delta_del_" + filename))
    ins_triples = parse_pod_data(ins_data)
    del_triples = parse_pod_data(del_data)
    _put_pod_data_in_database(conn, pod_url, ins_triples, db_lock, table_names[0])
    _put_pod_data_in_database(
        conn,
        pod_url,
        del_triples,
        db_lock,
        table_names[0],
        -1,
    )
    # Get the nu data
    nu_data = get_pod_data(join(pod_url, "nu_" + filename))
    nu_triples = parse_pod_data(nu_data)
    _put_pod_data_in_database(conn, pod_url, nu_triples, db_lock, table_names[1])


def handle_pod_connection(
    conn: DuckDBPyConnection,
    pod_url: str,
    filename: str,
    db_lock: Lock,
    graphs_and_deltas: tuple[
        custom_Graph,
        tuple[custom_Graph, custom_Graph, custom_Graph],
    ],
    table_name: str,
) -> None:
    """Handles the connection to a pod and stores its data in the DuckDB database.

    Args:
        conn (DuckDBPyConnection): The DuckDB connection object.
        pod_url (str): The URL of the pod to connect to.
    """
    data, deltas = graphs_and_deltas
    _put_data_in_pod(pod_url, filename, data)
    _put_delta_in_pod(
        deltas,
        pod_url,
        ("delta_ins_" + filename, "delta_del_" + filename),
        "nu_" + filename,
    )
    # Get the normal data
    pod_data = get_pod_data(join(pod_url, filename))
    triples = parse_pod_data(pod_data)
    _put_pod_data_in_database(conn, pod_url, triples, db_lock, table_name)
    print(f"Data from pod {pod_url} stored in database.")


def handle_pod_connection_we_are(
    pod_url: str,
    filename: str,
    triple_amount: int,
    hospital_amount: int,
    rating_interval: tuple[int, int],
    dates: tuple[date, date],
    duckdb_conn: DuckDBPyConnection,
    lock: Lock,
    table_name: str,
    delta_amount: int,
    reification: bool = False,
) -> None:
    """Handles the we are POC connection cases.

    Args:
        pod_url (str): URL to each pod.
        filename (str): Filename to store the data in.
        triple_amount (int): Amount of triples to generate.
        hospital_amount (int): Amount of possible hospitals.
        rating_interval (tuple[int, int]): Rating interval.
        dates (tuple[date, date]): Interval of dates to choose.
    """
    # Put the normal data.
    (
        turtle_to_insert,
        delete_delta,
        insert_delta,
        nu_to_insert,
    ) = generate_random_ratings(
        "http://example.org/we_are/",
        triple_amount,
        hospital_amount,
        rating_interval,
        dates,
        delta_amount,
    )

    _put_data_in_pod(pod_url, filename, turtle_to_insert=turtle_to_insert)
    pod_data = get_pod_data(join(pod_url, filename))
    triples = parse_pod_data(pod_data)
    if not reification:
        _put_pod_data_in_database(duckdb_conn, pod_url, triples, lock, table_name)
    else:
        _put_pod_data_in_database_reif(
            duckdb_conn,
            pod_url,
            triples,
            lock,
            table_name,
            "http://example.org/we_are/",
        )
        print("Put down data reified.")

    # Put down delta data
    _put_data_in_pod(
        pod_url,
        "delta_del_" + filename,
        turtle_to_insert=delete_delta,
    )
    _put_data_in_pod(
        pod_url,
        "delta_ins_" + filename,
        turtle_to_insert=insert_delta,
    )

    # Put down the nu graph
    _put_data_in_pod(
        pod_url,
        "nu_" + filename,
        turtle_to_insert=nu_to_insert,
    )
