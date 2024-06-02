from rdflib.plugins.sparql.parserutils import CompValue
from pandas import DataFrame
from eval_incremental import duckdb_conn
from os.path import join

from SQL_Constructor.SQL_Constructor import (
    get_table_name,
    get_schema_w_table_name,
    insert_delta_query,
    insert_query,
    select_query,
)


def readQueryIncrem(
    part: CompValue,
    schema: list[list[str]],
    output_dir: str,
) -> list[str]:
    """Reads all queries of the incremental approach

    Args:
        part (CompValue): Current part of the query
        schema (list[list[str]]): All schemas
        output_dir (str): Output directory

    Returns:
        list[str]: All queries
    """
    all_queries: list[str] = list()
    for var_list in schema:
        file_name: str = "delta" + get_schema_w_table_name(
            part, var_list
        )
        with open(file_name, "r") as file:
            all_queries.append(file.read())
    return all_queries


def readQuery(
    part: CompValue,
    schema: list[list[str]],
    output_dir: str,
) -> list[str]:
    """Reads the query from the file.

    Args:
        part (CompValue): _description_
        schema (list[list[str]]): _description_

    Returns:
        str: _description_
    """
    all_queries: list[str] = list()
    for var_list in schema:
        file_name: str = (
            join(
                output_dir,
                get_schema_w_table_name(part, var_list),
            )
            + ".sql"
        )
        with open(file_name, "r") as file:
            all_queries.append(file.read())
    return all_queries


def evalIncremBGP(
    part: CompValue,
    schemas: list[list[str]],
    output_dir: str,
    increm: bool = False,
) -> None:
    """Evaluate the BGP

    Args:
        part (CompValue): Current part of the query
        schemas (list[list[str]]): Schemas of the part of the query
        increm (bool, optional): Indicates if incremental or not. Defaults to False.
    """
    if not increm:
        all_queries: list[str] = readQuery(
            part, schemas, output_dir
        )
    else:
        all_queries: list[str] = readQuery(
            part, schemas, output_dir
        )
    # TODO: duckdb


def evalIncremPart(
    part: CompValue,
    schemas: dict[str, list[list[str]]],
    output_dir: str,
    increm: bool = False,
) -> list[DataFrame]:
    """Evaluates the query

    Args:
        part (CompValue): Current part of the query
        schemas (dict[str, list[list[str]]]): _description_
    """
    if part.name == "SelectQuery":
        dfs: list[DataFrame] = list()
        for schema in schemas[get_table_name(part)]:
            handle = duckdb_conn.sql(
                select_query(part, schema)
            )
            df = handle.df()
            dfs.append(df)
        return dfs
    if "p" in part:
        evalIncremPart(part.p, schemas, output_dir, increm)
    elif "p1" in part and "p2" in part:
        evalIncremPart(part.p1, schemas, output_dir, increm)
        evalIncremPart(part.p2, schemas, output_dir, increm)
    if increm:
        all_queries: list[str] = readQueryIncrem(
            part, schemas[get_table_name(part)], output_dir
        )
    else:
        all_queries: list[str] = readQuery(
            part, schemas[get_table_name(part)], output_dir
        )

    for query in all_queries:
        result_handle = duckdb_conn.sql(query)
        result: DataFrame = result_handle.df()

        if not result.empty:
            for schema in schemas[get_table_name(part)]:
                match increm:
                    case True:
                        insert: str = insert_delta_query(
                            part, result, schema
                        )
                    case False:
                        insert: str = insert_query(
                            part, result, schema
                        )
                duckdb_conn.sql(insert)

    return DataFrame()
