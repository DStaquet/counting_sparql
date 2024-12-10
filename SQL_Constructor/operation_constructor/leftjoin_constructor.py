from SQL_Constructor.base_constructor import (
    __encode_schema_name,
    __encode_table_name,
    countKCountsTogether,
    make_join,
    create_table_w_select,
)
from SQL_Constructor.operation_constructor.diff_constructor import (
    delta_diff_sub,
    diff_query_sub,
)

from rdflib.plugins.sparql.parserutils import CompValue

from SQL_Constructor.operation_constructor.join_constructor import (
    join_query,
    delta_join_queries_part_func,
)
from SQL_Constructor.base_constructor import (
    make_group_by,
    make_join,
)


def __delta_join_part(
    part: CompValue,
    schemas1: list[set[str]],
    schemas2: list[set[str]],
) -> str:
    """Generates the delta join part of the left join query.

    Args:
        part (CompValue): Current part of the query
        schemas1 (list[set[str]]): Schemas of the left child of the part
        schemas2 (list[set[str]]): Schemas of the right child of the part

    Returns:
        str: Join part of the left join query.
    """
    if len(schemas1) == 0 or len(schemas2) == 0:
        raise ValueError("No schemas to join on.")
    elif len(schemas1) == 1 and len(schemas2) == 1:
        return delta_join_queries_part_func(
            part,
            schemas1,
            schemas2,
            new_table_name="delta_"
            + __encode_table_name(part)
            + "_"
            + __encode_schema_name(
                str(sorted(schemas1[0])),
            ),
        )
    else:
        return delta_join_queries_part_func(
            part,
            schemas1,
            schemas2,
        )


def __delta_diff_part(
    part: CompValue,
    schemas1: list[set[str]],
    schemas2: list[set[str]],
) -> str:
    """Generates the delta diff part of the left join query.

    Args:
        part (CompValue): Current part of the query
        schemas1 (list[set[str]]): Schemas of the left child of the part
        schemas2 (list[set[str]]): Schemas of the right child of the part

    Returns:
        str: Diff part of the left join query.
    """
    if len(schemas1) == 0:
        raise ValueError("No schemas to diff on.")
    elif len(schemas1) == 1:
        diff_queries: dict[str, list[str]] = delta_diff_sub(
            part,
            schemas1,
            schemas2,
            new_table_name="prep_delta_"
            + __encode_table_name(part)
            + "_"
            + __encode_schema_name(
                str(sorted(schemas1[0])),
            ),
            append_schemas=False,
        )
    else:
        diff_queries: dict[str, list[str]] = delta_diff_sub(
            part,
            schemas1,
            schemas2,
        )

    diff_queries_str: str = make_group_by(
        diff_queries, schemas1
    )

    """diff_queries_str += countKCountsTogether(
        schemas1,
        to_table="delta_" + __encode_table_name(part),
        from_table="prep_delta_"
        + __encode_table_name(part),
    )"""

    return diff_queries_str


def delta_left_join_query(
    part: CompValue,
    schemas1: list[set[str]],
    schemas2: list[set[str]],
) -> str:
    # First delta rules of the left join
    # Join deltas
    leftjoin_delta_join_part: str = (
        delta_join_queries_part_func(
            part,
            schemas1,
            schemas2,
            new_table_name="delta_"
            + __encode_table_name(part),
        )
    )

    # Second part of the leftjoin delta
    # Diff deltas
    leftjoin_diff_delta_part: str = __delta_diff_part(
        part,
        schemas1,
        schemas2,
    )

    return (
        leftjoin_delta_join_part + leftjoin_diff_delta_part
    )


def leftjoin_schemas(
    schemas1: list[set[str]],
    schemas2: list[set[str]],
) -> list[set[str]]:
    """Constructs the schemas of the leftjoin part of the query.

    Args:
        part (CompValue): Current part of the query
        schemas1 (list[set[str]]): Schemas of the left child of the part
        schemas2 (list[set[str]]): Schemas of the right child of the part

    Returns:
        list[set[str]]: Schemas of the leftjoin part of the query
    """
    new_schema = []
    for schema in schemas1:
        new_schema.append(schema)
        for schema2 in schemas2:
            new_schema.append(schema.union(schema2))
    return new_schema


def __join_part(
    part: CompValue,
    schemas1: list[set[str]],
    schemas2: list[set[str]],
) -> str:
    """Generates the join query.

    Args:
        part (CompValue): Current part of the query.

    Returns:
        str: Query string for the join operation.
    """
    if len(schemas1) == 0 or len(schemas2) == 0:
        raise ValueError("No schemas to join on.")
    elif len(schemas1) == 1 and len(schemas2) == 1:
        return join_query(
            part,
            __encode_table_name(part.p1),
            __encode_table_name(part.p2),
            schemas1,
            schemas2,
            __encode_table_name(part)
            + "_"
            + __encode_schema_name(
                str(sorted(schemas1[0])),
            ),
        )
    else:
        return join_query(
            part,
            __encode_table_name(part.p1),
            __encode_table_name(part.p2),
            schemas1,
            schemas2,
            __encode_table_name(part),
        )


def left_join_query(
    part: CompValue,
    schemas1: list[set[str]] = [],
    schemas2: list[set[str]] = [],
) -> str:
    """Generates the leftjoin query.

    Args:
        part (CompValue): Current part of the query.

    Returns:
        str: Query string for the leftjoin operation.
    """
    leftjoin_join: str = __join_part(
        part, schemas1, schemas2
    )
    leftjoin_diff_dict: dict[str, list[str]] = (
        diff_query_sub(part, schemas1, schemas2)
    )

    leftjoin_diff: str = ""
    for key in leftjoin_diff_dict:
        if len(leftjoin_diff_dict[key]) > 1:
            raise ValueError(
                "Left join diff should not have multiple queries."
            )
        leftjoin_diff += create_table_w_select(
            key, leftjoin_diff_dict[key][0]
        )

    return leftjoin_join + leftjoin_diff
