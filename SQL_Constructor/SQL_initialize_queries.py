"""Modules to import"""

from typing import Union
from os.path import join

from rdflib.plugins.sparql.parserutils import CompValue
import sqlparse
from duckdb import DuckDBPyConnection

from SQL_Constructor import base_constructor
from SQL_Constructor.singular_file_constructor import TableNames
import SQL_Constructor.table_constructor
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
from SQL_Constructor.aggregation_constructor import (
    aggregation_constructor as SQL_aggregate,
)


def write_query_to_output_dir(
    output_dir: str,
    query: str,
    filename: str,
    append: bool = False,
    filename_prefix: str = "",
    no_format: bool = False,
) -> None:
    """Writes the query to the output directory

    Args:
        part (CompValue): Current part of the query
        output_dir (str): Directory to write the SQL queries
        query (str): The query to write
        append (bool, optional): Whether to append to the file. Defaults to False.
        name (str, optional): The prefix of the file. Defaults to "".
    """
    if not no_format:
        query = sqlparse.format(query, reindent=True, keyword_case="upper")
    if not append:
        with open(
            f"{output_dir}/{filename_prefix}{filename}.sql",
            "w",
            encoding="utf-8",
        ) as f:
            f.write(query)
    else:
        with open(
            f"{output_dir}/{filename_prefix}{filename}.sql",
            "a",
            encoding="utf-8",
        ) as f:
            f.write(query)


def build_increm_queries(
    part: CompValue,
    output_dir: str,
    table_names: TableNames,
    schemas1: list[set[str]] | None = None,
    schemas2: list[set[str]] | None = None,
) -> list[set[str]]:
    """Builds the incremental queries

    Args:
        part (CompValue): Current part of the query
        output_dir (str): Directory to write the SQL queries
        schemas1 (list[set[str]] | None, optional): Schemas of the first part. Defaults to None.
        schemas2 (list[set[str]] | None, optional): Schemas of the second part. Defaults to None.

    Returns:
        list[set[str]]: The schemas of the part
    """
    if schemas1 is None:
        schemas1 = []
    if schemas2 is None:
        schemas2 = []

    if "p" in part:
        schemas1 = build_increm_queries(
            part.p, output_dir, table_names, schemas1, schemas2
        )
    elif "p1" in part and "p2" in part:
        schemas1 = build_increm_queries(
            part.p1, output_dir, table_names, schemas1, schemas2
        )
        schemas2 = build_increm_queries(
            part.p2,
            output_dir,
            table_names,
        )
    part_schemas: Union[list[set[str]], None] = None
    # Construct the SQL query
    match part.name:
        case "BGP":
            (
                delta_queries,
                delta_join_queries,
            ) = SQL_bgp.delta_bgp_queries(part, table_names)
            write_query_to_output_dir(
                output_dir,
                delta_queries,
                SQL_Constructor.table_constructor.get_table_name(part),
                False,
                "delta_",
            )
            write_query_to_output_dir(
                output_dir,
                delta_join_queries,
                SQL_Constructor.table_constructor.get_table_name(part) + "_join",
                False,
                "delta_",
            )
            part_schemas = [part.get("_vars")]
        case "Filter":
            filter_query: str = SQL_filter.filter_query(part, schemas1, True)
            write_query_to_output_dir(
                output_dir,
                filter_query,
                SQL_Constructor.table_constructor.get_table_name(part),
                filename_prefix="delta_",
            )
            part_schemas = schemas1
        case "Join":
            join_query, join_query_outer_join = SQL_join.delta_join_queries_part_func(
                part, schemas1, schemas2
            )
            write_query_to_output_dir(
                output_dir,
                join_query,
                "delta_" + SQL_Constructor.table_constructor.get_table_name(part),
            )
            write_query_to_output_dir(
                output_dir,
                join_query_outer_join,
                "delta_"
                + SQL_Constructor.table_constructor.get_table_name(part)
                + "_outer_join",
            )
            part_schemas = SQL_join.join_schemas(schemas1, schemas2)
        case "Project":
            project_query_tuple = SQL_project.delta_project_query(part, schemas1)
            if isinstance(project_query_tuple, tuple):
                project_query, project_query_join = project_query_tuple
            else:
                project_query = project_query_tuple
                project_query_join = None
            write_query_to_output_dir(
                output_dir,
                project_query,
                SQL_Constructor.table_constructor.get_table_name(part),
                filename_prefix="delta_",
            )
            if project_query_join is not None:
                write_query_to_output_dir(
                    output_dir,
                    project_query_join,
                    SQL_Constructor.table_constructor.get_table_name(part) + "_join",
                    filename_prefix="delta_",
                )
            part_schemas = SQL_project.project_schemas(part, schemas1)
        case "LeftJoin":
            left_join_query, left_join_query_outer_join = (
                SQL_leftjoin.delta_left_join_query(part, schemas1, schemas2)
            )
            write_query_to_output_dir(
                output_dir,
                left_join_query,
                SQL_Constructor.table_constructor.get_table_name(part),
                filename_prefix="delta_",
            )
            write_query_to_output_dir(
                output_dir,
                left_join_query_outer_join,
                SQL_Constructor.table_constructor.get_table_name(part) + "_outer_join",
                filename_prefix="delta_",
            )
            part_schemas = SQL_leftjoin.leftjoin_schemas(schemas1, schemas2)
        case "Minus":
            minus_query, minus_query_join = SQL_minus.delta_minus_query(
                part, schemas1, schemas2
            )
            write_query_to_output_dir(
                output_dir,
                minus_query,
                SQL_Constructor.table_constructor.get_table_name(part),
                filename_prefix="delta_",
            )
            write_query_to_output_dir(
                output_dir,
                minus_query_join,
                SQL_Constructor.table_constructor.get_table_name(part) + "_join",
                filename_prefix="delta_",
            )
            part_schemas = schemas1
        case "Union":
            union_query: str = SQL_union.delta_union_query(part, schemas1, schemas2)
            write_query_to_output_dir(
                output_dir,
                union_query,
                SQL_Constructor.table_constructor.get_table_name(part),
                filename_prefix="delta_",
            )
            part_schemas = SQL_union.union_schemas(schemas1, schemas2)
        case "SelectQuery":
            select_query: str = base_constructor.delta_select_query(part, schemas1)
            write_query_to_output_dir(
                output_dir,
                select_query,
                SQL_Constructor.table_constructor.get_table_name(part),
                filename_prefix="delta_",
            )
            part_schemas = schemas1
        case "AggregateJoin":
            aggregate_join_query: str = SQL_aggregate.delta_aggregate_join_query(part)
            write_query_to_output_dir(
                output_dir,
                aggregate_join_query,
                SQL_Constructor.table_constructor.get_table_name(part),
                filename_prefix="delta_",
                no_format=True,
            )
            part_schemas = schemas1
        case _:
            raise NotImplementedError(f"Operation {part.name} not implemented yet.")
    if part_schemas is None:
        part_schemas = schemas1
    if part.name == "SelectQuery":
        nu_query = base_constructor.select_query(
            part, part_schemas, "nu_", temp_prefix="TEMP"
        )
        nu_query_sum = ""
    elif part.name in ["Group", "Extend"]:
        return part_schemas
    else:
        if part.name == "AggregateJoin":
            nu_query = ""
            nu_query_sum = ""
        else:
            nu_query, nu_query_sum = base_constructor.nu_queries(part, part_schemas)
    write_query_to_output_dir(
        output_dir,
        nu_query,
        SQL_Constructor.table_constructor.get_table_name(part),
        filename_prefix="nu_",
    )
    write_query_to_output_dir(
        output_dir,
        nu_query_sum,
        SQL_Constructor.table_constructor.get_table_name(part) + "_sum",
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
    for var in part.p1.get("_vars"):
        minus_columns.append(var)
    for var in part.p2.get("_vars").difference(part.p1.get("_vars")):
        minus_columns.append(var)
    return minus_columns


def build_queries(
    part: CompValue, output_dir: str, mother_resource_table_name: str
) -> list[set[str]]:
    """Constructs the non_incremental queries

    Args:
        part (CompValue): Current part of the query
        output_dir (str): Where to write the SQL queries
    """
    if "p" in part:
        schemas1 = build_queries(part.p, output_dir, mother_resource_table_name)
        schemas2 = []
    elif "p1" in part and "p2" in part:
        schemas1 = build_queries(part.p1, output_dir, mother_resource_table_name)
        schemas2 = build_queries(part.p2, output_dir, mother_resource_table_name)
    else:
        schemas1 = []
        schemas2 = []
    # Construct the SQL query
    match part.name:
        case "BGP":
            bgp_query, _ = SQL_bgp.bgp_table_query(part, mother_resource_table_name)
            bgp_query: str = SQL_Constructor.table_constructor.create_table_w_select(
                SQL_Constructor.table_constructor.get_table_name(part),
                bgp_query,
            )
            write_query_to_output_dir(
                output_dir,
                bgp_query,
                SQL_Constructor.table_constructor.get_table_name(part),
            )
            return [part.get("_vars")]
        case "Filter":
            filter_query: str = SQL_filter.filter_query(part, schemas1)
            write_query_to_output_dir(
                output_dir,
                filter_query,
                SQL_Constructor.table_constructor.get_table_name(part),
            )
            return schemas1
        case "Project":
            project_query_tuple = SQL_project.project_query(part, schemas1)
            if isinstance(project_query_tuple, tuple):
                project_query, project_query_join = project_query_tuple
            else:
                project_query = project_query_tuple
                project_query_join = None
            write_query_to_output_dir(
                output_dir,
                project_query,
                SQL_Constructor.table_constructor.get_table_name(part),
            )
            if project_query_join is not None:
                write_query_to_output_dir(
                    output_dir,
                    project_query_join,
                    SQL_Constructor.table_constructor.get_table_name(part) + "_join",
                )
            return SQL_Constructor.hash_writer.project_schemas(part, schemas1)
        case "LeftJoin":
            left_join_query: str = SQL_leftjoin.left_join_query(
                part, schemas1, schemas2
            )
            write_query_to_output_dir(
                output_dir,
                left_join_query,
                SQL_Constructor.table_constructor.get_table_name(part),
            )
            return SQL_leftjoin.leftjoin_schemas(schemas1, schemas2)
        case "Join":
            join_query_tuple = SQL_join.join_query_str_constr(
                part,
                (
                    SQL_Constructor.table_constructor.get_table_name(part.p1),
                    SQL_Constructor.table_constructor.get_table_name(part.p2),
                ),
                schemas1,
                schemas2,
            )
            if isinstance(join_query_tuple, tuple):
                join_query, join_query_outer_join = join_query_tuple
                write_query_to_output_dir(
                    output_dir,
                    join_query_outer_join,
                    SQL_Constructor.table_constructor.get_table_name(part)
                    + "_outer_join",
                )
            else:
                join_query = join_query_tuple
            write_query_to_output_dir(
                output_dir,
                join_query,
                SQL_Constructor.table_constructor.get_table_name(part),
            )
            return SQL_join.join_schemas(schemas1, schemas2)
        case "Minus":
            minus_query: str = SQL_minus.minus_query(part, schemas1, schemas2)
            write_query_to_output_dir(
                output_dir,
                minus_query,
                SQL_Constructor.table_constructor.get_table_name(part),
            )
            return schemas1
        case "Union":
            union_query: str = SQL_union.union_query(part, schemas1, schemas2)
            write_query_to_output_dir(
                output_dir,
                union_query,
                SQL_Constructor.table_constructor.get_table_name(part),
            )
            return SQL_union.union_schemas(schemas1, schemas2)
        case "SelectQuery":
            select_query: str = base_constructor.select_query(part, schemas1)
            write_query_to_output_dir(
                output_dir,
                select_query,
                SQL_Constructor.table_constructor.get_table_name(part),
            )
            return schemas1
        case "AggregateJoin":
            aggregate_join_query: str = SQL_aggregate.aggregate_join_query(part)
            write_query_to_output_dir(
                output_dir,
                aggregate_join_query,
                SQL_Constructor.table_constructor.get_table_name(part),
            )
            return SQL_aggregate.aggregate_schemas(part, schemas1)
        case _:
            raise NotImplementedError(f"Operation {part.name} not implemented yet.")

    return schemas1
