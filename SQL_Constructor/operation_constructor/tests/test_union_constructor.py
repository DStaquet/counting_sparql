"""Test cases for the union constructor in SQL_Constructor.
These tests ensure that the union queries are generated correctly and that they produce the
expected SQL output."""

from pytest import mark
from rdflib.term import Variable
from sqlparse import format as sql_format
from duckdb import DuckDBPyConnection, connect

from SQL_Constructor.operation_constructor.union_constructor import (
    union_query,
    delta_union_query,
)
from SQL_Constructor.operation_constructor.tests.base_functions import (
    reset_seed,
    all_type_leaves,
)
from build_data import get_query_object, readQueryFile


@mark.parametrize(
    "query_file,expected_sql,schemas1,schemas2",
    [
        (
            "SQL_Constructor/operation_constructor/tests/queries/union/union_2_schemas.sparql",
            "SQL_Constructor/operation_constructor/tests/queries/union/union_2_schemas.sql",
            [
                {Variable("x"), Variable("y")},
            ],
            [
                {Variable("x"), Variable("z")},
            ],
        ),
        (
            "SQL_Constructor/operation_constructor/tests/queries/union/union_3_schemas.sparql",
            "SQL_Constructor/operation_constructor/tests/queries/union/union_3_schemas.sql",
            [
                {Variable("x"), Variable("z")},
                {Variable("y"), Variable("w")},
            ],
            [
                {Variable("x"), Variable("z")},
            ],
        ),
    ],
)
def test_union_query(
    query_file: str,
    expected_sql: str,
    schemas1: list[set[str]],
    schemas2: list[set[str]],
) -> None:
    """Test if the union_query function works correctly."""
    reset_seed()

    part = get_query_object(readQueryFile(query_file)).algebra

    union_leaves = all_type_leaves(part, "Union")

    union_queries: str = ""
    for union in reversed(union_leaves):
        union_query_str = union_query(union, schemas1, schemas2)
        union_queries = sql_format(
            union_query_str,
            reindent=True,
            keyword_case="upper",
        )

    with open(expected_sql, "r", encoding="utf-8") as f:
        expected_sql = f.read()

    assert union_queries == expected_sql


@mark.parametrize(
    "query_file,expected_sql,schemas1,schemas2",
    [
        (
            "SQL_Constructor/operation_constructor/tests/queries/union/union_2_schemas.sparql",
            "SQL_Constructor/operation_constructor/tests/queries/union/union_2_schemas_delta.sql",
            [
                {Variable("x"), Variable("y")},
            ],
            [
                {Variable("x"), Variable("z")},
            ],
        ),
        (
            "SQL_Constructor/operation_constructor/tests/queries/union/union_3_schemas.sparql",
            "SQL_Constructor/operation_constructor/tests/queries/union/union_3_schemas_delta.sql",
            [
                {Variable("x"), Variable("z")},
                {Variable("y"), Variable("w")},
            ],
            [
                {Variable("x"), Variable("z")},
            ],
        ),
    ],
)
def test_delta_union_query(
    query_file: str,
    expected_sql: str,
    schemas1: list[set[str]],
    schemas2: list[set[str]],
) -> None:
    """Test if the delta_union_query function works correctly."""
    reset_seed()

    part = get_query_object(readQueryFile(query_file)).algebra

    union_leaves = all_type_leaves(part, "Union")

    union_queries: str = ""
    for union in reversed(union_leaves):
        union_query_str = delta_union_query(union, schemas1, schemas2)
        union_queries = sql_format(
            union_query_str,
            reindent=True,
            keyword_case="upper",
        )

    with open(expected_sql, "r", encoding="utf-8") as f:
        expected_sql = f.read()

    assert union_queries == expected_sql


def _drop_union_tables(
    duckdb_conn: DuckDBPyConnection,
    union_name_first: str,
    union_name_second: str = "",
) -> None:
    """Drops the union tables."""
    duckdb_conn.execute(f"DROP TABLE IF EXISTS {union_name_first};")
    duckdb_conn.execute(f"DROP TABLE IF EXISTS delta_{union_name_first};")
    if union_name_second != "":
        duckdb_conn.execute(f"DROP TABLE IF EXISTS {union_name_second};")
        duckdb_conn.execute(f"DROP TABLE IF EXISTS delta_{union_name_second};")


def _build_bgps(
    bgp_name_one: str,
    bgp_name_two: str,
    duckdb_conn: DuckDBPyConnection,
) -> None:
    """Builds the BGPs for the union query."""
    duckdb_conn.execute(
        f"CREATE OR REPLACE TABLE {bgp_name_one} (x TEXT, y TEXT, k_count INT);"
    )
    duckdb_conn.execute(
        f"INSERT INTO {bgp_name_one} (x, y, k_count) VALUES ('a', 'b', 1), ('b', 'a', 1), ('b', 'c', 1);"
    )

    duckdb_conn.execute(
        f"CREATE OR REPLACE TABLE {bgp_name_two} (y TEXT, z TEXT, k_count INT);"
    )
    duckdb_conn.execute(
        f"INSERT INTO {bgp_name_two} (y, z, k_count) VALUES ('a', 'b', 1), ('b', 'a', 1), ('b', 'c', 1);"
    )


def _build_overlap_bgps(
    bgp_name_one: str,
    bgp_name_two: str,
    duckdb_conn: DuckDBPyConnection,
) -> None:
    """Constructs the BPGS for the overlap query."""
    duckdb_conn.execute(
        f"CREATE OR REPLACE TABLE {bgp_name_one} (x TEXT, y TEXT, k_count INT);"
    )
    duckdb_conn.execute(
        f"INSERT INTO {bgp_name_one} (x, y, k_count) VALUES ('a', 'b', 1), ('b', 'a', 1), ('b', 'c', 1);"
    )

    duckdb_conn.execute(
        f"CREATE OR REPLACE TABLE {bgp_name_two} (y TEXT, x TEXT, k_count INT);"
    )
    duckdb_conn.execute(
        f"INSERT INTO {bgp_name_two} (y, x, k_count) VALUES ('a', 'b', 1), ('b', 'a', 1), ('b', 'c', 1);"
    )


@mark.parametrize(
    "query_file,expected_output_first,expected_output_second,schemas1,schemas2,bgp_name_one,bgp_name_two,union_name_first,union_name_second,database_name",
    [
        (
            "SQL_Constructor/operation_constructor/tests/queries/union/union_test_output.sparql",
            [("a", "b", 1), ("b", "a", 1), ("b", "c", 1)],
            [("a", "b", 1), ("b", "a", 1), ("b", "c", 1)],
            [
                {Variable("x"), Variable("y")},
            ],
            [
                {Variable("y"), Variable("z")},
            ],
            "BGP_8639977824181032562",
            "BGP_2618228559727801994",
            "Union_2528614756135159102_schema_4427885478980723971",
            "Union_2528614756135159102_schema_3025895693912107038",
            "database/union_test_output.db",
        )
    ],
)
def test_union_query_output_no_overlap(
    query_file: str,
    expected_output_first,
    expected_output_second,
    schemas1: list[set[str]],
    schemas2: list[set[str]],
    bgp_name_one: str,
    bgp_name_two: str,
    union_name_first: str,
    union_name_second: str,
    database_name: str,
) -> None:
    """Test if the union_query function works correctly."""
    reset_seed()

    part = get_query_object(readQueryFile(query_file)).algebra

    union_leaves = all_type_leaves(part, "Union")

    union_queries: str = ""
    for union in reversed(union_leaves):
        union_query_str = union_query(union, schemas1, schemas2)
        union_queries = sql_format(
            union_query_str,
            reindent=True,
            keyword_case="upper",
        )

    # Connect to the database
    duckdb_conn = connect(database_name)

    # Build the BGPs
    _build_bgps(bgp_name_one, bgp_name_two, duckdb_conn)

    # Drop the union tables
    _drop_union_tables(duckdb_conn, union_name_first, union_name_second)

    # Execute the query
    duckdb_conn.execute(union_queries)

    # Get the result
    result_first = duckdb_conn.execute(f"SELECT * FROM {union_name_first};").fetchall()

    # Get the second result
    result_second = duckdb_conn.execute(
        f"SELECT * FROM {union_name_second};"
    ).fetchall()

    assert result_first == expected_output_first
    assert result_second == expected_output_second


@mark.parametrize(
    "query_file,expected_output,schemas1,schemas2,bgp_name_one,bgp_name_two,union_name,database_name",
    [
        (
            "SQL_Constructor/operation_constructor/tests/queries/union/union_test_output_overlap.sparql",
            [
                ("a", "b", 2),
                ("b", "a", 2),
                ("b", "c", 1),
                ("c", "b", 1),
            ],
            [
                {Variable("x"), Variable("y")},
            ],
            [
                {Variable("y"), Variable("x")},
            ],
            "BGP_8639977824181032562",
            "BGP_6687709572126218303",
            "Union_1205960165662540522",
            "database/union_test_output_overlap.db",
        )
    ],
)
def test_union_query_output_overlap(
    query_file: str,
    expected_output: list[tuple[str, str, int]],
    schemas1: list[set[str]],
    schemas2: list[set[str]],
    bgp_name_one: str,
    bgp_name_two: str,
    union_name: str,
    database_name: str,
) -> None:
    """Test if the union_query function works correctly."""
    reset_seed()

    part = get_query_object(readQueryFile(query_file)).algebra

    union_leaves = all_type_leaves(part, "Union")

    union_queries: str = ""
    for union in reversed(union_leaves):
        union_query_str = union_query(union, schemas1, schemas2)
        union_queries = sql_format(
            union_query_str,
            reindent=True,
            keyword_case="upper",
        )

    # Connect to the database
    duckdb_conn = connect(database_name)

    # Build the BGPs
    _build_overlap_bgps(bgp_name_one, bgp_name_two, duckdb_conn)

    # Drop the union tables
    _drop_union_tables(duckdb_conn, union_name)

    # Execute the query
    duckdb_conn.execute(union_queries)

    # Get the result
    result = duckdb_conn.execute(f"SELECT * FROM {union_name};").fetchall()

    assert sorted(result) == sorted(expected_output)


def _build_delta_bgps(
    bgp_name_one: str,
    bgp_name_two: str,
    duckdb_conn: DuckDBPyConnection,
) -> None:
    """Constructs the BPGS for the overlap query."""
    duckdb_conn.execute(
        f"CREATE OR REPLACE TABLE delta_{bgp_name_one} (x TEXT, y TEXT, k_count INT);"
    )
    duckdb_conn.execute(
        f"INSERT INTO delta_{bgp_name_one} (x, y, k_count) VALUES ('b', 'a', -1), ('c', 'b', 1);"
    )

    duckdb_conn.execute(
        f"CREATE OR REPLACE TABLE delta_{bgp_name_two} (y TEXT, z TEXT, k_count INT);"
    )
    duckdb_conn.execute(
        f"INSERT INTO delta_{bgp_name_two} (y, z, k_count) VALUES ('b', 'a', -1), ('c', 'b', 1);"
    )

    duckdb_conn.execute(
        f"CREATE OR REPLACE TABLE nu_{bgp_name_one} (x TEXT, y TEXT, k_count INT);"
    )
    duckdb_conn.execute(
        f"INSERT INTO nu_{bgp_name_one} (x, y, k_count) VALUES ('a', 'b', 1), ('b', 'c', 1), ('c', 'b', 1);"
    )
    duckdb_conn.execute(
        f"CREATE OR REPLACE TABLE nu_{bgp_name_two} (y TEXT, z TEXT, k_count INT);"
    )
    duckdb_conn.execute(
        f"INSERT INTO nu_{bgp_name_two} (y, z, k_count) VALUES ('a', 'b', 1), ('b', 'c', 1), ('c', 'b', 1);"
    )


@mark.parametrize(
    "query_file,expected_output_first,expected_output_second,schemas1,schemas2,bgp_name_one,bgp_name_two,union_name_first,union_name_second,database_name",
    [
        (
            "SQL_Constructor/operation_constructor/tests/queries/union/union_test_output.sparql",
            [("b", "a", -1), ("c", "b", 1)],
            [("b", "a", -1), ("c", "b", 1)],
            [
                {Variable("x"), Variable("y")},
            ],
            [
                {Variable("y"), Variable("z")},
            ],
            "BGP_8639977824181032562",
            "BGP_2618228559727801994",
            "Union_2528614756135159102_schema_4427885478980723971",
            "Union_2528614756135159102_schema_3025895693912107038",
            "database/union_test_output.db",
        )
    ],
)
def test_union_query_output_delta(
    query_file: str,
    expected_output_first,
    expected_output_second,
    schemas1: list[set[str]],
    schemas2: list[set[str]],
    bgp_name_one: str,
    bgp_name_two: str,
    union_name_first: str,
    union_name_second: str,
    database_name: str,
) -> None:
    """Test if the union_query function works correctly."""
    reset_seed()

    part = get_query_object(readQueryFile(query_file)).algebra

    union_leaves = all_type_leaves(part, "Union")

    union_queries: str = ""
    for union in reversed(union_leaves):
        union_query_str = delta_union_query(union, schemas1, schemas2)
        union_queries = sql_format(
            union_query_str,
            reindent=True,
            keyword_case="upper",
        )

    # Connect to the database
    duckdb_conn = connect(database_name)

    # Build the BGPs
    _build_bgps(bgp_name_one, bgp_name_two, duckdb_conn)
    _build_delta_bgps(bgp_name_one, bgp_name_two, duckdb_conn)

    # Drop the union tables
    _drop_union_tables(duckdb_conn, union_name_first, union_name_second)

    # Execute the query
    duckdb_conn.execute(union_queries)

    # Get the result
    result_first = duckdb_conn.execute(
        f"SELECT * FROM delta_{union_name_first};"
    ).fetchall()

    # Get the second result
    result_second = duckdb_conn.execute(
        f"SELECT * FROM delta_{union_name_second};"
    ).fetchall()

    assert sorted(result_first) == sorted(expected_output_first)
    assert sorted(result_second) == sorted(expected_output_second)


def _build_overlap_delta_bgps(
    bgp_name_one: str,
    bgp_name_two: str,
    duckdb_conn: DuckDBPyConnection,
) -> None:
    """Constructs the BPGS for the overlap query."""
    duckdb_conn.execute(
        f"CREATE OR REPLACE TABLE delta_{bgp_name_one} (x TEXT, y TEXT, k_count INT);"
    )
    duckdb_conn.execute(
        f"INSERT INTO delta_{bgp_name_one} (x, y, k_count) VALUES ('b', 'a', -1), ('c', 'b', 1);"
    )

    duckdb_conn.execute(
        f"CREATE OR REPLACE TABLE delta_{bgp_name_two} (y TEXT, x TEXT, k_count INT);"
    )
    duckdb_conn.execute(
        f"INSERT INTO delta_{bgp_name_two} (y, x, k_count) VALUES ('b', 'a', -1), ('c', 'b', 1);"
    )

    duckdb_conn.execute(
        f"CREATE OR REPLACE TABLE nu_{bgp_name_one} (x TEXT, y TEXT, k_count INT);"
    )
    duckdb_conn.execute(
        f"INSERT INTO nu_{bgp_name_one} (x, y, k_count) VALUES ('a', 'b', 1), ('b', 'c', 1), ('c', 'b', 1);"
    )
    duckdb_conn.execute(
        f"CREATE OR REPLACE TABLE nu_{bgp_name_two} (y TEXT, x TEXT, k_count INT);"
    )
    duckdb_conn.execute(
        f"INSERT INTO nu_{bgp_name_two} (y, x, k_count) VALUES ('a', 'b', 1), ('b', 'c', 1), ('c', 'b', 1);"
    )


@mark.parametrize(
    "query_file,expected_output,schemas1,schemas2,bgp_name_one,bgp_name_two,union_name,database_name",
    [
        (
            "SQL_Constructor/operation_constructor/tests/queries/union/union_test_output_overlap.sparql",
            [
                ("b", "a", -1),
                ("a", "b", -1),
                ("c", "b", 1),
                ("b", "c", 1),
            ],
            [
                {Variable("x"), Variable("y")},
            ],
            [
                {Variable("y"), Variable("x")},
            ],
            "BGP_8639977824181032562",
            "BGP_6687709572126218303",
            "Union_1205960165662540522",
            "database/union_test_output_overlap.db",
        )
    ],
)
def test_union_query_output_overlap_delta(
    query_file: str,
    expected_output,
    schemas1: list[set[str]],
    schemas2: list[set[str]],
    bgp_name_one: str,
    bgp_name_two: str,
    union_name: str,
    database_name: str,
) -> None:
    """Test if the union_query function works correctly."""
    reset_seed()

    part = get_query_object(readQueryFile(query_file)).algebra

    union_leaves = all_type_leaves(part, "Union")

    union_queries: str = ""
    for union in reversed(union_leaves):
        union_query_str = delta_union_query(union, schemas1, schemas2)
        union_queries = sql_format(
            union_query_str,
            reindent=True,
            keyword_case="upper",
        )

    # Connect to the database
    duckdb_conn = connect(database_name)

    # Build the BGPs
    _build_overlap_bgps(bgp_name_one, bgp_name_two, duckdb_conn)
    _build_overlap_delta_bgps(bgp_name_one, bgp_name_two, duckdb_conn)

    # Drop the union tables
    _drop_union_tables(duckdb_conn, union_name)

    # Execute the query
    duckdb_conn.execute(union_queries)

    # Get the result
    result = duckdb_conn.execute(f"SELECT * FROM delta_{union_name};").fetchall()

    assert sorted(result) == sorted(expected_output)
