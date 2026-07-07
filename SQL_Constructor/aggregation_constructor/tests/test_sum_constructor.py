"""Module to test the sum constructor."""

from pytest import mark

from rdflib.plugins.sparql.parserutils import CompValue
from duckdb import DuckDBPyConnection, connect  # type: ignore

# from rdflib.term import Variable

from SQL_Constructor.aggregation_constructor.sum_constructor import (
    sum_join_query,
    delta_sum_join_query,
)

from SQL_Constructor.table_constructor import get_table_name

from SQL_Constructor.operation_constructor.tests.base_functions import (
    reset_seed,
    all_type_leaves,
)
from build_data import readQueryFile, get_query_object

AGGREGATION_VAL = CompValue("Aggregate_Join", vars="x")
AGGREGATION_SAMPLE = CompValue("Aggregate_Sample", vars="y")


@mark.parametrize(
    "query_file, aggregate_values, aggregate_sample, expected_output_file",
    [
        (
            "SQL_Constructor/aggregation_constructor/tests/queries/sum_join_query_1.rq",
            [AGGREGATION_VAL],
            AGGREGATION_SAMPLE,
            "SQL_Constructor/aggregation_constructor/tests/queries/sum_join_query_1_output.sql",
        ),
    ],
)
def test_sum_join_query(
    query_file: str,
    aggregate_values: list[CompValue],
    aggregate_sample: CompValue,
    expected_output_file: str,
) -> None:
    """Tests the sum query for aggregation."""
    reset_seed()

    part = get_query_object(readQueryFile(query_file)).algebra

    sum_leaves = all_type_leaves(part, "AggregateJoin")

    with open(expected_output_file, "r", encoding="utf-8") as f:
        expected_output = f.read()

    for sum_leaf in sum_leaves:
        output = sum_join_query(
            aggregate_values,
            aggregate_sample,
            sum_leaf,
        )

        print("Output:\n", output)
        print("Expected Output:\n", expected_output)

        assert output in expected_output


def _build_bgps(bgp_name: str, duckdb_conn: DuckDBPyConnection) -> None:
    """Helper function to build the BGP tables for testing."""
    duckdb_conn.execute(f"""
        CREATE OR REPLACE TABLE {bgp_name} AS
        SELECT 1 AS x, 'Product1' AS y, 1 as k_count
        UNION ALL
        SELECT 3 AS x, 'Product1' AS y, 1 as k_count;
        """)


# def _drop_bgps(bgp_name: str, duckdb_conn: DuckDBPyConnection) -> None:
#     """Helper function to drop the BGP tables for testing."""
#     duckdb_conn.execute(f"DROP TABLE IF EXISTS {bgp_name};")


@mark.parametrize(
    "query_file, aggregate_values, aggregate_sample, duckdb_file",
    [
        (
            "SQL_Constructor/aggregation_constructor/tests/queries/sum_join_query_1.rq",
            [AGGREGATION_VAL],
            AGGREGATION_SAMPLE,
            "database/aggregation.db",
        ),
    ],
)
def test_sum_join_output(
    query_file: str,
    aggregate_values: list[CompValue],
    aggregate_sample: CompValue,
    duckdb_file: str,
) -> None:
    """Tests the sum query for aggregation."""
    reset_seed()

    duckdb_conn = connect(duckdb_file)

    part = get_query_object(readQueryFile(query_file)).algebra

    sum_leaves = all_type_leaves(part, "AggregateJoin")

    # with open(expected_output, "r", encoding="utf-8") as f:
    #     expected_output_str = f.read()

    for sum_leaf in sum_leaves:
        output = sum_join_query(
            aggregate_values,
            aggregate_sample,
            sum_leaf,
        )

        bgp_name = get_table_name(sum_leaf.p.p)

        # Create bgp to pull from
        _build_bgps(bgp_name, duckdb_conn)

        # Create table
        create_table_query = (
            f"CREATE OR REPLACE TABLE {get_table_name(part)} AS " + output
        )
        duckdb_conn.execute(create_table_query)

        print("Output:\n", output)
        # print("Expected Output:\n", expected_output_str)

        assert duckdb_conn.execute(
            f"SELECT * FROM {get_table_name(part)}"
        ).fetchall() == [
            ("Product1", 4, 1),
        ]


@mark.parametrize(
    "query_file, aggregate_values, aggregate_sample, expected_output_file",
    [
        (
            "SQL_Constructor/aggregation_constructor/tests/queries/sum_join_query_1.rq",
            [AGGREGATION_VAL],
            AGGREGATION_SAMPLE,
            "SQL_Constructor/aggregation_constructor/tests/queries/sum_join_query_delta_1_output.sql",
        ),
    ],
)
def test_sum_join_delta(
    query_file: str,
    aggregate_values: list[CompValue],
    aggregate_sample: CompValue,
    expected_output_file: str,
) -> None:
    """Tests the sum query for aggregation."""
    reset_seed()

    part = get_query_object(readQueryFile(query_file)).algebra

    sum_leaves = all_type_leaves(part, "AggregateJoin")

    with open(expected_output_file, "r", encoding="utf-8") as f:
        expected_output = f.read()

    for sum_leaf in sum_leaves:
        output = delta_sum_join_query(
            aggregate_values,
            aggregate_sample,
            sum_leaf,
        )

        print("Output:\n", output)
        print("Expected Output:\n", expected_output)

        assert output in expected_output


def _build_delta_bgps(bgp_name: str, duckdb_conn: DuckDBPyConnection) -> None:
    """Helper function to build the delta BGP tables for testing."""
    # Delta table
    duckdb_conn.execute(f"""
        CREATE OR REPLACE TABLE delta_{bgp_name} AS
        SELECT * FROM (
            VALUES
                (1, 'Product1', -1),
            ) AS t(x, y, k_count);
        """)
    # Nu table
    duckdb_conn.execute(f"""
        CREATE OR REPLACE TABLE nu_{bgp_name} AS
        SELECT * FROM (
            VALUES
                (1, 'Product1', 1),
            ) AS t(x, y, k_count);
        """)


@mark.parametrize(
    "query_file, aggregate_values, aggregate_sample, duckdb_file",
    [
        (
            "SQL_Constructor/aggregation_constructor/tests/queries/sum_join_query_1.rq",
            [AGGREGATION_VAL],
            AGGREGATION_SAMPLE,
            "database/sum_aggregation.db",
        ),
    ],
)
def test_sum_join_delta_output(
    query_file: str,
    aggregate_values: list[CompValue],
    aggregate_sample: CompValue,
    duckdb_file: str,
) -> None:
    """Tests the sum query for aggregation."""
    reset_seed()

    duckdb_conn = connect(duckdb_file)

    part = get_query_object(readQueryFile(query_file)).algebra

    sum_leaves = all_type_leaves(part, "AggregateJoin")

    # with open(expected_output, "r", encoding="utf-8") as f:
    #     expected_output_str = f.read()

    for sum_leaf in sum_leaves:
        agg_output = sum_join_query(
            aggregate_values,
            aggregate_sample,
            sum_leaf,
        )
        create_table_query = (
            f"CREATE OR REPLACE TABLE {get_table_name(sum_leaf)} AS " + agg_output
        )
        duckdb_conn.execute(create_table_query)

        output = delta_sum_join_query(
            aggregate_values,
            aggregate_sample,
            sum_leaf,
        )

        bgp_name = get_table_name(sum_leaf.p.p)

        # Create bgp to pull from
        _build_bgps(bgp_name, duckdb_conn)
        _build_delta_bgps(bgp_name, duckdb_conn)

        # Create table
        create_table_query = (
            f"CREATE OR REPLACE TABLE nu_{get_table_name(sum_leaf)} AS " + output
        )
        duckdb_conn.execute(create_table_query)

        print("Output:\n", output)
        # print("Expected Output:\n", expected_output_str)

        print(
            duckdb_conn.execute(
                f"SELECT * FROM nu_{get_table_name(sum_leaf)}"
            ).fetchall()
        )

        assert duckdb_conn.execute(
            f"SELECT * FROM nu_{get_table_name(sum_leaf)}"
        ).fetchall() == [
            ("Product1", 3, 1),
        ]
