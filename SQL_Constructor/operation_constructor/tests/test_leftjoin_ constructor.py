from SQL_Constructor.operation_constructor.leftjoin_constructor import (
    left_join_query,
    delta_left_join_query,
)
from SQL_Constructor.base_constructor import get_table_name
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
    part = get_query_object(
        readQueryFile(query_file)
    ).algebra

    leftjoin_leaves = all_type_leaves(part, "LeftJoin")

    for leftjoin_leaf in reversed(leftjoin_leaves):
        leftjoin_query: str = format(
            left_join_query(
                leftjoin_leaf, schemas1, schemas2
            ),
            reindent=True,
            keyword_case="upper",
        )

    with open(expected_sql) as f:
        expected_sql = f.read()

    assert leftjoin_query == expected_sql


@mark.parametrize(
    "query_file,expected_sql,schemas1,schemas2",
    [
        (
            "SQL_Constructor/operation_constructor/tests/queries/leftjoin/leftjoin_1_schema.sparql",
            "SQL_Constructor/operation_constructor/tests/queries/leftjoin/leftjoin_1_schema_delta.sql",
            [{Variable("x")}],
            [{Variable("x"), Variable("y")}],
        ),
        (
            "SQL_Constructor/operation_constructor/tests/queries/leftjoin/leftjoin_2_schemas.sparql",
            "SQL_Constructor/operation_constructor/tests/queries/leftjoin/leftjoin_2_schemas_delta.sql",
            [{Variable("x")}],
            [
                {Variable("x"), Variable("y")},
                {Variable("x"), Variable("w")},
            ],
        ),
    ],
)
def test_delta_left_join_query(
    query_file: str,
    expected_sql: str,
    schemas1: list[set[str]],
    schemas2: list[set[str]],
) -> None:
    """Test if the delta left join query is correct."""
    reset_seed()

    # Read the query file
    part = get_query_object(
        readQueryFile(query_file)
    ).algebra

    leftjoin_leaves = all_type_leaves(part, "LeftJoin")

    for leftjoin_leaf in reversed(leftjoin_leaves):
        delta_leftjoin_tuple = delta_left_join_query(
            leftjoin_leaf, schemas1, schemas2
        )
        delta_leftjoin_query: str = format(
            delta_leftjoin_tuple[0],
            reindent=True,
            keyword_case="upper",
        )

    with open(expected_sql) as f:
        expected = f.read()

    assert delta_leftjoin_query == expected
