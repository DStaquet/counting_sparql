"""Tests a quick aggregation query with SUM in the projection."""

import argparse
import os
import sys
from random import randint, sample

from csv import DictReader
from time import time

from duckdb import connect, DuckDBPyConnection

from experiments.time_operators import timing_per_operator
from build_data import (
    load_delta_table_in_graph,
    load_table_in_graph,
    setup_query_files,
    readQueryFile,
    get_query_object,
)
from setup_queries import get_query_output_dir


def _values_per_product(
    product_ids: list[str],
    m_values_count: int,
    max_value: int,
) -> dict[str, list[int]]:
    return_dict: dict[str, list[int]] = {}

    for product_id in product_ids:
        for _ in range(m_values_count):
            return_dict[product_id] = return_dict.get(
                product_id, []
            ) + [randint(1, max_value)]

    return return_dict


def _generate_synthethic_products_data(
    duckdb_conn: DuckDBPyConnection,
    n_product_count: int,
    m_product_values_count: int,
    table_name: str,
    max_value: int = 1000,
) -> tuple[str, dict[str, list[int]]]:
    duckdb_conn.execute(
        f"DROP TABLE IF EXISTS {table_name};"
    )
    duckdb_conn.execute(
        f"CREATE TABLE IF NOT EXISTS {table_name}"
        + " (product_id VARCHAR, value1 INT, k_count INT);"
    )

    # Construct all synthetic product ids and their values
    product_ids = [
        "http://example.org/" + str(n)
        for n in range(1, n_product_count + 1)
    ]
    products_w_values: dict[str, list[int]] = (
        _values_per_product(
            product_ids, m_product_values_count, max_value
        )
    )

    # Generate the SQL insert statement
    insert_line = f"INSERT INTO {table_name} (product_id, value1, k_count) VALUES "
    for product_id, values in products_w_values.items():
        for value in values:
            insert_line += f"('{product_id}', {value}, 1),"
    insert_line = insert_line[:-1] + ";"

    # Returns the insert line and the generated products with values to use to to
    # generate deltas later on
    return insert_line, products_w_values


def _generate_product_data(
    duckdb_conn: DuckDBPyConnection,
    data_file: str,
    table_name: str,
) -> str:

    # Dropping and creating Products table
    duckdb_conn.execute(
        f"DROP TABLE IF EXISTS {table_name};"
    )
    duckdb_conn.execute(
        f"CREATE TABLE IF NOT EXISTS {table_name} "
        + "(product_id VARCHAR, value1 INT, k_count INT);"
    )

    # Inserting product data based on given data file
    insert_line = f"INSERT INTO {table_name} (product_id, value1, k_count) VALUES "
    with open(data_file, "r", encoding="utf-8") as data_f:
        csv_dict = DictReader(data_f)
        for line in csv_dict:
            if "PropertyNumeric" in line["p"]:
                insert_line += f"('{line['s']}', {int(line['o'])}, {int(line['k_count'])}),"
    insert_line = insert_line[:-1] + ";"
    return insert_line


def _generate_deltas(
    duckdb_conn: DuckDBPyConnection,
    products: dict[str, list[int]],
    delta_counts: tuple[int, int],
    table_name: str,
    max_value: int = 1000,
) -> tuple[str, dict[str, list[int]]]:
    duckdb_conn.execute(
        f"DROP TABLE IF EXISTS {table_name};"
    )
    duckdb_conn.execute(
        f"CREATE TABLE IF NOT EXISTS {table_name} "
        + "(product_id VARCHAR, value1 INT, k_count INT);"
    )

    delta_count, sample_size = delta_counts
    # Choose random products to delete values from
    to_delete_from_products = sample(
        list(products.keys()), delta_count // 2
    )
    to_insert_to_products = sample(
        list(products.keys()), delta_count // 2
    )

    # Add delete statements to delta SQL
    delta_sql = "INSERT INTO delta_Products (product_id, value1, k_count) VALUES "
    for product_id in to_delete_from_products:
        if products[product_id]:
            values_to_delete = sample(
                products[product_id], sample_size
            )
            for value_to_delete in values_to_delete:
                delta_sql += f"('{product_id}', {value_to_delete}, -1),"
                products[product_id].remove(value_to_delete)
    # Add insert statements to delta SQL
    for product_id in to_insert_to_products:
        for _ in range(sample_size):
            new_value = randint(1, max_value)
            delta_sql += (
                f"('{product_id}', {new_value}, 1),"
            )
            products[product_id].append(new_value)
    delta_sql = delta_sql[:-1] + ";"

    return delta_sql, products


def _generate_nu_query(
    duckdb_conn: DuckDBPyConnection,
    table_name: str,
    products: dict[str, list[int]],
) -> str:
    duckdb_conn.execute(
        f"DROP TABLE IF EXISTS nu_{table_name};"
    )
    duckdb_conn.execute(
        f"CREATE TABLE IF NOT EXISTS nu_{table_name} "
        + "(product_id VARCHAR, value1 INT, k_count INT);"
    )

    nu_sql = "INSERT INTO nu_Products (product_id, value1, k_count) VALUES "
    for product_id, values in products.items():
        for value in values:
            nu_sql += f"('{product_id}', {value}, 1),"
    nu_sql = nu_sql[:-1] + ";"
    return nu_sql


def prep_aggregation_table(
    duckdb_conn: DuckDBPyConnection,
    args_namespace: argparse.Namespace,
) -> None:
    """Prepares the previous table to run the aggregation on."""

    max_value_value = 1000

    print("Generating synthetic products data...")
    g_build_query, product_dict = (
        _generate_synthethic_products_data(
            duckdb_conn,
            args_namespace.n,
            args_namespace.m,
            table_name="Products",
            max_value=max_value_value,
        )
    )
    duckdb_conn.execute(g_build_query)

    print("Generating delta products data...")
    delta_query, product_dict_nu = _generate_deltas(
        duckdb_conn,
        product_dict,
        delta_counts=(
            args_namespace.delta_count,
            args_namespace.sample_size,
        ),
        table_name="delta_Products",
        max_value=max_value_value,
    )
    duckdb_conn.execute(delta_query)

    print("Generating nu products data...")
    nu_build_query = _generate_nu_query(
        duckdb_conn, "Products", product_dict_nu
    )
    duckdb_conn.execute(nu_build_query)


def prep_aggregation_query(
    duckdb_conn: DuckDBPyConnection,
    args_namespace: argparse.Namespace,
) -> None:
    """Prepares and runs an aggregation query."""

    # Setup query files
    setup_query_files(
        args_namespace.query_file, args_namespace.query_dir
    )

    q_query_object = get_query_object(
        readQueryFile(args_namespace.query_file)
    )
    # algebra.pprintAlgebra(q_query_object)

    # Output directory
    query_output_dir: str = get_query_output_dir(
        args_namespace.query_dir, q_query_object
    )

    load_table_in_graph(
        args_namespace.data_file,
        duckdb_conn,
    )
    load_delta_table_in_graph(
        args_namespace.delta_file,
        duckdb_conn,
        args_namespace.nu_file,
    )

    duckdb_conn.execute(
        readQueryFile(
            os.path.join(
                query_output_dir, "drop_tables.sql"
            )
        )
    )
    duckdb_conn.execute(
        readQueryFile(
            os.path.join(
                query_output_dir,
                "drop_delta_tables.sql",
            )
        )
    )

    timing_per_operator(
        q_query_object.algebra.p,
        query_output_dir,
        duckdb_conn,
    )

    timing_per_operator(
        q_query_object.algebra.p,
        query_output_dir,
        duckdb_conn,
        increm=True,
    )


if __name__ == "__main__":
    hashseed = os.getenv("PYTHONHASHSEED")
    if not hashseed:
        os.environ["PYTHONHASHSEED"] = "0"
        os.execv(
            sys.executable, [sys.executable] + sys.argv
        )

    parser = argparse.ArgumentParser(
        description="Time aggregation query."
    )
    parser.add_argument(
        "query_file",
        type=str,
        help="The query file to run.",
    )
    parser.add_argument(
        "query_dir",
        type=str,
        help="The directory where the SQL queries are stored.",
    )
    """ parser.add_argument(
        "data_file",
        type=str,
        help="The base graph data file to use.",
    )
    parser.add_argument(
        "delta_file",
        type=str,
        help="The delta graph data file to use.",
    )
    parser.add_argument(
        "nu_file",
        type=str,
        help="The nu file to use.",
    ) """
    parser.add_argument(
        "--runs",
        "-r",
        type=int,
        default=3,
        help="The number of runs to average over.",
    )
    parser.add_argument(
        "--db",
        type=str,
        default=":memory:",
        help="The database to connect to.",
    )
    parser.add_argument(
        "aggregation_sql_file",
        type=str,
        help="The SQL file that contains the aggregation operator.",
    )
    parser.add_argument(
        "aggregation_delta_sql_file",
        type=str,
        help="The SQL file that contains the aggregation operator for the delta.",
    )
    parser.add_argument(
        "aggregation_nu_sql_file",
        type=str,
        help="The SQL file that contains the aggregation operator for the nu.",
    )
    parser.add_argument(
        "--n",
        "-n",
        type=int,
        default=1000,
        help="Number of products to generate.",
    )
    parser.add_argument(
        "--m",
        "-m",
        type=int,
        default=10,
        help="Number of values per product to generate.",
    )
    parser.add_argument(
        "--delta_count",
        "-dc",
        type=int,
        default=100,
        help="Number of delta changes to generate.",
    )
    parser.add_argument(
        "--sample_size",
        "-sas",
        type=int,
        default=1,
        help="Number of values to change per product in delta.",
    )

    args = parser.parse_args()

    conn: DuckDBPyConnection = connect(
        database=args.db, read_only=False
    )

    with open(
        args.aggregation_sql_file, "r", encoding="utf-8"
    ) as f:
        aggregation_sql = f.read()
    with open(
        args.aggregation_delta_sql_file,
        "r",
        encoding="utf-8",
    ) as f:
        aggregation_delta_sql = f.read()
    with open(
        args.aggregation_nu_sql_file,
        "r",
        encoding="utf-8",
    ) as f:
        aggregation_nu_sql = f.read()

    avg_increm_time: float = 0.0
    avg_scratch_time: float = 0.0

    print("Preparing products tables...")
    prep_aggregation_table(
        conn,
        args,
    )

    for run in range(args.runs):
        print(f"Run {run+1}/{args.runs}")

        print("Running aggregation incrementally...")
        conn.execute("DROP TABLE IF EXISTS Agg;")
        conn.execute("DROP TABLE IF EXISTS nu_Agg_increm;")
        conn.execute(aggregation_sql)
        conn.execute("DROP TABLE IF EXISTS delta_Agg;")
        conn.execute("DROP TABLE IF EXISTS temp_Agg;")
        start_time = time()
        conn.execute(aggregation_delta_sql)
        end_time = time()
        print(
            f"Delta aggregation completed in {(end_time - start_time)*1000} milliseconds."
        )
        avg_increm_time += (end_time - start_time) * 1000
        print(
            "Average incremental time so far: ",
            avg_increm_time / (run + 1),
        )

        print("Running aggregation from scratch...")
        conn.execute("DROP TABLE IF EXISTS nu_Agg;")
        start_time = time()
        conn.execute(aggregation_nu_sql)
        end_time = time()
        print(
            f"Scratch aggregation completed in {(end_time - start_time)*1000} milliseconds."
        )
        avg_scratch_time += (end_time - start_time) * 1000
        print(
            "Average scratch time so far: ",
            avg_scratch_time / (run + 1),
        )
        print()

    avg_increm_time /= args.runs
    avg_scratch_time /= args.runs
    print(
        f"Average incremental aggregation time: {avg_increm_time} milliseconds."
    )
    print(
        f"Average scratch aggregation time: {avg_scratch_time} milliseconds."
    )

    print("Done.")
