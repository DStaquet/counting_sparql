from SQL_Constructor.hash_writer import setup_hash_values
from build_data import dropTablesRec, readQueryFile
from eval_incremental.eval_incremental import (
    constructTablesRec,
    deleteTablesRec,
)
from SQL_Constructor import SQL_initialize_queries
from SQL_Constructor.table_constructor import (
    get_table_name,
)
from rdflib.plugins.sparql.parserutils import CompValue
from rdflib.plugins.sparql.sparql import Query
from rdflib.plugins.sparql import parser, algebra
from os.path import join, exists
from os import mkdir


def __non_increm_queries(
    part: CompValue,
    output_dir: str,
    og_table_name: str = "G",
) -> None:
    """Constructs the non_incremental queries

    Args:
        part (CompValue): Current part of the query
        output_dir (str): Where to write the SQL queries
    """
    SQL_initialize_queries.build_queries(part, output_dir, og_table_name)


def __increm_queries(
    part: CompValue,
    output_dir: str,
    table_name: str = "G",
) -> None:
    """Builds up the incremental queries

    Args:
        part (CompValue): The algebra of the query
        output_dir (str): Directory to write the output to
    """
    SQL_initialize_queries.build_increm_queries(part, output_dir, table_name=table_name)


def setup_tables(query: CompValue, output_dir: str) -> None:
    """Sets up the tables to use for the queries

    Args:
        query (CompValue): Algebra or part of the query
    """

    # constructs the hash value info file
    handle = open(join(output_dir, "hash_values.json"), "w")
    handle.write("{\n")
    handle.close()
    setup_hash_values(query, output_dir)
    handle = open(join(output_dir, "hash_values.json"), "a")
    handle.write("}")
    handle.close()

    # Drop all the tables before the setup
    drop_queries, drop_delta_queries, _ = dropTablesRec(query, output_dir)
    # Delete all the tables before the setup
    delete_queries: str = deleteTablesRec(query)
    # Construct the tables
    construct_queries: str = constructTablesRec(query)

    # Write the queries to the output directory
    SQL_initialize_queries.write_query_to_output_dir(
        output_dir,
        drop_queries,
        "drop_tables",
    )
    SQL_initialize_queries.write_query_to_output_dir(
        output_dir,
        drop_delta_queries,
        "drop_delta_tables",
    )
    SQL_initialize_queries.write_query_to_output_dir(
        output_dir,
        delete_queries,
        "delete_tables",
    )
    SQL_initialize_queries.write_query_to_output_dir(
        output_dir,
        construct_queries,
        "construct_tables",
    )


def get_query_output_dir(
    output_dir: str,
    q_query_object: Query,
    temp_dir: bool = False,
) -> str:
    """Get the query output directory

    Args:
        output_dir (str): Output directory
        q_query_object (CompValue): Object containing the query

    Returns:
        str: String containing the query output directory
    """
    query_output_dir: str = join(
        output_dir,
        "query_" + get_table_name(q_query_object.algebra),
    )
    if not exists(query_output_dir):
        mkdir(query_output_dir)
    if temp_dir:
        query_output_dir = join(
            output_dir,
            "query_" + get_table_name(q_query_object.algebra),
            "temp_tables",
        )
    if not exists(query_output_dir):
        mkdir(query_output_dir)
    return query_output_dir


def setup_queries(
    query_str: str,
    output_dir: str,
    increm: bool = False,
    temp_dir: bool = False,
    og_table_name: str = "G",
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

    query_output_dir: str = get_query_output_dir(output_dir, q_query_object, temp_dir)
    if not exists(query_output_dir):
        mkdir(query_output_dir)

    if increm:
        __increm_queries(q_query_object.algebra, query_output_dir, og_table_name)
    else:
        __non_increm_queries(q_query_object.algebra, query_output_dir, og_table_name)

    # setup_tables(q_query_object.algebra, query_output_dir)


if __name__ == "__main__":
    import os
    import sys

    hashseed = os.getenv("PYTHONHASHSEED")
    if not hashseed:
        os.environ["PYTHONHASHSEED"] = "0"
        os.execv(sys.executable, [sys.executable] + sys.argv)

    if len(sys.argv) < 4:
        print("Usage: python query_parser.py <query> <data> <output_dir>")
        exit(1)
    else:
        query_str: str = sys.argv[1]
        data_str: str = sys.argv[2]
        output_dir: str = sys.argv[3]

    query: str = readQueryFile(query_str)
    setup_queries(query, output_dir)
    setup_queries(query, output_dir, True)
