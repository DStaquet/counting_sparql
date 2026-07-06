"""Modules to construct AVG sparql to SQL queries from."""

from rdflib.plugins.sparql.parserutils import CompValue


from SQL_Constructor.aggregation_constructor.count_constructor import count_join_query
from SQL_Constructor.table_constructor import get_table_name
from SQL_Constructor.aggregation_constructor.sum_constructor import (
    sum_join_query,
)


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
    count_query = count_join_query(
        aggregate_values, aggregate_sample, part
    )
    sum_query = sum_join_query(
        aggregate_values, aggregate_sample, part
    )

    # Constructs select clause
    select_clause = (
        f"SELECT sum_agg.{aggregate_sample.vars}, "
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
        " WHERE sum_agg."
        + aggregate_sample.vars
        + " = count_agg."
        + aggregate_sample.vars
        + ";"
    )

    return (
        select_clause + from_clause + group_by_clause,
        sum_query,
        count_query,
    )


def delta_avg_join_query(
    aggregate_values: list[CompValue],
    aggregate_sample: CompValue,
    part: CompValue,
) -> tuple[str, str, str]:
    """Writes the delta queries for the average.

    Args:
        aggregate_values (list[CompValue]): Aggregate values to aggregate on.
        aggregate_sample (CompValue): Sample to group by on.
        part (CompValue): Current part of the query.

    Returns:
        tuple[str, str, str]: delta queries for count, sum and avg itself.
    """
    # Create count delta
    count_delta = count_join_query(
        aggregate_values,
        aggregate_sample,
        part,
        delta_part="delta_",
    )
    sum_delta = sum_join_query(
        aggregate_values,
        aggregate_sample,
        part,
        delta_part="delta_",
    )

    # Select clause
    select_clause = (
        f"SELECT combined_sum.{aggregate_sample.vars}, "
        + ", ".join(
            f"combined_sum.{value.vars} / combined_count.{value.vars} as {value.vars}"
            for value in aggregate_values
        )
        + ", 1 as k_count"
    )

    # FROM clause
    sum_table = get_table_name(part) + "_sum"
    count_table = get_table_name(part) + "_count"
    from_clause = (
        f" FROM (SELECT * FROM {sum_table}"
        + f" UNION SELECT * FROM delta_{sum_table}) as combined_sum, "
        + f"(SELECT * FROM {count_table} UNION "
        + f"SELECT * FROM delta_{count_table}) as combined_count"
    )

    # GROUP BY clause
    group_by_clause = (
        " WHERE combined_sum."
        + aggregate_sample.vars
        + " = combined_count."
        + aggregate_sample.vars
        + ";\n\n"
    )

    return (
        count_delta,
        sum_delta,
        select_clause + from_clause + group_by_clause,
    )
