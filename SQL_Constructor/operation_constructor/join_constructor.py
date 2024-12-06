from SQL_Constructor import base_constructor
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
    is_delta_and_first: tuple[bool, bool] = (False, False),
) -> str:
    """Generates the join part according to two parts in the parse tree.

    Args:
        part (CompValue): Current part of the algebra.

    Returns:
        str: The SQL query to join both parts.
    """
    if is_delta_and_first[0]:
        new_table_name = (
            "delta_" + base_constructor.get_table_name(part)
        )
    else:
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

        # Construct for prep table if delta, otherwise insert into
        if is_delta_and_first[0]:
            temp_prefix: str = " TEMP "
            prep_prefix: str = "prep_"
        else:
            temp_prefix: str = ""
            prep_prefix: str = ""
        if (
            is_delta_and_first[0] and is_delta_and_first[1]
        ) or not is_delta_and_first[0]:
            join_query = create_table_w_select(
                prep_prefix + new_table_name,
                join_query,
                temp_prefix=temp_prefix,
            )
        else:
            join_query = insert_into_w_select(
                prep_prefix + new_table_name,
                join_query,
                list(schemas1[0].union(schemas2[0])),
            )

        if (
            is_delta_and_first[0]
            and not is_delta_and_first[1]
        ):
            join_query += create_table_w_select(
                new_table_name,
                "SELECT "
                + ", ".join(
                    f"{var}"
                    for var in sorted(
                        schemas1[0].union(schemas2[0])
                    )
                    if var != "k_count"
                )
                + ", SUM(k_count) AS k_count\nFROM "
                + prep_prefix
                + new_table_name
                + "\nGROUP BY "
                + ", ".join(
                    f"{var}"
                    for var in sorted(
                        schemas1[0].union(schemas2[0])
                    )
                    if var != "k_count"
                )
                + ";",
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
                if (curr_join_schema in double_schemas) or (
                    is_delta_and_first[0]
                    and len(join_schemas_list) > 1
                ):
                    temp_prefix: str = " TEMP "
                    prep_prefix: str = "prep_"
                else:
                    temp_prefix: str = ""
                    prep_prefix: str = ""
                if len(join_schemas_list) == 1:
                    if (
                        is_delta_and_first[0]
                        and is_delta_and_first[1]
                        and curr_join_schema
                        not in already_seen_join_schemas
                    ) or (
                        not is_delta_and_first[0]
                        and curr_join_schema
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
                            list(curr_join_schema),
                        )
                else:
                    if (
                        is_delta_and_first[0]
                        and is_delta_and_first[1]
                        and curr_join_schema
                        not in already_seen_join_schemas
                    ) or (
                        not is_delta_and_first[0]
                        and curr_join_schema
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

        if not is_delta_and_first[0] or (
            is_delta_and_first[0]
            and not is_delta_and_first[1]
        ):
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
                    new_table_name + schema_suffix,
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
        if (
            is_delta_and_first[0]
            and not is_delta_and_first[1]
        ):
            for joined_schema in [
                joined_schema
                for joined_schema in join_schemas_list
                if joined_schema not in double_schemas
            ]:
                if len(join_schemas_list) == 1:
                    schema_suffix: str = ""
                else:
                    schema_suffix: str = (
                        "_"
                        + __encode_schema_name(
                            str(sorted(joined_schema))
                        )
                    )
                join_query += create_table_w_select(
                    new_table_name + schema_suffix,
                    "SELECT "
                    + ", ".join(
                        f"{var}"
                        for var in sorted(joined_schema)
                        if var != "k_count"
                    )
                    + ", SUM(k_count) AS k_count\nFROM prep_"
                    + new_table_name
                    + schema_suffix
                    + "\nGROUP BY "
                    + ", ".join(
                        f"{var}"
                        for var in sorted(joined_schema)
                        if var != "k_count"
                    )
                    + ";",
                )

    return join_query


def delta_join_queries_part_func(
    part: CompValue,
    schemas1: list[set[str]],
    schemas2: list[set[str]],
) -> str:
    """Constructs the delta join queries

    Args:
        part (CompValue): Current part of the query

    Returns:
        str: SQL query for the delta join
    """
    first_delta_query: str = join_query(
        part,
        "delta_" + base_constructor.get_table_name(part.p1),
        __encode_table_name(part.p2),
        schemas1,
        schemas2,
        is_delta_and_first=(True, True),
    )

    second_delta_query: str = join_query(
        part,
        "nu_" + base_constructor.get_table_name(part.p1),
        "delta_" + base_constructor.get_table_name(part.p2),
        schemas1,
        schemas2,
        is_delta_and_first=(True, False),
    )

    """delta_prep_sum: str = (
        base_constructor.delta_prep_sum_query(part)
    )
    delta_queries_sum = (
        base_constructor.create_table_w_select(
            "delta_"
            + base_constructor.get_table_name(part),
            delta_prep_sum,
        )
    )"""

    return first_delta_query + second_delta_query
