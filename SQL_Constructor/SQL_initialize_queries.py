from rdflib.plugins.sparql.parserutils import CompValue
from SQL_Constructor import base_constructor
from typing import Union

import sqlparse
import json

from SQL_Constructor.operation_constructor import (
    bgp_constructor as SQL_bgp,
    filter_constructor as SQL_filter,
    project_constructor as SQL_project,
    join_constructor as SQL_join,
    leftjoin_constructor as SQL_leftjoin,
    minus_constructor as SQL_minus,
)


def write_query_to_output_dir(
    output_dir: str,
    query: str,
    filename: str,
    append: bool = False,
    name: str = "",
) -> None:
    """Writes the query to the output directory

    Args:
        part (CompValue): Current part of the query
        output_dir (str): Directory to write the SQL queries
        query (str): The query to write
        append (bool, optional): Whether to append to the file. Defaults to False.
        name (str, optional): The prefix of the file. Defaults to "".
    """
    query = sqlparse.format(
        query, reindent=True, keyword_case="upper"
    )
    if not append:
        with open(
            f"{output_dir}/{name}{filename}.sql",
            "w",
        ) as f:
            f.write(query)
    else:
        with open(
            f"{output_dir}/{name}{filename}.sql",
            "a",
        ) as f:
            f.write(query)


def __delta_bgp_queries(
    part: CompValue,
) -> tuple[str, str, str, str]:
    """Builds up the different delta BGP queries for the incremental query.

    Args:
        part (CompValue): Current part of the query

    Returns:
        list[str]: List of the delta queries for the BGP
    """
    delta_queries: str = ""
    delta_join_queries: str = ""
    delta_join_tables: str = ""
    last_delta_query_name: str = ""
    first_insert = True
    temp_suffix = ""
    for triple_index in range(len(part.triples)):
        delta_query, known_vars = (
            base_constructor.bgp_delta_table_query(
                part, triple_index + 1
            )
        )
        delta_query_name = (
            "delta_"
            + base_constructor.get_table_name(part)
            + "_"
            + str(triple_index + 1)
        )
        delta_join_tables += (
            base_constructor.create_table_w_select(
                delta_query_name,
                delta_query + ";\n",
                temp_prefix="TEMP",
            )
        )
        if last_delta_query_name != "" and (
            triple_index + 1
        ) < len(part.triples):
            delta_join_query = (
                base_constructor.outer_join_queries(
                    part,
                    delta_query_name + "_temp",
                    last_delta_query_name + temp_suffix,
                    delta_query_name,
                    known_vars,
                    triple_index + 1,
                )
            )
            delta_join_queries += delta_join_query
            last_delta_query_name = delta_query_name
            temp_suffix = "_temp"
        elif (triple_index + 1) == len(
            part.triples
        ) and triple_index != 0:
            delta_join_query = (
                base_constructor.final_outer_join_query(
                    part,
                    last_delta_query_name + "_temp",
                    delta_query_name,
                    known_vars,
                )
            )
            delta_join_queries += delta_join_query
            last_delta_query_name = delta_query_name
        else:
            # This is unconventional, but skips the first query making
            last_delta_query_name = delta_query_name
        if first_insert:
            first_insert = False
            delta_queries += (
                base_constructor.create_table_w_select(
                    "delta_prep_"
                    + base_constructor.get_table_name(part),
                    delta_query + ";\n",
                    temp_prefix="TEMP",
                )
            )
        else:
            delta_queries += (
                base_constructor.insert_into_w_select(
                    "delta_prep_"
                    + base_constructor.get_table_name(part),
                    delta_query + ";\n",
                    list(known_vars),
                )
            )

    delta_long_join_query: str = (
        base_constructor.delta_outer_join_long_query(part)
    )
    delta_long_w_create = (
        base_constructor.create_table_w_select(
            "delta_"
            + base_constructor.get_table_name(part),
            delta_long_join_query,
        )
    )

    return (
        delta_queries,
        delta_join_queries,
        delta_long_w_create,
        delta_join_tables,
    )


def __delta_join_queries(part: CompValue) -> str:
    """Constructs the delta join queries

    Args:
        part (CompValue): Current part of the query

    Returns:
        str: SQL query for the delta join
    """
    first_delta_query: str = (
        base_constructor.create_table_w_select(
            "delta_"
            + base_constructor.get_table_name(part),
            SQL_join.join_query(
                part,
                "delta_"
                + base_constructor.get_table_name(part.p1),
                base_constructor.get_table_name(part.p2),
            ),
        )
    )

    second_delta_query: str = (
        base_constructor.insert_into_w_select(
            "delta_"
            + base_constructor.get_table_name(part),
            SQL_join.join_query(
                part,
                "nu_"
                + base_constructor.get_table_name(part.p1),
                "delta_"
                + base_constructor.get_table_name(part.p2),
            ),
            list(part.p1._vars.union(part.p2._vars)),
        )
    )

    delta_prep_sum: str = (
        base_constructor.delta_prep_sum_query(part)
    )
    delta_queries_sum = (
        base_constructor.create_table_w_select(
            "delta_"
            + base_constructor.get_table_name(part),
            delta_prep_sum,
        )
    )

    return (
        first_delta_query
        + second_delta_query
        + delta_queries_sum
    )


def build_increm_queries(
    part: CompValue, output_dir: str
) -> None:
    """Constructs the incremental queries

    Args:
        part (CompValue): Current part of the query
        output_dir (str): Where to write the SQL queries.
    """
    if "p" in part:
        build_increm_queries(part.p, output_dir)
    elif "p1" in part and "p2" in part:
        build_increm_queries(part.p1, output_dir)
        build_increm_queries(part.p2, output_dir)
    # Construct the SQL query
    use_PV = False
    match part.name:
        case "BGP":
            (
                delta_queries,
                delta_join_queries,
                delta_long_join_query,
                delta_join_tables,
            ) = __delta_bgp_queries(part)
            delta_prep_sum: str = (
                base_constructor.delta_prep_sum_query(part)
            )
            delta_queries_sum = (
                base_constructor.create_table_w_select(
                    "delta_"
                    + base_constructor.get_table_name(part),
                    delta_prep_sum,
                )
            )
            write_query_to_output_dir(
                output_dir,
                delta_join_tables,
                base_constructor.get_table_name(part)
                + "_tables",
                False,
                "delta_",
            )
            write_query_to_output_dir(
                output_dir,
                delta_queries + delta_queries_sum,
                base_constructor.get_table_name(part),
                False,
                "delta_",
            )
            write_query_to_output_dir(
                output_dir,
                delta_queries_sum,
                base_constructor.get_table_name(part)
                + "_sum",
                False,
                "delta_",
            )
            write_query_to_output_dir(
                output_dir,
                delta_join_queries,
                base_constructor.get_table_name(part)
                + "_join",
                False,
                "delta_",
            )
            write_query_to_output_dir(
                output_dir,
                delta_long_join_query,
                base_constructor.get_table_name(part)
                + "_long_join",
                False,
                "delta_",
            )
        case "Filter":
            filter_query: str = (
                base_constructor.create_table_w_select(
                    "delta_"
                    + base_constructor.get_table_name(part),
                    SQL_filter.delta_filter_query(part),
                )
            )
            write_query_to_output_dir(
                output_dir,
                filter_query,
                base_constructor.get_table_name(part),
                name="delta_",
            )
        case "Join":
            join_query: str = __delta_join_queries(part)
            write_query_to_output_dir(
                output_dir,
                join_query,
                "delta_"
                + base_constructor.get_table_name(part),
            )
        case "Project":
            use_PV = True
            project_query: str = (
                base_constructor.create_table_w_select(
                    "delta_"
                    + base_constructor.get_table_name(part),
                    base_constructor.delta_project_query(
                        part
                    ),
                )
            )
            write_query_to_output_dir(
                output_dir,
                project_query,
                base_constructor.get_table_name(part),
                name="delta_",
            )
        case "LeftJoin":
            left_join_query: str = (
                base_constructor.delta_left_join_query(part)
            )
            write_query_to_output_dir(
                output_dir,
                left_join_query,
                base_constructor.get_table_name(part),
                name="delta_",
            )
        case "Minus":
            minus_query: str = (
                base_constructor.delta_minus_query(part)
            )
            write_query_to_output_dir(
                output_dir,
                minus_query,
                base_constructor.get_table_name(part),
                name="delta_",
            )
        case "Union":
            union_query: str = (
                base_constructor.delta_union_query(part)
            )
            write_query_to_output_dir(
                output_dir,
                union_query,
                base_constructor.get_table_name(part),
                name="delta_",
            )
        case "SelectQuery":
            select_query: str = (
                base_constructor.delta_select_query(part)
            )
            write_query_to_output_dir(
                output_dir,
                select_query,
                base_constructor.get_table_name(part),
                name="delta_",
            )
    nu_query: str = base_constructor.nu_queries(
        part, use_PV
    )
    write_query_to_output_dir(
        output_dir,
        nu_query,
        base_constructor.get_table_name(part),
        name="nu_",
    )


def construct_minus_columns(part: CompValue) -> list[str]:
    """Constructs the columns related to the minus operation

    Args:
        part (CompValue): Current part of the query

    Returns:
        list[str]: All values related to the minus operation
    """
    minus_columns: list[str] = []
    for var in part.p1._vars:
        minus_columns.append(var)
    for var in part.p2._vars.difference(part.p1._vars):
        minus_columns.append(var)
    return minus_columns


def build_queries(
    part: CompValue, output_dir: str
) -> list[set[str]]:
    """Constructs the non_incremental queries

    Args:
        part (CompValue): Current part of the query
        output_dir (str): Where to write the SQL queries
    """
    if "p" in part:
        schemas1 = build_queries(part.p, output_dir)
    elif "p1" in part and "p2" in part:
        schemas1 = build_queries(part.p1, output_dir)
        schemas2 = build_queries(part.p2, output_dir)
    # Construct the SQL query
    match part.name:
        case "BGP":
            bgp_query, known_vars = SQL_bgp.bgp_table_query(
                part
            )
            bgp_query: str = (
                base_constructor.create_table_w_select(
                    base_constructor.get_table_name(part),
                    bgp_query,
                )
            )
            write_query_to_output_dir(
                output_dir,
                bgp_query,
                base_constructor.get_table_name(part),
            )
            return [part._vars]
        case "Filter":
            filter_query: str = SQL_filter.filter_query(
                part, schemas1
            )
            write_query_to_output_dir(
                output_dir,
                filter_query,
                base_constructor.get_table_name(part),
            )
            return schemas1
        case "Project":
            project_query: str = SQL_project.project_query(
                part, schemas1
            )
            write_query_to_output_dir(
                output_dir,
                project_query,
                base_constructor.get_table_name(part),
            )
            return base_constructor.project_schemas(
                part, schemas1
            )
        case "LeftJoin":
            left_join_query: str = (
                SQL_leftjoin.left_join_query(
                    part, schemas1, schemas2
                )
            )
            write_query_to_output_dir(
                output_dir,
                left_join_query,
                base_constructor.get_table_name(part),
            )
            return base_constructor.leftjoin_schemas(
                part, schemas1, schemas2
            )
        case "Join":
            join_query: str = SQL_join.join_query(
                part,
                base_constructor.get_table_name(part.p1),
                base_constructor.get_table_name(part.p2),
                schemas1,
                schemas2,
            )
            write_query_to_output_dir(
                output_dir,
                join_query,
                base_constructor.get_table_name(part),
            )
            return base_constructor.join_schemas(
                part, schemas1, schemas2
            )
        case "Minus":
            minus_query: str = SQL_minus.minus_query(
                part, schemas1, schemas2
            )
            write_query_to_output_dir(
                output_dir,
                minus_query,
                base_constructor.get_table_name(part),
            )
            return schemas1
        case "Union":
            union_query: str = base_constructor.union_query(
                part, schemas1, schemas2
            )
            write_query_to_output_dir(
                output_dir,
                union_query,
                base_constructor.get_table_name(part),
            )
            return base_constructor.union_schemas(
                part, schemas1, schemas2
            )
        case "SelectQuery":
            select_query: str = (
                base_constructor.select_query(part)
            )
            write_query_to_output_dir(
                output_dir,
                select_query,
                base_constructor.get_table_name(part),
            )
            return schemas1
    return schemas1
