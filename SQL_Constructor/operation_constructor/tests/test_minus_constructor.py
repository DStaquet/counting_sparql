from SQL_Constructor.operation_constructor.minus_constructor import (
    minus_query,
    delta_minus_query,
)
from SQL_Constructor.operation_constructor.tests.base_functions import (
    all_type_leaves,
    reset_seed,
)
from incremental_query_parser import (
    get_query_object,
    readQueryFile,
)

from rdflib.plugins.sparql.parserutils import CompValue
from rdflib.term import Variable
from sqlparse import format
from pytest import mark


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
