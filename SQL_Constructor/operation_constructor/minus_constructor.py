from SQL_Constructor.base_constructor import (
    __encode_table_name,
    __encode_schema_name,
    countKCountsTogether,
    create_table_w_select,
    insert_into_w_select,
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
    tables_to_make: dict[str, list[str]]
) -> str:
    """Generates the join query string.

    Args:
        tables_to_make (dict[str, list[set[str]]]): Dictionary with key
        being to table to write to and value being all queries that need
        to be unioned in the table.

    Returns:
        str: Minus query string with outer join union.
    """
    return ""


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
            split_schema_check = key.split("_schema_")[-1]
            if (
                "schema_" + split_schema_check
                == __encode_schema_name(str(sorted(schema)))
                or len(schemas) == 1
            ):
                all_queries += countKCountsTogether(
                    schema, key, "prep_" + key
                )
    return all_queries


def delta_minus_query(
    part: CompValue,
    schemas1: list[set[str]],
    schemas2: list[set[str]],
) -> str:
    """Returns the delta minus query.

    Args:
        part (CompValue): Current part of the query.

    Returns:
        str: Query string for the delta minus operation.
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

    return delta_diff_queries_str
