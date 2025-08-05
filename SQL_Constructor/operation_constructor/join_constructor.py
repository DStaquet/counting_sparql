"""Modules to import"""

from rdflib.plugins.sparql.parserutils import CompValue

from SQL_Constructor import table_constructor
from SQL_Constructor.base_constructor import (
    __encode_schema_name,
    combine_dict_queries,
    make_group_by,
    make_join,
    add_table_to_dict,
)
from SQL_Constructor.table_constructor import (
    create_table_w_select,
    __encode_table_name,
)


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


def sch2_select_clause(
    sch1: set[str], sch2: set[str]
) -> str:
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


def _sort_vars_by_tuples(
    schema1: set[str], schema2: set[str] | None
) -> list[tuple[str, str]]:
    """Sorts the schemas by the number of variables.

    Args:
        schemas1 (list[set[str]]): Schema of the left child of the join
        schemas2 (list[set[str]] | None): Schema of the right child of the join

    Returns:
        list[tuple[str, str]]: Sorted schemas
    """
    sorted_vars: list[tuple[str, str]] = list()
    for var in schema1:
        sorted_vars.append(("r1", var))
    if schema2 is not None:
        for var in schema2:
            if var not in schema1:
                sorted_vars.append(("r2", var))
    return sorted(sorted_vars, key=lambda x: x[1])


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
        join_query_str: str = (
            "SELECT "
            + ", ".join(
                f"r1.{var} AS {var}"
                for var in sorted(
                    part.p1.get("_vars").union(
                        part.p2.get("_vars")
                    )
                )
            )
            + ", r1.k_count * r2.k_count as k_count\n"
        )
        join_query_str += "FROM "
        join_query_str += table_name_one
        join_query_str += " AS r1 JOIN "
        join_query_str += table_name_two
        join_query_str += " AS r2 "
        if (
            part.p1.get("_vars").intersection(
                part.p2.get("_vars")
            )
            != set()
        ):
            join_query_str += "ON "
            join_query_str += " AND ".join(
                f"r1.{var} = r2.{var}"
                for var in sorted(
                    part.p1.get("_vars").intersection(
                        part.p2.get("_vars")
                    )
                )
            )
        join_query_str += ";\n"

    else:
        sorted_vars = _sort_vars_by_tuples(
            schemas1[0], schemas2[0]
        )
        join_query_str: str = (
            "SELECT "
            + ", ".join(
                f"{key}.{var} AS {var}"
                for key, var in sorted_vars
            )
            + ", r1.k_count * r2.k_count as k_count\n"
            + "FROM "
            + table_name_one
            + " AS r1, "
            + table_name_two
            + " AS r2 "
        )
        if schemas1[0].intersection(schemas2[0]) != set():
            join_query_str += "WHERE " + " AND ".join(
                f"r1.{var} = r2.{var}"
                for var in sorted(
                    schemas1[0].intersection(schemas2[0])
                )
            )
        join_query_str += ";\n"

    return join_query_str


def __join_query_mult_schema(
    schemas1: list[set[str]],
    schemas2: list[set[str]],
    table_name_one: str,
    table_name_two: str,
    new_table_name: str,
    is_leftjoin_part: bool = False,
) -> dict[str, list[str]]:
    """Constructs a join query for multiple schemas.

    Args:
        schemas1 (list[set[str]]): Schemas of the first table child
        schemas2 (list[set[str]]): Schemas of the second table child

    Returns:
        dict[str, list[str]]: Dictionary containing the join queries per key
    """
    join_queries_dict: dict[str, list[str]] = dict()

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

            sorted_vars = _sort_vars_by_tuples(sch1, sch2)
            if sch1.intersection(sch2) == set():
                curr_join_query: str = (
                    "SELECT "
                    + ", ".join(
                        f"{key}.{var} AS {var}"
                        for key, var in sorted_vars
                    )
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
                        f"{key}.{var} AS {var}"
                        for key, var in sorted_vars
                    )
                    + ", r1.k_count * r2.k_count as k_count\n"
                    + "FROM "
                    + table_name_one
                    + sch1_suffix
                    + " AS r1, "
                    + table_name_two
                    + sch2_suffix
                    + " AS r2 "
                    + "WHERE "
                    + " AND ".join(
                        f"r1.{var} = r2.{var}"
                        for var in sorted(
                            sch1.intersection(sch2)
                        )
                    )
                    + ";\n"
                )

            curr_join_schema: set[str] = sch1.union(sch2)

            if (
                len(join_schemas(schemas1, schemas2)) == 1
                and not is_leftjoin_part
            ):
                join_queries_dict = add_table_to_dict(
                    new_table_name,
                    curr_join_query,
                    join_queries_dict,
                )
            else:
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
    table_names: tuple[str, str],
    schemas1: list[set[str]] | None = None,
    schemas2: list[set[str]] | None = None,
    new_table_name: str | None = None,
) -> str | tuple[str, str]:
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
    table_name_one, table_name_two = table_names
    if schemas1 is None:
        schemas1 = []
    if schemas2 is None:
        schemas2 = []

    join_queries_dict: dict[str, list[str]] = join_query(
        part,
        (table_name_one, table_name_two, new_table_name),
        schemas1,
        schemas2,
    )

    join_queries: str = ""
    join_queries_outer: str | None = None
    for key in join_queries_dict:
        if len(join_queries_dict[key]) > 1:
            join_queries += make_group_by(
                join_queries_dict,
                join_schemas(schemas1, schemas2),
            )
            if join_queries_outer is None:
                join_queries_outer = make_join(
                    join_queries_dict,
                    join_schemas(schemas1, schemas2),
                )
            else:
                join_queries_outer += make_join(
                    join_queries_dict,
                    join_schemas(schemas1, schemas2),
                )
        else:
            join_queries += create_table_w_select(
                key, join_queries_dict[key][0]
            )

    if join_queries_outer is None:
        return join_queries
    else:
        return join_queries, join_queries_outer


def join_query(
    part: CompValue,
    table_names: tuple[str, str, str | None],
    schemas1: list[set[str]] | None = None,
    schemas2: list[set[str]] | None = None,
    bools: tuple[tuple[bool, bool], bool] = (
        (False, False),
        False,
    ),
) -> dict[str, list[str]]:
    """Generates the join queries based on the part and schemas.

    Args:
        part (CompValue): Current part of the query.
        table_names (tuple[str, str, str  |  None]): Current table names (first_table, second_table, new_table).
        schemas1 (list[set[str]] | None, optional): First schema. Defaults to None which creates an empty list.
        schemas2 (list[set[str]] | None, optional): Second schemas. Defaults to None which creates an empty list.
        bools (tuple[tuple[bool, bool], bool], optional): Tuple for to indicate if it is a delta and the first plus
            bool to indicate if it is for a leftjoin. Defaults to ( (False, False), False, ).

    Raises:
        ValueError: There are no schemas to join on.

    Returns:
        dict[str, list[str]]: Dictionary containing the join queries per key.
    """
    is_delta_and_first, is_leftjoin_part = bools
    table_name_one, table_name_two, new_table_name = (
        table_names
    )
    if schemas1 is None:
        schemas1 = []
    if schemas2 is None:
        schemas2 = []

    if is_delta_and_first[0] and new_table_name is None:
        new_table_name = (
            "delta_"
            + table_constructor.get_table_name(part)
        )
    else:
        if new_table_name is None:
            new_table_name = __encode_table_name(part)

    join_queries_dict: dict[str, list[str]] = dict()

    if len(schemas1) == 0 or len(schemas2) == 0:
        raise ValueError("No schemas to join on.")
    elif (
        len(schemas1) == 1 and len(schemas2) == 1
    ) and not is_leftjoin_part:

        join_queries_dict[new_table_name] = [
            __join_query_one_schema(
                part,
                schemas1,
                schemas2,
                table_name_one,
                table_name_two,
            )
        ]

    else:

        join_queries_dict = __join_query_mult_schema(
            schemas1,
            schemas2,
            table_name_one,
            table_name_two,
            new_table_name,
            is_leftjoin_part=is_leftjoin_part,
        )

    return join_queries_dict


def delta_join_queries_part_func(
    part: CompValue,
    schemas1: list[set[str]],
    schemas2: list[set[str]],
    new_table_name: str | None = None,
    is_leftjoin_part: bool = False,
) -> tuple[str, str]:
    """Constructs the delta join queries

    Args:
        part (CompValue): Current part of the query

    Returns:
        str: SQL query for the delta join
    """
    first_delta_query: dict[str, list[str]] = join_query(
        part,
        (
            "delta_"
            + table_constructor.get_table_name(part.p1),
            __encode_table_name(part.p2),
            new_table_name,
        ),
        schemas1,
        schemas2,
        bools=((True, True), is_leftjoin_part),
    )

    second_delta_query: dict[str, list[str]] = join_query(
        part,
        (
            "nu_"
            + table_constructor.get_table_name(part.p1),
            "delta_"
            + table_constructor.get_table_name(part.p2),
            new_table_name,
        ),
        schemas1,
        schemas2,
        bools=((True, False), is_leftjoin_part),
    )

    combined_delta_query_dict = combine_dict_queries(
        first_delta_query, second_delta_query
    )

    join_delta_queries: str = make_group_by(
        combined_delta_query_dict,
        join_schemas(schemas1, schemas2),
        is_delta=True,
    )

    join_delta_queries_outer_join: str = make_join(
        combined_delta_query_dict,
        join_schemas(schemas1, schemas2),
        is_delta=True,
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
            for var in sorted(part.p1.get("_vars"))
            if var != "k_count"
        )
        + ", "
        + ", ".join(
            var
            for var in sorted(
                part.p2.get("_vars").difference(
                    part.p1.get("_vars")
                )
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
    if (
        part1.get("_vars").intersection(part2.get("_vars"))
        != set()
    ):
        first_query += " AND ".join(
            f"r1.{var} = r2.{var}"
            for var in part1.get("_vars").intersection(
                part2.get("_vars")
            )
        )
        first_query += "\n"
    else:
        first_query += "TRUE\n"
    first_query += "ON CONFLICT DO\nUPDATE SET\n\t"
    first_query += (
        "k_count = EXCLUDED.k_count + k_count\n"
        + "WHERE "
        + " AND ".join(
            f"{var} = EXCLUDED.{var}"
            for var in part1.get("_vars")
        )
        + " AND ".join(
            f"{var} = EXCLUDED.{var}"
            for var in part2.get("_vars").difference(
                part1.get("_vars")
            )
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
    if (
        part1.get("_vars").intersection(part2.get("_vars"))
        != set()
    ):
        second_query += " AND ".join(
            f"r1.{var} = r2.{var}"
            for var in part1.get("_vars").intersection(
                part2.get("_vars")
            )
        )
        second_query += "\n"
    else:
        second_query += "TRUE\n"
    second_query += "ON CONFLICT DO\nUPDATE SET\n\t"
    second_query += (
        "k_count = EXCLUDED.k_count + k_count\n"
        + "WHERE "
        + " AND ".join(
            f"{var} = EXCLUDED.{var}"
            for var in part1.get("_vars")
        )
        + " AND ".join(
            f"{var} = EXCLUDED.{var}"
            for var in part2.get("_vars").difference(
                part1.get("_vars")
            )
        )
    )
    second_query += ";\n"

    return first_query + second_query
