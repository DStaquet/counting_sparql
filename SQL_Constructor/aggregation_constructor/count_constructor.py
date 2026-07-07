"""Modules to construct SQL queries for COUNT aggregation"""

from rdflib.plugins.sparql.parserutils import CompValue

from SQL_Constructor.table_constructor import (
    get_table_name,
)

# def count_join_query2(
#     aggregate_values: list[CompValue],
#     aggregate_sample: CompValue,
#     part: CompValue,
#     delta_part: str = "",
# ) -> str:
#     """Constructs the SQL query for a COUNT aggregation.

#     Args:
#         aggregate_obj (CompValue): Object representing the COUNT aggregation
#         aggregate_sample (CompValue): Sample variable for the aggregation
#     Returns:
#         str: SQL query for the COUNT aggregation
#     """
#     pass


def count_join_query(
    aggregate_values: list[CompValue],
    aggregate_sample: CompValue,
    part: CompValue,
    delta_part: str = "",
) -> str:
    """Generates the count join query from SPARQL to SQL

    Args:
        aggregate_values (list[CompValue]): Values to aggregate on
        aggregate_sample (CompValue): Values to aggregate
        part (CompValue): Current part of the query
        delta_part (str, optional): Indicates a delta. Defaults to "".

    Returns:
        str: _description_
    """
    # Constructs select clause
    select_clause = (
        f"SELECT {aggregate_sample.vars}, "
        + ", ".join(
            f"COUNT(CAST ({value.vars} AS INT) * k_count) AS {value.vars}"
            for value in aggregate_values
        )
        + ", 1 AS k_count"
    )

    # Construct FROM clause
    from_clause = (
        "\nFROM " + delta_part + get_table_name(part.p.p)
    )

    # Constructs GROUP BY clause
    group_by_clause = (
        "\nGROUP BY " + aggregate_sample.vars + ";\n\n"
    )

    return select_clause + from_clause + group_by_clause
    