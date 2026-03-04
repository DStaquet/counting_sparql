"""
Constructs a singular file of the query in SQL to support incremental view maintenance.
"""

import sqlparse  # type: ignore
from rdflib.plugins.sparql.parserutils import CompValue

from SQL_Constructor.table_constructor import get_table_name


class TableNames:
    """Class for passing the table names"""

    def __init__(self, og_table_name: str, delta_table_name: str) -> None:
        self.og_table_name = og_table_name
        self.delta_table_name = delta_table_name
        self.join_query, self.nu_table_name = self._join_query_and_nu_table_name()

    def _join_query_and_nu_table_name(self) -> tuple[str, str]:
        """Sets the join query and nu table name

        Returns:
            tuple[str, str]: Join query and nu table name.
        """
        self.join_query, self.nu_table_name = join_base_graph_and_delta_graph(
            self.og_table_name, self.delta_table_name
        )
        return self.join_query, self.nu_table_name

    def __str__(self) -> str:
        return (
            f"TableNames(og_table_name: {self.og_table_name},"
            + f" delta_table_name: {self.delta_table_name},"
            + f" join_query: {self.join_query},"
            + f" nu_table_name: {self.nu_table_name})"
        )


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
        curr_query = queries_dict[key][0] + queries_dict[key][1]
    else:
        query = queries_dict[key]
        if isinstance(query, str):
            curr_query = query
        else:
            raise ValueError("Query is not a string")

    if "p" in part:
        return entire_run_query(part.p, queries_dict) + curr_query
    elif "p1" in part and "p2" in part:
        return (
            entire_run_query(part.p1, queries_dict)
            + entire_run_query(part.p2, queries_dict)
            + curr_query
        )
    return curr_query


def join_base_graph_and_delta_graph(
    table_name: str, delta_table_name: str
) -> tuple[str, str]:
    """Joins a given base graph and delta graph and return a tuple with the nu_name as well as
    the query to join the tables.

    Args:
        table_name (str): Table of the base graph to join
        delta_table_name (str): Table of the delta graph to join

    Returns:
        str: Query to join the base and delta graphs and nu_table name.
    """
    create_clause = f"CREATE TEMP TABLE nu_{table_name} AS "
    select_clause: str = "SELECT s, p, o, G.k_count + delta_G.k_count AS k_count "
    from_clause: str = (
        f"FROM {table_name} AS G NATURAL JOIN {delta_table_name} AS delta_G;"
    )
    return (
        sqlparse.format(create_clause + select_clause + from_clause, reindent=True)  # type: ignore
        + "\n\n",
        "nu_" + table_name,
    )
