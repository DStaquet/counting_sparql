"""Modules to import"""

from rdflib.plugins.sparql.parserutils import CompValue
from rdflib.term import Variable

from SQL_Constructor import table_constructor
from SQL_Constructor.base_constructor import (
    make_group_by,
    make_join,
)
from SQL_Constructor.singular_file_constructor import TableNames


def _bgp_table_query_select_clause(
    part: CompValue,
    g_per_triple: dict[tuple[str, str, str], str],
) -> tuple[str, set[str]]:
    # Construct select clause
    first = False
    known_vars: set[str] = set()
    bgp_select_clause: str = "SELECT "
    for var in sorted(part.get("_vars")):
        for index in range(3):
            for triple in sorted(part.triples):
                if triple[index] == var and var not in known_vars:
                    if not first:
                        first = True
                    else:
                        bgp_select_clause += ", "
                    bgp_select_clause += g_per_triple[triple] + "."
                    if index == 0:
                        bgp_select_clause += "s"
                    elif index == 1:
                        bgp_select_clause += "p"
                    else:
                        bgp_select_clause += "o"
                    bgp_select_clause += " AS " + var
                    known_vars.add(var)
    bgp_select_clause += ", G1.k_count AS k_count"

    return bgp_select_clause, known_vars


def _bgp_table_query_where_clause_for_variables(
    part: CompValue,
    g_per_triple: dict[tuple[str, str, str], str],
    indexes: tuple[int, int],
    known_var_dict: dict[str, str],
    first: bool,
) -> str:
    triple_index, var_index = indexes
    where_clause: str = ""

    current_g: str = g_per_triple[part.triples[triple_index]]
    if part.triples[triple_index][var_index] not in known_var_dict:
        match var_index:
            case 0:
                current_g += ".s"
            case 1:
                current_g += ".p"
            case 2:
                current_g += ".o"
        known_var_dict[part.triples[triple_index][var_index]] = current_g
    else:
        if not first:
            first = True
        else:
            where_clause += " AND "
        current_g = known_var_dict[part.triples[triple_index][var_index]]
        where_clause += (
            current_g + " = " + g_per_triple[part.triples[triple_index]] + "."
        )
        match var_index:
            case 0:
                where_clause += "s"
            case 1:
                where_clause += "p"
            case 2:
                where_clause += "o"

    return where_clause


def _bgp_table_query_where_clause(
    part: CompValue,
    g_per_triple: dict[tuple[str, str, str], str],
) -> str:
    # construct where clause
    where_clause: str = " WHERE "
    first: bool = False
    known_var_dict: dict[str, str] = dict()
    for triple_index, _ in enumerate(part.triples):
        for var_index in range(3):
            indexes: tuple[int, int] = (
                triple_index,
                var_index,
            )
            if part.triples[triple_index][var_index] in part.get("_vars"):
                if isinstance(
                    part.triples[triple_index][var_index],
                    Variable,
                ):
                    where_clause += _bgp_table_query_where_clause_for_variables(
                        part,
                        g_per_triple,
                        indexes,
                        known_var_dict,
                        first,
                    )
            elif not isinstance(
                part.triples[triple_index][var_index],
                Variable,
            ):
                if not first:
                    first = True
                else:
                    where_clause += " AND "
                where_clause += g_per_triple[part.triples[triple_index]] + "."
                if var_index == 0:
                    where_clause += "s"
                elif var_index == 1:
                    where_clause += "p"
                else:
                    where_clause += "o"
                where_clause += (
                    " = '" + part.triples[triple_index][var_index].n3() + "'"
                )

    return where_clause


def bgp_table_query(part: CompValue, table_name: str) -> tuple[str, set[str]]:
    """Creates three different parts to simulate an SQL query to get the data from a BGP given the triple patterns in the BGP part of the query.

    Args:
        part (CompValue): The BGP part of the query.

    Returns:
        str: The entire SQL query to get the data from the BGP.
    """
    g_per_triple: dict[tuple[str, str, str], str] = dict()

    # Construct from clause
    from_clause: str = " FROM "
    count = 1
    for triple in part.triples:
        if count > 1:
            from_clause += ", "
        g_per_triple[triple] = table_name + str(count)
        count += 1
        from_clause += table_name + " " + g_per_triple[triple]

    bgp_select_clause, known_vars = _bgp_table_query_select_clause(
        part, g_per_triple)

    where_clause = _bgp_table_query_where_clause(part, g_per_triple)

    return (
        (bgp_select_clause + "\n" + from_clause + "\n" + where_clause + ";\n"),
        known_vars,
    )


def _bgp_delta_table_query_select_clause(
    part: CompValue,
    g_per_triple: dict[tuple[str, str, str], str],
    triple_count: int,
) -> tuple[str, set[str]]:
    # Construct select clause
    first = False
    known_vars: set = set()
    bgp_select_clause: str = "SELECT "
    for var in sorted(part.get("_vars")):
        for index in range(3):
            for triple in sorted(part.triples):
                if triple[index] == var and var not in known_vars:
                    if not first:
                        first = True
                    else:
                        bgp_select_clause += ", "
                    bgp_select_clause += g_per_triple[triple] + "."
                    if index == 0:
                        bgp_select_clause += "s"
                    elif index == 1:
                        bgp_select_clause += "p"
                    else:
                        bgp_select_clause += "o"
                    bgp_select_clause += " AS " + var
                    known_vars.add(var)
    bgp_select_clause += ", G" + str(triple_count) + ".k_count "

    return bgp_select_clause, known_vars


def _bgp_delta_table_query_where_clause(
    part: CompValue,
    g_per_triple: dict[tuple[str, str, str], str],
) -> str:
    # construct where clause
    where_clause: str = " WHERE "
    first: bool = False
    known_var_dict: dict[str, str] = dict()
    for triple_index, _ in enumerate(part.triples):
        for var_index in range(3):
            if part.triples[triple_index][var_index] in part.get("_vars"):
                if isinstance(
                    part.triples[triple_index][var_index],
                    Variable,
                ):
                    current_g: str = g_per_triple[part.triples[triple_index]]
                    if part.triples[triple_index][var_index] not in known_var_dict:
                        match var_index:
                            case 0:
                                current_g += ".s"
                            case 1:
                                current_g += ".p"
                            case 2:
                                current_g += ".o"
                        known_var_dict[part.triples[triple_index][var_index]] = (
                            current_g
                        )
                    else:
                        if not first:
                            first = True
                        else:
                            where_clause += " AND "
                        current_g = known_var_dict[
                            part.triples[triple_index][var_index]
                        ]
                        where_clause += (
                            current_g
                            + " = "
                            + g_per_triple[part.triples[triple_index]]
                            + "."
                        )
                        match var_index:
                            case 0:
                                where_clause += "s"
                            case 1:
                                where_clause += "p"
                            case 2:
                                where_clause += "o"
            elif not isinstance(
                part.triples[triple_index][var_index],
                Variable,
            ):
                if not first:
                    first = True
                else:
                    where_clause += " AND "
                where_clause += g_per_triple[part.triples[triple_index]] + "."
                if var_index == 0:
                    where_clause += "s"
                elif var_index == 1:
                    where_clause += "p"
                else:
                    where_clause += "o"
                where_clause += (
                    " = '" + part.triples[triple_index][var_index].n3() + "'"
                )

    return where_clause


def _bgp_delta_from_clause(
    part: CompValue,
    delta_index: int,
    table_names: TableNames,
    g_per_triple: dict[tuple[str, str, str], str],
) -> str:
    """Constructs the from clause for the BGP delta table query."""
    from_clause: str = " FROM "
    """ count = 1
    for triple in part.triples:
        if count > 1:
            from_clause += ", "
        delta_tables = ""
        if count == delta_index:
            delta_tables = "delta_"
        elif count < delta_index:
            delta_tables = "nu_"
        g_per_triple[triple] = "G" + str(count)
        count += 1
        from_clause += (
            delta_tables + table_names.og_table_name + " " + g_per_triple[triple]
        ) """
    for triple_index, triple in enumerate(part.triples):
        delta_tables: str | None = None
        if triple_index != 0:
            from_clause += ", "
        if triple_index + 1 > delta_index:
            delta_tables = table_names.og_table_name
        if triple_index + 1 == delta_index:
            delta_tables = table_names.delta_table_name
        elif triple_index + 1 < delta_index:
            delta_tables = table_names.nu_table_name
        g_per_triple[triple] = "G" + str(triple_index + 1)
        if delta_tables is None:
            raise ValueError("Tables not given correctly for the delta query")
        from_clause += delta_tables + " " + g_per_triple[triple]

    return from_clause


def bgp_delta_table_query(
    part: CompValue,
    delta_index: int,
    table_names: TableNames,
) -> tuple[str, set[str]]:
    """Constructs the BGP delta table query for the given part of the query.

    Args:
        part (CompValue): Current part of the query
        triple_count (int): Counts the number of triples in the BGP

    Returns:
        tuple[str, set[str]]: Tuple with the SQL query and the known variables in the BGP
    """
    g_per_triple: dict[tuple[str, str, str], str] = {}

    # FROM clause
    from_clause = _bgp_delta_from_clause(
        part, delta_index, table_names, g_per_triple)

    bgp_select_clause, known_vars = _bgp_delta_table_query_select_clause(
        part, g_per_triple, delta_index
    )

    where_clause = _bgp_delta_table_query_where_clause(part, g_per_triple)

    return (
        (bgp_select_clause + "\n" + from_clause + "\n" + where_clause),
        known_vars,
    )


def delta_bgp_queries(
    part: CompValue,
    table_names: TableNames,
) -> tuple[str, str]:
    """Builds up the different delta BGP queries for the incremental query.

    Args:
        part (CompValue): Current part of the query

    Returns:
        list[str]: List of the delta queries for the BGP
    """
    delta_queries: str = ""
    delta_join_queries: str = ""

    bgp_name: str = "delta_" + table_constructor.get_table_name(part)

    dict_with_bgps: dict[str, list[str]] = dict()
    for triple_index in range(len(part.triples)):
        if bgp_name not in dict_with_bgps:
            dict_with_bgps[bgp_name] = [
                bgp_delta_table_query(
                    part, triple_index + 1, table_names)[0] + ";\n"
            ]
        else:
            dict_with_bgps[bgp_name].append(
                bgp_delta_table_query(
                    part, triple_index + 1, table_names)[0] + ";\n"
            )

    delta_join_queries = make_join(dict_with_bgps, [part.get(
        "_vars")], True, temp_delta_prefix=" TEMP ")  # type: ignore

    delta_queries = make_group_by(
        dict_with_bgps, [part.get("_vars")], True)  # type: ignore

    return (
        delta_queries,
        delta_join_queries,
    )
