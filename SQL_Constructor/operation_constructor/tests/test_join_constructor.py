from SQL_Constructor.operation_constructor.join_constructor import (
    join_query_str_constr,
    delta_join_queries_part_func,
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
    part = get_query_object(
        readQueryFile(query_file)
    ).algebra

    join_leaves = all_type_leaves(part, "Join")

    # Execute the join query
    join_queries: str = ""
    for join_leaf in join_leaves:
        join_query_tuple = join_query_str_constr(
            join_leaf,
            get_table_name(join_leaf.p1),
            get_table_name(join_leaf.p2),
            schemas1,
            schemas2,
        )
        if isinstance(join_query_tuple, tuple):
            join_queries += format(
                join_query_tuple[0],
                reindent=True,
                keyword_case="upper",
            )
        else:
            join_queries += format(
                join_query_tuple,
                reindent=True,
                keyword_case="upper",
            )

    # Read the expected SQL query
    with open(expected_sql, "r") as f:
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
    part = get_query_object(
        readQueryFile(query_file)
    ).algebra

    join_leaves = all_type_leaves(part, "Join")

    # Execute the join query
    join_queries: str = ""
    for join_leaf in join_leaves:
        join_query, _ = delta_join_queries_part_func(
            join_leaf,
            schemas1,
            schemas2,
        )
        join_queries += format(
            join_query,
            reindent=True,
            keyword_case="upper",
        )

    # Read the expected SQL query
    with open(expected_sql, "r") as f:
        expected_sql_str = f.read()

    # Compare the expected SQL query with the generated SQL query
    assert join_queries == expected_sql_str
