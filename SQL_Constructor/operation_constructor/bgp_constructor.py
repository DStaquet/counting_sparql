from SQL_Constructor.base_constructor import (
    __encode_table_name,
)


from rdflib.plugins.sparql.parserutils import CompValue
from rdflib.term import Variable


def bgp_table_query(
    part: CompValue,
) -> tuple[str, set[str]]:
    """Creates three different parts to simulate an SQL query to get the data from a BGP given the triple patterns in the BGP part of the query.

    Args:
        part (CompValue): The BGP part of the query.

    Returns:
        str: The entire SQL query to get the data from the BGP.
    """
    table_name: str = __encode_table_name(part)
    g_per_triple: dict[tuple[str, str, str], str] = dict()

    # Construct from clause
    from_clause: str = " FROM "
    count = 1
    for triple in part.triples:
        if count > 1:
            from_clause += ", "
        g_per_triple[triple] = "G" + str(count)
        count += 1
        from_clause += "G " + g_per_triple[triple]

    # Construct select clause
    first = False
    known_vars: set = set()
    bgp_select_clause: str = "SELECT "
    for var in sorted(part._vars):
        for index in range(3):
            for triple in sorted(part.triples):
                if (
                    triple[index] == var
                    and var not in known_vars
                ):
                    if not first:
                        first = True
                    else:
                        bgp_select_clause += ", "
                    bgp_select_clause += (
                        g_per_triple[triple] + "."
                    )
                    if index == 0:
                        bgp_select_clause += "s"
                    elif index == 1:
                        bgp_select_clause += "p"
                    else:
                        bgp_select_clause += "o"
                    bgp_select_clause += " AS " + var
                    known_vars.add(var)
    """bgp_select_clause += ", ("
    bgp_select_clause += "*".join(
        f"{g}.k_count" for g in g_per_triple.values()
    )"""
    bgp_select_clause += f", G1.k_count AS k_count"

    # construct where clause
    where_clause: str = " WHERE "
    first: bool = False
    known_var_dict: dict[str, str] = dict()
    for triple_index in range(len(part.triples)):
        for var_index in range(3):
            if (
                part.triples[triple_index][var_index]
                in part._vars
            ):
                if (
                    type(
                        part.triples[triple_index][
                            var_index
                        ]
                    )
                    == Variable
                ):
                    current_g: str = g_per_triple[
                        part.triples[triple_index]
                    ]
                    if (
                        part.triples[triple_index][
                            var_index
                        ]
                        not in known_var_dict
                    ):
                        match var_index:
                            case 0:
                                current_g += ".s"
                            case 1:
                                current_g += ".p"
                            case 2:
                                current_g += ".o"
                        known_var_dict[
                            part.triples[triple_index][
                                var_index
                            ]
                        ] = current_g
                    else:
                        if not first:
                            first = True
                        else:
                            where_clause += " AND "
                        current_g = known_var_dict[
                            part.triples[triple_index][
                                var_index
                            ]
                        ]
                        where_clause += (
                            current_g
                            + " = "
                            + g_per_triple[
                                part.triples[triple_index]
                            ]
                            + "."
                        )
                        match var_index:
                            case 0:
                                where_clause += "s"
                            case 1:
                                where_clause += "p"
                            case 2:
                                where_clause += "o"
                '''for triple_index2 in range(
                    triple_index + 1, len(part.triples)
                ):
                    for var_index2 in range(3):
                        if (
                            part.triples[triple_index][
                                var_index
                            ]
                            == part.triples[triple_index2][
                                var_index2
                            ]
                            and type(
                                part.triples[triple_index][
                                    var_index
                                ]
                            )
                            == Variable
                        ):
                            if not first:
                                first = True
                            else:
                                where_clause += " AND "
                            where_clause += (
                                g_per_triple[
                                    part.triples[
                                        triple_index
                                    ]
                                ]
                                + "."
                            )
                            if var_index == 0:
                                where_clause += "s"
                            elif var_index == 1:
                                where_clause += "p"
                            else:
                                where_clause += "o"
                            where_clause += " = "
                            where_clause += (
                                g_per_triple[
                                    part.triples[
                                        triple_index2
                                    ]
                                ]
                                + "."
                            )
                            if var_index2 == 0:
                                where_clause += "s"
                            elif var_index2 == 1:
                                where_clause += "p"
                            else:
                                where_clause += "o"'''
            elif (
                type(part.triples[triple_index][var_index])
                != Variable
            ):
                if not first:
                    first = True
                else:
                    where_clause += " AND "
                where_clause += (
                    g_per_triple[part.triples[triple_index]]
                    + "."
                )
                if var_index == 0:
                    where_clause += "s"
                elif var_index == 1:
                    where_clause += "p"
                else:
                    where_clause += "o"
                where_clause += (
                    " = '"
                    + str(
                        part.triples[triple_index][
                            var_index
                        ]
                    )
                    + "'"
                )

    return (
        (
            bgp_select_clause
            + "\n"
            + from_clause
            + "\n"
            + where_clause
            + ";\n"
        ),
        known_vars,
    )
