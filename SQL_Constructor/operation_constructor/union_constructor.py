from SQL_Constructor.base_constructor import (
    __encode_schema_name,
    __encode_table_name,
    create_table_w_select,
)


from rdflib.plugins.sparql.parserutils import CompValue


def __union_query_sub(
    part: CompValue,
    schema1: set[str],
    schema2: set[str],
    add_schemas: bool = False,
    is_delta: bool = False,
) -> str:
    if add_schemas:
        sch1_suffix: str = "_" + __encode_schema_name(
            str(sorted(schema1))
        )
        sch2_suffix: str = "_" + __encode_schema_name(
            str(sorted(schema2))
        )
    else:
        sch1_suffix = ""
        sch2_suffix = ""

    if is_delta:
        delta_prefix: str = "delta_"
    else:
        delta_prefix = ""

    if schema1 == schema2:
        union_query: str = (
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
        union_query += " AND ".join(
            f"r1.{var} = r2.{var}"
            for var in sorted(schema1)
        )
        union_query += ";\n"

        if add_schemas:
            union_query = create_table_w_select(
                delta_prefix
                + __encode_table_name(part)
                + sch1_suffix,
                union_query,
            )
        else:
            union_query = create_table_w_select(
                delta_prefix + __encode_table_name(part),
                union_query,
            )

    else:
        # Left table
        left_union_query: str = (
            "SELECT "
            + ", ".join(f"{var}" for var in sorted(schema1))
            + ", k_count\n"
            + "FROM "
            + delta_prefix
            + __encode_table_name(part.p1)
            + sch1_suffix
            + ";\n"
        )

        right_union_query: str = (
            "SELECT "
            + ", ".join(f"{var}" for var in sorted(schema2))
            + ", k_count\n"
            + "FROM "
            + delta_prefix
            + __encode_table_name(part.p2)
            + sch2_suffix
            + ";\n"
        )

        union_query = create_table_w_select(
            delta_prefix
            + __encode_table_name(part)
            + "_"
            + __encode_schema_name(str(sorted(schema1))),
            left_union_query,
        )

        union_query += create_table_w_select(
            delta_prefix
            + __encode_table_name(part)
            + "_"
            + __encode_schema_name(str(sorted(schema2))),
            right_union_query,
        )

    return union_query


def union_query(
    part: CompValue,
    schemas1: list[set[str]] = [],
    schemas2: list[set[str]] = [],
    is_delta: bool = False,
) -> str:
    """Generates the union query.

    Args:
        part (CompValue): Current part of the query.

    Returns:
        str: Query string containing the union operation.
    """
    if len(schemas1) == 1 and len(schemas2) == 1:
        return __union_query_sub(
            part,
            schemas1[0],
            schemas2[0],
            is_delta=is_delta,
        )
    else:
        all_queries: str = ""
        for sch1 in schemas1:
            for sch2 in schemas2:
                all_queries += __union_query_sub(
                    part,
                    sch1,
                    sch2,
                    True,
                    is_delta=is_delta,
                )
        return all_queries
    """union_query: str = (
        "SELECT "
        + ", ".join(
            f"(CASE WHEN r1.{var} IS NOT NULL THEN r1.{var} ELSE r2.{var} END) AS {var}"
            for var in sorted(part.p1._vars)
        )
        + ", coalesce(r1.k_count, 0) + coalesce(r2.k_count, 0) as k_count\n"
        + "FROM "
        + __encode_table_name(part.p1)
        + " AS r1 FULL OUTER JOIN "
        + __encode_table_name(part.p2)
        + " AS r2 ON "
    )
    union_query += " AND ".join(
        f"r1.{var} = r2.{var}"
        for var in sorted(
            part.p1._vars.intersection(part.p2._vars)
        )
    )
    union_query += ";\n"

    union_query_right: str = (
        "SELECT "
        + ", ".join(
            f"(CASE WHEN r1.{var} IS NOT NULL THEN r1.{var} ELSE r2.{var} END) AS {var}"
            for var in sorted(part.p2._vars)
        )
        + ", coalesce(r1.k_count, 0) + coalesce(r2.k_count, 0) as k_count\n"
        + "FROM "
        + __encode_table_name(part.p1)
        + " AS r1 FULL OUTER JOIN "
        + __encode_table_name(part.p2)
        + " AS r2 ON "
    )

    return create_table_w_select(
        __encode_table_name(part)
        + "_"
        + __encode_schema_name(str(sorted(part.p1._vars))),
        union_query,
    ) + create_table_w_select(
        __encode_table_name(part)
        + "_"
        + __encode_schema_name(str(sorted(part.p2._vars))),
        union_query_right,
    )"""


def union_schemas(
    part: CompValue,
    schemas1: list[set[str]],
    schemas2: list[set[str]],
) -> list[set[str]]:
    """Constructs the schemas of the union part of the query.

    Args:
        part (CompValue): Current part of the query
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
    """union_query = (
        "SELECT "
        + ", ".join(
            f"(CASE WHEN r1.{var} IS NOT NULL THEN r1.{var} ELSE r2.{var} END) AS {var}"
            for var in sorted(part.p1._vars)
        )
        + ", coalesce(r1.k_count, 0) + coalesce(r2.k_count, 0) as k_count\n"
    )
    union_query += (
        "FROM delta_"
        + __encode_table_name(part.p1)
        + " AS r1 FULL OUTER JOIN delta_"
        + __encode_table_name(part.p2)
        + " AS r2 ON "
    )
    union_query += " AND ".join(
        f"r1.{var} = r2.{var}"
        for var in sorted(
            part.p1._vars.intersection(part.p2._vars)
        )
    )
    union_query += ";\n"

    union_query_right = (
        "SELECT "
        + ", ".join(
            f"(CASE WHEN r1.{var} IS NOT NULL THEN r1.{var} ELSE r2.{var} END) AS {var}"
            for var in sorted(part.p2._vars)
        )
        + ", coalesce(r1.k_count, 0) + coalesce(r2.k_count, 0) as k_count\n"
    )
    union_query_right += (
        "FROM delta_"
        + __encode_table_name(part.p1)
        + " AS r1 FULL OUTER JOIN delta_"
        + __encode_table_name(part.p2)
        + " AS r2 ON "
    )
    union_query_right += " AND ".join(
        f"r1.{var} = r2.{var}"
        for var in sorted(
            part.p1._vars.intersection(part.p2._vars)
        )
    )
    union_query_right += ";\n"

    return create_table_w_select(
        "delta_"
        + __encode_table_name(part)
        + "_"
        + __encode_schema_name(str(sorted(part.p1._vars))),
        union_query,
    ) + create_table_w_select(
        "delta_"
        + __encode_table_name(part)
        + "_"
        + __encode_schema_name(str(sorted(part.p2._vars))),
        union_query_right,
    )"""
