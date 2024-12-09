from SQL_Constructor.base_constructor import (
    __encode_schema_name,
    __encode_table_name,
    create_table_w_select,
    insert_into_w_select,
)


from rdflib.plugins.sparql.parserutils import CompValue


def __delta_on_negate_part(
    part: CompValue,
    schemas1: list[set[str]],
    schemas2: list[set[str]],
    new_table_name: str | None = None,
    minus: bool = False,
) -> str:
    """Generates the delta on negate part of the left join query.

    Args:
        part (CompValue): Current part of the query.
        schemas1 (list[set[str]]): Schemas of the left child of the part.
        schemas2 (list[set[str]]): Schemas of the right child of the part.
        new_table_name (str | None, optional): Table name to write to. Defaults to None.

    Returns:
        str: Queries to make diff part of delta.
    """
    if new_table_name is None:
        new_table_name = __encode_table_name(part)

    nu_from_table: str = "nu_" + __encode_table_name(
        part.p1
    )
    delta_from_table: str = "delta_" + __encode_table_name(
        part.p2
    )
    old_delta_from_table_name: str = __encode_table_name(
        part.p2
    )

    diff_queries: str = ""

    if len(schemas1) == 0:
        raise ValueError("No schemas to join on.")
    for sch1 in schemas1:

        if minus:
            schemas2 = [
                sch2
                for sch2 in schemas2
                if sch1.intersection(sch2) != set()
            ]

        curr_diff_query_select_left: str = (
            "SELECT * FROM "
            + nu_from_table
            + " as s1 JOIN "
            + delta_from_table
            + " as s2 ON "
            + " AND ".join(
                f"s1.{var} = s2.{var}"
                for var in sorted(schemas1[0])
            )
        )
        curr_diff_query_select_right: str = (
            "SELECT "
            + ", ".join(
                f"s1.{var} as {var}" for var in sorted(sch1)
            )
            + ", -s1.k_count as k_count"
            + " FROM "
            + nu_from_table
            + " as s1 JOIN "
            + delta_from_table
            + " as s2 ON "
            + " AND ".join(
                f"s1.{var} = s2.{var}"
                for var in sorted(sch1)
            )
        )

        curr_diff_query_left: str = ""
        curr_diff_query_right: str = ""
        if len(schemas2) > 0:
            curr_diff_query_left = " WHERE " + " AND ".join(
                f" EXISTS ("
                + __diffSch2Subquery(
                    part,
                    old_delta_from_table_name,
                    sch2,
                    sch1,
                    len(schemas2),
                    index + 3,
                    is_delta=True,
                    delta_swap="-",
                )
                + ")"
                for index, sch2 in enumerate(schemas2)
            )
            curr_diff_query_right = (
                " WHERE "
                + " AND ".join(
                    f"NOT EXISTS ("
                    + __diffSch2Subquery(
                        part,
                        old_delta_from_table_name,
                        sch2,
                        sch1,
                        len(schemas2),
                        index + 3,
                        is_delta=True,
                    )
                    + ")"
                    for index, sch2 in enumerate(schemas2)
                )
            )
        curr_diff_query = (
            curr_diff_query_select_left
            + curr_diff_query_left
            + " UNION "
            + curr_diff_query_select_right
            + curr_diff_query_right
            + ";\n"
        )

        if __check_if_same_diff_schema(schemas1, schemas2):
            schema_both_suffix: str = ""
        else:
            schema_both_suffix: str = (
                "_"
                + __encode_schema_name(str(sorted(sch1)))
            )

        diff_queries += insert_into_w_select(
            new_table_name + schema_both_suffix,
            curr_diff_query,
        )

    return diff_queries


def delta_diff_sub(
    part: CompValue,
    schemas1: list[set[str]],
    schemas2: list[set[str]],
    new_table_name: str | None = None,
    append_schemas: bool = True,
    minus: bool = False,
) -> str:
    """Generates the minus subquery.

    Args:
        part (CompValue): Current part of the query containing the minus operation.

    Returns:
        str: Query string of the needed minus operation.
    """

    delta_table_name: str = (
        "delta_prep_" + __encode_table_name(part)
    )

    diff_delta_first_part: str = diff_query_sub(
        part,
        schemas1,
        schemas2,
        first_from_table="delta_"
        + __encode_table_name(part.p1),
        new_table_name=delta_table_name,
        append_schemas=append_schemas,
        minus=minus,
    )

    diff_delta_second_part: str = __delta_on_negate_part(
        part,
        schemas1,
        schemas2,
        delta_table_name,
        minus=minus,
    )

    return diff_delta_first_part + diff_delta_second_part


def __diffSch2Subquery(
    part: CompValue,
    second_table_name: str,
    sch2: set[str],
    sch1: set[str],
    schemas2_len: int,
    index: int,
    is_delta: bool = False,
    delta_swap: str = "",
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
    if is_delta and delta_swap != "":
        subquery_diff_str += f" AND {delta_swap}s2.k_count = s{index}.k_count"

    return subquery_diff_str


def __check_if_same_diff_schema(
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
            if (
                sch1.union(sch1.intersection(sch2))
                not in join_schemas
            ):
                join_schemas.append(
                    sch1.union(sch1.intersection(sch2))
                )
    print(join_schemas)
    return len(join_schemas) == 1


def diff_query_sub(
    part: CompValue,
    schemas1: list[set[str]] = [],
    schemas2: list[set[str]] = [],
    minus: bool = False,
    first_from_table: str | None = None,
    second_from_table: str | None = None,
    new_table_name: str | None = None,
    append_schemas: bool = False,
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

    if new_table_name is None:
        new_table_name = __encode_table_name(part)

    if len(schemas1) == 0 or len(schemas2) == 0:
        raise ValueError("No schemas to join on.")
    else:
        for sch1 in schemas1:
            if len(schemas1) <= 1:
                schemas1_suffix: str = ""
                schemas_both_suffix: str = ""
            else:
                schemas1_suffix: str = (
                    "_"
                    + __encode_schema_name(
                        str(sorted(sch1))
                    )
                )

            if (
                __check_if_same_diff_schema(
                    schemas1, schemas2
                )
                and not append_schemas
            ):
                schemas_both_suffix: str = ""
            else:
                schemas_both_suffix: str = (
                    "_"
                    + __encode_schema_name(
                        str(sorted(sch1))
                    )
                )

            schemas2_len = len(schemas2)
            if minus:
                schemas2 = [
                    sch2
                    for sch2 in schemas2
                    if sch1.intersection(sch2) != set()
                ]

            curr_diff_query: str = (
                "SELECT "
                + ", ".join(
                    f"s1.{var} as {var}"
                    for var in sorted(sch1)
                )
                + ", s1.k_count as k_count"
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
                        schemas2_len,
                        index + 2,
                    )
                    + ")"
                    for index, sch2 in enumerate(schemas2)
                )
            curr_diff_query += ";\n"
            diff_query += create_table_w_select(
                new_table_name + schemas_both_suffix,
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
