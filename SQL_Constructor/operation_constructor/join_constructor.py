from SQL_Constructor.base_constructor import (
    __encode_schema_name,
    __encode_table_name,
    create_table_w_select,
    insert_into_w_select,
    join_schemas,
)


from rdflib.plugins.sparql.parserutils import CompValue


def join_query(
    part: CompValue,
    table_name_one: str,
    table_name_two: str,
    schemas1: list[set[str]] = [],
    schemas2: list[set[str]] = [],
    new_table_name: str | None = None,
) -> str:
    """Generates the join part according to two parts in the parse tree.

    Args:
        part (CompValue): Current part of the algebra.

    Returns:
        str: The SQL query to join both parts.
    """
    if new_table_name is None:
        new_table_name = __encode_table_name(part)

    def sch2SelectClause(
        sch1: set[str], sch2: set[str]
    ) -> str:
        if sch1.intersection(sch2) == set():
            return ""
        else:
            return ", " + ", ".join(
                f"r2.{var} AS {var}"
                for var in sorted(sch2.difference(sch1))
            )

    if len(schemas1) == 0 or len(schemas2) == 0:
        raise ValueError("No schemas to join on.")
    elif len(schemas1) == 1 and len(schemas2) == 1:
        if schemas1[0] == schemas2[0]:
            join_query: str = (
                "SELECT "
                + ", ".join(
                    f"r1.{var} AS {var}"
                    for var in sorted(
                        part.p1._vars.union(part.p2._vars)
                    )
                )
                + ", r1.k_count * r2.k_count as k_count\n"
            )
            join_query += "FROM "
            join_query += table_name_one
            join_query += " AS r1 JOIN "
            join_query += table_name_two
            join_query += " AS r2 "
            if (
                part.p1._vars.intersection(part.p2._vars)
                != set()
            ):
                join_query += "ON "
                join_query += " AND ".join(
                    f"r1.{var} = r2.{var}"
                    for var in sorted(
                        part.p1._vars.intersection(
                            part.p2._vars
                        )
                    )
                )
            join_query += ";\n"
        else:
            join_query: str = (
                "SELECT "
                + ", ".join(
                    f"r1.{var} AS {var}"
                    for var in sorted(schemas1[0])
                )
                + sch2SelectClause(schemas1[0], schemas2[0])
                + ", r1.k_count * r2.k_count as k_count\n"
                + "FROM "
                + table_name_one
                + " AS r1, "
                + table_name_two
                + " AS r2 ON "
                + " AND ".join(
                    f"r1.{var} = r2.{var}"
                    for var in sorted(
                        schemas1[0].intersection(
                            schemas2[0]
                        )
                    )
                )
                + ";\n"
            )

        join_query = create_table_w_select(
            new_table_name, join_query
        )

    else:

        # Construct for prep table
        already_seen_join_schemas = list()
        double_schemas = list()
        for sch1 in schemas1:
            for sch2 in schemas2:
                curr_join_schema: set[str] = sch1.union(
                    sch2
                )
                if (
                    curr_join_schema
                    not in already_seen_join_schemas
                ):
                    already_seen_join_schemas.append(
                        curr_join_schema
                    )
                else:
                    double_schemas.append(curr_join_schema)
        already_seen_join_schemas = list()

        join_query: str = ""
        join_schemas_list = join_schemas(
            part, schemas1, schemas2
        )
        for sch1 in schemas1:
            for sch2 in schemas2:
                if not len(schemas1) == 1:
                    sch1_suffix: str = (
                        "_"
                        + __encode_schema_name(
                            str(sorted(sch1))
                        )
                    )
                else:
                    sch1_suffix: str = ""
                if not len(schemas2) == 1:
                    sch2_suffix: str = (
                        "_"
                        + __encode_schema_name(
                            str(sorted(sch2))
                        )
                    )
                else:
                    sch2_suffix: str = ""

                if sch1.intersection(sch2) == set():
                    curr_join_query: str = (
                        "SELECT "
                        + ", ".join(
                            f"r1.{var} AS {var}"
                            for var in sorted(sch1)
                        )
                        + sch2SelectClause(sch1, sch2)
                        + ", r1.k_count * r2.k_count as k_count\n"
                    )
                    curr_join_query += "FROM "
                    curr_join_query += (
                        table_name_one + sch1_suffix
                    )
                    curr_join_query += " AS r1, "
                    curr_join_query += (
                        table_name_two + sch2_suffix
                    )
                    curr_join_query += " AS r2;\n"
                else:
                    curr_join_query: str = (
                        "SELECT "
                        + ", ".join(
                            f"r1.{var} AS {var}"
                            for var in sorted(sch1)
                        )
                        + sch2SelectClause(sch1, sch2)
                        + ", r1.k_count * r2.k_count as k_count\n"
                        + "FROM "
                        + table_name_one
                        + sch1_suffix
                        + " AS r1, "
                        + table_name_two
                        + sch2_suffix
                        + " AS r2 "
                        + "ON "
                        + " AND ".join(
                            f"r1.{var} = r2.{var}"
                            for var in sorted(
                                sch1.intersection(sch2)
                            )
                        )
                        + ";\n"
                    )

                # Checks if the join schema has already been seen
                # to insert to same table
                curr_join_schema: set[str] = sch1.union(
                    sch2
                )
                if curr_join_schema in double_schemas:
                    temp_prefix: str = " TEMP "
                    prep_prefix: str = "prep_"
                else:
                    temp_prefix: str = ""
                    prep_prefix: str = ""
                if len(join_schemas_list) == 1:
                    if (
                        curr_join_schema
                        not in already_seen_join_schemas
                    ):
                        already_seen_join_schemas.append(
                            curr_join_schema
                        )
                        join_query += create_table_w_select(
                            prep_prefix + new_table_name,
                            curr_join_query,
                            temp_prefix=temp_prefix,
                        )
                    else:
                        join_query += insert_into_w_select(
                            prep_prefix + new_table_name,
                            curr_join_query,
                            curr_join_schema,
                        )
                else:
                    if (
                        curr_join_schema
                        not in already_seen_join_schemas
                    ):
                        already_seen_join_schemas.append(
                            curr_join_schema
                        )
                        join_query += create_table_w_select(
                            prep_prefix
                            + new_table_name
                            + "_"
                            + __encode_schema_name(
                                str(
                                    sorted(curr_join_schema)
                                )
                            ),
                            curr_join_query,
                            temp_prefix=temp_prefix,
                        )
                    else:
                        join_query += insert_into_w_select(
                            prep_prefix
                            + new_table_name
                            + "_"
                            + __encode_schema_name(
                                str(
                                    sorted(curr_join_schema)
                                )
                            ),
                            curr_join_query,
                            sorted(sch1)
                            + sorted(sch2.difference(sch1)),
                            False,
                        )

        for joined_schemas in double_schemas:
            if len(join_schemas_list) == 1:
                schema_suffix: str = ""
            else:
                schema_suffix: str = (
                    "_"
                    + __encode_schema_name(
                        str(sorted(joined_schemas))
                    )
                )
            join_query += create_table_w_select(
                new_table_name,
                "SELECT "
                + ", ".join(
                    f"{var}"
                    for var in sorted(joined_schemas)
                    if var != "k_count"
                )
                + ", SUM(k_count) AS k_count\nFROM prep_"
                + new_table_name
                + schema_suffix
                + "\nGROUP BY "
                + ", ".join(
                    f"{var}"
                    for var in sorted(joined_schemas)
                    if var != "k_count"
                )
                + ";",
            )

    return join_query
