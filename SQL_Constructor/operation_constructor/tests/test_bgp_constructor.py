from SQL_Constructor.operation_constructor.bgp_constructor import (
    bgp_table_query,
    delta_bgp_queries,
)
from incremental_query_parser import (
    readQueryFile,
    get_query_object,
)
from SQL_Constructor.base_constructor import (
    create_table_w_select,
    get_table_name,
)
from SQL_Constructor.operation_constructor.tests.base_functions import (
    all_type_leaves,
    reset_seed,
)

from pytest import mark

from rdflib.plugins.sparql.parserutils import CompValue

from sqlparse import format

from duckdb import DuckDBPyConnection, connect


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

        bgp_queries += format(
            create_table_w_select(
                get_table_name(bgp), current_query
            ),
            reindent=True,
        )

    with open(expected_sql) as f:
        expected_query = f.read()

    assert bgp_queries == expected_query


def __constructBaseGraph(
    duckdb_conn: DuckDBPyConnection,
) -> None:
    """Constructs the G graph table in the database."""
    duckdb_conn.execute(
        "CREATE OR REPLACE TABLE G (s TEXT, p TEXT, o TEXT, k_count INT);"
    )
    duckdb_conn.execute(
        "INSERT INTO G (s, p, o, k_count) VALUES ('a', 'http://example.org/r', 'b', 1), ('a', 'http://example.org/r', 'd', 1), ('b', 'http://example.org/r', 'c', 1), ('d', 'http://example.org/r', 'c', 1), ('c', 'http://example.org/r', 'e', 1);"
    )


def __dropBGPTables(
    bgp_name: str, duckdb_conn: DuckDBPyConnection
) -> None:
    """Drops the tables created by the BGP query."""
    duckdb_conn.execute(f"DROP TABLE IF EXISTS {bgp_name};")
    duckdb_conn.execute(
        f"DROP TABLE IF EXISTS delta_{bgp_name};"
    )


def __constructDeltaBaseGraph(
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
        curr_bgp_query = format(
            create_table_w_select(
                get_table_name(bgp), current_query
            ),
            reindent=True,
        )

        with connect(database) as con:
            __constructBaseGraph(con)

            __dropBGPTables(get_table_name(bgp), con)
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
            __constructBaseGraph(con)
            __constructDeltaBaseGraph(con)

            __dropBGPTables(get_table_name(bgp), con)
            con.execute(current_query)

            result = con.execute(
                f"SELECT * FROM delta_{get_table_name(bgp)}"
            ).fetchall()

        assert result == expected_output
