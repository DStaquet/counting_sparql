from SQL_Constructor.table_constructor import (
    __encode_table_name,
)
from SQL_Constructor.base_constructor import make_join
from SQL_Constructor.base_constructor import make_group_by
from SQL_Constructor.operation_constructor.diff_constructor import (
    diff_query_sub,
    delta_diff_sub,
)


from rdflib.plugins.sparql.parserutils import CompValue
from rdflib.term import Variable

from SQL_Constructor.table_constructor import (
    create_table_w_select,
)


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
        part, (schemas1, schemas2), minus=True
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

    delta_diff_queries_str: str = make_group_by(
        delta_diff_queries,
        schemas1,
        is_delta=True,
    )

    delta_diff_join_queries: str = make_join(
        delta_diff_queries,
        schemas1,
        is_delta=True,
    )

    return delta_diff_queries_str, delta_diff_join_queries
