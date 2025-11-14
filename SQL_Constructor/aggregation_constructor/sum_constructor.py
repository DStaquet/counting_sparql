"""Module to construct SQL queries for SUM aggregation"""

from rdflib.plugins.sparql.parserutils import CompValue

from SQL_Constructor.table_constructor import (
    get_table_name,
)


def sum_join_query(
    aggregate_values: list[CompValue],
    aggregate_sample: CompValue,
    part: CompValue,
) -> str:
    """Constructs the SQL query for a SUM aggregation.

    Args:
        aggregate_obj (CompValue): Object representing the SUM aggregation
        aggregate_sample (CompValue): Sample variable for the aggregation
        schemas1 (list[set]): List of already calculated schemas
            lower in the parse tree

    Returns:
        str: SQL query for the SUM aggregation
    """
    # Construct SELECT clause
    select_clause = (
        f"SELECT {aggregate_sample.vars}, "
        + ", ".join(
            f"SUM(CAST ({value.vars} AS INT)) AS {value.vars}"
            for value in aggregate_values
        )
        + ", 1 AS k_count"
    )

    # Construct FROM clause
    from_clause = " FROM " + get_table_name(part.p.p)

    # Construct GROUP BY clause
    group_by_clause = (
        " GROUP BY " + aggregate_sample.vars + ";"
    )

    return select_clause + from_clause + group_by_clause


def _delta_sum_join_query_additions(
    aggregate_values: list[CompValue],
    aggregate_sample: CompValue,
    part: CompValue,
) -> str:
    """Constructs the SELECT clause for a delta SUM aggregation.

    Args:
        aggregate_values (list[CompValue]): List of CompValue objects representing
            the SUM aggregations
        aggregate_sample (CompValue): Sample variable for the aggregation
    Returns:
        str: SQL SELECT clause for the delta SUM aggregation
    """
    # Create select clause
    select_clause = (
        f"SELECT {aggregate_sample.vars}, "
        + ", ".join(
            f"(CAST (delta_Agg.{value.vars} AS INT) "
            + f"+ CAST (Agg.{value.vars} AS INT)) AS {value.vars}"
            for value in aggregate_values
        )
        + ", 1 AS k_count"
    )

    # From clause
    from_clause = (
        " FROM delta_"
        + get_table_name(part.p.p)
        + " AS delta_Agg"
        + " JOIN "
        + get_table_name(part.p.p)
        + " AS Agg"
        + f" ON delta_Agg.{aggregate_sample.vars} = Agg.{aggregate_sample.vars}"
    )

    # Where clause
    where_clause = (
        " WHERE "
        + f"delta_Agg.{aggregate_sample.vars} IN (SELECT {aggregate_sample.vars}"
        + f" FROM delta_{get_table_name(part.p.p)})"
    )

    return select_clause + from_clause + where_clause


def _delta_sum_join_query_subtractions(
    aggregate_values: list[CompValue],
    aggregate_sample: CompValue,
    part: CompValue,
) -> str:
    """Constructs the SELECT clause for a delta SUM aggregation subtractions.

    Args:
        aggregate_values (list[CompValue]): List of CompValue objects representing
            the SUM aggregations
        aggregate_sample (CompValue): Sample variable for the aggregation
    Returns:
        str: SQL SELECT clause for the delta SUM aggregation subtractions
    """
    # Create select clause
    select_clause = (
        f"SELECT {aggregate_sample.vars}, "
        + ", ".join(
            f"(CAST (delta_Agg.{value.vars} AS INT) "
            + f"- CAST (Agg.{value.vars} AS INT)) AS {value.vars}"
            for value in aggregate_values
        )
        + ", 1 AS k_count"
    )

    # From clause
    from_clause = (
        " FROM delta_"
        + get_table_name(part.p.p)
        + " AS delta_Agg"
        + " JOIN "
        + get_table_name(part.p.p)
        + " AS Agg"
        + f" ON delta_Agg.{aggregate_sample.vars} = Agg.{aggregate_sample.vars}"
    )

    # Where clause
    where_clause = (
        " WHERE "
        + f"delta_Agg.{aggregate_sample.vars} NOT IN (SELECT {aggregate_sample.vars}"
        + f" FROM nu_{get_table_name(part.p.p)})"
    )

    return select_clause + from_clause + where_clause


def _delta_sum_join_query_deletions(
    aggregate_values: list[CompValue],
    aggregate_sample: CompValue,
    part: CompValue,
) -> str:
    """Constructs the SELECT clause for a delta SUM aggregation deletions.

    Args:
        aggregate_values (list[CompValue]): List of CompValue objects representing
            the SUM aggregations
        aggregate_sample (CompValue): Sample variable for the aggregation
    Returns:
        str: SQL SELECT clause for the delta SUM aggregation deletions
    """
    # Create select clause
    select_clause = (
        f"SELECT {aggregate_sample.vars}, "
        + ", ".join(
            f"Agg.{value.vars}"
            for value in aggregate_values
        )
        + ", -Agg.k_count AS k_count"
    )

    # From clause
    from_clause = (
        " FROM "
        + get_table_name(part.p.p)
        + " AS Agg"
        + " JOIN delta_"
        + get_table_name(part.p.p)
        + " AS delta_Agg"
        + f" ON delta_Agg.{aggregate_sample.vars} = Agg.{aggregate_sample.vars}"
    )

    return select_clause + from_clause


def delta_sum_join_query(
    aggregate_values: list[CompValue],
    aggregate_sample: CompValue,
    part: CompValue,
) -> str:
    """Constructs the SQL query for a delta SUM aggregation.

    Args:
        aggregate_obj (CompValue): Object representing the SUM aggregation
        aggregate_sample (CompValue): Sample variable for the aggregation
        schemas1 (list[set]): List of already calculated schemas
            lower in the parse tree
    Returns:
        str: SQL query for the delta SUM aggregation
    """
    # Create select clause
    additions_clause = _delta_sum_join_query_additions(
        aggregate_values,
        aggregate_sample,
        part,
    )

    # Deletions clause
    deletions_clause = _delta_sum_join_query_deletions(
        aggregate_values,
        aggregate_sample,
        part,
    )

    # Subtractions clause
    subtractions_clause = (
        _delta_sum_join_query_subtractions(
            aggregate_values,
            aggregate_sample,
            part,
        )
    )

    return (
        additions_clause
        + " UNION "
        + deletions_clause
        + " UNION "
        + subtractions_clause
        + ";"
    )
