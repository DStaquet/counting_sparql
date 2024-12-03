from rdflib.plugins.sparql.parserutils import CompValue
from SQL_Constructor import SQL_Constructor
from typing import Union

import sqlparse
import json


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
            SQL_Constructor.bgp_delta_table_query(
                part, triple_index + 1
            )
        )
        delta_query_name = (
            "delta_"
            + SQL_Constructor.get_table_name(part)
            + "_"
            + str(triple_index + 1)
        )
        delta_join_tables += (
            SQL_Constructor.create_table_w_select(
                delta_query_name,
                delta_query + ";\n",
                temp_prefix="TEMP",
            )
        )
        if last_delta_query_name != "" and (
            triple_index + 1
        ) < len(part.triples):
            delta_join_query = (
                SQL_Constructor.outer_join_queries(
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
                SQL_Constructor.final_outer_join_query(
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
                SQL_Constructor.create_table_w_select(
                    "delta_prep_"
                    + SQL_Constructor.get_table_name(part),
                    delta_query + ";\n",
                    temp_prefix="TEMP",
                )
            )
        else:
            delta_queries += (
                SQL_Constructor.insert_into_w_select(
                    "delta_prep_"
                    + SQL_Constructor.get_table_name(part),
                    delta_query + ";\n",
                    list(known_vars),
                )
            )

    delta_long_join_query: str = (
        SQL_Constructor.delta_outer_join_long_query(part)
    )
    delta_long_w_create = (
        SQL_Constructor.create_table_w_select(
            "delta_" + SQL_Constructor.get_table_name(part),
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
        SQL_Constructor.create_table_w_select(
            "delta_" + SQL_Constructor.get_table_name(part),
            SQL_Constructor.join_query(
                part,
                "delta_"
                + SQL_Constructor.get_table_name(part.p1),
                SQL_Constructor.get_table_name(part.p2),
            ),
        )
    )

    second_delta_query: str = (
        SQL_Constructor.insert_into_w_select(
            "delta_" + SQL_Constructor.get_table_name(part),
            SQL_Constructor.join_query(
                part,
                "nu_"
                + SQL_Constructor.get_table_name(part.p1),
                "delta_"
                + SQL_Constructor.get_table_name(part.p2),
            ),
            list(part.p1._vars.union(part.p2._vars)),
        )
    )

    delta_prep_sum: str = (
        SQL_Constructor.delta_prep_sum_query(part)
    )
    delta_queries_sum = (
        SQL_Constructor.create_table_w_select(
            "delta_" + SQL_Constructor.get_table_name(part),
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
                SQL_Constructor.delta_prep_sum_query(part)
            )
            delta_queries_sum = (
                SQL_Constructor.create_table_w_select(
                    "delta_"
                    + SQL_Constructor.get_table_name(part),
                    delta_prep_sum,
                )
            )
            write_query_to_output_dir(
                output_dir,
                delta_join_tables,
                SQL_Constructor.get_table_name(part)
                + "_tables",
                False,
                "delta_",
            )
            write_query_to_output_dir(
                output_dir,
                delta_queries + delta_queries_sum,
                SQL_Constructor.get_table_name(part),
                False,
                "delta_",
            )
            write_query_to_output_dir(
                output_dir,
                delta_queries_sum,
                SQL_Constructor.get_table_name(part)
                + "_sum",
                False,
                "delta_",
            )
            write_query_to_output_dir(
                output_dir,
                delta_join_queries,
                SQL_Constructor.get_table_name(part)
                + "_join",
                False,
                "delta_",
            )
            write_query_to_output_dir(
                output_dir,
                delta_long_join_query,
                SQL_Constructor.get_table_name(part)
                + "_long_join",
                False,
                "delta_",
            )
        case "Filter":
            filter_query: str = (
                SQL_Constructor.create_table_w_select(
                    "delta_"
                    + SQL_Constructor.get_table_name(part),
                    SQL_Constructor.delta_filter_query(
                        part
                    ),
                )
            )
            write_query_to_output_dir(
                output_dir,
                filter_query,
                SQL_Constructor.get_table_name(part),
                name="delta_",
            )
        case "Join":
            join_query: str = __delta_join_queries(part)
            write_query_to_output_dir(
                output_dir,
                join_query,
                "delta_"
                + SQL_Constructor.get_table_name(part),
            )
        case "Project":
            use_PV = True
            project_query: str = (
                SQL_Constructor.create_table_w_select(
                    "delta_"
                    + SQL_Constructor.get_table_name(part),
                    SQL_Constructor.delta_project_query(
                        part
                    ),
                )
            )
            write_query_to_output_dir(
                output_dir,
                project_query,
                SQL_Constructor.get_table_name(part),
                name="delta_",
            )
        case "LeftJoin":
            left_join_query: str = (
                SQL_Constructor.delta_left_join_query(part)
            )
            write_query_to_output_dir(
                output_dir,
                left_join_query,
                SQL_Constructor.get_table_name(part),
                name="delta_",
            )
        case "Minus":
            minus_query: str = (
                SQL_Constructor.delta_minus_query(part)
            )
            write_query_to_output_dir(
                output_dir,
                minus_query,
                SQL_Constructor.get_table_name(part),
                name="delta_",
            )
        case "Union":
            union_query: str = (
                SQL_Constructor.delta_union_query(part)
            )
            write_query_to_output_dir(
                output_dir,
                union_query,
                SQL_Constructor.get_table_name(part),
                name="delta_",
            )
        case "SelectQuery":
            select_query: str = (
                SQL_Constructor.delta_select_query(part)
            )
            write_query_to_output_dir(
                output_dir,
                select_query,
                SQL_Constructor.get_table_name(part),
                name="delta_",
            )
    nu_query: str = SQL_Constructor.nu_queries(part, use_PV)
    write_query_to_output_dir(
        output_dir,
        nu_query,
        SQL_Constructor.get_table_name(part),
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
            bgp_query, known_vars = (
                SQL_Constructor.bgp_table_query(part)
            )
            bgp_query: str = (
                SQL_Constructor.create_table_w_select(
                    SQL_Constructor.get_table_name(part),
                    bgp_query,
                )
            )
            write_query_to_output_dir(
                output_dir,
                bgp_query,
                SQL_Constructor.get_table_name(part),
            )
            return [part._vars]
        case "Filter":
            filter_query: str = (
                SQL_Constructor.filter_query(part, schemas1)
            )
            write_query_to_output_dir(
                output_dir,
                filter_query,
                SQL_Constructor.get_table_name(part),
            )
            return schemas1
        case "Project":
            project_query: str = (
                SQL_Constructor.project_query(
                    part, schemas1
                )
            )
            write_query_to_output_dir(
                output_dir,
                project_query,
                SQL_Constructor.get_table_name(part),
            )
            return SQL_Constructor.project_schemas(
                part, schemas1
            )
        case "LeftJoin":
            left_join_query: str = (
                SQL_Constructor.left_join_query(
                    part, schemas1, schemas2
                )
            )
            write_query_to_output_dir(
                output_dir,
                left_join_query,
                SQL_Constructor.get_table_name(part),
            )
            return SQL_Constructor.leftjoin_schemas(
                part, schemas1, schemas2
            )
        case "Join":
            join_query: str = SQL_Constructor.join_query(
                part,
                SQL_Constructor.get_table_name(part.p1),
                SQL_Constructor.get_table_name(part.p2),
                schemas1,
                schemas2,
            )
            write_query_to_output_dir(
                output_dir,
                join_query,
                SQL_Constructor.get_table_name(part),
            )
            return SQL_Constructor.join_schemas(
                part, schemas1, schemas2
            )
        case "Minus":
            minus_query: str = SQL_Constructor.minus_query(
                part, schemas1, schemas2
            )
            write_query_to_output_dir(
                output_dir,
                minus_query,
                SQL_Constructor.get_table_name(part),
            )
            return schemas1
        case "Union":
            union_query: str = SQL_Constructor.union_query(
                part, schemas1, schemas2
            )
            write_query_to_output_dir(
                output_dir,
                union_query,
                SQL_Constructor.get_table_name(part),
            )
            return SQL_Constructor.union_schemas(
                part, schemas1, schemas2
            )
        case "SelectQuery":
            select_query: str = (
                SQL_Constructor.select_query(part)
            )
            write_query_to_output_dir(
                output_dir,
                select_query,
                SQL_Constructor.get_table_name(part),
            )
            return schemas1
    return schemas1
