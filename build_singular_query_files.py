"""
Builds a singular SQL file to use for the scratch or incremental query.
"""

import os
import sys
from os.path import join, exists
from argparse import ArgumentParser, Namespace

from rdflib.plugins.sparql.sparql import Query

from SQL_Constructor.singular_file_constructor import (
    entire_run_query,
)
from setup_queries import (
    setup_queries,
    setup_tables,
    get_query_output_dir,
)
from build_data import (
    get_query_object,
    readQueryFile,
    get_query_input,
)
from benchmarker.dict_maker import constructDictFromTree


def _delete_temp_dir(query_dir: str, q_query_object: Query) -> None:
    temp_dir = get_query_output_dir(query_dir, q_query_object, temp_dir=True)
    if exists(temp_dir):
        for file in os.listdir(temp_dir):
            os.remove(join(temp_dir, file))
        os.rmdir(temp_dir)


def _setup_tables(query: str, output_dir: str) -> None:
    q_query_object: Query = get_query_object(readQueryFile(query))

    query_output_dir = get_query_output_dir(output_dir, q_query_object, temp_dir=True)

    setup_tables(q_query_object.algebra, query_output_dir)


def _setup_one_file(query: str, query_dir: str) -> None:
    q_query_object: Query = get_query_object(readQueryFile(query))

    # Builds the query directories and finds the query input directory
    query_output_dir = get_query_output_dir(query_dir, q_query_object)
    if not exists(query_output_dir):
        os.mkdir(query_output_dir)
    query_input_dir = get_query_input(query_dir, q_query_object, temp_dir=True)

    # Construct dictionaries with all queries based on the query algebra
    sql_queries = constructDictFromTree(q_query_object.algebra, query_input_dir)
    sql_delta_queries = constructDictFromTree(
        q_query_object.algebra, query_input_dir, increm=True
    )

    entire_query = entire_run_query(q_query_object.algebra, sql_queries)
    with open(
        join(query_output_dir, "base_query.sql"),
        "w",
        encoding="utf-8",
    ) as handle:
        handle.write(entire_query)
    entire_increm_query = entire_run_query(q_query_object.algebra, sql_delta_queries)
    with open(
        join(query_output_dir, "increm_query.sql"),
        "w",
        encoding="utf-8",
    ) as handle:
        handle.write(entire_increm_query)


def _main(arguments: Namespace) -> None:
    query = readQueryFile(arguments.query)
    setup_queries(
        query,
        arguments.dir,
        increm=False,
        temp_dir=True,
        og_table_name=arguments.table_name,
        delta_table_name=arguments.delta_table_name,
    )
    setup_queries(
        query,
        arguments.dir,
        increm=True,
        temp_dir=True,
        og_table_name=arguments.table_name,
        delta_table_name=arguments.delta_table_name,
    )
    _setup_tables(arguments.query, arguments.dir)
    _setup_one_file(arguments.query, arguments.dir)
    _delete_temp_dir(arguments.dir, get_query_object(query))


if __name__ == "__main__":
    hashseed = os.getenv("PYTHONHASHSEED")
    if not hashseed:
        os.environ["PYTHONHASHSEED"] = "0"
        os.execv(sys.executable, [sys.executable] + sys.argv)

    parser = ArgumentParser(
        description="Builds a singular SQL file to use for the scratch or incremental query."
    )
    parser.add_argument(
        "query",
        help="The query to build a singular SQL file for.",
    )
    parser.add_argument(
        "dir",
        help="The directory to output the singular SQL file to.",
    )
    parser.add_argument(
        "-tn",
        "--table_name",
        help="The name of the original table to use in the SQL queries.",
        default="G",
    )
    parser.add_argument(
        "-dtn",
        "--delta_table_name",
        help="The name of the delta table to use in the SQL queries.",
        default="delta_G",
    )
    args = parser.parse_args()

    _main(args)
