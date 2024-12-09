from SQL_Constructor.operation_constructor.bgp_constructor import (
    bgp_table_query,
)
from incremental_query_parser import (
    readQueryFile,
    get_query_object,
)
from SQL_Constructor.base_constructor import (
    create_table_w_select,
    get_table_name,
)
from SQL_Constructor.operation_constructor.tests.base_functions import (
    reset_seed,
)

from pytest import mark

from rdflib.plugins.sparql.parserutils import CompValue

from sqlparse import format


def __all_type_leaves(
    part: CompValue, type_name: str
) -> list[CompValue]:
    """Gives a list of all BGP patterns in the query.

    Args:
        part (Compvalue): Current algebraic expression

    Returns:
        list[CompValue]: All BGP patterns in the query.
    """
    return_list: list[CompValue] = []
    if (
        part.p == None
        and part.p1 == None
        and part.p2 == None
        and part.name == type_name
    ):
        return_list.append(part)
    if "p" in part:
        return return_list + __all_type_leaves(
            part.p, type_name
        )
    elif "p1" in part and "p2" in part:
        return (
            return_list
            + __all_type_leaves(part.p1, type_name)
            + __all_type_leaves(part.p2, type_name)
        )
    else:
        return return_list


@mark.parametrize(
    "query_file,expected_sql",
    [
        (
            "/home/dore/Documents/1_Universiteit/counting_sparql/counting_sparql/SQL_Constructor/operation_constructor/tests/queries/bgp/bgp_test_1_pattern.sparql",
            "/home/dore/Documents/1_Universiteit/counting_sparql/counting_sparql/SQL_Constructor/operation_constructor/tests/queries/bgp/bgp_test_1_pattern.sql",
        ),
        (
            "/home/dore/Documents/1_Universiteit/counting_sparql/counting_sparql/SQL_Constructor/operation_constructor/tests/queries/bgp/bgp_test_2_pattern.sparql",
            "/home/dore/Documents/1_Universiteit/counting_sparql/counting_sparql/SQL_Constructor/operation_constructor/tests/queries/bgp/bgp_test_2_pattern.sql",
        ),
        (
            "/home/dore/Documents/1_Universiteit/counting_sparql/counting_sparql/SQL_Constructor/operation_constructor/tests/queries/bgp/bgp_test_3_pattern.sparql",
            "/home/dore/Documents/1_Universiteit/counting_sparql/counting_sparql/SQL_Constructor/operation_constructor/tests/queries/bgp/bgp_test_3_pattern.sql",
        ),
    ],
)
def test_bgp_table_query(
    query_file: str, expected_sql: str
):
    """Tests the bgp_table_query function."""
    reset_seed()

    part = get_query_object(
        readQueryFile(query_file)
    ).algebra

    # Find only BGP patterns
    bgp_leaves: list[CompValue] = __all_type_leaves(
        part, "BGP"
    )

    bgp_queries: str = ""
    for bgp in reversed(bgp_leaves):
        current_query, _ = bgp_table_query(bgp)

        bgp_queries += format(
            create_table_w_select(
                get_table_name(bgp), current_query
            ),
            reindent=True,
        )

    with open(expected_sql) as f:
        expected_query = f.read()

    assert bgp_queries == expected_query
