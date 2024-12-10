from SQL_Constructor import base_constructor
from SQL_Constructor.base_constructor import (
    __encode_schema_name,
    __encode_table_name,
    combine_dict_queries,
    make_group_by,
    make_join,
    create_table_w_select,
    add_table_to_dict,
)


from rdflib.plugins.sparql.parserutils import CompValue


def join_schemas(
    schemas1: list[set[str]],
    schemas2: list[set[str]],
) -> list[set[str]]:
    """Constructs the schemas of the join part of the query.

    Args:
        part (CompValue): Current part of the query
        schemas1 (list[set[str]]): Schema of the left child of the join
        schemas2 (list[set[str]]): Schema of the right child of the join

    Returns:
        list[set[str]]: Schema of the join part of the query
    """
    new_schema = []
    for schema in schemas1:
        for schema2 in schemas2:
            if schema.union(schema2) not in new_schema:
                new_schema.append(schema.union(schema2))
    return new_schema


def sch2SelectClause(sch1: set[str], sch2: set[str]) -> str:
    """Returns the schema of the second table

    Args:
        sch1 (set[str]): _description_
        sch2 (set[str]): _description_

    Returns:
        str: _description_
    """
    return ", " + ", ".join(
        f"r2.{var} AS {var}"
        for var in sorted(sch2.difference(sch1))
    )


def __join_query_one_schema(
    part: CompValue,
    schemas1: list[set[str]],
    schemas2: list[set[str]],
    table_name_one: str,
    table_name_two: str,
) -> str:
    """Generates the SQL queries for only one schema.

    Args:
        schemas1 (list[set[str]]): Schema of the left child of the join
        schemas2 (list[set[str]]): Schema of the right child of the join

    Returns:
        str: Query string for the join operation
    """
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
                    schemas1[0].intersection(schemas2[0])
                )
            )
            + ";\n"
        )

    return join_query


def __join_query_mult_schema(
    part: CompValue,
    schemas1: list[set[str]],
    schemas2: list[set[str]],
    table_name_one: str,
    table_name_two: str,
    new_table_name: str,
) -> dict[str, list[str]]:
    """Constructs a join query for multiple schemas.

    Args:
        schemas1 (list[set[str]]): Schemas of the first table child
        schemas2 (list[set[str]]): Schemas of the second table child

    Returns:
        dict[str, list[str]]: Dictionary containing the join queries per key
    """
    join_queries_dict: dict[str, list[str]] = dict()

    """# Construct for prep table
    already_seen_join_schemas = list()
    double_schemas = list()
    for sch1 in schemas1:
        for sch2 in schemas2:
            curr_join_schema: set[str] = sch1.union(sch2)
            if (
                curr_join_schema
                not in already_seen_join_schemas
            ):
                already_seen_join_schemas.append(
                    curr_join_schema
                )
            else:
                double_schemas.append(curr_join_schema)
    already_seen_join_schemas = list()"""

    """join_query: str = ""
    join_schemas_list = join_schemas(
        part, schemas1, schemas2
    )"""
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

            curr_join_schema: set[str] = sch1.union(sch2)
            join_queries_dict = add_table_to_dict(
                new_table_name
                + "_"
                + __encode_schema_name(
                    str(sorted(curr_join_schema))
                ),
                curr_join_query,
                join_queries_dict,
            )

    return join_queries_dict


def join_query_str_constr(
    part: CompValue,
    table_name_one: str,
    table_name_two: str,
    schemas1: list[set[str]] = [],
    schemas2: list[set[str]] = [],
    new_table_name: str | None = None,
) -> str:
    """Generates the string with all the join queries.

    Args:
        part (CompValue): Current part of the query.
        table_name_one (str): First table name.
        table_name_two (str): Second table name.
        schemas1 (list[set[str]], optional): Schemas of the left child of the part. Defaults to [].
        schemas2 (list[set[str]], optional): Schemas of the right child of the part. Defaults to [].
        new_table_name (str | None, optional): Table to write to. Defaults to None.

    Returns:
        str: String containing the join queries.
    """
    join_queries_dict: dict[str, list[str]] = join_query(
        part,
        table_name_one,
        table_name_two,
        schemas1,
        schemas2,
        new_table_name=new_table_name,
    )

    join_queries: str = ""
    for key in join_queries_dict:
        if len(join_queries_dict[key]) > 1:
            raise ValueError(
                "More than one query for a single table"
            )
        else:
            join_queries += create_table_w_select(
                key, join_queries_dict[key][0]
            )

    return join_queries


def join_query(
    part: CompValue,
    table_name_one: str,
    table_name_two: str,
    schemas1: list[set[str]] = [],
    schemas2: list[set[str]] = [],
    new_table_name: str | None = None,
    is_delta_and_first: tuple[bool, bool] = (False, False),
) -> dict[str, list[str]]:
    """Generates the join part according to two parts in the parse tree.

    Args:
        part (CompValue): Current part of the algebra.

    Returns:
        str: The SQL query to join both parts.
    """
    if is_delta_and_first[0] and new_table_name is None:
        new_table_name = (
            "delta_" + base_constructor.get_table_name(part)
        )
    else:
        if new_table_name is None:
            new_table_name = __encode_table_name(part)

    join_queries_dict: dict[str, list[str]] = dict()

    if len(schemas1) == 0 or len(schemas2) == 0:
        raise ValueError("No schemas to join on.")
    elif len(schemas1) == 1 and len(schemas2) == 1:

        join_queries_dict[new_table_name] = [
            __join_query_one_schema(
                part,
                schemas1,
                schemas2,
                table_name_one,
                table_name_two,
            )
        ]

        """# Construct for prep table if delta, otherwise insert into
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
            )"""

    else:

        join_queries_dict = __join_query_mult_schema(
            part,
            schemas1,
            schemas2,
            table_name_one,
            table_name_two,
            new_table_name,
        )

        """# Checks if the join schema has already been seen
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
                        )"""

        """if not is_delta_and_first[0] or (
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
                )"""

    return join_queries_dict


def delta_join_queries_part_func(
    part: CompValue,
    schemas1: list[set[str]],
    schemas2: list[set[str]],
    new_table_name: str | None = None,
) -> tuple[str, str]:
    """Constructs the delta join queries

    Args:
        part (CompValue): Current part of the query

    Returns:
        str: SQL query for the delta join
    """
    first_delta_query: dict[str, list[str]] = join_query(
        part,
        "delta_" + base_constructor.get_table_name(part.p1),
        __encode_table_name(part.p2),
        schemas1,
        schemas2,
        is_delta_and_first=(True, True),
        new_table_name=new_table_name,
    )

    second_delta_query: dict[str, list[str]] = join_query(
        part,
        "nu_" + base_constructor.get_table_name(part.p1),
        "delta_" + base_constructor.get_table_name(part.p2),
        schemas1,
        schemas2,
        is_delta_and_first=(True, False),
        new_table_name=new_table_name,
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

    combined_delta_query_dict = combine_dict_queries(
        first_delta_query, second_delta_query
    )

    join_delta_queries: str = make_group_by(
        combined_delta_query_dict,
        join_schemas(schemas1, schemas2),
    )

    join_delta_queries_outer_join: str = make_join(
        combined_delta_query_dict,
        join_schemas(schemas1, schemas2),
    )

    return join_delta_queries, join_delta_queries_outer_join


def left_join_select_clause(part: CompValue) -> str:
    """Returns the lefjoin select clause for the delta rule.

    Args:
        part (CompValue): Current part of the query.

    Returns:
        str: String containing the leftjoin variable clause.
    """
    return_str: str = (
        ", ".join(
            var
            for var in sorted(part.p1._vars)
            if var != "k_count"
        )
        + ", "
        + ", ".join(
            var
            for var in sorted(
                part.p2._vars.difference(part.p1._vars)
            )
            if var != "k_count"
        )
    )
    return return_str


def delta_join_sub(
    part1: CompValue, part2: CompValue, join_part: CompValue
) -> str:
    """Generates the delta join subquery.

    Args:
        part1 (CompValue): First part of the join.
        part2 (CompValue): Second part of the join.
    """
    # R1 JOIN delta_R2
    first_query: str = (
        "INSERT INTO delta_"
        + __encode_table_name(join_part)
        + "\n"
    )
    first_query += (
        "SELECT "
        + left_join_select_clause(join_part)
        + ", r1.k_count * r2.k_count as k_count\n"
    )
    first_query += (
        "FROM delta_"
        + __encode_table_name(part1)
        + " AS r1 JOIN "
        + __encode_table_name(part2)
        + " AS r2 "
    )
    first_query += "ON "
    if part1._vars.intersection(part2._vars) != set():
        first_query += " AND ".join(
            f"r1.{var} = r2.{var}"
            for var in part1._vars.intersection(part2._vars)
        )
        first_query += "\n"
    else:
        first_query += "TRUE\n"
    first_query += "ON CONFLICT DO\nUPDATE SET\n\t"
    first_query += (
        "k_count = EXCLUDED.k_count + k_count\n"
        + "WHERE "
        + " AND ".join(
            f"{var} = EXCLUDED.{var}" for var in part1._vars
        )
        + " AND ".join(
            f"{var} = EXCLUDED.{var}"
            for var in part2._vars.difference(part1._vars)
        )
    )
    first_query += ";\n"

    second_query: str = (
        "INSERT INTO delta_"
        + __encode_table_name(join_part)
    )
    second_query += (
        "\nSELECT "
        + left_join_select_clause(join_part)
        + ", r1.k_count * r2.k_count as k_count\n"
    )
    second_query += (
        "FROM nu_"
        + __encode_table_name(part1)
        + " AS r1 JOIN delta_"
        + __encode_table_name(part2)
        + " AS r2\n"
    )
    second_query += "ON "
    if part1._vars.intersection(part2._vars) != set():
        second_query += " AND ".join(
            f"r1.{var} = r2.{var}"
            for var in part1._vars.intersection(part2._vars)
        )
        second_query += "\n"
    else:
        second_query += "TRUE\n"
    second_query += "ON CONFLICT DO\nUPDATE SET\n\t"
    second_query += (
        "k_count = EXCLUDED.k_count + k_count\n"
        + "WHERE "
        + " AND ".join(
            f"{var} = EXCLUDED.{var}" for var in part1._vars
        )
        + " AND ".join(
            f"{var} = EXCLUDED.{var}"
            for var in part2._vars.difference(part1._vars)
        )
    )
    second_query += ";\n"

    return first_query + second_query
