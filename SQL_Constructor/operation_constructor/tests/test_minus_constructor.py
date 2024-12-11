from SQL_Constructor.operation_constructor.minus_constructor import (
    minus_query,
    delta_minus_query,
)
from SQL_Constructor.operation_constructor.tests.base_functions import (
    all_type_leaves,
    reset_seed,
    connect,
    DuckDBPyConnection,
)
from incremental_query_parser import (
    get_query_object,
    readQueryFile,
)

from rdflib.plugins.sparql.parserutils import CompValue
from rdflib.term import Variable
from sqlparse import format
from pytest import mark

from pandas import DataFrame
from pandas.testing import assert_frame_equal
from numpy import array


@mark.parametrize(
    "query_file,expected_sql,schemas1,schemas2",
    [
        (
            "SQL_Constructor/operation_constructor/tests/queries/minus/minus_1_schema.sparql",
            "SQL_Constructor/operation_constructor/tests/queries/minus/minus_1_schema.sql",
            [{Variable("x")}],
            [
                {
                    Variable("y"),
                    Variable("x"),
                }
            ],
        ),
        (
            "SQL_Constructor/operation_constructor/tests/queries/minus/minus_2_schemas.sparql",
            "SQL_Constructor/operation_constructor/tests/queries/minus/minus_2_schemas.sql",
            [
                {
                    Variable("x"),
                }
            ],
            [
                {
                    Variable("x"),
                    Variable("y"),
                },
                {
                    Variable("x"),
                    Variable("z"),
                },
            ],
        ),
        (
            "SQL_Constructor/operation_constructor/tests/queries/minus/minus_4_schemas.sparql",
            "SQL_Constructor/operation_constructor/tests/queries/minus/minus_4_schemas.sql",
            [
                {
                    Variable("x"),
                },
                {
                    Variable("y"),
                },
            ],
            [
                {
                    Variable("x"),
                    Variable("y"),
                },
                {
                    Variable("x"),
                    Variable("z"),
                },
            ],
        ),
    ],
)
def test_minus_query(
    query_file: str,
    expected_sql: str,
    schemas1: list[set[str]],
    schemas2: list[set[str]],
) -> None:
    """Tests the minus_query function."""
    reset_seed()

    part = get_query_object(
        readQueryFile(query_file)
    ).algebra

    # Find only Minus patterns
    minus_leaves: list[CompValue] = all_type_leaves(
        part, "Minus"
    )

    minus_queries: str = ""
    for minus in reversed(minus_leaves):
        current_query = minus_query(
            minus, schemas1, schemas2
        )

        minus_queries += format(
            current_query,
            reindent=True,
            keyword_case="upper",
        )

    with open(expected_sql) as f:
        sql_queries = f.read()

    assert minus_queries == sql_queries


@mark.parametrize(
    "query_file,expected_sql,schemas1,schemas2",
    [
        (
            "SQL_Constructor/operation_constructor/tests/queries/minus/minus_1_schema.sparql",
            "SQL_Constructor/operation_constructor/tests/queries/minus/minus_1_schema_delta.sql",
            [{Variable("x")}],
            [
                {
                    Variable("y"),
                    Variable("x"),
                }
            ],
        ),
        (
            "SQL_Constructor/operation_constructor/tests/queries/minus/minus_2_schemas.sparql",
            "SQL_Constructor/operation_constructor/tests/queries/minus/minus_2_schemas_delta.sql",
            [
                {
                    Variable("x"),
                }
            ],
            [
                {
                    Variable("x"),
                    Variable("y"),
                },
                {
                    Variable("x"),
                    Variable("z"),
                },
            ],
        ),
        (
            "SQL_Constructor/operation_constructor/tests/queries/minus/minus_4_schemas.sparql",
            "SQL_Constructor/operation_constructor/tests/queries/minus/minus_4_schemas_delta.sql",
            [
                {
                    Variable("x"),
                },
                {
                    Variable("y"),
                },
            ],
            [
                {
                    Variable("x"),
                    Variable("y"),
                },
                {
                    Variable("x"),
                    Variable("z"),
                },
            ],
        ),
    ],
)
def test_delta_minus_query(
    query_file: str,
    expected_sql: str,
    schemas1: list[set[str]],
    schemas2: list[set[str]],
) -> None:
    """Tests the delta_minus_query function."""
    reset_seed()

    part = get_query_object(
        readQueryFile(query_file)
    ).algebra

    # Find only Minus patterns
    minus_leaves: list[CompValue] = all_type_leaves(
        part, "Minus"
    )

    minus_queries: str = ""
    for minus in reversed(minus_leaves):
        current_query, current_join_query = (
            delta_minus_query(minus, schemas1, schemas2)
        )

        minus_queries += format(
            current_query,
            reindent=True,
            keyword_case="upper",
        )

    with open(expected_sql) as f:
        sql_queries = f.read()

    assert minus_queries == sql_queries


def __buildBGPs(
    bgp_name_one: str,
    bgp_name_two: str,
    minus_table: str,
    duckdb_conn: DuckDBPyConnection,
) -> None:
    """Builds up the BGPs for the query."""
    # Drop tables if they exist
    for table in [bgp_name_one, bgp_name_two, minus_table]:
        duckdb_conn.execute(
            "DROP TABLE IF EXISTS " + table + ";"
        )

    # Build first BGP
    duckdb_conn.execute(
        "CREATE TABLE IF NOT EXISTS "
        + bgp_name_one
        + " (x TEXT, y TEXT, k_count INT);"
    )
    duckdb_conn.execute(
        "INSERT INTO "
        + bgp_name_one
        + " (x, y, k_count) VALUES ('a', 'b', 1), ('a', 'd', 1);"
    )

    # Build second BGP
    duckdb_conn.execute(
        "CREATE TABLE IF NOT EXISTS "
        + bgp_name_two
        + " (y TEXT, k_count INT);"
    )
    duckdb_conn.execute(
        "INSERT INTO "
        + bgp_name_two
        + " (y, k_count) VALUES ('b', 1);"
    )


@mark.parametrize(
    "query_file,expected_output,database,schemas1,schemas2,bgp_name_one,bgp_name_two,minus_table",
    [
        (
            "SQL_Constructor/operation_constructor/tests/queries/minus/minus_output_test.sparql",
            [["a", "d", 1]],
            "database/minus_test.db",
            [{Variable("x"), Variable("y")}],
            [{Variable("y")}],
            "BGP_2112036525527516625",
            "BGP_1699582530383365185",
            "Minus_6413830616648920484",
        )
    ],
)
def test_minus_output(
    query_file: str,
    expected_output,
    database: str,
    schemas1: list[set[str]],
    schemas2: list[set[str]],
    bgp_name_one: str,
    bgp_name_two: str,
    minus_table: str,
) -> None:
    """Tests the output of the minus query."""
    reset_seed()

    part = get_query_object(
        readQueryFile(query_file)
    ).algebra

    # Find only Minus patterns
    minus_leaves: list[CompValue] = all_type_leaves(
        part, "Minus"
    )

    minus_queries: str = ""
    for minus in reversed(minus_leaves):
        current_query = minus_query(
            minus, schemas1, schemas2
        )

        minus_queries += format(
            current_query,
            reindent=True,
            keyword_case="upper",
        )

    # Connect to the database
    duckdb_conn = connect(database)

    # Build the BGPs
    __buildBGPs(
        bgp_name_one, bgp_name_two, minus_table, duckdb_conn
    )

    # Execute the query
    duckdb_conn.execute(minus_queries)

    output_df = duckdb_conn.sql(
        "SELECT * FROM " + minus_table + ";"
    ).df()

    """to_compare_df = DataFrame(
        expected_output, columns=["x", "y", "k_count"]
    )"""

    values = output_df.values.tolist()

    assert values == expected_output
