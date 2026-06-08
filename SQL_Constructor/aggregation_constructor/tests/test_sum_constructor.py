"""Module to test the sum constructor."""

from pytest import mark

from rdflib.plugins.sparql.parserutils import CompValue
from rdflib.term import Variable

from SQL_Constructor.aggregation_constructor.sum_constructor import (
    sum_join_query,
    delta_sum_join_query,
)

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
def test_sum_join_query_output(
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
