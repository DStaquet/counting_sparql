from SQL_Constructor.base_constructor import (
    __encode_schema_name,
    count_k_counts_together,
    make_join,
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
from SQL_Constructor.table_constructor import (
    create_table_w_select,
    __encode_table_name,
)


'''def __delta_join_part(
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
        )'''


def __delta_diff_part(
    part: CompValue,
    schemas1: list[set[str]],
    schemas2: list[set[str]],
    is_leftjoin_part: bool = False,
) -> tuple[str, str]:
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
    else:
        diff_queries: dict[str, list[str]] = delta_diff_sub(
            part,
            schemas1,
            schemas2,
            append_schemas=is_leftjoin_part,
        )

    diff_queries_str: str = make_group_by(
        diff_queries, schemas1, is_delta=True
    )

    diff_queries_outer_join: str = make_join(
        diff_queries, schemas1, is_delta=True
    )

    """diff_queries_str += countKCountsTogether(
        schemas1,
        to_table="delta_" + __encode_table_name(part),
        from_table="prep_delta_"
        + __encode_table_name(part),
    )"""

    return diff_queries_str, diff_queries_outer_join


def delta_left_join_query(
    part: CompValue,
    schemas1: list[set[str]],
    schemas2: list[set[str]],
) -> tuple[str, str]:
    """Generates the leftjoin query strings

    Args:
        part (CompValue): Current part of the query
        schemas1 (list[set[str]]): Schemas of the first child of the part
        schemas2 (list[set[str]]): Schemas of the second child of the part

    Returns:
        tuple[str, str]: Tuple containing the leftjoin query strings
    """
    # First delta rules of the left join
    # Join deltas
    is_leftjoin: bool = True
    if len(schemas1) == 1 and len(schemas2) == 1:
        if schemas1[0].intersection(schemas2[0]) == set():
            is_leftjoin = False
    (
        leftjoin_delta_join_part,
        leftjoin_delta_join_part_outer_join,
    ) = delta_join_queries_part_func(
        part,
        schemas1,
        schemas2,
        new_table_name="delta_" + __encode_table_name(part),
        is_leftjoin_part=is_leftjoin,
    )

    # Second part of the leftjoin delta
    # Diff deltas
    (
        leftjoin_diff_delta_part,
        leftjoin_diff_delta_part_outer_join,
    ) = __delta_diff_part(
        part,
        schemas1,
        schemas2,
        is_leftjoin_part=is_leftjoin,
    )

    return (
        leftjoin_delta_join_part + leftjoin_diff_delta_part,
        leftjoin_delta_join_part_outer_join
        + leftjoin_diff_delta_part_outer_join,
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
        if schema.intersection(schemas2[0]) != set():
            new_schema.append(schema)
        for schema2 in schemas2:
            new_schema.append(schema.union(schema2))
    return new_schema


def __join_part(
    part: CompValue,
    schemas1: list[set[str]],
    schemas2: list[set[str]],
) -> dict[str, list[str]]:
    """Generates the join query.

    Args:
        part (CompValue): Current part of the query.

    Returns:
        str: Query string for the join operation.
    """
    if len(schemas1) == 0 or len(schemas2) == 0:
        raise ValueError("No schemas to join on.")
    elif len(schemas1) == 1 and len(schemas2) == 1:
        if schemas1[0].intersection(schemas2[0]) != set():
            suffix = "_" + __encode_schema_name(
                str(
                    sorted(schemas1[0].union(schemas2[0])),
                )
            )
        else:
            suffix = ""
        return join_query(
            part,
            (
                __encode_table_name(part.p1),
                __encode_table_name(part.p2),
                __encode_table_name(part) + suffix,
            ),
            schemas1,
            schemas2,
        )
    else:
        return join_query(
            part,
            (
                __encode_table_name(part.p1),
                __encode_table_name(part.p2),
                __encode_table_name(part),
            ),
            schemas1,
            schemas2,
            bools=((False, False), True),
        )


def __leftJoinWithCreate(
    leftjoin_join_dict: dict[str, list[str]],
    leftjoin_diff_dict: dict[str, list[str]],
) -> str:
    """Generates the leftjoin query.

    Args:
        leftjoin_join_dict (dict[str, list[str]]): Dictionary containing the join
        queries of the leftjoin
        leftjoin_diff_dict (dict[str, list[str]]): Dictionary containing the diff
        queries of the leftjoin

    Returns:
        str: String of the leftjoin queries
    """
    # Join queries
    leftjoin_join: str = ""
    for key in leftjoin_join_dict:
        """if len(leftjoin_join_dict[key]) > 1:
        raise ValueError(
            "Left join should not have multiple queries."
        )"""
        leftjoin_join += create_table_w_select(
            key, leftjoin_join_dict[key][0]
        )

    # Diff queries
    leftjoin_diff: str = ""
    for key in leftjoin_diff_dict:
        """if len(leftjoin_diff_dict[key]) > 1:
        raise ValueError(
            "Left join diff should not have multiple queries."
        )"""
        leftjoin_diff += create_table_w_select(
            key, leftjoin_diff_dict[key][0]
        )

    return leftjoin_join + leftjoin_diff


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
    leftjoin_join_dict: dict[str, list[str]] = __join_part(
        part, schemas1, schemas2
    )
    leftjoin_diff_dict: dict[str, list[str]] = (
        diff_query_sub(
            part, (schemas1, schemas2), append_schemas=True
        )
    )

    return __leftJoinWithCreate(
        leftjoin_join_dict, leftjoin_diff_dict
    )
