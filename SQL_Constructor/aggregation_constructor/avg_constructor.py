from rdflib.plugins.sparql.parserutils import CompValue


from SQL_Constructor.table_constructor import get_table_name
from SQL_Constructor.aggregation_constructor.sum_constructor import (
    sum_join_query,
)


def _count_join_query(
    aggregate_values: list[CompValue],
    aggregate_sample: CompValue,
    part: CompValue,
) -> str:
    # Constructs select clause
    select_clause = (
        f"SELECT {aggregate_sample.vars}, "
        + ", ".join(
            f"COUNT(CAST ({value.vars} AS INT) * k_count) as {value.vars}"
            for value in aggregate_values
        )
        + ", 1 as k_count"
    )

    # Construct FROM clause
    from_clause = " FROM " + get_table_name(part.p.p)

    # Constructs GROUP BY clause
    group_by_clause = (
        " GROUP BY " + aggregate_sample.vars + ";"
    )

    return select_clause + from_clause + group_by_clause


def avg_join_query(
    aggregate_values: list[CompValue],
    aggregate_sample: CompValue,
    part: CompValue,
) -> tuple[str, str, str]:
    """Constructs the SQL query for an AVG aggregation.

    Args:
        aggregate_values (list[CompValue]): Object representing the AVG aggregation.
        aggregate_sample (CompValue): Sample variable to GROUP BY on
        part (CompValue): Current part of the query.

    Returns:
        str: _description_
    """
    count_query = _count_join_query(
        aggregate_values, aggregate_sample, part
    )
    sum_query = sum_join_query(
        aggregate_values, aggregate_sample, part
    )

    # Constructs select clause
    select_clause = (
        f"SELECT {aggregate_sample.vars}, "
        + ", ".join(
            f"sum_agg.{value.vars} / count_agg.{value.vars} as {value.vars}"
            for value in aggregate_values
        )
        + ", 1 as k_count"
    )

    # Construct FROM clause
    from_clause = (
        " FROM "
        + get_table_name(part)
        + "_sum as sum_agg, "
        + get_table_name(part)
        + "_count as count_agg"
    )

    # Constructs GROUP BY clause
    group_by_clause = (
        " GROUP BY " + aggregate_sample.vars + ";"
    )

    return (
        select_clause + from_clause + group_by_clause,
        sum_query,
        count_query,
    )
