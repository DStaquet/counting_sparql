from SQL_Constructor.SQL_Constructor import get_table_name
from rdflib.plugins.sparql.parserutils import CompValue


def join_delta_rules_bgp(query_str: str) -> str:
    """Takes the delta rules and returns it with a join query.

    Args:
        query_str (str): The delta rules.

    Returns:
        str: Delta rules utilizing a join.
    """
    delta_queries: list[str] = query_str.split(";")[:-1]
    for query in delta_queries:
        print(query, "test")
