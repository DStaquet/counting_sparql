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

from rdflib.plugins.sparql.parserutils import CompValue
from rdflib.term import Variable
from sqlparse import format
from pytest import mark

from duckdb import DuckDBPyConnection, connect


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
        delta_leftjoin_join_query: str = format(
            delta_leftjoin_tuple[1],
            reindent=True,
            keyword_case="upper",
        )

    with open(expected_sql) as f:
        expected = f.read()

    assert delta_leftjoin_query == expected

    with open(expected_sql_join) as f:
        expected_join = f.read()

    assert delta_leftjoin_join_query == expected_join


def __dropLeftjoinTables(
    duckdb_conn: DuckDBPyConnection,
    leftjoin_name: str,
) -> None:
    """Drops the left join tables."""
    duckdb_conn.execute(
        f"DROP TABLE IF EXISTS {leftjoin_name};"
    )
    duckdb_conn.execute(
        f"DROP TABLE IF EXISTS delta_{leftjoin_name};"
    )


def __buildBGPs(
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
    duckdb_conn.execute(
        f"INSERT INTO {bgp_two_name} VALUES ('b', 'c', 1);"
    )


@mark.parametrize(
    "query_file,expected_output_joined,expected_output_not_joined,schemas1,schemas2,bgp_one_name,bgp_two_name,leftjoin_name_joined,leftjoin_name_not_joined,database_name",
    [
        (
            "SQL_Constructor/operation_constructor/tests/queries/leftjoin/leftjoin_test_output.sparql",
            [("a", "b", "c", 1)],
            [("a", "d", 1)],
            [{Variable("x"), Variable("y")}],
            [{Variable("y"), Variable("z")}],
            "BGP_4313253051102226119",
            "BGP_5439676414810165533",
            "LeftJoin_5968519747945714539_schema_2520463472976857627",
            "LeftJoin_5968519747945714539_schema_5536938746033674259",
            "database/leftjoin_test_output.db",
        ),
    ],
)
def test_leftjoin_query_output(
    query_file: str,
    expected_output_joined,
    expected_output_not_joined,
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

    # Execute the query
    duckdb_conn: DuckDBPyConnection = connect(database_name)

    # Create the tables
    __buildBGPs(bgp_one_name, bgp_two_name, duckdb_conn)

    for leftjoin_table_name in [
        leftjoin_name_joined,
        leftjoin_name_not_joined,
    ]:
        __dropLeftjoinTables(
            duckdb_conn, leftjoin_table_name
        )
    duckdb_conn.execute(leftjoin_query)

    # Check if the joined output is correct
    result = duckdb_conn.execute(
        f"SELECT * FROM {leftjoin_name_joined};"
    ).fetchall()
    assert result == expected_output_joined

    # Check if the not joined output is correct
    result = duckdb_conn.execute(
        f"SELECT * FROM {leftjoin_name_not_joined};"
    ).fetchall()
    assert result == expected_output_not_joined


def __buildDeltaBGPs(
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
    duckdb_conn.execute(
        f"INSERT INTO nu_{bgp_two_name} VALUES ('d', 'c', 1);"
    )


@mark.parametrize(
    "query_file,expected_output_joined,expected_output_not_joined,schemas1,schemas2,bgp_one_name,bgp_two_name,leftjoin_name_joined,leftjoin_name_not_joined,database_name",
    [
        (
            "SQL_Constructor/operation_constructor/tests/queries/leftjoin/leftjoin_test_output.sparql",
            [("a", "d", "c", 1), ("a", "b", "c", -1)],
            [("a", "d", -1), ("d", "b", 1)],
            [{Variable("x"), Variable("y")}],
            [{Variable("y"), Variable("z")}],
            "BGP_4313253051102226119",
            "BGP_5439676414810165533",
            "LeftJoin_5968519747945714539_schema_2520463472976857627",
            "LeftJoin_5968519747945714539_schema_5536938746033674259",
            "database/leftjoin_test_output.db",
        )
    ],
)
def test_leftjoin_query_output_delta(
    query_file: str,
    expected_output_joined,
    expected_output_not_joined,
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
        delta_leftjoin_join_query: str = format(
            delta_leftjoin_tuple[1],
            reindent=True,
            keyword_case="upper",
        )

    # Execute the query
    duckdb_conn: DuckDBPyConnection = connect(database_name)

    # Create the tables
    __buildBGPs(bgp_one_name, bgp_two_name, duckdb_conn)
    __buildDeltaBGPs(
        bgp_one_name, bgp_two_name, duckdb_conn
    )

    for method in [
        delta_leftjoin_query,
        delta_leftjoin_join_query,
    ]:
        for leftjoin_table_name in [
            leftjoin_name_joined,
            leftjoin_name_not_joined,
        ]:
            __dropLeftjoinTables(
                duckdb_conn, leftjoin_table_name
            )
        duckdb_conn.execute(method)

        # Check if the joined output is correct
        result = duckdb_conn.execute(
            f"SELECT x, y, z, k_count FROM delta_{leftjoin_name_joined};"
        ).fetchall()
        assert sorted(result) == sorted(
            expected_output_joined
        )

        # Check if the not joined output is correct
        result = duckdb_conn.execute(
            f"SELECT x, y, k_count FROM delta_{leftjoin_name_not_joined};"
        ).fetchall()
        assert sorted(result) == sorted(
            expected_output_not_joined
        )
