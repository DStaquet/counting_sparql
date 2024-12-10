from SQL_Constructor.operation_constructor.union_constructor import (
    union_query,
    delta_union_query,
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

    part = get_query_object(
        readQueryFile(query_file)
    ).algebra

    union_leaves = all_type_leaves(part, "Union")

    union_queries: str = ""
    for union in reversed(union_leaves):
        union_query_str = union_query(
            union, schemas1, schemas2
        )
        union_queries = format(
            union_query_str,
            reindent=True,
            keyword_case="upper",
        )

    with open(expected_sql, "r") as f:
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

    part = get_query_object(
        readQueryFile(query_file)
    ).algebra

    union_leaves = all_type_leaves(part, "Union")

    union_queries: str = ""
    for union in reversed(union_leaves):
        union_query_str = delta_union_query(
            union, schemas1, schemas2
        )
        union_queries = format(
            union_query_str,
            reindent=True,
            keyword_case="upper",
        )

    with open(expected_sql, "r") as f:
        expected_sql = f.read()

    assert union_queries == expected_sql
