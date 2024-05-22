from incremental_query_parser import readQueryFile
from eval_incremental.eval_incremental import (
    constructTablesRec,
    dropTablesRec,
)
from SQL_Constructor import (
    SQL_Constructor,
    SQL_initialize_queries,
)
from rdflib.plugins.sparql.parserutils import CompValue
from rdflib.plugins.sparql import parser, algebra


def __non_increm_queries(
    part: CompValue, output_dir: str
) -> None:
    """Constructs the non_incremental queries

    Args:
        part (CompValue): Current part of the query
        output_dir (str): Where to write the SQL queries
    """
    SQL_initialize_queries.build_queries(part, output_dir)


def setup_tables(query: CompValue) -> None:
    """Sets up the tables to use for the queries

    Args:
        query (CompValue): Algebra or part of the query
    """
    # Drop all the tables before the setup
    dropTablesRec(query)
    # Construct the tables
    constructTablesRec(query)


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
    setup_tables(q_query_object.algebra)
    if increm:
        pass
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
