"""Module for testing the count constructor."""

from pytest import mark

from rdflib.plugins.sparql.parserutils import CompValue
#from duckdb import DuckDBPyConnection, connect # type: ignore

from SQL_Constructor.aggregation_constructor.count_constructor import (
    count_join_query,
)
from SQL_Constructor.operation_constructor.tests.base_functions import (
    reset_seed,
    all_type_leaves,
)
#from SQL_Constructor.table_constructor import get_table_name

from build_data import readQueryFile, get_query_object

AGGREGATION_VAL = CompValue("Aggregate_Join", vars="x")
AGGREGATION_SAMPLE = CompValue("Aggregate_Sample", vars="y")

@mark.parametrize(
    "query_file, aggregate_values, aggregate_sample, expected_output_file",
    [
        (
            "SQL_Constructor/aggregation_constructor/tests/queries/count_join_query_1.rq",
            [AGGREGATION_VAL],
            AGGREGATION_SAMPLE,
            "SQL_Constructor/aggregation_constructor/tests/queries/count_join_query_1.sql",
        ),
    ],
)
def test_count_join_query(
    query_file: str,
    aggregate_values: list[CompValue],
    aggregate_sample: CompValue,
    expected_output_file: str,
) -> None:
    """Tests the count query for aggregation."""
    reset_seed()

    part = get_query_object(readQueryFile(query_file)).algebra

    count_leaves = all_type_leaves(part, "AggregateJoin")

    with open(expected_output_file, "r", encoding="utf-8") as f:
        expected_output = f.read()

    for count_leaf in count_leaves:
        output = count_join_query(
            aggregate_values,
            aggregate_sample,
            count_leaf,
        )

        print("Output:\n", output)
        print("Expected Output:\n", expected_output)

        assert output in expected_output