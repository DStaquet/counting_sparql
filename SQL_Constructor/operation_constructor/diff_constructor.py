from SQL_Constructor.base_constructor import (
    __encode_schema_name,
    __encode_table_name,
    create_table_w_select,
)


from rdflib.plugins.sparql.parserutils import CompValue


def delta_diff_sub(
    part: CompValue,
    schemas1: list[set[str]],
    schemas2: list[set[str]],
) -> str:
    """Generates the minus subquery.

    Args:
        part (CompValue): Current part of the query containing the minus operation.

    Returns:
        str: Query string of the needed minus operation.
    """

    diff_delta_first_part: str = diff_query_sub(
        part,
        schemas1,
        schemas2,
        first_from_table="delta_"
        + __encode_table_name(part.p1),
    )

    return diff_delta_first_part

    """# R1 MINUS delta_R2
    first_query: str = (
        "INSERT INTO delta_"
        + __encode_table_name(part)
        + "\n"
    )
    first_query += "SELECT " + ", ".join(
        var for var in sorted(part.p1._vars)
    )
    if part.p2._vars.difference(part.p1._vars) != set():
        first_query += ", " + ", ".join(
            f"coalesce(p2.{var}, 'UNBOUND')"
            for var in sorted(
                part.p2._vars.difference(part.p1._vars)
            )
        )
    first_query += ", p1.k_count as k_count\n"
    first_query += (
        "FROM delta_"
        + __encode_table_name(part.p1)
        + " AS p1\n"
    )
    first_query += "WHERE (" + ", ".join(
        f"p1.{var}"
        for var in sorted(
            part.p1._vars.intersection(part.p2._vars)
        )
    )
    first_query += ") NOT IN (SELECT " + ", ".join(
        f"p2.{var}"
        for var in sorted(
            part.p1._vars.intersection(part.p2._vars)
        )
    )
    first_query += (
        " FROM "
        + __encode_table_name(part.p2)
        + " AS p2)\n"
    )
    first_query += "ON CONFLICT DO\nUPDATE SET\n\t"
    first_query += (
        "k_count = EXCLUDED.k_count + k_count\n"
        + "WHERE "
        + " AND ".join(
            f"{var} = EXCLUDED.{var}"
            for var in sorted(part.p1._vars)
        )
        + " AND "
        + " AND ".join(
            f"{var} = EXCLUDED.{var}"
            for var in sorted(
                part.p2._vars.difference(part.p1._vars)
            )
        )
    )
    first_query += ";\n"

    # R1_nu MINUS delta_R2 - First part
    second_query_first: str = (
        "INSERT INTO delta_"
        + __encode_table_name(part)
        + "\n"
    )
    first_query += "SELECT " + ", ".join(
        var for var in sorted(part.p1._vars)
    )
    if part.p2._vars.difference(part.p1._vars) != set():
        first_query += ", " + ", ".join(
            f"coalesce(p2.{var}, 'UNBOUND')"
            for var in sorted(
                part.p2._vars.difference(part.p1._vars)
            )
        )
    first_query += ", p1.k_count as k_count\n"
    second_query_first += "FROM "
    second_query_first += (
        "nu_"
        + __encode_table_name(part.p1)
        + " AS p1, delta_"
        + __encode_table_name(part.p2)
        + " AS delta_p2\n"
    )
    if part.p1._vars.intersection(part.p2._vars) != set():
        second_query_first += "WHERE (" + ", ".join(
            f"p1.{var} = delta_p2.{var}"
            for var in sorted(
                part.p1._vars.intersection(part.p2._vars)
            )
        )
        second_query_first += (
            ", -delta_p2.k_count) IN (SELECT "
            + ", ".join(
                f"{var}"
                for var in sorted(
                    part.p1._vars.intersection(
                        part.p2._vars
                    )
                )
            )
            + ", k_count\n"
        )
        second_query_first += (
            "FROM "
            + __encode_table_name(part.p2)
            + " AS p2)\n"
        )
    second_query_first += "ON CONFLICT DO\nUPDATE SET\n\t"
    second_query_first += (
        "k_count = EXCLUDED.k_count + k_count\n"
        + "WHERE "
        + " AND ".join(
            f"{var} = EXCLUDED.{var}"
            for var in sorted(part.p1._vars)
        )
        + " AND "
        + " AND ".join(
            f"{var} = EXCLUDED.{var}"
            for var in sorted(
                part.p2._vars.difference(part.p1._vars)
            )
        )
    )
    second_query_first += ";\n"

    # R1_nu MINUS delta_R2 - Second part
    second_query_second: str = (
        "INSERT INTO delta_"
        + __encode_table_name(part)
        + "\n"
    )
    first_query += "SELECT " + ", ".join(
        var for var in sorted(part.p1._vars)
    )
    if part.p2._vars.difference(part.p1._vars) != set():
        first_query += ", " + ", ".join(
            f"coalesce(p2.{var}, 'UNBOUND')"
            for var in sorted(
                part.p2._vars.difference(part.p1._vars)
            )
        )
    first_query += ", -p1.k_count as k_count\n"
    second_query_second += "FROM "
    second_query_second += (
        "nu_"
        + __encode_table_name(part.p1)
        + " AS p1, delta_"
        + __encode_table_name(part.p2)
        + " AS delta_p2\n"
    )
    if part.p1._vars.intersection(part.p2._vars) != set():
        second_query_second += "WHERE (" + ", ".join(
            f"p1.{var} = delta_p2.{var}"
            for var in sorted(
                part.p1._vars.intersection(part.p2._vars)
            )
        )
        second_query_second += (
            ", k_count) NOT IN (SELECT "
            + ", ".join(
                f"{var}"
                for var in sorted(
                    part.p1._vars.intersection(
                        part.p2._vars
                    )
                )
            )
            + ", k_count\n"
        )
        second_query_second += (
            "FROM "
            + __encode_table_name(part.p2)
            + " AS p2)\n"
        )
    second_query_second += "ON CONFLICT DO\nUPDATE SET\n\t"
    second_query_second += (
        "k_count = EXCLUDED.k_count + k_count\n"
        + "WHERE "
        + " AND ".join(
            f"{var} = EXCLUDED.{var}"
            for var in sorted(part.p1._vars)
        )
        + " AND "
        + " AND ".join(
            f"{var} = EXCLUDED.{var}"
            for var in sorted(
                part.p2._vars.difference(part.p1._vars)
            )
        )
    )
    second_query_second += ";\n"

    second_query: str = (
        second_query_first + second_query_second
    )

    return first_query + second_query"""


def __diffSch2Subquery(
    part: CompValue,
    second_table_name: str,
    sch2: set[str],
    sch1: set[str],
    schemas2_len: int,
    index: int,
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
        + second_table_name
        + sch2_suffix
        + f" AS s{index}"
        + " WHERE "
        + " AND ".join(
            f"s1.{var} = s{index}.{var}"
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
    first_from_table: str | None = None,
    second_from_table: str | None = None,
) -> str:
    """Generates the difference subquery.

    Args:
        part (CompValue): Current part of the query containing the dofference operation.

    Returns:
        str: Query string of the needed difference operation.
    """
    diff_query = ""

    if first_from_table is None:
        first_from_table = __encode_table_name(part.p1)
    if second_from_table is None:
        second_from_table = __encode_table_name(part.p2)

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
                + first_from_table
                + schemas1_suffix
                + " AS s1"
            )
            if len(schemas2) > 0:
                curr_diff_query += " WHERE " + " AND ".join(
                    f"NOT EXISTS ("
                    + __diffSch2Subquery(
                        part,
                        second_from_table,
                        sch2,
                        sch1,
                        len(schemas2),
                        index + 2,
                    )
                    + ")"
                    for index, sch2 in enumerate(schemas2)
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
