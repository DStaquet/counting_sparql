"""Modules to import"""

from rdflib.plugins.sparql.parserutils import CompValue

from SQL_Constructor.base_constructor import (
    __encode_schema_name,
)
from SQL_Constructor.table_constructor import (
    create_table_w_select,
    __encode_table_name,
)


def __union_query_sub_same_schema(
    part: CompValue,
    schema1: set[str],
    schema2: set[str],
    schema1_len: int,
    schema2_len: int,
    add_schemas: bool = False,
    is_delta: bool = False,
) -> str:
    """Generates the union query for the same schema.

    Args:
        part (CompValue): Current part of the query.
        schema1 (set[str]): Schema of the left child of the union.
        schema2 (set[str]): Schema of the right child of the union.
        add_schemas (bool, optional): True if schemas need to be added. Defaults to False.
        is_delta (bool, optional): True if it is a delta query. Defaults to False.

    Returns:
        str: Query of same schema union operation.
    """
    if schema1_len > 1:
        sch1_suffix: str = "_" + __encode_schema_name(
            str(sorted(schema1))
        )
    else:
        sch1_suffix = ""
    if schema2_len > 1:
        sch2_suffix: str = "_" + __encode_schema_name(
            str(sorted(schema2))
        )
    else:
        sch2_suffix = ""

    if is_delta:
        delta_prefix: str = "delta_"
    else:
        delta_prefix = ""

    union_query_str: str = (
        "SELECT "
        + ", ".join(
            f"(CASE WHEN r1.{var} IS NOT NULL THEN r1.{var} ELSE r2.{var} END) AS {var}"
            for var in sorted(schema1)
        )
        + ", coalesce(r1.k_count, 0) + coalesce(r2.k_count, 0) as k_count\n"
        + "FROM "
        + delta_prefix
        + __encode_table_name(part.p1)
        + sch1_suffix
        + " AS r1 FULL OUTER JOIN "
        + delta_prefix
        + __encode_table_name(part.p2)
        + sch2_suffix
        + " AS r2 ON "
    )
    union_query_str += " AND ".join(
        f"r1.{var} = r2.{var}" for var in sorted(schema1)
    )
    union_query_str += ";\n"

    if add_schemas:
        suffix = "_" + __encode_schema_name(
            str(sorted(schema1))
        )
        union_query_str = create_table_w_select(
            delta_prefix
            + __encode_table_name(part)
            + suffix,
            union_query_str,
        )
    else:
        union_query_str = create_table_w_select(
            delta_prefix + __encode_table_name(part),
            union_query_str,
        )

    return union_query_str


def __union_query_sub(
    part: CompValue,
    schema1: set[str],
    from_table: str,
    add_schemas: bool = False,
    is_delta: bool = False,
) -> str:
    if add_schemas:
        sch1_suffix: str = "_" + __encode_schema_name(
            str(sorted(schema1))
        )
    else:
        sch1_suffix = ""

    if is_delta:
        delta_prefix: str = "delta_"
    else:
        delta_prefix = ""

    # Left table
    left_union_query: str = (
        "SELECT "
        + ", ".join(f"{var}" for var in sorted(schema1))
        + ", k_count\n"
        + "FROM "
        + delta_prefix
        + from_table
        + sch1_suffix
        + ";\n"
    )

    union_query_str = create_table_w_select(
        delta_prefix
        + __encode_table_name(part)
        + "_"
        + __encode_schema_name(str(sorted(schema1))),
        left_union_query,
    )

    return union_query_str


def _union_query_mult_schema(
    part: CompValue,
    schemas1: list[set[str]],
    schemas2: list[set[str]],
    is_delta: bool,
) -> str:
    """Generates the union query for multiple schemas."""
    all_queries: str = ""
    already_seen: list[set[str]] = []
    for sch1 in schemas1:
        for sch2 in schemas2:
            if sch1 == sch2:
                all_queries += (
                    __union_query_sub_same_schema(
                        part,
                        sch1,
                        sch2,
                        len(schemas1),
                        len(schemas2),
                        True,
                        is_delta=is_delta,
                    )
                )
                already_seen.append(sch1)
    for sch1 in schemas1:
        if sch1 in already_seen:
            continue
        all_queries += __union_query_sub(
            part,
            sch1,
            __encode_table_name(part.p1),
            True,
            is_delta=is_delta,
        )
    for sch2 in schemas2:
        if sch2 in already_seen:
            continue
        all_queries += __union_query_sub(
            part,
            sch2,
            __encode_table_name(part.p2),
            True,
            is_delta=is_delta,
        )

    return all_queries


def union_query(
    part: CompValue,
    schemas1: list[set[str]] | None = None,
    schemas2: list[set[str]] | None = None,
    is_delta: bool = False,
) -> str:
    """Generates the union query.

    Args:
        part (CompValue): Current part of the query.

    Returns:
        str: Query string containing the union operation.
    """
    if schemas1 is None:
        schemas1 = []
    if schemas2 is None:
        schemas2 = []

    if len(schemas1) == 1 and len(schemas2) == 1:
        if schemas1[0] == schemas2[0]:
            return __union_query_sub_same_schema(
                part,
                schemas1[0],
                schemas2[0],
                len(schemas1),
                len(schemas2),
                False,
                is_delta=is_delta,
            )
        else:
            return __union_query_sub(
                part,
                schemas1[0],
                __encode_table_name(part.p1),
                is_delta=is_delta,
            ) + __union_query_sub(
                part,
                schemas2[0],
                __encode_table_name(part.p2),
                is_delta=is_delta,
            )
    else:
        all_queries: str = _union_query_mult_schema(
            part, schemas1, schemas2, is_delta
        )

        return all_queries


def union_schemas(
    schemas1: list[set[str]],
    schemas2: list[set[str]],
) -> list[set[str]]:
    """Constructs the schemas of the union part of the query.

    Args:
        schemas1 (list[set[str]]): Schema of the left child of the union
        schemas2 (list[set[str]]): Schema of the right child of the union

    Returns:
        list[set[str]]: Schema of the union part of the query
    """
    schemas = schemas1.copy()
    for schema in schemas2:
        if schema not in schemas:
            schemas.append(schema)
    return schemas


def delta_union_query(
    part: CompValue,
    schemas1: list[set[str]],
    schemas2: list[set[str]],
) -> str:
    """Generates the union delta query.

    Args:
        part (CompValue): Current part of the query.

    Returns:
        str: Query string for the delta union operation.
    """
    return union_query(part, schemas1, schemas2, True)
