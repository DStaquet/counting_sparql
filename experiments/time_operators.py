from rdflib.plugins.sparql.parserutils import CompValue
from time import time
from duckdb import DuckDBPyConnection
from os.path import join

from build_data import readQueryFile
from SQL_Constructor.table_constructor import get_table_name


def timing_dict_combiner(
    dict1: dict[str, dict[str, float]],
    dict2: dict[str, dict[str, float]],
) -> dict[str, dict[str, float]]:
    """Combines two timing dictionaries

    Args:
        dict1 (dict[str, dict[str, float]]): First dictionary
        dict2 (dict[str, dict[str, float]]): Second dictionary

    Returns:
        dict[str, dict[str, float]]: Returns the combined dictionary
    """
    if sorted(dict1.keys()) != sorted(dict2.keys()):
        raise ValueError(
            "The keys of the dictionaries do not match"
        )

    combined_dict: dict[str, dict[str, float]] = dict()

    for key in dict1.keys():
        combined_dict[key] = dict()
        for sub_key in dict1[key].keys():
            combined_dict[key][sub_key] = (
                dict1[key][sub_key] + dict2[key][sub_key]
            )

    return combined_dict


def timer(
    query_dir: str,
    part: CompValue,
    increm_prefix: str,
    duckdb_conn: DuckDBPyConnection,
) -> float:
    # Read query file
    query_str: str = readQueryFile(
        join(
            query_dir, increm_prefix + get_table_name(part)
        )
        + ".sql"
    )

    start_timer: float = time()
    duckdb_conn.execute(query_str)
    end_timer: float = time()

    return (end_timer - start_timer) * 1000


def timing_per_operator(
    part: CompValue,
    query_dir: str,
    duckdb_conn: DuckDBPyConnection,
    increm: bool = False,
) -> dict[str, dict[str, float]]:
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
                part.p, query_dir, duckdb_conn, increm
            )
        else:
            timings = timing_per_operator(
                part.p1, query_dir, duckdb_conn, increm
            )
            timings.update(
                timing_per_operator(
                    part.p2, query_dir, duckdb_conn, increm
                )
            )
    else:
        timings: dict[str, dict[str, float]] = dict()

    if not increm:
        timing_scratch: float = timer(
            query_dir, part, "", duckdb_conn
        )
        timings[get_table_name(part)] = {
            "scratch": timing_scratch,
        }
    else:
        timing_increm: float = timer(
            query_dir, part, "delta_", duckdb_conn
        )
        _ = timer(query_dir, part, "nu_", duckdb_conn)
        timings[get_table_name(part)] = {
            "incremental": timing_increm,
        }

    return timings


def time_operators_both(
    scratch: dict[str, dict[str, float]],
    increm: dict[str, dict[str, float]],
) -> dict[str, dict[str, float]]:
    """Combines both operators into one dictionary.

    Args:
        scratch (dict[str, dict[str, float]]): Scratch dictionary
        increm (dict[str, dict[str, float]]): Incremental dictionary

    Returns:
        dict[str, dict[str, float]]: Timing dictionary of both operators
    """
    if sorted(scratch.keys()) != sorted(increm.keys()):
        raise ValueError(
            "The keys of the dictionaries do not match"
        )

    combined_dict: dict[str, dict[str, float]] = dict()

    for key in scratch.keys():
        combined_dict[key] = {
            "scratch": scratch[key]["scratch"],
            "incremental": increm[key]["incremental"],
        }

    return combined_dict
