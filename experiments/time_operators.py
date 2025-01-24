from rdflib.plugins.sparql.parserutils import CompValue
from time import time
from duckdb import DuckDBPyConnection
from os.path import join

from build_data import readQueryFile
from SQL_Constructor.base_constructor import get_table_name


def timing_per_operator(
    part: CompValue,
    query_dir: str,
    duckdb_conn: DuckDBPyConnection,
) -> dict[str, float]:
    """Times the operations per operator

    Args:
        part (CompValue): The algebra of the query

    Returns:
        dict[str, float]: The time per operator
    """
    if part.p != None or (
        part.p1 != None and part.p2 != None
    ):
        if part.p != None:
            timings = timing_per_operator(
                part.p, query_dir, duckdb_conn
            )
        else:
            timings = timing_per_operator(
                part.p1, query_dir, duckdb_conn
            )
            timings.update(
                timing_per_operator(
                    part.p2, query_dir, duckdb_conn
                )
            )
    else:
        timings: dict[str, float] = dict()

    # Read query file
    query_str: str = readQueryFile(
        join(query_dir, get_table_name(part)) + ".sql"
    )

    # Scratch time
    start_timer: float = time()
    duckdb_conn.execute(query_str)
    end_timer: float = time()
    timings[get_table_name(part)] = (
        end_timer - start_timer
    ) * 1000

    # Incremental time
    delta_query_str = readQueryFile(
        join(query_dir, "delta_" + get_table_name(part))
        + ".sql"
    )

    start_timer = time()
    duckdb_conn.execute(delta_query_str)
    end_timer = time()
    timings["delta_" + get_table_name(part)] = (
        end_timer - start_timer
    ) * 1000

    return timings
