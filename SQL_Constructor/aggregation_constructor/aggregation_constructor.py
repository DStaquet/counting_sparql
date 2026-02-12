"""Module to generate SQL queries for aggregation operations"""

from rdflib.plugins.sparql.parserutils import CompValue

from SQL_Constructor.aggregation_constructor.sum_constructor import (
    sum_join_query,
    delta_sum_join_query,
)
from SQL_Constructor.aggregation_constructor.avg_constructor import (
    avg_join_query,
    delta_avg_join_query,
)

from SQL_Constructor.table_constructor import (
    create_table_w_select,
    get_table_name,
)


def aggregate_schemas(
    part: CompValue,
    schemas1: list[set],
) -> list[set]:
    """Generates the schema for an AggregateJoin operation.
    Args:
        part (CompValue): Current part of the query
        schemas1 (list[set]): List of already calculated schemas
            lower in the parse tree
    Returns:
        list[set]: The schema for the AggregateJoin operation
    """
    aggregate_values, aggregate_sample = (
        _get_aggregate_objects(part)
    )

    new_schemas: list[set] = []

    for schema1 in schemas1:
        new_schema: set = set()
        for aggregate_var in schema1:
            if aggregate_var in aggregate_sample.get(
                "_vars"
            ) or aggregate_var in aggregate_values[0].get(
                "_vars"
            ):
                new_schema.add(aggregate_var)
        new_schemas.append(new_schema)

    return new_schemas


def _get_aggregate_objects(
    part: CompValue,
) -> tuple[list[CompValue], CompValue]:
    """Extracts the name of the aggregate function from a CompValue object.

    Args:
        aggregate (CompValue): The CompValue object representing the aggregate function.
    Returns:
        str: The name of the aggregate function.
    """
    # Gets the aggregate and its name
    aggregate_list = part.get("A")
    aggregate_values: list[CompValue] = []
    if len(aggregate_list) > 1:
        for aggregate in range(len(aggregate_list) - 1):
            aggregate_values.append(
                aggregate_list[aggregate]
            )
    else:
        for aggregate, _ in enumerate(aggregate_list):
            aggregate_values.append(
                aggregate_list[aggregate]
            )
    aggregate_sample: CompValue = aggregate_list[-1]

    return aggregate_values, aggregate_sample


def aggregate_join_query(
    part: CompValue,
) -> str:
    """Generates the SQL query for an AggregateJoin operation.

    Args:
        part (CompValue): Current part of the query
        schemas1 (list[set]): List of already calculated schemas
            lower in the parse tree
    Returns:
        str: The SQL query for the AggregateJoin operation
    """
    aggregate_values, aggregate_sample = (
        _get_aggregate_objects(part)
    )

    # Match the aggregate name to the corresponding function
    match aggregate_values[0].name:
        case "Aggregate_Sum":
            sum_query: str = sum_join_query(
                aggregate_values,
                aggregate_sample,
                part,
            )
            return create_table_w_select(
                get_table_name(part), sum_query
            )
        case "Aggregate_Avg":
            avg_query, sum_query, count_query = (
                avg_join_query(
                    aggregate_values, aggregate_sample, part
                )
            )
            return (
                create_table_w_select(
                    get_table_name(part) + "_sum", sum_query
                )
                + create_table_w_select(
                    get_table_name(part) + "_count",
                    count_query,
                )
                + create_table_w_select(
                    get_table_name(part), avg_query
                )
            )
        case _:
            raise NotImplementedError(
                f"Aggregate {aggregate_values[0].name} not implemented"
            )


def delta_aggregate_join_query(
    part: CompValue,
) -> str:
    """Generates the SQL query for a DeltaAggregateJoin operation.

    Args:
        part (CompValue): Current part of the query
        schemas1 (list[set]): List of already calculated schemas
            lower in the parse tree
    Returns:
        str: The SQL query for the DeltaAggregateJoin operation
    """
    aggregate_values, aggregate_sample = (
        _get_aggregate_objects(part)
    )

    # Match the aggregate name to the corresponding function
    match aggregate_values[0].name:
        case "Aggregate_Sum":
            sum_query: str = delta_sum_join_query(
                aggregate_values,
                aggregate_sample,
                part,
            )
            return create_table_w_select(
                "delta_" + get_table_name(part), sum_query
            )
        case "Aggregate_Avg":
            count_delta, sum_delta, avg_delta = (
                delta_avg_join_query(
                    aggregate_values, aggregate_sample, part
                )
            )
            return (
                create_table_w_select(
                    "delta_"
                    + get_table_name(part)
                    + "_sum",
                    sum_delta,
                )
                + create_table_w_select(
                    "delta_"
                    + get_table_name(part)
                    + "_count",
                    count_delta,
                )
                + create_table_w_select(
                    "delta_" + get_table_name(part),
                    avg_delta,
                )
            )
        case _:
            raise NotImplementedError(
                f"Delta Aggregate {aggregate_values[0].name} not implemented"
            )
