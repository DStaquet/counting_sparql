from rdflib.plugins.sparql.parserutils import CompValue
from SQL_Constructor import base_constructor
from typing import Union

import sqlparse

import SQL_Constructor.hash_writer
from SQL_Constructor.operation_constructor import (
    bgp_constructor as SQL_bgp,
    filter_constructor as SQL_filter,
    project_constructor as SQL_project,
    join_constructor as SQL_join,
    leftjoin_constructor as SQL_leftjoin,
    minus_constructor as SQL_minus,
    union_constructor as SQL_union,
)


def write_query_to_output_dir(
    output_dir: str,
    query: str,
    filename: str,
    append: bool = False,
    filename_prefix: str = "",
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
            f"{output_dir}/{filename_prefix}{filename}.sql",
            "w",
        ) as f:
            f.write(query)
    else:
        with open(
            f"{output_dir}/{filename_prefix}{filename}.sql",
            "a",
        ) as f:
            f.write(query)


def build_increm_queries(
    part: CompValue,
    output_dir: str,
    schemas1: list[set[str]] = [],
    schemas2: list[set[str]] = [],
) -> list[set[str]]:
    """Constructs the incremental queries

    Args:
        part (CompValue): Current part of the query
        output_dir (str): Where to write the SQL queries.
    """
    if "p" in part:
        schemas1 = build_increm_queries(
            part.p, output_dir, schemas1, schemas2
        )
    elif "p1" in part and "p2" in part:
        schemas1 = build_increm_queries(
            part.p1, output_dir, schemas1, schemas2
        )
        schemas2 = build_increm_queries(part.p2, output_dir)
    part_schemas: Union[list[set[str]], None] = None
    # Construct the SQL query
    match part.name:
        case "BGP":
            (
                delta_queries,
                delta_join_queries,
            ) = SQL_bgp.delta_bgp_queries(part)
            write_query_to_output_dir(
                output_dir,
                delta_queries,
                base_constructor.get_table_name(part),
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
            part_schemas = [part._vars]
        case "Filter":
            filter_query: str = SQL_filter.filter_query(
                part, schemas1, True
            )
            write_query_to_output_dir(
                output_dir,
                filter_query,
                base_constructor.get_table_name(part),
                filename_prefix="delta_",
            )
            part_schemas = schemas1
        case "Join":
            join_query, join_query_outer_join = (
                SQL_join.delta_join_queries_part_func(
                    part, schemas1, schemas2
                )
            )
            write_query_to_output_dir(
                output_dir,
                join_query,
                "delta_"
                + base_constructor.get_table_name(part),
            )
            write_query_to_output_dir(
                output_dir,
                join_query_outer_join,
                "delta_"
                + base_constructor.get_table_name(part)
                + "_outer_join",
            )
            part_schemas = SQL_join.join_schemas(
                schemas1, schemas2
            )
        case "Project":
            project_query_tuple = (
                SQL_project.delta_project_query(
                    part, schemas1
                )
            )
            if isinstance(project_query_tuple, tuple):
                project_query, project_query_join = (
                    project_query_tuple
                )
            else:
                project_query = project_query_tuple
                project_query_join = None
            write_query_to_output_dir(
                output_dir,
                project_query,
                base_constructor.get_table_name(part),
                filename_prefix="delta_",
            )
            if project_query_join != None:
                write_query_to_output_dir(
                    output_dir,
                    project_query_join,
                    base_constructor.get_table_name(part)
                    + "_join",
                    filename_prefix="delta_",
                )
            part_schemas = SQL_project.project_schemas(
                part, schemas1
            )
        case "LeftJoin":
            left_join_query, left_join_query_outer_join = (
                SQL_leftjoin.delta_left_join_query(
                    part, schemas1, schemas2
                )
            )
            write_query_to_output_dir(
                output_dir,
                left_join_query,
                base_constructor.get_table_name(part),
                filename_prefix="delta_",
            )
            write_query_to_output_dir(
                output_dir,
                left_join_query_outer_join,
                base_constructor.get_table_name(part)
                + "_outer_join",
                filename_prefix="delta_",
            )
            part_schemas = SQL_leftjoin.leftjoin_schemas(
                schemas1, schemas2
            )
        case "Minus":
            minus_query, minus_query_join = (
                SQL_minus.delta_minus_query(
                    part, schemas1, schemas2
                )
            )
            write_query_to_output_dir(
                output_dir,
                minus_query,
                base_constructor.get_table_name(part),
                filename_prefix="delta_",
            )
            write_query_to_output_dir(
                output_dir,
                minus_query_join,
                base_constructor.get_table_name(part)
                + "_join",
                filename_prefix="delta_",
            )
            part_schemas = schemas1
        case "Union":
            union_query: str = SQL_union.delta_union_query(
                part, schemas1, schemas2
            )
            write_query_to_output_dir(
                output_dir,
                union_query,
                base_constructor.get_table_name(part),
                filename_prefix="delta_",
            )
            part_schemas = SQL_union.union_schemas(
                schemas1, schemas2
            )
        case "SelectQuery":
            select_query: str = (
                base_constructor.delta_select_query(part)
            )
            write_query_to_output_dir(
                output_dir,
                select_query,
                base_constructor.get_table_name(part),
                filename_prefix="delta_",
            )
            part_schemas = schemas1
    if part_schemas == None:
        part_schemas = schemas1
    if part.name == "SelectQuery":
        nu_query = base_constructor.select_query(
            part, part_schemas, True
        )
        nu_query_sum = ""
    else:
        nu_query, nu_query_sum = (
            base_constructor.nu_queries(part, part_schemas)
        )
    write_query_to_output_dir(
        output_dir,
        nu_query,
        base_constructor.get_table_name(part),
        filename_prefix="nu_",
    )
    write_query_to_output_dir(
        output_dir,
        nu_query_sum,
        base_constructor.get_table_name(part) + "_sum",
        filename_prefix="nu_",
    )

    return part_schemas


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
            project_query_tuple = SQL_project.project_query(
                part, schemas1
            )
            if isinstance(project_query_tuple, tuple):
                project_query, project_query_join = (
                    project_query_tuple
                )
            else:
                project_query = project_query_tuple
                project_query_join = None
            write_query_to_output_dir(
                output_dir,
                project_query,
                base_constructor.get_table_name(part),
            )
            if project_query_join != None:
                write_query_to_output_dir(
                    output_dir,
                    project_query_join,
                    base_constructor.get_table_name(part)
                    + "_join",
                )
            return (
                SQL_Constructor.hash_writer.project_schemas(
                    part, schemas1
                )
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
            return SQL_leftjoin.leftjoin_schemas(
                schemas1, schemas2
            )
        case "Join":
            join_query_tuple = (
                SQL_join.join_query_str_constr(
                    part,
                    base_constructor.get_table_name(
                        part.p1
                    ),
                    base_constructor.get_table_name(
                        part.p2
                    ),
                    schemas1,
                    schemas2,
                )
            )
            if isinstance(join_query_tuple, tuple):
                join_query, join_query_outer_join = (
                    join_query_tuple
                )
                write_query_to_output_dir(
                    output_dir,
                    join_query_outer_join,
                    base_constructor.get_table_name(part)
                    + "_outer_join",
                )
            else:
                join_query = join_query_tuple
            write_query_to_output_dir(
                output_dir,
                join_query,
                base_constructor.get_table_name(part),
            )
            return SQL_join.join_schemas(schemas1, schemas2)
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
            union_query: str = SQL_union.union_query(
                part, schemas1, schemas2
            )
            write_query_to_output_dir(
                output_dir,
                union_query,
                base_constructor.get_table_name(part),
            )
            return SQL_union.union_schemas(
                schemas1, schemas2
            )
        case "SelectQuery":
            select_query: str = (
                base_constructor.select_query(
                    part, schemas1
                )
            )
            write_query_to_output_dir(
                output_dir,
                select_query,
                base_constructor.get_table_name(part),
            )
            return schemas1
    return schemas1
