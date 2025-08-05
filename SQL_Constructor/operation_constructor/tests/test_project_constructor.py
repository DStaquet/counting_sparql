"""Test cases for the project query and delta project query functions in the SQL Constructor module.
These tests ensure that the project queries are generated correctly and that they produce the
expected SQL output.
"""

from pytest import mark
from rdflib.term import Variable
from sqlparse import format as sql_format
from duckdb import DuckDBPyConnection, connect

from SQL_Constructor.operation_constructor.project_constructor import (
    project_query,
    delta_project_query,
)
from SQL_Constructor.operation_constructor.tests.base_functions import (
    reset_seed,
    all_type_leaves,
)
from build_data import readQueryFile, get_query_object


@mark.parametrize(
    "query_file,expected_sql,schemas",
    [
        (
            "SQL_Constructor/operation_constructor/tests/queries/projection/project_1_schema.sparql",
            "SQL_Constructor/operation_constructor/tests/queries/projection/project_1_schema.sql",
            [{Variable("x"), Variable("y")}],
        ),
        (
            "SQL_Constructor/operation_constructor/tests/queries/projection/project_2_schema.sparql",
            "SQL_Constructor/operation_constructor/tests/queries/projection/project_2_schema.sql",
            [
                {Variable("x"), Variable("y")},
                {Variable("x"), Variable("z")},
            ],
        ),
    ],
)
def test_project_query(
    query_file: str,
    expected_sql: str,
    schemas: list[set[str]],
) -> None:
    """Test if the project_query function works correctly."""
    reset_seed()

    part = get_query_object(
        readQueryFile(query_file)
    ).algebra

    project_leaves = all_type_leaves(part, "Project")

    project_queries: str = ""
    for project in reversed(project_leaves):
        project_query_tuple = project_query(
            project, schemas
        )
        if isinstance(project_query_tuple, tuple):
            project_query_curr: str = project_query_tuple[0]
            project_queries_formatted: str = sql_format(
                project_query_curr,
                reindent=True,
                keyword_case="upper",
            )
            project_queries += project_queries_formatted
        else:
            project_queries += sql_format(
                project_query_tuple,
                reindent=True,
                keyword_case="upper",
            )

    with open(expected_sql, "r", encoding="utf-8") as f:
        expected = f.read()

    assert project_queries == expected


@mark.parametrize(
    "query_file,expected_sql,schemas",
    [
        (
            "SQL_Constructor/operation_constructor/tests/queries/projection/project_1_schema.sparql",
            "SQL_Constructor/operation_constructor/tests/queries/projection/project_1_schema_delta.sql",
            [{Variable("x"), Variable("y")}],
        ),
        (
            "SQL_Constructor/operation_constructor/tests/queries/projection/project_2_schema.sparql",
            "SQL_Constructor/operation_constructor/tests/queries/projection/project_2_schema_delta.sql",
            [
                {Variable("x"), Variable("y")},
                {Variable("x"), Variable("z")},
            ],
        ),
    ],
)
def test_delta_project_query(
    query_file: str,
    expected_sql: str,
    schemas: list[set[str]],
) -> None:
    """Test if the project_query function works correctly."""
    reset_seed()

    part = get_query_object(
        readQueryFile(query_file)
    ).algebra

    project_leaves = all_type_leaves(part, "Project")

    project_queries: str = ""
    for project in reversed(project_leaves):
        project_query_tuple = delta_project_query(
            project, schemas
        )
        if isinstance(project_query_tuple, tuple):
            project_query_curr: str = project_query_tuple[0]
            project_queries_formatted: str = sql_format(
                project_query_curr,
                reindent=True,
                keyword_case="upper",
            )
            project_queries += project_queries_formatted
        else:
            project_queries += sql_format(
                project_query_tuple,
                reindent=True,
                keyword_case="upper",
            )

    with open(expected_sql, "r", encoding="utf-8") as f:
        expected = f.read()

    assert project_queries == expected


def _drop_project_tables(
    project_name: str,
    duckdb_conn: DuckDBPyConnection,
) -> None:
    """Drops the project tables."""
    duckdb_conn.execute(
        f"DROP TABLE IF EXISTS {project_name};"
    )
    duckdb_conn.execute(
        f"DROP TABLE IF EXISTS delta_{project_name};"
    )


def _construct_delta_bgp(
    bgp_name: str,
    duckdb_conn: DuckDBPyConnection,
) -> None:
    """Constructs the delta BGPs from the query."""
    duckdb_conn.execute(
        f"CREATE OR REPLACE TABLE delta_{bgp_name} (x TEXT, y TEXT, k_count INT);"
    )
    duckdb_conn.execute(
        f"INSERT INTO delta_{bgp_name} VALUES ('a', 'c', -1), ('b', 'c', 1);"
    )


def _construct_bgp(
    bgp_name: str,
    duckdb_conn: DuckDBPyConnection,
) -> None:
    """Constructs the BGPs from the query."""
    duckdb_conn.execute(
        f"CREATE OR REPLACE TABLE {bgp_name} (x TEXT, y TEXT, k_count INT);"
    )
    duckdb_conn.execute(
        f"INSERT INTO {bgp_name} VALUES ('a', 'b', 1), ('a', 'c', 1);"
    )


@mark.parametrize(
    "query_file,expected_output,schemas,bgp_name,project_name,database",
    [
        (
            "SQL_Constructor/operation_constructor/tests/queries/projection/project_1_schema.sparql",
            [("a", 2)],
            [{Variable("x"), Variable("y")}],
            "BGP_4313253051102226119",
            "Project_2538293893191694556",
            ":memory:",
        )
    ],
)
def test_project_query_output(
    query_file: str,
    expected_output,
    schemas: list[set[str]],
    bgp_name: str,
    project_name: str,
    database: str,
) -> None:
    """Check if the output of the project_query function is correct."""
    reset_seed()

    part = get_query_object(
        readQueryFile(query_file)
    ).algebra

    project_leaves = all_type_leaves(part, "Project")

    project_queries: str = ""
    for project in reversed(project_leaves):
        project_query_tuple = project_query(
            project, schemas
        )
        if isinstance(project_query_tuple, tuple):
            project_query_curr: str = project_query_tuple[0]
            project_queries_formatted: str = sql_format(
                project_query_curr,
                reindent=True,
                keyword_case="upper",
            )
            project_queries += project_queries_formatted
        else:
            project_queries += sql_format(
                project_query_tuple,
                reindent=True,
                keyword_case="upper",
            )

    # Connect to the database
    duckb_conn = connect(database)

    # Construct the BGP tables
    _construct_bgp(bgp_name, duckb_conn)

    # Drop the project tables
    _drop_project_tables(project_name, duckb_conn)

    # Execute the project query
    duckb_conn.execute(project_queries)

    # Check if the output is correct
    result = duckb_conn.execute(
        f"SELECT * FROM {project_name};"
    ).fetchall()
    assert result == expected_output


@mark.parametrize(
    "query_file,expected_output,schemas,bgp_name,project_name,database",
    [
        (
            "SQL_Constructor/operation_constructor/tests/queries/projection/project_1_schema.sparql",
            [("a", -1), ("b", 1)],
            [{Variable("x"), Variable("y")}],
            "BGP_4313253051102226119",
            "Project_2538293893191694556",
            ":memory:",
        )
    ],
)
def test_project_query_delta_output(
    query_file: str,
    expected_output,
    schemas: list[set[str]],
    bgp_name: str,
    project_name: str,
    database: str,
) -> None:
    """Check if the output of the project_query function is correct."""
    reset_seed()

    part = get_query_object(
        readQueryFile(query_file)
    ).algebra

    project_leaves = all_type_leaves(part, "Project")

    delta_project_queries: str = ""
    for project in reversed(project_leaves):
        project_query_tuple = delta_project_query(
            project, schemas
        )
        if isinstance(project_query_tuple, tuple):
            project_query_curr: str = project_query_tuple[0]
            project_queries_formatted: str = sql_format(
                project_query_curr,
                reindent=True,
                keyword_case="upper",
            )
            delta_project_queries += (
                project_queries_formatted
            )
        else:
            delta_project_queries += sql_format(
                project_query_tuple,
                reindent=True,
                keyword_case="upper",
            )

    # Connect to the database
    duckb_conn = connect(database)

    # Construct the BGP tables
    _construct_bgp(bgp_name, duckb_conn)
    _construct_delta_bgp(bgp_name, duckb_conn)

    # Drop the project tables
    _drop_project_tables(project_name, duckb_conn)

    # Execute the project query
    duckb_conn.execute(delta_project_queries)

    # Check if the output is correct
    result = duckb_conn.execute(
        f"SELECT * FROM delta_{project_name};"
    ).fetchall()
    assert result == expected_output
