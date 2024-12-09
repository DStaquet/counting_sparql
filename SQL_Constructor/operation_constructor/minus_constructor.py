from SQL_Constructor.base_constructor import (
    __encode_table_name,
    countKCountsTogether,
)
from SQL_Constructor.operation_constructor.diff_constructor import (
    diff_query_sub,
    delta_diff_sub,
)


from rdflib.plugins.sparql.parserutils import CompValue


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
    return diff_query_sub(part, schemas1, schemas2, True)


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
        delta_diff_queries: str = delta_diff_sub(
            part,
            schemas1,
            schemas2,
            minus=True,
            append_schemas=False,
        )
    else:
        delta_diff_queries: str = delta_diff_sub(
            part,
            schemas1,
            schemas2,
            minus=True,
        )

    delta_diff_queries += countKCountsTogether(
        part,
        schemas1,
        "delta_" + __encode_table_name(part),
        "delta_prep_" + __encode_table_name(part),
    )

    return delta_diff_queries
