from SQL_Constructor.operation_constructor.filter_constructor import (
    filter_query,
)
from SQL_Constructor.operation_constructor.tests.base_functions import (
    reset_seed,
    all_type_leaves,
)
from incremental_query_parser import (
    get_query_object,
    readQueryFile,
)

from rdflib.term import Variable
from pytest import mark
from sqlparse import format

from duckdb import DuckDBPyConnection, connect


@mark.parametrize(
    "query_file,expected_sql,expected_delta,schemas",
    [
        (
            "SQL_Constructor/operation_constructor/tests/queries/filter/filter_1_schema.sparql",
            "SQL_Constructor/operation_constructor/tests/queries/filter/filter_1_schema.sql",
            "SQL_Constructor/operation_constructor/tests/queries/filter/filter_1_schema_delta.sql",
            [{Variable("x"), Variable("z")}],
        ),
        (
            "SQL_Constructor/operation_constructor/tests/queries/filter/filter_2_schemas.sparql",
            "SQL_Constructor/operation_constructor/tests/queries/filter/filter_2_schemas.sql",
            "SQL_Constructor/operation_constructor/tests/queries/filter/filter_2_schemas_delta.sql",
            [
                {Variable("x"), Variable("z")},
                {Variable("x"), Variable("y")},
            ],
        ),
        (
            "SQL_Constructor/operation_constructor/tests/queries/filter/filter_1_schema_with.sparql",
            "SQL_Constructor/operation_constructor/tests/queries/filter/filter_1_schema_with.sql",
            "SQL_Constructor/operation_constructor/tests/queries/filter/filter_1_schema_with_delta.sql",
            [{Variable("x"), Variable("y")}],
        ),
    ],
)
def test_filter_query(
    query_file: str,
    expected_sql: str,
    expected_delta: str,
    schemas: list[set[str]],
) -> None:
    """Tests if the filter_query function works correctly.

    Args:
        query_file (str): Query file to read query from.
        expected_sql (str): SQL file that's expected
    """
    reset_seed()

    part = get_query_object(
        readQueryFile(query_file)
    ).algebra

    # Find only Filter patterns
    filter_leaves = all_type_leaves(part, "Filter")

    filter_queries: str = ""
    delta_filter_queries: str = ""
    for filter_leaf in reversed(filter_leaves):
        filter_queries += format(
            filter_query(filter_leaf, schemas),
            reindent=True,
            uppercase=True,
        )
        delta_filter_queries += format(
            filter_query(
                filter_leaf, schemas, is_delta=True
            ),
            reindent=True,
            uppercase=True,
        )

    with open(expected_sql) as f:
        sql_queries = f.read()
    with open(expected_delta) as f:
        delta_sql_queries = f.read()

    assert filter_queries == sql_queries
    assert delta_filter_queries == delta_sql_queries


def __constructBGPs(
    bgp_name: str,
    duckdb_conn: DuckDBPyConnection,
) -> None:
    """Constructs the BGP tables."""
    duckdb_conn.execute(
        f"CREATE OR REPLACE TABLE {bgp_name} (x TEXT, y TEXT, k_count INT);"
    )
    duckdb_conn.execute(
        f"INSERT INTO {bgp_name} VALUES ('a', 'b', 1), ('b', 'b', 1), ('c', 'b', 1);"
    )


def __dropFilterTables(
    filter_name: str,
    duckdb_conn: DuckDBPyConnection,
) -> None:
    """Drops the filter tables."""
    duckdb_conn.execute(
        f"DROP TABLE IF EXISTS {filter_name};"
    )
    duckdb_conn.execute(
        f"DROP TABLE IF EXISTS delta_{filter_name};"
    )


def __constructDeltaBGPs(
    bgp_name: str,
    duckdb_conn: DuckDBPyConnection,
) -> None:
    """Constructs the delta BGP tables."""
    duckdb_conn.execute(
        f"CREATE OR REPLACE TABLE delta_{bgp_name} (x TEXT, y TEXT, k_count INT);"
    )
    duckdb_conn.execute(
        f"INSERT INTO delta_{bgp_name} VALUES ('a', 'a', 1), ('b', 'b', -1), ('b', 'c', 1), ('c', 'b', -1);"
    )


@mark.parametrize(
    "query_file,expected_output,expected_delta_output,schemas,bgp_name,filter_name,database_name",
    [
        (
            "SQL_Constructor/operation_constructor/tests/queries/filter/filter_1_schema_with.sparql",
            [("a", "b", 1), ("c", "b", 1)],
            [("b", "c", 1), ("c", "b", -1)],
            [{Variable("x"), Variable("y")}],
            "BGP_4313253051102226119",
            "Filter_5867829970618114298",
            ":memory:",
        )
    ],
)
def test_filter_query_output(
    query_file: str,
    expected_output,
    expected_delta_output,
    schemas: list[set[str]],
    bgp_name: str,
    filter_name: str,
    database_name: str,
) -> None:
    """Tests if the filter_query function works correctly."""
    reset_seed()

    part = get_query_object(
        readQueryFile(query_file)
    ).algebra

    # Find only Filter patterns
    filter_leaves = all_type_leaves(part, "Filter")

    filter_queries: str = ""
    delta_filter_queries: str = ""
    for filter_leaf in reversed(filter_leaves):
        filter_queries += format(
            filter_query(filter_leaf, schemas),
            reindent=True,
            uppercase=True,
        )
        delta_filter_queries += format(
            filter_query(
                filter_leaf, schemas, is_delta=True
            ),
            reindent=True,
            uppercase=True,
        )

    # Connect to DuckDB
    duckdb_conn = connect(database_name)

    # Construct the BGP tables
    __constructBGPs(bgp_name, duckdb_conn)
    __constructDeltaBGPs(bgp_name, duckdb_conn)

    # Drop the filter tables
    __dropFilterTables(filter_name, duckdb_conn)

    # Execute the filter queries
    duckdb_conn.execute(filter_queries)
    duckdb_conn.execute(delta_filter_queries)

    # Check if the output is correct
    result = duckdb_conn.execute(
        f"SELECT * FROM {filter_name};"
    ).fetchall()
    assert result == expected_output

    result = duckdb_conn.execute(
        f"SELECT * FROM delta_{filter_name};"
    ).fetchall()
    assert result == expected_delta_output
