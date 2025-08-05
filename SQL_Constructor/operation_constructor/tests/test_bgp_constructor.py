"""Modules to import"""

from pytest import mark

from rdflib.plugins.sparql.parserutils import CompValue

from sqlparse import format as sql_format

from duckdb import DuckDBPyConnection, connect

from SQL_Constructor.operation_constructor.bgp_constructor import (
    bgp_table_query,
    delta_bgp_queries,
)
from SQL_Constructor.operation_constructor.tests.base_functions import (
    all_type_leaves,
    reset_seed,
)
from SQL_Constructor.table_constructor import (
    get_table_name,
    create_table_w_select,
)
from build_data import readQueryFile, get_query_object


@mark.parametrize(
    "query_file,expected_sql",
    [
        (
            "SQL_Constructor/operation_constructor/tests/queries/bgp/bgp_test_1_pattern.sparql",
            "SQL_Constructor/operation_constructor/tests/queries/bgp/bgp_test_1_pattern.sql",
        ),
        (
            "SQL_Constructor/operation_constructor/tests/queries/bgp/bgp_test_2_pattern.sparql",
            "SQL_Constructor/operation_constructor/tests/queries/bgp/bgp_test_2_pattern.sql",
        ),
        (
            "SQL_Constructor/operation_constructor/tests/queries/bgp/bgp_test_3_pattern.sparql",
            "SQL_Constructor/operation_constructor/tests/queries/bgp/bgp_test_3_pattern.sql",
        ),
    ],
)
def test_bgp_table_query(
    query_file: str, expected_sql: str
):
    """Tests the bgp_table_query function."""
    reset_seed()

    part = get_query_object(
        readQueryFile(query_file)
    ).algebra

    # Find only BGP patterns
    bgp_leaves: list[CompValue] = all_type_leaves(
        part, "BGP"
    )

    bgp_queries: str = ""
    for bgp in reversed(bgp_leaves):
        current_query, _ = bgp_table_query(bgp)

        bgp_queries += sql_format(
            create_table_w_select(
                get_table_name(bgp), current_query
            ),
            reindent=True,
        )

    with open(expected_sql, encoding="utf-8") as f:
        expected_query = f.read()

    assert bgp_queries == expected_query


@mark.parametrize(
    "query_file,expected_sql,expected_join_sql",
    [
        (
            "SQL_Constructor/operation_constructor/tests/queries/bgp/bgp_test_1_pattern.sparql",
            "SQL_Constructor/operation_constructor/tests/queries/bgp/bgp_test_1_pattern_delta.sql",
            "SQL_Constructor/operation_constructor/tests/queries/bgp/bgp_test_1_pattern_delta_join.sql",
        ),
        (
            "SQL_Constructor/operation_constructor/tests/queries/bgp/bgp_test_2_pattern.sparql",
            "SQL_Constructor/operation_constructor/tests/queries/bgp/bgp_test_2_pattern_delta.sql",
            "SQL_Constructor/operation_constructor/tests/queries/bgp/bgp_test_2_pattern_delta_join.sql",
        ),
        (
            "SQL_Constructor/operation_constructor/tests/queries/bgp/bgp_test_3_pattern.sparql",
            "SQL_Constructor/operation_constructor/tests/queries/bgp/bgp_test_3_pattern_delta.sql",
            "SQL_Constructor/operation_constructor/tests/queries/bgp/bgp_test_3_pattern_delta_join.sql",
        ),
    ],
)
def test_bgp_table_delta_query(
    query_file: str,
    expected_sql: str,
    expected_join_sql: str,
) -> None:
    """Tests the delta_bgp_queries function."""
    reset_seed()

    part = get_query_object(
        readQueryFile(query_file)
    ).algebra

    # Find only BGP patterns
    bgp_leaves: list[CompValue] = all_type_leaves(
        part, "BGP"
    )

    bgp_queries: str = ""
    bgp_join_queries: str = ""
    for bgp in reversed(bgp_leaves):
        current_query, current_join_query = (
            delta_bgp_queries(bgp)
        )

        bgp_queries += sql_format(
            current_query,
            reindent=True,
            keyword_case="upper",
        )

        bgp_join_queries += sql_format(
            current_join_query,
            reindent=True,
        )

    with open(expected_sql, encoding="utf-8") as f:
        expected_query = f.read()

    assert bgp_queries == expected_query

    with open(expected_join_sql, encoding="utf-8") as f:
        expected_join_query = f.read()

    assert bgp_join_queries == expected_join_query


def _construct_base_graph(
    duckdb_conn: DuckDBPyConnection,
) -> None:
    """Constructs the G graph table in the database."""
    duckdb_conn.execute(
        "CREATE OR REPLACE TABLE G (s TEXT, p TEXT, o TEXT, k_count INT);"
    )
    duckdb_conn.execute(
        "INSERT INTO G (s, p, o, k_count) VALUES ('a', 'http://example.org/r', 'b', 1), ('a', 'http://example.org/r', 'd', 1), ('b', 'http://example.org/r', 'c', 1), ('d', 'http://example.org/r', 'c', 1), ('c', 'http://example.org/r', 'e', 1);"
    )


def _drop_bgp_tables(
    bgp_name: str, duckdb_conn: DuckDBPyConnection
) -> None:
    """Drops the tables created by the BGP query."""
    duckdb_conn.execute(f"DROP TABLE IF EXISTS {bgp_name};")
    duckdb_conn.execute(
        f"DROP TABLE IF EXISTS delta_{bgp_name};"
    )


def _construct_delta_base_graph(
    duckdb_conn: DuckDBPyConnection,
) -> None:
    """Constructs the delta_G graph table in the database."""
    duckdb_conn.execute(
        "CREATE OR REPLACE TABLE delta_G (s TEXT, p TEXT, o TEXT, k_count INT);"
    )
    duckdb_conn.execute(
        "INSERT INTO Delta_G (s, p, o, k_count) VALUES ('a', 'http://example.org/r', 'b', -1), ('b', 'http://example.org/r', 'd', 1);"
    )

    duckdb_conn.execute(
        "CREATE OR REPLACE TABLE nu_G (s TEXT, p TEXT, o TEXT, k_count INT);"
    )
    duckdb_conn.execute(
        "INSERT INTO nu_G (s, p, o, k_count) VALUES ('a', 'http://example.org/r', 'd', 1), ('b', 'http://example.org/r', 'c', 1), ('b', 'http://example.org/r', 'd', 1), ('d', 'http://example.org/r', 'c', 1), ('c', 'http://example.org/r', 'e', 1);"
    )


@mark.parametrize(
    "query_file,expected_output,database",
    [
        (
            "SQL_Constructor/operation_constructor/tests/queries/bgp/bgp_test_output.sparql",
            [
                ("a", "d", "c", "e", 1),
                ("a", "b", "c", "e", 1),
            ],
            "database/bgp_test.db",
        )
    ],
)
def test_bgp_query_output(
    query_file: str,
    expected_output,
    database: str,
) -> None:
    """Checks if the output of a BGP query is as expected."""
    reset_seed()

    part = get_query_object(
        readQueryFile(query_file)
    ).algebra

    # Find only BGP patterns
    bgp_leaves: list[CompValue] = all_type_leaves(
        part, "BGP"
    )

    for bgp in bgp_leaves:
        current_query, _ = bgp_table_query(bgp)
        curr_bgp_query = sql_format(
            create_table_w_select(
                get_table_name(bgp), current_query
            ),
            reindent=True,
        )

        with connect(database) as con:
            _construct_base_graph(con)

            _drop_bgp_tables(get_table_name(bgp), con)
            con.execute(curr_bgp_query)

            result = con.execute(
                f"SELECT * FROM {get_table_name(bgp)}"
            ).fetchall()

        assert result == expected_output


@mark.parametrize(
    "query_file,expected_output,database",
    [
        (
            "SQL_Constructor/operation_constructor/tests/queries/bgp/bgp_test_output.sparql",
            [
                ("a", "b", "c", "e", -1),
                ("b", "d", "c", "e", 1),
            ],
            "database/bgp_test.db",
        )
    ],
)
def test_bgp_query_output_delta(
    query_file: str,
    expected_output,
    database: str,
) -> None:
    """Checks if the delta output of a BGP query is as expected."""
    reset_seed()

    part = get_query_object(
        readQueryFile(query_file)
    ).algebra

    # Find only BGP patterns
    bgp_leaves: list[CompValue] = all_type_leaves(
        part, "BGP"
    )

    for bgp in bgp_leaves:
        current_query, _ = delta_bgp_queries(bgp)

        with connect(database) as con:
            _construct_base_graph(con)
            _construct_delta_base_graph(con)

            _drop_bgp_tables(get_table_name(bgp), con)
            con.execute(current_query)

            result = con.execute(
                f"SELECT * FROM delta_{get_table_name(bgp)}"
            ).fetchall()

        assert result == expected_output
