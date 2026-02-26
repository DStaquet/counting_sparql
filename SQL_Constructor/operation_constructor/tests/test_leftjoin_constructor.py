"""Tests for the left join query constructor in SQL_Constructor.
This module tests the functionality of generating left join queries
and delta left join queries, ensuring that the SQL generated matches
the expected output for various SPARQL queries."""

from rdflib.term import Variable
from sqlparse import format as sql_format
from pytest import mark
from duckdb import DuckDBPyConnection, connect

from SQL_Constructor.operation_constructor.leftjoin_constructor import (
    left_join_query,
    delta_left_join_query,
)
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
            "SQL_Constructor/operation_constructor/tests/queries/leftjoin/leftjoin_1_schema.sparql",
            "SQL_Constructor/operation_constructor/tests/queries/leftjoin/leftjoin_1_schema.sql",
            [{Variable("x")}],
            [{Variable("x"), Variable("y")}],
        ),
        (
            "SQL_Constructor/operation_constructor/tests/queries/leftjoin/leftjoin_2_schemas.sparql",
            "SQL_Constructor/operation_constructor/tests/queries/leftjoin/leftjoin_2_schemas.sql",
            [{Variable("x")}],
            [
                {Variable("x"), Variable("y")},
                {Variable("x"), Variable("w")},
            ],
        ),
    ],
)
def test_left_join_query(
    query_file: str,
    expected_sql: str,
    schemas1: list[set[str]],
    schemas2: list[set[str]],
) -> None:
    """Test if the left join query is correct."""
    reset_seed()

    # Read the query file
    part = get_query_object(readQueryFile(query_file)).algebra

    leftjoin_leaves = all_type_leaves(part, "LeftJoin")

    leftjoin_query: str | None = None

    for leftjoin_leaf in reversed(leftjoin_leaves):
        leftjoin_query = sql_format(
            left_join_query(leftjoin_leaf, schemas1, schemas2),
            reindent=True,
            keyword_case="upper",
        )

    with open(expected_sql, encoding="utf-8") as f:
        expected_sql = f.read()

    if leftjoin_query is None:
        raise ValueError("Left join query was not correctly generated.")

    assert leftjoin_query == expected_sql


@mark.parametrize(
    "query_file,expected_sql,expected_sql_join,schemas1,schemas2",
    [
        (
            "SQL_Constructor/operation_constructor/tests/queries/leftjoin/leftjoin_1_schema.sparql",
            "SQL_Constructor/operation_constructor/tests/queries/leftjoin/leftjoin_1_schema_delta.sql",
            "SQL_Constructor/operation_constructor/tests/queries/leftjoin/leftjoin_1_schema_join.sql",
            [{Variable("x")}],
            [{Variable("x"), Variable("y")}],
        ),
        (
            "SQL_Constructor/operation_constructor/tests/queries/leftjoin/leftjoin_2_schemas.sparql",
            "SQL_Constructor/operation_constructor/tests/queries/leftjoin/leftjoin_2_schemas_delta.sql",
            "SQL_Constructor/operation_constructor/tests/queries/leftjoin/leftjoin_2_schemas_delta_join.sql",
            [{Variable("x")}],
            [
                {Variable("x"), Variable("y")},
                {Variable("x"), Variable("w")},
            ],
        ),
        (
            "SQL_Constructor/operation_constructor/tests/queries/leftjoin/leftjoin_1_schema_no_overlap.sparql",
            "SQL_Constructor/operation_constructor/tests/queries/leftjoin/leftjoin_1_schema_no_overlap_delta.sql",
            "SQL_Constructor/operation_constructor/tests/queries/leftjoin/leftjoin_1_schema_no_overlap_join.sql",
            [{Variable("x")}],
            [{Variable("y")}],
        ),
    ],
)
def test_delta_left_join_query(
    query_file: str,
    expected_sql: str,
    expected_sql_join: str,
    schemas1: list[set[str]],
    schemas2: list[set[str]],
) -> None:
    """Test if the delta left join query is correct."""
    reset_seed()

    # Read the query file
    part = get_query_object(readQueryFile(query_file)).algebra

    leftjoin_leaves = all_type_leaves(part, "LeftJoin")

    delta_leftjoin_query: str | None = None
    delta_leftjoin_join_query: str | None = None

    for leftjoin_leaf in reversed(leftjoin_leaves):
        delta_leftjoin_tuple = delta_left_join_query(leftjoin_leaf, schemas1, schemas2)
        delta_leftjoin_query = sql_format(
            delta_leftjoin_tuple[0],
            reindent=True,
            keyword_case="upper",
        )
        delta_leftjoin_join_query = sql_format(
            delta_leftjoin_tuple[1],
            reindent=True,
            keyword_case="upper",
        )

    if delta_leftjoin_query is None or delta_leftjoin_join_query is None:
        raise ValueError("Left join query was not correctly generated.")

    with open(expected_sql, encoding="utf-8") as f:
        expected = f.read()

    assert delta_leftjoin_query == expected

    with open(expected_sql_join, encoding="utf-8") as f:
        expected_join = f.read()

    assert delta_leftjoin_join_query == expected_join


def _drop_leftjoin_tables(
    duckdb_conn: DuckDBPyConnection,
    leftjoin_name: str,
) -> None:
    """Drops the left join tables."""
    duckdb_conn.execute(f"DROP TABLE IF EXISTS {leftjoin_name};")
    duckdb_conn.execute(f"DROP TABLE IF EXISTS delta_{leftjoin_name};")


def _build_no_overlap_bgps(
    bgp_one_name: str,
    bgp_two_name: str,
    duckdb_conn: DuckDBPyConnection,
) -> None:
    """Builds the BGP tables for the no overlap test case"""
    duckdb_conn.execute(
        f"CREATE OR REPLACE TABLE {bgp_one_name} (x TEXT, k_count INT);"
    )
    duckdb_conn.execute(
        f"CREATE OR REPLACE TABLE {bgp_two_name} (y TEXT, k_count INT);"
    )

    # Insert data into the tables
    duckdb_conn.execute(f"INSERT INTO {bgp_one_name} VALUES ('b', 1), ('d', 1);")
    duckdb_conn.execute(f"INSERT INTO {bgp_two_name} VALUES ('c', 1);")


def _build_one_overlap_bgps(
    bgp_one_name: str,
    bgp_two_name: str,
    bgp_three_name: str,
    duckdb_conn: DuckDBPyConnection,
) -> None:
    """Builds the BGP tables for the one overlap test case"""
    duckdb_conn.execute(
        f"CREATE OR REPLACE TABLE {bgp_one_name} (x TEXT, k_count INT);"
    )
    duckdb_conn.execute(
        f"CREATE OR REPLACE TABLE {bgp_two_name} (y TEXT, k_count INT);"
    )
    duckdb_conn.execute(
        f"CREATE OR REPLACE TABLE {bgp_three_name} (x TEXT, y TEXT, k_count INT);"
    )

    # Insert data into the tables
    duckdb_conn.execute(f"INSERT INTO {bgp_one_name} VALUES ('b', 1), ('d', 1);")
    duckdb_conn.execute(f"INSERT INTO {bgp_two_name} VALUES ('c', 1);")
    duckdb_conn.execute(f"INSERT INTO {bgp_three_name} VALUES ('b', 'd', 1);")


def _build_bgps(
    bgp_one_name: str,
    bgp_two_name: str,
    duckdb_conn: DuckDBPyConnection,
) -> None:
    """Builds the BGP tables"""
    duckdb_conn.execute(
        f"CREATE OR REPLACE TABLE {bgp_one_name} (x TEXT, y TEXT, k_count INT);"
    )
    duckdb_conn.execute(
        f"CREATE OR REPLACE TABLE {bgp_two_name} (y TEXT, z TEXT, k_count INT);"
    )

    # Insert data into the tables
    duckdb_conn.execute(
        f"INSERT INTO {bgp_one_name} VALUES ('a', 'b', 1), ('a', 'd', 1);"
    )
    duckdb_conn.execute(f"INSERT INTO {bgp_two_name} VALUES ('b', 'c', 1);")


@mark.parametrize(
    "query_file,expected_output_joined,expected_output_not_joined,schemas1,schemas2,bgp_one_name,bgp_two_name,leftjoin_name_joined,leftjoin_name_not_joined,database_name",
    [
        (
            "SQL_Constructor/operation_constructor/tests/queries/leftjoin/leftjoin_test_output.sparql",
            [("a", "b", "c", 1)],
            [("a", "d", 1)],
            [{Variable("x"), Variable("y")}],
            [{Variable("y"), Variable("z")}],
            "BGP_8639977824181032562",
            "BGP_2618228559727801994",
            "LeftJoin_2528614756135159102_schema_3217831642713536503",
            "LeftJoin_2528614756135159102_schema_4427885478980723971",
            "database/leftjoin_test_output.db",
        ),
    ],
)
def test_leftjoin_query_output(
    query_file: str,
    expected_output_joined: list[tuple[str, str, str, int]],
    expected_output_not_joined: list[tuple[str, str, int]],
    schemas1: list[set[str]],
    schemas2: list[set[str]],
    bgp_one_name: str,
    bgp_two_name: str,
    leftjoin_name_joined: str,
    leftjoin_name_not_joined: str,
    database_name: str,
) -> None:
    """Tests if the output of the left join query is correct."""
    reset_seed()

    # Read the query file
    part = get_query_object(readQueryFile(query_file)).algebra

    leftjoin_leaves = all_type_leaves(part, "LeftJoin")

    for leftjoin_leaf in reversed(leftjoin_leaves):
        leftjoin_query: str = sql_format(
            left_join_query(leftjoin_leaf, schemas1, schemas2),
            reindent=True,
            keyword_case="upper",
        )

    # Execute the query
    duckdb_conn: DuckDBPyConnection = connect(database_name)

    # Create the tables
    _build_bgps(bgp_one_name, bgp_two_name, duckdb_conn)

    for leftjoin_table_name in [
        leftjoin_name_joined,
        leftjoin_name_not_joined,
    ]:
        _drop_leftjoin_tables(duckdb_conn, leftjoin_table_name)
    duckdb_conn.execute(leftjoin_query)

    # Check if the joined output is correct
    result = duckdb_conn.execute(f"SELECT * FROM {leftjoin_name_joined};").fetchall()
    assert result == expected_output_joined

    # Check if the not joined output is correct
    result = duckdb_conn.execute(
        f"SELECT * FROM {leftjoin_name_not_joined};"
    ).fetchall()
    assert result == expected_output_not_joined


def _build_delta_bgps(
    bgp_one_name: str,
    bgp_two_name: str,
    duckdb_conn: DuckDBPyConnection,
) -> None:
    """constructs the delta bgp tables"""
    duckdb_conn.execute(
        f"CREATE OR REPLACE TABLE delta_{bgp_one_name} (x TEXT, y TEXT, k_count INT);"
    )
    duckdb_conn.execute(
        f"CREATE OR REPLACE TABLE delta_{bgp_two_name} (y TEXT, z TEXT, k_count INT);"
    )

    # Insert data into the tables
    duckdb_conn.execute(
        f"INSERT INTO delta_{bgp_one_name} VALUES ('a', 'b', -1), ('d', 'b', 1);"
    )
    duckdb_conn.execute(
        f"INSERT INTO delta_{bgp_two_name} VALUES ('b', 'c', -1),('d', 'c', 1);"
    )

    # Construct the nu tables
    duckdb_conn.execute(
        f"CREATE OR REPLACE TABLE nu_{bgp_one_name} (x TEXT, y TEXT, k_count INT);"
    )
    duckdb_conn.execute(
        f"CREATE OR REPLACE TABLE nu_{bgp_two_name} (y TEXT, z TEXT, k_count INT);"
    )
    # Insert data into the tables
    duckdb_conn.execute(
        f"INSERT INTO nu_{bgp_one_name} VALUES ('a', 'd', 1), ('d', 'b', 1);"
    )
    duckdb_conn.execute(f"INSERT INTO nu_{bgp_two_name} VALUES ('d', 'c', 1);")


def _build_no_overlap_delta_bgps(
    bgp_one_name: str,
    bgp_two_name: str,
    duckdb_conn: DuckDBPyConnection,
) -> None:
    """Builds the delta BGPs for the no overlap test case."""
    duckdb_conn.execute(
        f"CREATE OR REPLACE TABLE delta_{bgp_one_name} (x TEXT, k_count INT);"
    )
    duckdb_conn.execute(
        f"CREATE OR REPLACE TABLE delta_{bgp_two_name} (y TEXT, k_count INT);"
    )

    # Insert data into the tables
    duckdb_conn.execute(f"INSERT INTO delta_{bgp_one_name} VALUES ('d', -1), ('e', 1);")
    duckdb_conn.execute(f"INSERT INTO delta_{bgp_two_name} VALUES ('c', -1), ('f', 1);")

    # Construct the nu tables
    duckdb_conn.execute(
        f"CREATE OR REPLACE TABLE nu_{bgp_one_name} (x TEXT, k_count INT);"
    )
    duckdb_conn.execute(
        f"CREATE OR REPLACE TABLE nu_{bgp_two_name} (y TEXT, k_count INT);"
    )

    # Insert data into the tables
    duckdb_conn.execute(f"INSERT INTO nu_{bgp_one_name} VALUES ('b', 1), ('e', 1);")
    duckdb_conn.execute(f"INSERT INTO nu_{bgp_two_name} VALUES ('f', 1);")


def _build_once_overlap_delta_bgps(
    bgp_one_name: str,
    bgp_two_name: str,
    bgp_three_name: str,
    duckdb_conn: DuckDBPyConnection,
) -> None:
    """Builds the delta BGPs for the one overlap test case."""
    duckdb_conn.execute(
        f"CREATE OR REPLACE TABLE delta_{bgp_one_name} (x TEXT, k_count INT);"
    )
    duckdb_conn.execute(
        f"CREATE OR REPLACE TABLE delta_{bgp_two_name} (y TEXT, k_count INT);"
    )
    duckdb_conn.execute(
        f"CREATE OR REPLACE TABLE delta_{bgp_three_name} (x TEXT, y TEXT, k_count INT);"
    )

    # Insert data into the tables
    duckdb_conn.execute(f"INSERT INTO delta_{bgp_one_name} VALUES ('b', -1);")
    duckdb_conn.execute(f"INSERT INTO delta_{bgp_two_name} VALUES ('c', -1), ('f', 1);")
    duckdb_conn.execute(
        f"INSERT INTO delta_{bgp_three_name} VALUES ('b', 'd', -1), ('b', 'c', 1);"
    )

    # Construct the nu tables
    duckdb_conn.execute(
        f"CREATE OR REPLACE TABLE nu_{bgp_one_name} (x TEXT, k_count INT);"
    )
    duckdb_conn.execute(
        f"CREATE OR REPLACE TABLE nu_{bgp_two_name} (y TEXT, k_count INT);"
    )
    duckdb_conn.execute(
        f"CREATE OR REPLACE TABLE nu_{bgp_three_name} (x TEXT, y TEXT, k_count INT);"
    )

    # Insert data into the tables
    duckdb_conn.execute(f"INSERT INTO nu_{bgp_one_name} VALUES ('d', 1);")
    duckdb_conn.execute(f"INSERT INTO nu_{bgp_two_name} VALUES ('f', 1);")
    duckdb_conn.execute(f"INSERT INTO nu_{bgp_three_name} VALUES ('b', 'c', 1)")


@mark.parametrize(
    "query_file,expected_output_joined,expected_output_not_joined,schemas1,schemas2,bgp_one_name,bgp_two_name,leftjoin_name_joined,leftjoin_name_not_joined,database_name",
    [
        (
            "SQL_Constructor/operation_constructor/tests/queries/leftjoin/leftjoin_test_output.sparql",
            [("a", "d", "c", 1), ("a", "b", "c", -1)],
            [("a", "d", -1), ("d", "b", 1)],
            [{Variable("x"), Variable("y")}],
            [{Variable("y"), Variable("z")}],
            "BGP_8639977824181032562",
            "BGP_2618228559727801994",
            "LeftJoin_2528614756135159102_schema_3217831642713536503",
            "LeftJoin_2528614756135159102_schema_4427885478980723971",
            "database/leftjoin_test_output.db",
        )
    ],
)
def test_leftjoin_query_output_delta(
    query_file: str,
    expected_output_joined: list[tuple[str, str, str, int]],
    expected_output_not_joined: list[tuple[str, str, int]],
    schemas1: list[set[str]],
    schemas2: list[set[str]],
    bgp_one_name: str,
    bgp_two_name: str,
    leftjoin_name_joined: str,
    leftjoin_name_not_joined: str,
    database_name: str,
) -> None:
    """Tests if the output of the left join query is correct."""
    reset_seed()

    # Read the query file
    part = get_query_object(readQueryFile(query_file)).algebra

    leftjoin_leaves = all_type_leaves(part, "LeftJoin")

    for leftjoin_leaf in reversed(leftjoin_leaves):
        delta_leftjoin_tuple = delta_left_join_query(leftjoin_leaf, schemas1, schemas2)
        delta_leftjoin_query: str = sql_format(
            delta_leftjoin_tuple[0],
            reindent=True,
            keyword_case="upper",
        )
        delta_leftjoin_join_query: str = sql_format(
            delta_leftjoin_tuple[1],
            reindent=True,
            keyword_case="upper",
        )

    # Execute the query
    duckdb_conn: DuckDBPyConnection = connect(database_name)

    # Create the tables
    _build_bgps(bgp_one_name, bgp_two_name, duckdb_conn)
    _build_delta_bgps(bgp_one_name, bgp_two_name, duckdb_conn)

    for method in [
        delta_leftjoin_query,
        delta_leftjoin_join_query,
    ]:
        for leftjoin_table_name in [
            leftjoin_name_joined,
            leftjoin_name_not_joined,
        ]:
            _drop_leftjoin_tables(duckdb_conn, leftjoin_table_name)
        duckdb_conn.execute(method)

        # Check if the joined output is correct
        result = duckdb_conn.execute(
            f"SELECT x, y, z, k_count FROM delta_{leftjoin_name_joined};"
        ).fetchall()
        assert sorted(result) == sorted(expected_output_joined)

        # Check if the not joined output is correct
        result = duckdb_conn.execute(
            f"SELECT x, y, k_count FROM delta_{leftjoin_name_not_joined};"
        ).fetchall()
        assert sorted(result) == sorted(expected_output_not_joined)


@mark.parametrize(
    "query_file,expected_output_joined,schemas1,schemas2,bgp_one_name,bgp_two_name,leftjoin_name_joined,leftjoin_name_not_joined,database_name",
    [
        (
            "SQL_Constructor/operation_constructor/tests/queries/leftjoin/leftjoin_1_schema_no_overlap.sparql",
            [
                ("b", "c", -1),
                ("d", "c", -1),
                ("b", "f", 1),
                ("e", "f", 1),
            ],
            [{Variable("x")}],
            [{Variable("y")}],
            "BGP_2378230508219361412",
            "BGP_5735499650974426227",
            "LeftJoin_272100257129553905",
            "LeftJoin_272100257129553905_schema_5974201903695169563",
            "database/leftjoin_test_output_no_overlap.db",
        ),
    ],
)
def test_leftjoin_query_output_delta_no_overlap(
    query_file: str,
    expected_output_joined: list[tuple[str, str, int]],
    schemas1: list[set[str]],
    schemas2: list[set[str]],
    bgp_one_name: str,
    bgp_two_name: str,
    leftjoin_name_joined: str,
    leftjoin_name_not_joined: str,
    database_name: str,
) -> None:
    """Test the output of the delta left join query with no overlap."""
    reset_seed()

    # Read the query file
    part = get_query_object(readQueryFile(query_file)).algebra

    leftjoin_leaves = all_type_leaves(part, "LeftJoin")

    delta_leftjoin_query: str | None = None
    delta_leftjoin_join_query: str | None = None

    for leftjoin_leaf in reversed(leftjoin_leaves):
        delta_leftjoin_tuple = delta_left_join_query(leftjoin_leaf, schemas1, schemas2)
        delta_leftjoin_query = sql_format(
            delta_leftjoin_tuple[0],
            reindent=True,
            keyword_case="upper",
        )
        delta_leftjoin_join_query = sql_format(
            delta_leftjoin_tuple[1],
            reindent=True,
            keyword_case="upper",
        )

    # Execute the query
    duckdb_conn: DuckDBPyConnection = connect(database_name)

    _build_no_overlap_bgps(bgp_one_name, bgp_two_name, duckdb_conn)
    _build_no_overlap_delta_bgps(bgp_one_name, bgp_two_name, duckdb_conn)

    if delta_leftjoin_query is None or delta_leftjoin_join_query is None:
        raise ValueError("Left join query was not correctly generated.")

    for method in [
        delta_leftjoin_query,
        delta_leftjoin_join_query,
    ]:
        for leftjoin_table_name in [
            leftjoin_name_joined,
            leftjoin_name_not_joined,
        ]:
            _drop_leftjoin_tables(duckdb_conn, leftjoin_table_name)
        duckdb_conn.execute(method)

        # Check if the joined output is correct
        result = duckdb_conn.execute(
            f"SELECT x, y, k_count FROM delta_{leftjoin_name_joined};"
        ).fetchall()
        assert sorted(result) == sorted(expected_output_joined)


@mark.parametrize(
    "query_file,expected_output_joined,expected_output_not_joined,schemas1,schemas2,bgp_one_name,bgp_two_name,bgp_three_name,leftjoin_name_joined,leftjoin_name_not_joined,database_name",
    [
        (
            "SQL_Constructor/operation_constructor/tests/queries/leftjoin/leftjoin_2_schema_no_overlap_once.sparql",
            [
                ("b", "c", -1),
                ("d", "c", -1),
                ("b", "d", -1),
                ("d", "f", 1),
            ],
            [],
            [{Variable("x")}],
            [
                {Variable("y")},
                {Variable("x"), Variable("y")},
            ],
            "BGP_2378230508219361412",
            "Union_1726670103683628374_schema_1432398095755278489",
            "Union_1726670103683628374_schema_4427885478980723971",
            "LeftJoin_1831412240124524561_schema_4427885478980723971",
            "LeftJoin_1831412240124524561_schema_8057865995004935963",
            "database/leftjoin_test_output_once_overlap.db",
        ),
    ],
)
def test_leftjoin_query_output_delta_no_overlap_once(
    query_file: str,
    expected_output_joined: list[tuple[str, str, int]],
    expected_output_not_joined: list[tuple[str, int]],
    schemas1: list[set[str]],
    schemas2: list[set[str]],
    bgp_one_name: str,
    bgp_two_name: str,
    bgp_three_name: str,
    leftjoin_name_joined: str,
    leftjoin_name_not_joined: str,
    database_name: str,
) -> None:
    """Test the output of the delta left join query with no overlap."""
    reset_seed()

    # Read the query file
    part = get_query_object(readQueryFile(query_file)).algebra

    leftjoin_leaves = all_type_leaves(part, "LeftJoin")

    delta_leftjoin_query: str | None = None
    delta_leftjoin_join_query: str | None = None

    for leftjoin_leaf in reversed(leftjoin_leaves):
        delta_leftjoin_tuple = delta_left_join_query(leftjoin_leaf, schemas1, schemas2)
        delta_leftjoin_query = sql_format(
            delta_leftjoin_tuple[0],
            reindent=True,
            keyword_case="upper",
        )
        delta_leftjoin_join_query = sql_format(
            delta_leftjoin_tuple[1],
            reindent=True,
            keyword_case="upper",
        )

    # Execute the query
    duckdb_conn: DuckDBPyConnection = connect(database_name)

    _build_one_overlap_bgps(
        bgp_one_name,
        bgp_two_name,
        bgp_three_name,
        duckdb_conn,
    )
    _build_once_overlap_delta_bgps(
        bgp_one_name,
        bgp_two_name,
        bgp_three_name,
        duckdb_conn,
    )

    if delta_leftjoin_query is None or delta_leftjoin_join_query is None:
        raise ValueError("Left join query was not correctly generated.")

    for method in [
        delta_leftjoin_query,
        delta_leftjoin_join_query,
    ]:
        for leftjoin_table_name in [
            leftjoin_name_joined,
            leftjoin_name_not_joined,
        ]:
            _drop_leftjoin_tables(duckdb_conn, leftjoin_table_name)
        duckdb_conn.execute(method)

        # Check if the joined output is correct
        result = duckdb_conn.execute(
            f"SELECT x, y, k_count FROM delta_{leftjoin_name_joined};"
        ).fetchall()
        assert sorted(result) == sorted(expected_output_joined)

        # Check if the not joined output is correct
        result = duckdb_conn.execute(
            f"SELECT x, k_count FROM delta_{leftjoin_name_not_joined};"
        ).fetchall()
        assert sorted(result) == sorted(expected_output_not_joined)
