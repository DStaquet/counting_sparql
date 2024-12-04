from SQL_Constructor.base_constructor import (
    __encode_schema_name,
    __encode_table_name,
    create_table_w_select,
)


from rdflib.plugins.sparql.parserutils import CompValue


def __diffSch2Subquery(
    part: CompValue,
    sch2: set[str],
    sch1: set[str],
    schemas2_len: int,
) -> str:
    """Generate the subquery to use in the diff query

    Args:
        sch2 (set[str]): Schema of the subquery
        sch1 (set[str]): Schema of the left table

    Returns:
        str: String containing the sub query for the schema
            combinations of sch1 and sch2.
    """
    if schemas2_len > 1:
        sch2_suffix: str = "_" + __encode_schema_name(
            str(sorted(sch2))
        )
    else:
        sch2_suffix: str = ""
    subquery_diff_str: str = (
        "FROM "
        + __encode_table_name(part.p2)
        + sch2_suffix
        + " WHERE "
        + " AND ".join(
            f"s1.{var} = s2.{var}"
            for var in sorted(sch1.intersection(sch2))
        )
    )

    return subquery_diff_str


def __check_if_same_schema(
    schemas1: list[set[str]],
    schemas2: list[set[str]],
) -> bool:
    """Checks if only one schema is the result of both joins.

    Args:
        schemas1 (list[set[str]]): Left schemas of the join.
        schemas2 (list[set[str]]): Right schemas of the join.

    Returns:
        bool: True if the schemas are the same, False otherwise.
    """
    join_schemas: list[set[str]] = list()
    for sch1 in schemas1:
        join_schemas.append(sch1)
        for sch2 in schemas2:
            join_schemas.append(sch1.union(sch2))
    return len(join_schemas) == 1


def diff_query_sub(
    part: CompValue,
    schemas1: list[set[str]] = [],
    schemas2: list[set[str]] = [],
    minus: bool = False,
) -> str:
    """Generates the difference subquery.

    Args:
        part (CompValue): Current part of the query containing the dofference operation.

    Returns:
        str: Query string of the needed difference operation.
    """
    diff_query = ""

    if len(schemas1) == 0 or len(schemas2) == 0:
        raise ValueError("No schemas to join on.")
    else:
        for sch1 in schemas1:
            if len(schemas1) > 1:
                schemas1_suffix: str = (
                    "_"
                    + __encode_schema_name(
                        str(sorted(sch1))
                    )
                )
            else:
                schemas1_suffix: str = ""

            if __check_if_same_schema(schemas1, schemas2):
                schemas_both_suffix: str = ""
            else:
                schemas_both_suffix: str = (
                    "_"
                    + __encode_schema_name(
                        str(sorted(sch1))
                    )
                )

            if minus:
                schemas2 = [
                    sch2
                    for sch2 in schemas2
                    if sch1.intersection(sch2) != set()
                ]

            curr_diff_query: str = (
                "SELECT "
                + ", ".join(
                    f"s1.{var}" for var in sorted(sch1)
                )
                + " FROM "
                + __encode_table_name(part.p1)
                + schemas1_suffix
            )
            if len(schemas2) > 0:
                curr_diff_query += " WHERE " + " AND ".join(
                    f"NOT EXISTS ("
                    + __diffSch2Subquery(
                        part, sch2, sch1, len(schemas2)
                    )
                    + ")"
                    for sch2 in schemas2
                )
            curr_diff_query += ";\n"
            diff_query += create_table_w_select(
                __encode_table_name(part)
                + schemas_both_suffix,
                curr_diff_query,
            )

    return diff_query
    """diff_query: str = (
        "INSERT INTO "
        + __encode_table_name(part)
        + "\n"
        + "SELECT "
        + ", ".join(var for var in sorted(part.p1._vars))
    )
    if part.p2._vars.difference(part.p1._vars) != set():
        diff_query += ", " + ", ".join(
            f"coalesce(p2.{var}, 'UNBOUND')"
            for var in sorted(
                part.p2._vars.difference(part.p1._vars)
            )
        )
    diff_query += (
        ", p1.k_count as k_count\n"
        + "FROM "
        + __encode_table_name(part.p1)
        + " AS p1\n"
    )
    diff_query += "WHERE (" + ", ".join(
        f"p1.{var}"
        for var in sorted(
            part.p1._vars.intersection(part.p2._vars)
        )
    )
    diff_query += ") NOT IN (SELECT " + ", ".join(
        f"p2.{var}"
        for var in sorted(
            part.p1._vars.intersection(part.p2._vars)
        )
    )
    diff_query += (
        " FROM "
        + __encode_table_name(part.p2)
        + " AS p2)\n"
    )
    diff_query += "ON CONFLICT DO\nUPDATE SET\n\t"
    diff_query += (
        "k_count = EXCLUDED.k_count + k_count\n"
        + "WHERE "
        + " AND ".join(
            f"{var} = EXCLUDED.{var}"
            for var in sorted(part.p1._vars)
        )
    )
    if part.p2._vars.difference(part.p1._vars) != set():
        diff_query += " AND " + " AND ".join(
            f"{var} = EXCLUDED.{var}"
            for var in sorted(
                part.p2._vars.difference(part.p1._vars)
            )
        )
    diff_query += ";\n"

    return diff_query"""
