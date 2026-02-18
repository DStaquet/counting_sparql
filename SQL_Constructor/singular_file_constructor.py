"""
Constructs a singular file of the query in SQL to support incremental view maintenance.
"""

from rdflib.plugins.sparql.parserutils import CompValue

from SQL_Constructor.table_constructor import get_table_name


def entire_run_query(
    part: CompValue,
    queries_dict: dict[str, str] | dict[str, list[str]],
) -> str:
    """Runs the given query.

    Args:
        part (CompValue): The given query.
        duckdb_conn (DuckDBPyConnection): Connection to the database.
    """
    if part.name in ["Group", "Extend"]:
        return entire_run_query(part.p, queries_dict)
    key = get_table_name(part)
    curr_query = ""
    if isinstance(queries_dict[key], list):
        curr_query = (
            queries_dict[key][0] + queries_dict[key][1]
        )
    else:
        query = queries_dict[key]
        if isinstance(query, str):
            curr_query = query
        else:
            raise ValueError("Query is not a string")

    if "p" in part:
        return (
            entire_run_query(part.p, queries_dict)
            + curr_query
        )
    elif "p1" in part and "p2" in part:
        return (
            entire_run_query(part.p1, queries_dict)
            + entire_run_query(part.p2, queries_dict)
            + curr_query
        )
    return curr_query
