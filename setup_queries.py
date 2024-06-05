from incremental_query_parser import readQueryFile
from eval_incremental.eval_incremental import (
    constructTablesRec,
    dropTablesRec,
)
from SQL_Constructor import SQL_initialize_queries
from SQL_Constructor.SQL_Constructor import get_table_name
from rdflib.plugins.sparql.parserutils import CompValue
from rdflib.plugins.sparql import parser, algebra
from os.path import join, exists
from os import mkdir


def __non_increm_queries(
    part: CompValue,
    output_dir: str,
) -> None:
    """Constructs the non_incremental queries

    Args:
        part (CompValue): Current part of the query
        output_dir (str): Where to write the SQL queries
    """
    query_output_dir: str = join(
        output_dir, "query_" + get_table_name(part)
    )
    if not exists(query_output_dir):
        mkdir(query_output_dir)
    SQL_initialize_queries.build_queries(
        part, query_output_dir
    )


def __increm_queries(
    part: CompValue,
    output_dir: str,
) -> None:
    """Builds up the incremental queries

    Args:
        part (CompValue): The algebra of the query
        output_dir (str): Directory to write the output to
    """
    query_output_dir: str = join(
        output_dir, "query_" + get_table_name(part)
    )
    if not exists(query_output_dir):
        mkdir(query_output_dir)
    SQL_initialize_queries.build_increm_queries(
        part, query_output_dir
    )


def setup_tables(query: CompValue, output_dir: str) -> None:
    """Sets up the tables to use for the queries

    Args:
        query (CompValue): Algebra or part of the query
    """
    # Drop all the tables before the setup
    drop_queries: str = dropTablesRec(query)
    # Construct the tables
    construct_queries: str = constructTablesRec(query)

    # Write the queries to the output directory
    SQL_initialize_queries.write_query_to_output_dir(
        join(output_dir, "query_" + get_table_name(query)),
        drop_queries,
        "drop_tables",
    )
    SQL_initialize_queries.write_query_to_output_dir(
        join(output_dir, "query_" + get_table_name(query)),
        construct_queries,
        "construct_tables",
    )


def setup_queries(
    query_str: str,
    data: str,
    output_dir: str,
    increm: bool = False,
) -> None:
    """Sets up the queries incrementally or non-incrementally

    Args:
        query_str (str): String containing the query
        data (str): The given data
        output_file (str): Output file to write the results
    """
    query_tree = parser.parseQuery(str(query_str))
    q_query_object = algebra.translateQuery(query_tree)
    # algebra.pprintAlgebra(q_query_object)

    setup_tables(q_query_object.algebra, output_dir)

    if increm:
        __increm_queries(q_query_object.algebra, output_dir)
    else:
        __non_increm_queries(
            q_query_object.algebra, output_dir
        )


if __name__ == "__main__":
    import os
    import sys

    hashseed = os.getenv("PYTHONHASHSEED")
    if not hashseed:
        os.environ["PYTHONHASHSEED"] = "0"
        os.execv(
            sys.executable, [sys.executable] + sys.argv
        )

    if len(sys.argv) < 4:
        print(
            "Usage: python query_parser.py <query> <data> <output_dir>"
        )
        exit(1)
    else:
        query_str: str = sys.argv[1]
        data_str: str = sys.argv[2]
        output_dir: str = sys.argv[3]

    query: str = readQueryFile(query_str)
    setup_queries(query, data_str, output_dir)
    setup_queries(query, data_str, output_dir, True)
