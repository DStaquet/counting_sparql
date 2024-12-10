from SQL_Constructor.base_constructor import (
    __encode_table_name,
    __encode_schema_name,
    countKCountsTogether,
    create_table_w_select,
    insert_into_w_select,
    outer_join_queries,
    final_outer_join_query,
)
from SQL_Constructor.operation_constructor.diff_constructor import (
    diff_query_sub,
    delta_diff_sub,
)


from rdflib.plugins.sparql.parserutils import CompValue
from rdflib.term import Variable


def minus_query(
    part: CompValue,
    schemas1: list[set[str]] = [],
    schemas2: list[set[str]] = [],
) -> str:
    """Generates the minus query.

    Args:
        part (CompValue): Current part of the query.

    Returns:
        str: Query string for the minus operation.
    """
    diff_dict: dict[str, list[str]] = diff_query_sub(
        part, schemas1, schemas2, True
    )

    all_minus_queries: str = ""
    for key in diff_dict:
        if len(diff_dict[key]) != 1:
            raise ValueError(
                "Minus query should only have one query per schema."
            )
        all_minus_queries += create_table_w_select(
            key, diff_dict[key][0]
        )

    return all_minus_queries


def __make_join(
    tables_to_make: dict[str, list[str]],
    schemas: list[set[str]],
) -> str:
    """Generates the join query string.

    Args:
        tables_to_make (dict[str, list[set[str]]]): Dictionary with key
        being to table to write to and value being all queries that need
        to be unioned in the table.

    Returns:
        str: Minus query string with outer join union.
    """
    all_queries: str = ""
    for key in tables_to_make:
        if len(schemas) == 1:
            curr_schema = schemas[0]
        else:
            for schema in schemas:
                if __schema_in_key(key, schema):
                    curr_schema = schema
        for q_index in range(len(tables_to_make[key])):
            all_queries += create_table_w_select(
                key + "_" + str(q_index),
                tables_to_make[key][q_index],
                temp_prefix=" TEMP ",
            )
            if (
                q_index == 1
                and len(tables_to_make[key]) > 1
            ):
                all_queries += outer_join_queries(
                    key + "_temp_" + str(q_index),
                    key + "_" + str(q_index - 1),
                    key + "_" + str(q_index),
                    curr_schema,
                )
            elif (
                q_index > 1
                and q_index < len(tables_to_make[key]) - 1
            ):
                all_queries += outer_join_queries(
                    key + "_temp_" + str(q_index),
                    key + "_temp_" + str(q_index - 1),
                    key + "_" + str(q_index),
                    curr_schema,
                )
            elif q_index == len(tables_to_make[key]) - 1:
                all_queries += final_outer_join_query(
                    key + "_temp_" + str(q_index - 1),
                    key + "_" + str(q_index),
                    curr_schema,
                    key,
                )
    return all_queries


def __schema_in_key(key: str, schema: set[str]) -> bool:
    """Checks if the schema is in the key.

    Args:
        key (str): The key to check
        schema (list[set[str]]): The schema to check

    Returns:
        bool: True if the schema is in the key, False otherwise.
    """
    split_schema_check = key.split("_schema_")[-1]
    return (
        "schema_" + split_schema_check
        == __encode_schema_name(str(sorted(schema)))
    )


def __make_group_by(
    tables_to_make: dict[str, list[str]],
    schemas: list[set[str]],
) -> str:
    """Generates the group by query string.

    Args:
        tables_to_make (dict[str, list[set[str]]]): Dictionary with key
        being to table to write to and value being all queries that need
        to be unioned in the table.
        schemas (list[set[Variable]]): List of schemas
        to use for group by

    Returns:
        str: Minus query string with group by.
    """
    all_queries: str = ""
    for key in tables_to_make:
        queries_seen_count = 0
        for query in tables_to_make[key]:
            if queries_seen_count == 0:
                all_queries += create_table_w_select(
                    "prep_" + key,
                    query,
                    temp_prefix=" TEMP ",
                )
            else:
                all_queries += insert_into_w_select(
                    "prep_" + key,
                    query,
                )
            queries_seen_count += 1
        for schema in schemas:
            if __schema_in_key(key, schema):
                all_queries += countKCountsTogether(
                    schema, key, "prep_" + key
                )
    return all_queries


def delta_minus_query(
    part: CompValue,
    schemas1: list[set[str]],
    schemas2: list[set[str]],
) -> tuple[str, str]:
    """Returns the delta minus query.

    Args:
        part (CompValue): Current part of the query.
        schemas1 (list[set[str]]): List of schemas for the first child part query.
        schemas2 (list[set[str]]): List of schemas for the second child part query.

    Returns:
        str: Query string for the delta minus operation.
        One containing the group by method and one containing the join method.
    """
    if len(schemas1) == 0:
        raise ValueError("Schema 1 is empty")
    elif len(schemas1) == 1:
        delta_diff_queries: dict[str, list[str]] = (
            delta_diff_sub(
                part,
                schemas1,
                schemas2,
                minus=True,
                append_schemas=False,
            )
        )
    else:
        delta_diff_queries: dict[str, list[str]] = (
            delta_diff_sub(
                part,
                schemas1,
                schemas2,
                minus=True,
            )
        )

    """delta_diff_queries += countKCountsTogether(
        part,
        schemas1,
        "delta_" + __encode_table_name(part),
        "delta_prep_" + __encode_table_name(part),
    )"""

    delta_diff_queries_str: str = __make_group_by(
        delta_diff_queries,
        schemas1,
    )

    delta_diff_join_queries: str = __make_join(
        delta_diff_queries,
        schemas1,
    )

    return delta_diff_queries_str, delta_diff_join_queries
