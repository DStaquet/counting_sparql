from SQL_Constructor.base_constructor import (
    __encode_schema_name,
    __encode_table_name,
    countKCountsTogether,
)
from SQL_Constructor.operation_constructor.diff_constructor import (
    delta_diff_sub,
    diff_query_sub,
)

from rdflib.plugins.sparql.parserutils import CompValue

from SQL_Constructor.operation_constructor.join_constructor import (
    delta_join_sub,
    join_query,
    delta_join_queries_part_func,
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
        diff_queries: str = delta_diff_sub(
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
        diff_queries: str = delta_diff_sub(
            part,
            schemas1,
            schemas2,
        )

    diff_queries += countKCountsTogether(
        part,
        schemas1,
        to_table="delta_" + __encode_table_name(part),
        from_table="prep_delta_"
        + __encode_table_name(part),
    )

    return diff_queries


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

    """leftjoin_join_delta_query: str = delta_join_sub(
        part.p1, part.p2, part
    )
    leftjoin_minus_delta_query: str = delta_diff_sub(part)

    return (
        leftjoin_join_delta_query
        + leftjoin_minus_delta_query
    )"""


def leftjoin_schemas(
    part: CompValue,
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

    """join_query: str = (
        "INSERT INTO " + __encode_table_name(part) + "\n"
    )
    join_query += "SELECT "
    join_query += __left_join_select_clause(part)
    join_query += ", r1.k_count * r2.k_count as k_count\n"
    join_query += "FROM "
    join_query += __encode_table_name(part.p1)
    join_query += " AS r1 JOIN "
    join_query += __encode_table_name(part.p2)
    join_query += " AS r2 "
    if part.p1._vars.intersection(part.p2._vars) != set():
        join_query += "ON "
        join_query += " AND ".join(
            f"r1.{var} = r2.{var}"
            for var in sorted(
                part.p1._vars.intersection(part.p2._vars)
            )
        )
    join_query += "\nON CONFLICT DO\nUPDATE SET\n\t"
    join_query += (
        "k_count = EXCLUDED.k_count + k_count\n"
        + "WHERE "
        + " AND ".join(
            f"{var} = EXCLUDED.{var}"
            for var in sorted(part.p1._vars)
        )
        + " AND ".join(
            f"{var} = EXCLUDED.{var}"
            for var in sorted(
                part.p2._vars.difference(part.p1._vars)
            )
        )
    )
    join_query += ";\n"
    return join_query"""


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
    leftjoin_diff: str = diff_query_sub(
        part, schemas1, schemas2
    )

    return leftjoin_join + leftjoin_diff
