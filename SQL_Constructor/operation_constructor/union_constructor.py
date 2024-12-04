from SQL_Constructor.base_constructor import __union_query


from rdflib.plugins.sparql.parserutils import CompValue


def union_query(
    part: CompValue,
    schemas1: list[set[str]] = [],
    schemas2: list[set[str]] = [],
) -> str:
    """Generates the union query.

    Args:
        part (CompValue): Current part of the query.

    Returns:
        str: Query string containing the union operation.
    """
    if len(schemas1) == 1 and len(schemas2) == 1:
        return __union_query(part, schemas1[0], schemas2[0])
    else:
        all_queries: str = ""
        for sch1 in schemas1:
            for sch2 in schemas2:
                all_queries += __union_query(
                    part, sch1, sch2, True
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
