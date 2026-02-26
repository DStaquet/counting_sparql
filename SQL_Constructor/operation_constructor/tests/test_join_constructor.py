"""Tests for the join constructor."""

from rdflib.term import Variable
from sqlparse import format as sql_format
from pytest import mark
from duckdb import DuckDBPyConnection, connect

from SQL_Constructor.operation_constructor.join_constructor import (
    join_query_str_constr,
    delta_join_queries_part_func,
)
from SQL_Constructor.table_constructor import get_table_name
from SQL_Constructor.operation_constructor.tests.base_functions import (
    all_type_leaves,
    reset_seed,
)
from build_data import get_query_object
from build_data import (
    readQueryFile,
)


@mark.parametrize(
    "query_file,expected_sql,schemas1,schemas2",
    [
        (
            "SQL_Constructor/operation_constructor/tests/queries/join/join_1_schema.sparql",
            "SQL_Constructor/operation_constructor/tests/queries/join/join_1_schema.sql",
            [{Variable("y"), Variable("w")}],
            [{Variable("x"), Variable("y")}],
        ),
        (
            "SQL_Constructor/operation_constructor/tests/queries/join/join_2_schemas.sparql",
            "SQL_Constructor/operation_constructor/tests/queries/join/join_2_schemas.sql",
            [{Variable("y"), Variable("w")}],
            [
                {Variable("x"), Variable("y")},
                {Variable("x"), Variable("w")},
            ],
        ),
        (
            "SQL_Constructor/operation_constructor/tests/queries/join/join_2_schema_no_overlap.sparql",
            "SQL_Constructor/operation_constructor/tests/queries/join/join_2_schema_no_overlap.sql",
            [{Variable("y"), Variable("w")}],
            [
                {Variable("x"), Variable("y")},
                {Variable("y"), Variable("w")},
            ],
        ),
    ],
)
def test_join_query(
    query_file: str,
    expected_sql: str,
    schemas1: list[set[str]],
    schemas2: list[set[str]],
) -> None:
    """Test if the join query is correct."""
    reset_seed()

    # Read the query file
    part = get_query_object(readQueryFile(query_file)).algebra

    join_leaves = all_type_leaves(part, "Join")

    # Execute the join query
    join_queries: str = ""
    for join_leaf in join_leaves:
        join_query_tuple = join_query_str_constr(
            join_leaf,
            (
                get_table_name(join_leaf.p1),
                get_table_name(join_leaf.p2),
            ),
            schemas1,
            schemas2,
        )
        if isinstance(join_query_tuple, tuple):
            join_queries += sql_format(
                join_query_tuple[0],
                reindent=True,
                keyword_case="upper",
            )
        else:
            join_queries += sql_format(
                join_query_tuple,
                reindent=True,
                keyword_case="upper",
            )

    # Read the expected SQL query
    with open(expected_sql, "r", encoding="utf-8") as f:
        expected_sql_str = f.read()

    # Compare the expected SQL query with the generated SQL query
    assert join_queries == expected_sql_str


@mark.parametrize(
    "query_file,expected_sql,schemas1,schemas2",
    [
        (
            "SQL_Constructor/operation_constructor/tests/queries/join/join_1_schema.sparql",
            "SQL_Constructor/operation_constructor/tests/queries/join/join_1_schema_delta.sql",
            [{Variable("y"), Variable("w")}],
            [{Variable("x"), Variable("y")}],
        ),
        (
            "SQL_Constructor/operation_constructor/tests/queries/join/join_2_schemas.sparql",
            "SQL_Constructor/operation_constructor/tests/queries/join/join_2_schemas_delta.sql",
            [{Variable("y"), Variable("w")}],
            [
                {Variable("x"), Variable("y")},
                {Variable("x"), Variable("w")},
            ],
        ),
        (
            "SQL_Constructor/operation_constructor/tests/queries/join/join_2_schema_no_overlap.sparql",
            "SQL_Constructor/operation_constructor/tests/queries/join/join_2_schema_no_overlap_delta.sql",
            [{Variable("y"), Variable("w")}],
            [
                {Variable("x"), Variable("y")},
                {Variable("y"), Variable("w")},
            ],
        ),
    ],
)
def test_delta_join_query(
    query_file: str,
    expected_sql: str,
    schemas1: list[set[str]],
    schemas2: list[set[str]],
) -> None:
    """Test if the delta join query is correct."""
    reset_seed()

    # Read the query file
    part = get_query_object(readQueryFile(query_file)).algebra

    join_leaves = all_type_leaves(part, "Join")

    # Execute the join query
    join_queries: str = ""
    for join_leaf in join_leaves:
        join_query, _ = delta_join_queries_part_func(
            join_leaf,
            schemas1,
            schemas2,
        )
        join_queries += sql_format(
            join_query,
            reindent=True,
            keyword_case="upper",
        )

    # Read the expected SQL query
    with open(expected_sql, "r", encoding="utf-8") as f:
        expected_sql_str = f.read()

    # Compare the expected SQL query with the generated SQL query
    assert join_queries == expected_sql_str


def _construct_bgps(
    bgp_one_name: str,
    bgp_two_name: str,
    duckdb_conn: DuckDBPyConnection,
) -> None:
    """Constructs the BGPs for the join query."""
    duckdb_conn.execute(
        f"CREATE OR REPLACE TABLE {bgp_one_name} (y TEXT, W TEXT, k_count INT);"
    )
    duckdb_conn.execute(
        f"INSERT INTO {bgp_one_name} (y, w, k_count) VALUES ('a', 'b', 1), ('b', 'c', 1), ('a', 'd', 1), ('d', 'c', 1);"
    )

    duckdb_conn.execute(
        f"CREATE OR REPLACE TABLE {bgp_two_name} (x TEXT, y TEXT, k_count INT);"
    )
    duckdb_conn.execute(
        f"INSERT INTO {bgp_two_name} (x, y, k_count) VALUES ('a', 'b', 1), ('b', 'c', 1), ('a', 'd', 1), ('d', 'c', 1);"
    )


def _drop_join_tables(
    join_table_name: str,
    duckdb_conn: DuckDBPyConnection,
) -> None:
    """Drops the join table."""
    duckdb_conn.execute(f"DROP TABLE IF EXISTS {join_table_name};")
    duckdb_conn.execute(f"DROP TABLE IF EXISTS delta_{join_table_name};")


@mark.parametrize(
    "query_file,expected_output,schemas1,schemas2,database_name,bgp_one,bgp_two,join_name",
    [
        (
            "SQL_Constructor/operation_constructor/tests/queries/join/join_1_schema.sparql",
            [("c", "a", "b", 1), ("c", "a", "d", 1)],
            [{Variable("y"), Variable("w")}],
            [{Variable("x"), Variable("y")}],
            ":memory:",
            "BGP_4828852104882819343",
            "BGP_8639977824181032562",
            "Join_8668205654064478100",
        )
    ],
)
def test_join_query_output(
    query_file: str,
    expected_output: str,
    schemas1: list[set[str]],
    schemas2: list[set[str]],
    database_name: str,
    bgp_one: str,
    bgp_two: str,
    join_name: str,
) -> None:
    """Check if the join query output is correct."""
    reset_seed()

    # Read the query file
    part = get_query_object(readQueryFile(query_file)).algebra

    join_leaves = all_type_leaves(part, "Join")

    # Execute the join query
    join_queries: str = ""

    for join_leaf in join_leaves:
        join_query_tuple = join_query_str_constr(
            join_leaf,
            (
                get_table_name(join_leaf.p1),
                get_table_name(join_leaf.p2),
            ),
            schemas1,
            schemas2,
        )
        if isinstance(join_query_tuple, tuple):
            join_queries += sql_format(
                join_query_tuple[0],
                reindent=True,
                keyword_case="upper",
            )
        else:
            join_queries += sql_format(
                join_query_tuple,
                reindent=True,
                keyword_case="upper",
            )

    # Execute the join query
    duckdb_conn: DuckDBPyConnection = connect(database_name)

    # Constructs the BGPs for the join query
    _construct_bgps(bgp_one, bgp_two, duckdb_conn)
    # Drops the join table
    _drop_join_tables(join_name, duckdb_conn)

    # Execute the join query
    duckdb_conn.execute(join_queries)

    # Check the output of the join query
    result = duckdb_conn.execute(f"SELECT * FROM {join_name};").fetchall()
    assert result == expected_output


def _construct_delta_bgps(
    bgp_one_name: str,
    bgp_two_name: str,
    duckdb_conn: DuckDBPyConnection,
) -> None:
    """Constructs the BGPs for the join query."""
    # Build the delta tables
    duckdb_conn.execute(
        f"CREATE OR REPLACE TABLE delta_{bgp_one_name} (y TEXT, w TEXT, k_count INT);"
    )
    duckdb_conn.execute(
        f"INSERT INTO delta_{bgp_one_name} (y, w, k_count) VALUES ('d', 'c', -1), ('b', 'd', 1);"
    )

    duckdb_conn.execute(
        f"CREATE OR REPLACE TABLE delta_{bgp_two_name} (x TEXT, y TEXT, k_count INT);"
    )
    duckdb_conn.execute(
        f"INSERT INTO delta_{bgp_two_name} (x, y, k_count) VALUES ('d', 'c', -1), ('b', 'd', 1);"
    )

    # Build the nu tables
    duckdb_conn.execute(
        f"CREATE OR REPLACE TABLE nu_{bgp_one_name} (y TEXT, w TEXT, k_count INT);"
    )
    duckdb_conn.execute(
        f"INSERT INTO nu_{bgp_one_name} (y, w, k_count) VALUES ('a', 'b', 1), ('b', 'c', 1), ('a', 'd', 1), ('b', 'd', 1);"
    )
    duckdb_conn.execute(
        f"CREATE OR REPLACE TABLE nu_{bgp_two_name} (x TEXT, y TEXT, k_count INT);"
    )
    duckdb_conn.execute(
        f"INSERT INTO nu_{bgp_two_name} (x, y, k_count) VALUES ('a', 'b', 1), ('b', 'c', 1), ('a', 'd', 1), ('b', 'd', 1);"
    )


@mark.parametrize(
    "query_file,expected_output,schemas1,schemas2,database_name,bgp_one,bgp_two,join_name",
    [
        (
            "SQL_Constructor/operation_constructor/tests/queries/join/join_1_schema.sparql",
            [("c", "a", "d", -1), ("d", "a", "b", 1)],
            [{Variable("y"), Variable("w")}],
            [{Variable("x"), Variable("y")}],
            ":memory:",
            "BGP_4828852104882819343",
            "BGP_8639977824181032562",
            "Join_8668205654064478100",
        )
    ],
)
def test_join_query_delta(
    query_file: str,
    expected_output: str,
    schemas1: list[set[str]],
    schemas2: list[set[str]],
    database_name: str,
    bgp_one: str,
    bgp_two: str,
    join_name: str,
) -> None:
    """Check if the join query output is correct."""
    reset_seed()

    # Read the query file
    part = get_query_object(readQueryFile(query_file)).algebra

    join_leaves = all_type_leaves(part, "Join")

    # Execute the join query
    join_queries: str = ""

    for join_leaf in join_leaves:
        join_query, _ = delta_join_queries_part_func(
            join_leaf,
            schemas1,
            schemas2,
        )
        join_queries += sql_format(
            join_query,
            reindent=True,
            keyword_case="upper",
        )

    # Execute the join query
    duckdb_conn: DuckDBPyConnection = connect(database_name)

    # Constructs the BGPs for the join query
    _construct_bgps(bgp_one, bgp_two, duckdb_conn)
    _construct_delta_bgps(bgp_one, bgp_two, duckdb_conn)
    # Drops the join table
    _drop_join_tables(join_name, duckdb_conn)

    # Execute the join query
    duckdb_conn.execute(join_queries)

    # Check the output of the join query
    result = duckdb_conn.execute(f"SELECT * FROM delta_{join_name};").fetchall()
    assert result == expected_output
