from SQL_Constructor.operation_constructor.diff_constructor import (
    diff_query_sub,
)


from rdflib.plugins.sparql.parserutils import CompValue


def minus_query(
    part: CompValue,
    schemas1: list[set[str]] = [],
    schemas2: list[set[str]] = [],
) -> str:
    """Generates the minus query.

    Args:
        part (CompValue): Current part of the query.

    Returns:
        str: Query string for the minus operation.
    """
    return diff_query_sub(part, schemas1, schemas2, True)
    """if part.p1._vars.intersection(part.p2._vars) == set():
        return (
            "INSERT INTO "
            + __encode_table_name(part)
            + " SELECT * FROM "
            + __encode_table_name(part.p1)
            + ";"
        )
    else:
        return __diff_query_sub(part)"""
