from SQL_Constructor.base_constructor import (
    __encode_table_name,
    countKCountsTogether,
)
from SQL_Constructor.operation_constructor.diff_constructor import (
    diff_query_sub,
    delta_diff_sub,
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


def delta_minus_query(
    part: CompValue,
    schemas1: list[set[str]],
    schemas2: list[set[str]],
) -> str:
    """Returns the delta minus query.

    Args:
        part (CompValue): Current part of the query.

    Returns:
        str: Query string for the delta minus operation.
    """
    if len(schemas1) == 0:
        raise ValueError("Schema 1 is empty")
    elif len(schemas1) == 1:
        delta_diff_queries: str = delta_diff_sub(
            part,
            schemas1,
            schemas2,
            minus=True,
            append_schemas=False,
        )
    else:
        delta_diff_queries: str = delta_diff_sub(
            part,
            schemas1,
            schemas2,
            minus=True,
        )

    delta_diff_queries += countKCountsTogether(
        part,
        schemas1,
        "delta_" + __encode_table_name(part),
        "delta_prep_" + __encode_table_name(part),
    )

    return delta_diff_queries
    """if part.p1._vars.intersection(part.p2._vars) == set():
        return (
            "INSERT INTO delta_"
            + __encode_table_name(part)
            + " SELECT * FROM delta_"
            + __encode_table_name(part.p1)
            + ";"
        )
    # R1 MINUS delta_R2
    first_query: str = (
        "INSERT INTO delta_"
        + __encode_table_name(part)
        + "\n"
    )
    first_query += (
        "SELECT "
        + ", ".join(
            f"p1.{var}" for var in sorted(part.p1._vars)
        )
        + ", p1.k_count as k_count\n"
    )
    first_query += (
        "FROM delta_"
        + __encode_table_name(part.p1)
        + " AS p1\n"
    )
    first_query += "WHERE (" + ", ".join(
        f"p1.{var}"
        for var in sorted(
            part.p1._vars.intersection(part.p2._vars)
        )
    )
    first_query += ") NOT IN (SELECT " + ", ".join(
        f"p2.{var}"
        for var in sorted(
            part.p1._vars.intersection(part.p2._vars)
        )
    )
    first_query += (
        " FROM "
        + __encode_table_name(part.p2)
        + " AS p2)\n"
    )
    first_query += "ON CONFLICT DO\nUPDATE SET\n\t"
    first_query += (
        "k_count = EXCLUDED.k_count + k_count\n"
        + "WHERE "
        + " AND ".join(
            f"{var} = EXCLUDED.{var}"
            for var in sorted(part.p1._vars)
        )
    )
    if part.p2._vars.difference(part.p1._vars) != set():
        first_query += " AND " + " AND ".join(
            f"{var} = EXCLUDED.{var}"
            for var in sorted(
                part.p2._vars.difference(part.p1._vars)
            )
        )
    first_query += ";\n"

    # R1_nu MINUS delta_R2 - First part
    second_query_first: str = (
        "INSERT INTO delta_"
        + __encode_table_name(part)
        + "\n"
    )
    second_query_first += (
        "SELECT "
        + ", ".join(
            f"p1.{var}" for var in sorted(part.p1._vars)
        )
        + ", p1.k_count as k_count\n"
    )
    second_query_first += "FROM "
    second_query_first += (
        "nu_"
        + __encode_table_name(part.p1)
        + " AS p1, delta_"
        + __encode_table_name(part.p2)
        + " AS p2, "
        + __encode_table_name(part.p2)
        + " AS p3\n"
    )
    if part.p1._vars.intersection(part.p2._vars) != set():
        second_query_first += "WHERE (" + ", ".join(
            f"p1.{var} = p2.{var}"
            for var in sorted(
                part.p1._vars.intersection(part.p2._vars)
            )
        )
        second_query_first += ") AND "
        second_query_first += ", ".join(
            f"p1.{var} = p3.{var}"
            for var in sorted(
                part.p1._vars.intersection(part.p2._vars)
            )
        )
        second_query_first += (
            " AND -p2.k_count = p3.k_count;\n"
        )

    # R1_nu MINUS delta_R2 - Second part
    second_query_second: str = (
        "\nINSERT INTO delta_"
        + __encode_table_name(part)
        + "\n"
    )
    second_query_second += (
        "SELECT "
        + ", ".join(
            f"p1.{var}" for var in sorted(part.p1._vars)
        )
        + ", -p1.k_count\n"
    )
    second_query_second += "FROM "
    second_query_second += (
        "nu_"
        + __encode_table_name(part.p1)
        + " AS p1, delta_"
        + __encode_table_name(part.p2)
        + " AS p2\n"
    )
    if part.p1._vars.intersection(part.p2._vars) != set():
        second_query_second += "WHERE (" + ", ".join(
            f"p1.{var} = p2.{var}"
            for var in sorted(
                part.p1._vars.intersection(part.p2._vars)
            )
        )
        second_query_second += (
            ") AND EXISTS (SELECT "
            + ", ".join(
                f"{var}"
                for var in sorted(
                    part.p1._vars.intersection(
                        part.p2._vars
                    )
                )
            )
        )
        second_query_second += (
            "\nFROM "
            + __encode_table_name(part.p2)
            + " AS p3"
            + " WHERE "
            + "p2.k_count = p3.k_count)"
        )

    second_query_second += ";\n"

    second_query: str = (
        second_query_first + second_query_second
    )

    return first_query + second_query"""
