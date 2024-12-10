from SQL_Constructor import base_constructor
from SQL_Constructor.base_constructor import (
    __encode_table_name,
)


from rdflib.plugins.sparql.parserutils import CompValue
from rdflib.term import Variable

from SQL_Constructor.base_constructor import (
    delta_outer_join_long_query,
)


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


def bgp_delta_table_query(
    part: CompValue, triple_count: int
) -> tuple[str, set[str]]:
    bgp_delta_table_name = "delta_" + __encode_table_name(
        part
    )
    g_per_triple: dict[tuple[str, str, str], str] = dict()

    # FROM clause
    from_clause: str = " FROM "
    count = 1
    for triple in part.triples:
        if count > 1:
            from_clause += ", "
        delta_tables = ""
        if count == triple_count:
            delta_tables = "delta_"
        elif count < triple_count:
            delta_tables = "nu_"
        g_per_triple[triple] = "G" + str(count)
        count += 1
        from_clause += (
            delta_tables + "G " + g_per_triple[triple]
        )

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
    bgp_select_clause += (
        ", G" + str(triple_count) + ".k_count "
    )

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
        ),
        known_vars,
    )


def delta_bgp_queries(
    part: CompValue,
) -> tuple[str, str, str, str]:
    """Builds up the different delta BGP queries for the incremental query.

    Args:
        part (CompValue): Current part of the query

    Returns:
        list[str]: List of the delta queries for the BGP
    """
    delta_queries: str = ""
    delta_join_queries: str = ""
    delta_join_tables: str = ""
    last_delta_query_name: str = ""
    first_insert = True
    temp_suffix = ""
    for triple_index in range(len(part.triples)):
        delta_query, known_vars = bgp_delta_table_query(
            part, triple_index + 1
        )
        delta_query_name = (
            "delta_"
            + base_constructor.get_table_name(part)
            + "_"
            + str(triple_index + 1)
        )
        delta_join_tables += (
            base_constructor.create_table_w_select(
                delta_query_name,
                delta_query + ";\n",
                temp_prefix="TEMP",
            )
        )
        if last_delta_query_name != "" and (
            triple_index + 1
        ) < len(part.triples):
            delta_join_query = (
                base_constructor.outer_join_queries(
                    delta_query_name + "_temp",
                    last_delta_query_name + temp_suffix,
                    delta_query_name,
                    known_vars,
                )
            )
            delta_join_queries += delta_join_query
            last_delta_query_name = delta_query_name
            temp_suffix = "_temp"
        elif (triple_index + 1) == len(
            part.triples
        ) and triple_index != 0:
            if len(part.triples) == 2:
                temp_suffix = ""
            else:
                temp_suffix = "_temp"
            delta_join_query = (
                base_constructor.final_outer_join_query(
                    last_delta_query_name + temp_suffix,
                    delta_query_name,
                    known_vars,
                    "delta_"
                    + base_constructor.get_table_name(part),
                )
            )
            delta_join_queries += delta_join_query
            last_delta_query_name = delta_query_name
        else:
            if len(part.triples) == 1:
                delta_join_queries += (
                    base_constructor.create_table_w_select(
                        "delta_"
                        + base_constructor.get_table_name(
                            part
                        ),
                        delta_query + ";\n",
                    )
                )
            # This is unconventional, but skips the first query making
            last_delta_query_name = delta_query_name
        if first_insert:
            first_insert = False
            delta_queries += (
                base_constructor.create_table_w_select(
                    "delta_prep_"
                    + base_constructor.get_table_name(part),
                    delta_query + ";\n",
                    temp_prefix="TEMP",
                )
            )
        else:
            delta_queries += (
                base_constructor.insert_into_w_select(
                    "delta_prep_"
                    + base_constructor.get_table_name(part),
                    delta_query + ";\n",
                    list(known_vars),
                )
            )

    _, known_vars = bgp_delta_table_query(part, 1)
    delta_long_join_query: str = (
        delta_outer_join_long_query(part, known_vars)
    )
    delta_long_w_create = (
        base_constructor.create_table_w_select(
            "delta_"
            + base_constructor.get_table_name(part),
            delta_long_join_query,
        )
    )

    return (
        delta_queries,
        delta_join_queries,
        delta_long_w_create,
        delta_join_tables,
    )
