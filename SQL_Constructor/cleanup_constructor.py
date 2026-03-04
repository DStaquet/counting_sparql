"""Module that puts the generated nu tables into their respective base tables for the next iteration."""

from rdflib.plugins.sparql.parserutils import CompValue
import sqlparse  # type: ignore

from SQL_Constructor.table_constructor import get_table_name


def _join_base_and_delta_tables(table_name: str, nu_table_name: str) -> str:
    """Puts the values from nu into base.

    Args:
        table_name (str): Base table name.
        nu_table_name (str): Nu table name.

    Returns:
        str: Query to put nu tble into base for next iteration.
    """
    return f"CREATE OR REPLACE TABLE {table_name} AS SELECT * FROM {nu_table_name};"


def recur_query_join_base_and_delta_tables(part: CompValue) -> tuple[str, str]:
    """Recursively joins the base and delta tables for all subqueries.

    Args:
        part (CompValue): The given query.
        table_names (TableNames): The table names.

    Returns:
        str: Query to put nu tble into base for next iteration for all subqueries.
    """
    if part.name in ["Group", "Extend"]:
        return recur_query_join_base_and_delta_tables(part.p)

    table_name = get_table_name(part)
    nu_table_name = "nu_" + table_name
    curr_query = (
        sqlparse.format(  # type: ignore
            _join_base_and_delta_tables(table_name, nu_table_name),
            reindent=True,
            keyword_case="upper",
        )
        + "\n\n"
    )

    if "p" not in part and "p1" not in part:
        if part.name == "BGP":
            return (curr_query, table_name)
        else:
            return ("", table_name)
    else:
        if "p" in part:
            return (
                recur_query_join_base_and_delta_tables(part.p)[0] + curr_query,
                table_name,
            )
        elif "p1" in part and "p2" in part:
            p1_query, _ = recur_query_join_base_and_delta_tables(part.p1)
            p2_query, _ = recur_query_join_base_and_delta_tables(part.p2)
            return (
                p1_query + p2_query + curr_query,
                table_name,
            )
        else:
            raise ValueError("Invalid query part")
