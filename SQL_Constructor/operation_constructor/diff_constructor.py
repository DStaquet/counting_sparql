"""Modules to import"""

from rdflib.plugins.sparql.parserutils import CompValue

from SQL_Constructor.base_constructor import (
    __encode_schema_name,
    combine_dict_queries,
    add_table_to_dict,
)
from SQL_Constructor.table_constructor import (
    __encode_table_name,
)


def _vars_to_join_on(
    sch1: set[str], sch2: set[str]
) -> set[str]:
    """Finds the variables to join on."""
    return sch1.intersection(sch2)


def __delta_on_negate_part_left_query_select(
    sch1: set[str],
    tables: tuple[str, str],
    suffixes: tuple[str, str],
    join_temp: str,
    vars_to_join_on: set[str],
) -> str:
    sch1_suffix, sch2_suffix = suffixes
    nu_from_table, delta_from_table = tables

    # Select query part for the left side of the delta on negate part
    curr_diff_query_select_left: str = (
        "SELECT "
        + ", ".join(
            f"s1.{var} as {var}" for var in sorted(sch1)
        )
    )
    curr_diff_query_select_left += (
        ", s1.k_count as k_count"
        + " FROM "
        + nu_from_table
        + sch1_suffix
        + f" as s1 {join_temp} "
        + delta_from_table
        + sch2_suffix
        + " as s2 "
    )
    if vars_to_join_on:
        curr_diff_query_select_left += "ON " + " AND ".join(
            f"s1.{var} = s2.{var}"
            for var in sorted(vars_to_join_on)
        )

    return curr_diff_query_select_left


def __delta_on_negate_part_right_query_select(
    sch1: set[str],
    tables: tuple[str, str],
    suffixes: tuple[str, str],
    join_temp: str,
    vars_to_join_on: set[str],
) -> str:
    sch1_suffix, sch2_suffix = suffixes
    nu_from_table, delta_from_table = tables

    curr_diff_query_select_right: str = (
        "SELECT "
        + ", ".join(
            f"s1.{var} as {var}" for var in sorted(sch1)
        )
        + ", -s1.k_count as k_count"
        + " FROM "
        + nu_from_table
        + sch1_suffix
        + f" as s1 {join_temp} "
        + delta_from_table
        + sch2_suffix
        + " as s2 "
    )
    if vars_to_join_on:
        curr_diff_query_select_right += (
            "ON "
            + " AND ".join(
                f"s1.{var} = s2.{var}"
                for var in sorted(vars_to_join_on)
            )
        )

    return curr_diff_query_select_right


def __delta_on_negate_part_query_selects(
    sch1: set[str],
    tables: tuple[str, str],
    suffixes: tuple[str, str],
    join_temp: str,
    vars_to_join_on: set[str],
) -> tuple[str, str]:
    """Generates the select queries for the delta on negate part."""
    curr_diff_query_select_left: str = (
        __delta_on_negate_part_left_query_select(
            sch1,
            tables,
            suffixes,
            join_temp,
            vars_to_join_on,
        )
    )
    curr_diff_query_select_right: str = (
        __delta_on_negate_part_right_query_select(
            sch1,
            tables,
            suffixes,
            join_temp,
            vars_to_join_on,
        )
    )
    return (
        curr_diff_query_select_left,
        curr_diff_query_select_right,
    )


def __delta_on_negate_part_suffixes(
    sch1: set[str],
    sch2: set[str],
    schemas1: list[set[str]],
    schemas2: list[set[str]],
    minus: bool,
) -> tuple[str, str, int]:
    schemas2_len = len(schemas2)
    if minus:
        schemas2 = [
            sch2
            for sch2 in schemas2
            if sch1.intersection(sch2) != set()
        ]

    if len(schemas2) > 1:
        sch2_suffix: str = "_" + __encode_schema_name(
            str(sorted(sch2))
        )
    else:
        sch2_suffix: str = ""

    if len(schemas1) > 1:
        sch1_suffix: str = "_" + __encode_schema_name(
            str(sorted(sch1))
        )
    else:
        sch1_suffix: str = ""

    return sch1_suffix, sch2_suffix, schemas2_len


def _delta_on_negate_curr_selects(
    schemas: tuple[set[str], set[str]],
    schemas_lists: tuple[list[set[str]], list[set[str]]],
    curr_selects: tuple[list[str], list[str]],
    tables: dict[str, str],
    minus: bool,
) -> tuple[tuple[list[str], list[str]], int]:
    sch1, sch2 = schemas
    schemas1, schemas2 = schemas_lists
    curr_left_selects, curr_right_selects = curr_selects

    sch1_suffix, sch2_suffix, schemas2_len = (
        __delta_on_negate_part_suffixes(
            sch1,
            sch2,
            schemas1,
            schemas2,
            minus,
        )
    )

    vars_to_join_on = _vars_to_join_on(sch1, sch2)
    if vars_to_join_on == set():
        join_temp = ","
    else:
        join_temp = "JOIN"

    (
        curr_diff_query_select_left,
        curr_diff_query_select_right,
    ) = __delta_on_negate_part_query_selects(
        sch1,
        (
            tables["nu_from_table"],
            tables["delta_from_table"],
        ),
        (sch1_suffix, sch2_suffix),
        join_temp,
        vars_to_join_on,
    )

    curr_left_selects.append(curr_diff_query_select_left)
    curr_right_selects.append(curr_diff_query_select_right)

    return (
        curr_left_selects,
        curr_right_selects,
    ), schemas2_len


def _delta_on_negate_part_curr_queries_in_diff_queries(
    curr_selects: tuple[list[str], list[str]],
    curr_diff_queries: tuple[str, str],
    tables: dict[str, str],
    schema_info: tuple[
        tuple[
            tuple[list[set[str]], list[set[str]]],
            dict[str, set[str]],
        ],
        bool,
    ],
    diff_queries: dict[str, list[str]],
) -> dict[str, list[str]]:
    (schemas, single_schemas), _ = schema_info
    curr_left_selects, curr_right_selects = curr_selects
    curr_diff_query_left, curr_diff_query_right = (
        curr_diff_queries
    )

    for schema_index, _ in enumerate(curr_left_selects):
        curr_diff_query = (
            curr_left_selects[schema_index]
            + curr_diff_query_left
            + " UNION "
            + curr_right_selects[schema_index]
            + curr_diff_query_right
            + ";\n"
        )

        if (
            __check_if_same_diff_schema(
                schemas[0], schemas[1]
            )
            and not schema_info[1]
        ):
            schema_both_suffix: str = ""
        else:
            schema_both_suffix: str = (
                "_"
                + __encode_schema_name(
                    str(sorted(single_schemas["sch1"]))
                )
            )

        curr_table_name = (
            tables["new_table_name"] + schema_both_suffix
        )
        diff_queries = add_table_to_dict(
            curr_table_name,
            curr_diff_query,
            diff_queries,
        )

    return diff_queries


def _delta_on_negate_part_curr_queries(
    append_schemas: bool,
    all_schemas: tuple[
        tuple[list[set[str]], list[set[str]]],
        dict[str, set[str]],
    ],
    curr_selects: tuple[list[str], list[str]],
    tables: dict[str, str],
    diff_queries: dict[str, list[str]],
) -> dict[str, list[str]]:
    schemas = all_schemas[0]
    single_schemas = all_schemas[1]
    schemas2_len: int = len(schemas[1])

    curr_diff_query_left: str = ""
    curr_diff_query_right: str = ""
    if len(schemas[1]) > 0 and _check_if_overlap(
        single_schemas["sch1"], schemas[1]
    ):
        curr_diff_query_left = " WHERE " + " AND ".join(
            " NOT EXISTS ("
            + _diff_sch2_subquery(
                "nu_" + tables["old_delta_from_table_name"],
                (
                    (single_schemas["sch1"], sch2),
                    schemas2_len,
                ),
                index + 3,
                is_delta=True,
            )
            + ")"
            for index, sch2 in enumerate(schemas[1])
            if single_schemas["sch1"].intersection(sch2)
            != set()
        )
        curr_diff_query_right = " WHERE " + " AND ".join(
            "NOT EXISTS ("
            + _diff_sch2_subquery(
                tables["old_delta_from_table_name"],
                (
                    (single_schemas["sch1"], sch2),
                    schemas2_len,
                ),
                index + 3,
                is_delta=True,
            )
            + ")"
            for index, sch2 in enumerate(schemas[1])
            if single_schemas["sch1"].intersection(sch2)
            != set()
        )

        diff_queries = _delta_on_negate_part_curr_queries_in_diff_queries(
            curr_selects,
            (curr_diff_query_left, curr_diff_query_right),
            tables,
            (all_schemas, append_schemas),
            diff_queries,
        )

    return diff_queries


def __delta_on_negate_part_diff_queries(
    schemas: tuple[list[set[str]], list[set[str]]],
    minus: bool,
    tables: dict[str, str],
    append_schemas: bool,
) -> dict[str, list[str]]:

    diff_queries: dict[str, list[str]] = dict()

    curr_left_selects: list[str] = list()
    curr_right_selects: list[str] = list()

    if len(schemas[0]) == 0:
        raise ValueError("No schemas to join on.")
    # None match
    none_match: bool = True
    sch2 = set()
    for sch1 in schemas[0]:
        for sch2 in schemas[1]:
            if sch1.intersection(sch2) == set():
                continue
            none_match = False

            (
                curr_left_selects,
                curr_right_selects,
            ), _ = _delta_on_negate_curr_selects(
                (sch1, sch2),
                schemas,
                (curr_left_selects, curr_right_selects),
                tables,
                minus,
            )

        if none_match:
            return diff_queries

        diff_queries = _delta_on_negate_part_curr_queries(
            append_schemas,
            (schemas, {"sch1": sch1, "sch2": sch2}),
            (curr_left_selects, curr_right_selects),
            tables,
            diff_queries,
        )

    return diff_queries


def __delta_on_negate_part(
    part: CompValue,
    schemas: tuple[list[set[str]], list[set[str]]],
    new_table_name: str | None = None,
    minus: bool = False,
    append_schemas: bool = False,
) -> dict[str, list[str]]:
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

    tables: dict[str, str] = {
        "nu_from_table": nu_from_table,
        "delta_from_table": delta_from_table,
        "old_delta_from_table_name": old_delta_from_table_name,
        "new_table_name": new_table_name,
    }

    diff_queries: dict[str, list[str]] = (
        __delta_on_negate_part_diff_queries(
            schemas,
            minus,
            tables,
            append_schemas,
        )
    )

    return diff_queries


def delta_diff_sub(
    part: CompValue,
    schemas1: list[set[str]],
    schemas2: list[set[str]],
    append_schemas: bool = True,
    minus: bool = False,
) -> dict[str, list[str]]:
    """Generates the minus subquery.

    Args:
        part (CompValue): Current part of the query containing the minus operation.

    Returns:
        str: Query string of the needed minus operation.
    """

    delta_table_name: str = "delta_" + __encode_table_name(
        part
    )

    tables: dict[str, str | None] = {
        "first_from_table": "delta_"
        + __encode_table_name(part.p1),
        "second_from_table": None,
        "new_table_name": delta_table_name,
    }
    diff_delta_first_part: dict[str, list[str]] = (
        diff_query_sub(
            part,
            (schemas1, schemas2),
            tables=tables,
            append_schemas=append_schemas,
            minus=minus,
        )
    )

    diff_delta_second_part: dict[str, list[str]] = (
        __delta_on_negate_part(
            part,
            (
                schemas1,
                schemas2,
            ),
            delta_table_name,
            minus=minus,
            append_schemas=append_schemas,
        )
    )

    return combine_dict_queries(
        diff_delta_first_part, diff_delta_second_part
    )


def _diff_sch2_subquery(
    second_table_name: str,
    schema_info: tuple[tuple[set[str], set[str]], int],
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
    (sch1, sch2), schemas2_len = schema_info

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
    )
    if sch1.intersection(sch2) != set():
        subquery_diff_str += " WHERE " + " AND ".join(
            f"s1.{var} = s{index}.{var}"
            for var in sorted(sch1.intersection(sch2))
        )
        if is_delta and delta_swap != "":
            subquery_diff_str += f" AND {delta_swap}s2.k_count = s{index}.k_count"
    else:
        if is_delta and delta_swap != "":
            subquery_diff_str += f" WHERE {delta_swap}s2.k_count = s{index}.k_count"

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
    return len(join_schemas) == 1


def _check_if_overlap(
    sch1: set[str], schemas2: list[set[str]]
) -> bool:
    """Gives True if there is an overlap between the schemas, False otherwise.

    Args:
        schemas1 (list[set[str]]): Schemas of the first child of the part
        schemas2 (list[set[str]]): Schemas of the second child of the part

    Returns:
        bool: True if there is an overlap, False otherwise
    """
    for sch2 in schemas2:
        if sch1.intersection(sch2) != set():
            return True
    return False


def diff_query_sub(
    part: CompValue,
    schemas: tuple[
        list[set[str]] | None, list[set[str]] | None
    ] = (None, None),
    tables: dict[str, str | None] | None = None,
    minus: bool = False,
    append_schemas: bool = False,
) -> dict[str, list[str]]:
    """Generates the difference subquery.

    Args:
        part (CompValue): Current part of the query containing the dofference operation.

    Returns:
        str: Query string of the needed difference operation.
    """
    if tables is None:
        tables = {
            "first_from_table": None,
            "second_from_table": None,
            "new_table_name": None,
        }

    schemas1, schemas2 = schemas
    if schemas1 is None:
        schemas1 = []
    if schemas2 is None:
        schemas2 = []

    diff_query: dict[str, list[str]] = {}

    if tables["first_from_table"] is None:
        first_from_table = __encode_table_name(part.p1)
    else:
        first_from_table = tables["first_from_table"]
    if tables["second_from_table"] is None:
        second_from_table = __encode_table_name(part.p2)
    else:
        second_from_table = tables["second_from_table"]

    if tables["new_table_name"] is None:
        new_table_name = __encode_table_name(part)
    else:
        new_table_name = tables["new_table_name"]

    if len(schemas1) == 0 or len(schemas2) == 0:
        raise ValueError("No schemas to join on.")

    if (
        len(schemas1) == 1
        and len(schemas2) == 1
        and schemas1[0].intersection(schemas2[0]) == set()  # type: ignore
    ):
        return {}

    for sch1 in schemas1:
        if len(schemas1) <= 1:
            schemas1_suffix: str = ""
            schemas_both_suffix: str = ""
        else:
            schemas1_suffix: str = (
                "_"
                + __encode_schema_name(str(sorted(sch1)))
            )

        if (
            __check_if_same_diff_schema(schemas1, schemas2)
            and not append_schemas
        ):
            schemas_both_suffix: str = ""
        else:
            schemas_both_suffix: str = (
                "_"
                + __encode_schema_name(str(sorted(sch1)))
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
                f"s1.{var} as {var}" for var in sorted(sch1)
            )
            + ", s1.k_count as k_count"
            + " FROM "
            + first_from_table
            + schemas1_suffix
            + " AS s1"
        )
        if len(schemas2) > 0 and _check_if_overlap(
            sch1, schemas2
        ):
            curr_diff_query += " WHERE " + " AND ".join(
                "NOT EXISTS ("
                + _diff_sch2_subquery(
                    second_from_table,
                    ((sch1, sch2), schemas2_len),
                    index + 2,
                )
                + ")"
                for index, sch2 in enumerate(schemas2)
                if sch1.intersection(sch2) != set()
            )
        curr_diff_query += ";\n"

        # Add all queries to the table they need to end up in
        diff_query[new_table_name + schemas_both_suffix] = [
            curr_diff_query
        ]

    return diff_query
