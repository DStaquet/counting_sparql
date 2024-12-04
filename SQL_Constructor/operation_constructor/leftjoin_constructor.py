from SQL_Constructor.base_constructor import (
    __encode_schema_name,
    __encode_table_name,
)
from SQL_Constructor.operation_constructor.diff_constructor import (
    diff_query_sub,
)

from rdflib.plugins.sparql.parserutils import CompValue

from SQL_Constructor.operation_constructor.join_constructor import (
    join_query,
)


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
