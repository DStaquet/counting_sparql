from SQL_Constructor.operation_constructor.project_constructor import (
    project_query,
    delta_project_query,
)
from SQL_Constructor.operation_constructor.tests.base_functions import (
    reset_seed,
    all_type_leaves,
)
from incremental_query_parser import (
    get_query_object,
    readQueryFile,
)

from pytest import mark
from rdflib.term import Variable
from sqlparse import format


@mark.parametrize(
    "query_file,expected_sql,schemas",
    [
        (
            "SQL_Constructor/operation_constructor/tests/queries/projection/project_1_schema.sparql",
            "SQL_Constructor/operation_constructor/tests/queries/projection/project_1_schema.sql",
            [{Variable("x"), Variable("y")}],
        )
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
        project_queries += format(
            project_query(project, schemas),
            reindent=True,
            uppercase=True,
        )

    with open(expected_sql, "r") as f:
        expected = f.read()

    assert project_queries == expected


@mark.parametrize(
    "query_file,expected_sql,schemas",
    [
        (
            "SQL_Constructor/operation_constructor/tests/queries/projection/project_1_schema.sparql",
            "SQL_Constructor/operation_constructor/tests/queries/projection/project_1_schema_delta.sql",
            [{Variable("x"), Variable("y")}],
        )
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
        project_queries += format(
            delta_project_query(project, schemas),
            reindent=True,
            uppercase=True,
        )

    with open(expected_sql, "r") as f:
        expected = f.read()

    assert project_queries == expected
