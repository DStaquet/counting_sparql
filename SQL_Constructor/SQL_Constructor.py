from hashlib import sha256

from rdflib.plugins.sparql.sparql import FrozenBindings
from rdflib.plugins.sparql.parserutils import (
    CompValue,
    Expr,
)
from rdflib.term import Variable

from pandas import DataFrame

from os.path import isdir
from os import listdir


def drop_all_tables(
    part: CompValue,
) -> tuple[str, str, str]:
    """Queries to drop all the tables

    Args:
        part (CompValue): Current part of the algebra

    Returns:
        tuple[str, str, str]: The drop queries for the table, delta table, and nu table.
    """
    drop_query: str = (
        """
    DROP TABLE IF EXISTS """
        + __encode_table_name(part)
        + """;"""
    )

    drop_delta_query: str = (
        """
    DROP TABLE IF EXISTS delta_"""
        + __encode_table_name(part)
        + """;"""
    )

    drop_nu_query: str = (
        """
    DROP TABLE IF EXISTS nu_"""
        + __encode_table_name(part)
        + """;"""
    )

    return drop_query, drop_delta_query, drop_nu_query


def get_table_name(part: CompValue) -> str:
    return __encode_table_name(part)


def get_create_vars(variables: set) -> str:
    return __create_vars(variables)


def __create_vars(variables: set) -> str:
    """Creates the variable part in the string for the query.

    Args:
        variables (set): Given variables

    Returns:
        str: Query string for the variables
    """
    var_str: str = ""
    for var in sorted(variables):
        if var == "k_count":
            continue
        var_str += "\t" + var + " VARCHAR(255),\n"
    var_str += "\tk_count INT,\n"
    return var_str


def __encode_table_name(part: CompValue) -> str:
    """Encodes the table name to a usable string for SQL.

    Args:
        part (CompValue): Current part of the algebra

    Returns:
        str: Encoded table name
    """
    return_str: str = ""

    if part.name == "BGP":
        for triple in sorted(part.triples):
            return_str += str(triple)
        for var in sorted(part._vars):
            return_str += str(type(var)) + str(var)
        return (
            part.name
            + "_"
            + str(
                abs(
                    hash(
                        (
                            "".join(
                                ltr
                                for ltr in return_str
                                if ltr.isalnum()
                            )
                        )
                    )
                )
            )
        )
    elif part.name == "values":
        return (
            part.name
            + "_"
            + str(
                abs(
                    hash(
                        (
                            "".join(
                                x
                                for x in part.__str__()
                                if x.isalnum()
                            )
                        )
                    )
                )
            )
        )
    elif "PV" in part:
        for var in sorted(part.PV):
            return_str += str(type(var)) + str(var)
        return_str = "".join(
            x for x in return_str if x.isalnum()
        )
    else:
        for var in sorted(part._vars):
            return_str += str(type(var)) + str(var)
        return_str = "".join(
            x for x in return_str if x.isalnum()
        )
    if "p" in part:
        return (
            part.name
            + "_"
            + str(
                abs(
                    hash(
                        (
                            return_str
                            + "__"
                            + __encode_table_name(part.p)
                        )
                    )
                )
            )
        )
    else:
        return (
            part.name
            + "_"
            + str(
                abs(
                    hash(
                        (
                            return_str
                            + "__"
                            + __encode_table_name(part.p1)
                            + "__"
                            + __encode_table_name(part.p2)
                        )
                    )
                )
            )
        )


def values_var(res: list) -> str:
    """Creates the values part in the string for the query.

    Args:
        res (list): Given list of results

    Returns:
        str: Values part of the query
    """
    known_vars: set = set()
    var_str: str = ""
    for elem in res:
        for assignment in elem:
            if assignment not in known_vars:
                var_str += (
                    "\t"
                    + assignment
                    + " VARCHAR(255),\n\tvalue VARCHAR(255),\n"
                )
                known_vars.add(assignment)
    var_str += (
        "\tPRIMARY KEY("
        + "".join(x for x in known_vars)
        + ")\n"
    )
    return var_str


def drop_delta_table(part: CompValue) -> str:
    return f"DROP TABLE IF EXISTS delta_{__encode_table_name(part)};"


def make_tables(
    part: CompValue, variables: set
) -> tuple[str, str, str]:
    """Construct the queries to create the tables for the given part of the algebra.

    Args:
        part (CompValue): Current part of the algebra
        variables (set): Variables in the part

    Returns:
        tuple[str, str, str]: Query strings for the table, delta table, and nu table.
    """

    if part.name == "BGP":
        # BGP old table
        create_table_str: str = (
            f"CREATE TABLE IF NOT EXISTS "
            + __encode_table_name(part)
            + " (\n"
            + "\t"
        )
        for var in variables:
            create_table_str += var + " VARCHAR(255),\n\t"
        create_table_str += "k_count INT,\n"
        create_table_str += (
            "\tPRIMARY KEY ("
            + ",".join(var for var in variables)
            + ")\n"
            + ");"
        )

        # BGP delta table
        create_table_delta_bgp: str = (
            f"CREATE TABLE IF NOT EXISTS delta_"
            + __encode_table_name(part)
            + " (\n"
            + "\t"
        )
        for var in variables:
            create_table_delta_bgp += (
                var + " VARCHAR(255),\n\t"
            )
        create_table_delta_bgp += "k_count INT,\n"
        create_table_delta_bgp += (
            "\tPRIMARY KEY ("
            + ",".join(var for var in variables)
            + ")\n"
            + ");"
        )

        # BGP nu table
        create_table_bgp_nu: str = (
            f"CREATE TABLE IF NOT EXISTS nu_"
            + __encode_table_name(part)
            + " (\n"
            + "\t"
        )
        for var in variables:
            create_table_bgp_nu += (
                var + " VARCHAR(255),\n\t"
            )
        create_table_bgp_nu += "k_count INT,\n"
        create_table_bgp_nu += (
            "\tPRIMARY KEY ("
            + ",".join(var for var in variables)
            + ")\n"
            + ");"
        )

    elif part.name == "values" or (
        part.name == "ToMultiSet"
        and "p" in part
        and part.p.name == "values"
    ):
        if part.name == "ToMultiSet":
            res: list = part.p.res
        else:
            res: list = part.res
        create_table_str: str = (
            f"CREATE TABLE IF NOT EXISTS "
            + __encode_table_name(part)
            + " (\n"
            + values_var(res)
            + ");"
        )

        create_table_delta_bgp: str = (
            f"CREATE TABLE IF NOT EXISTS delta_"
            + __encode_table_name(part)
            + " (\n"
            + values_var(res)
            + ");"
        )

        create_table_bgp_nu: str = (
            f"CREATE TABLE IF NOT EXISTS nu_"
            + __encode_table_name(part)
            + " (\n"
            + values_var(res)
            + ");"
        )

    elif "PV" in part or (
        part.name == "Distinct" and "PV" in part.p
    ):
        if part.name == "Distinct":
            variables = part.p.PV
        else:
            variables = part.PV
        create_table_str: str = (
            f"CREATE TABLE IF NOT EXISTS "
            + __encode_table_name(part)
            + " (\n"
            + __create_vars(variables)
            + "\tPRIMARY KEY ("
            + ",".join(var for var in variables)
            + ")\n"
            + ");"
        )

        create_table_delta_bgp: str = (
            f"CREATE TABLE IF NOT EXISTS delta_"
            + __encode_table_name(part)
            + " (\n"
            + __create_vars(variables)
            + "\tPRIMARY KEY ("
            + ",".join(var for var in variables)
            + ")\n"
            + ");"
        )

        create_table_bgp_nu: str = (
            f"CREATE TABLE IF NOT EXISTS nu_"
            + __encode_table_name(part)
            + " (\n"
            + __create_vars(variables)
            + "\tPRIMARY KEY ("
            + ",".join(var for var in variables)
            + ")\n"
            + ");"
        )

    else:
        create_table_str: str = (
            f"CREATE TABLE IF NOT EXISTS "
            + __encode_table_name(part)
            + " (\n"
            + __create_vars(variables)
            + "\tPRIMARY KEY ("
            + ",".join(var for var in variables)
            + ")\n"
            + ");"
        )

        create_table_delta_bgp: str = (
            f"CREATE TABLE IF NOT EXISTS delta_"
            + __encode_table_name(part)
            + " (\n"
            + __create_vars(variables)
            + "\tPRIMARY KEY ("
            + ",".join(var for var in variables)
            + ")\n"
            + ");"
        )

        create_table_bgp_nu: str = (
            f"CREATE TABLE IF NOT EXISTS nu_"
            + __encode_table_name(part)
            + " (\n"
            + __create_vars(variables)
            + "\tPRIMARY KEY ("
            + ",".join(var for var in variables)
            + ")\n"
            + ");"
        )

    return (
        create_table_str,
        create_table_delta_bgp,
        create_table_bgp_nu,
    )


def add_on_conflict_insert_clause(
    tbl_name: str,
    solution_mapping: FrozenBindings,
    sorted_variables: list,
) -> str:
    """Add the ON CONFLICT clause to the insert query.

    Args:
        tbl_name (str): Name of the table
        solution_mapping (FrozenBindings): Solution mappings.
        sorted_variables (list): List of sorted variables.

    Returns:
        str: On conflict insert clause.
    """
    update_clause = "ON CONFLICT DO\nUPDATE\nSET k_count = k_count + 1\nWHERE "
    count: int = 0
    for var in sorted_variables:
        if not count >= (len(sorted_variables) - 1):
            update_clause += (
                var
                + " = '"
                + str(solution_mapping[var])
                + "' AND "
            )
            count += 1
        else:
            update_clause += (
                var
                + " = '"
                + str(solution_mapping[var])
                + "'"
            )

    return update_clause


def construct_bgp_insert(
    part: CompValue,
    filled_in_triples: list[tuple[str, str, str]],
) -> str:
    """Constructs the insert query for the BGP part of the algebra.

    Args:
        part (CompValue): Current part of the algebra
        filled_in_triples (list[tuple[str, str, str]]): Triples to insert

    Returns:
        str: Query string for the BGP insert query.
    """
    insert_str: str = (
        "INSERT INTO "
        + __encode_table_name(part)
        + "\nVALUES\n\t"
    )
    for triple in filled_in_triples:
        insert_str += (
            "('"
            + triple[0]
            + "', '"
            + triple[1]
            + "', '"
            + triple[2]
            + "', 1),\n\t"
        )
    insert_str += "ON CONFLICT DO\nUPDATE SET\n\t"
    insert_str += (
        "k_count = EXCLUDED.k_count + 1\n"
        + "WHERE s = EXCLUDED.S AND  p = EXCLUDED.p AND o = EXCLUDED.o;"
    )
    return insert_str


def bgp_delta_table_query(
    part: CompValue, triple_count: int
) -> str:
    """Create the delta table query for the BGP part of the algebra.

    Args:
        part (CompValue): Current part of the algebra
        triple_count (int): Number of triples in the BGP

    Returns:
        str: _description_
    """
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
        g_per_triple[triple] = (
            delta_tables + "G" + str(count)
        )
        count += 1
        from_clause += (
            delta_tables + "G " + g_per_triple[triple]
        )

    # Construct select clause
    first = False
    known_vars: set = set()
    bgp_select_clause: str = "SELECT "
    for triple in part.triples:
        for index in range(3):
            for var in part._vars:
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
        ", delta_G" + str(triple_count) + ".k_count "
    )

    # construct where clause
    where_clause: str = " WHERE "
    first: bool = False
    for triple_index in range(len(part.triples)):
        for var_index in range(3):
            if (
                part.triples[triple_index][var_index]
                in part._vars
            ):
                for triple_index2 in range(
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
        bgp_select_clause
        + "\n"
        + from_clause
        + "\n"
        + where_clause
        + ";\n"
    )


def bgp_query(
    part: CompValue, schemas: dict[str, list[list[str]]]
) -> str:
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
    for triple in part.triples:
        for index in range(3):
            for var in part._vars:
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

    # construct where clause
    where_clause: str = " WHERE "
    first: bool = False
    for triple_index in range(len(part.triples)):
        for var_index in range(3):
            if (
                part.triples[triple_index][var_index]
                in part._vars
            ):
                for triple_index2 in range(
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

    schemas[table_name] = list()
    schemas[table_name].append(list())
    for var in known_vars:
        if var not in schemas[table_name]:
            schemas[table_name][0].append(
                var
            )  # Uses 0 as BGP will always have one schema

    return (
        bgp_select_clause
        + "\n"
        + from_clause
        + "\n"
        + where_clause
        + ";\n"
    )


def insert_delta_query(
    part: CompValue,
    results: DataFrame,
    increm_table_name_part: str = "",
) -> str:
    insert_str: str = (
        "INSERT INTO "
        + increm_table_name_part
        + __encode_table_name(part)
        + " ("
    )
    first: bool = True
    for key in sorted(results.keys()):
        if first:
            first = False
        else:
            insert_str += ", "
        insert_str += key
    insert_str += ") VALUES\n"

    for row_index in range(len(results)):
        insert_str += "\t("
        first: bool = True
        for key in sorted(results.keys()):
            if first:
                first = False
            else:
                insert_str += ", "
            if key != "k_count":
                insert_str += "'"
            insert_str += str(results[key].loc[row_index])
            if key != "k_count":
                insert_str += "'"
        insert_str += "),\n"

    insert_str += "ON CONFLICT DO\nUPDATE SET\n\t"
    insert_str += "k_count = EXCLUDED.k_count + k_count\n"
    insert_str += "WHERE "
    first: bool = True
    for key in results:
        if key == "k_count":
            continue
        if first:
            first = False
        else:
            insert_str += " AND "
        insert_str += str(key) + " = EXCLUDED." + str(key)
    insert_str += ";"

    return insert_str


def insert_query(
    part: CompValue,
    results: DataFrame,
    increm_table_name_part: str = "",
) -> str:
    insert_str: str = (
        "INSERT INTO "
        + increm_table_name_part
        + __encode_table_name(part)
        + " ("
    )
    first: bool = True
    for key in sorted(results.keys()):
        if first:
            first = False
        else:
            insert_str += ", "
        insert_str += key
    insert_str += ") VALUES\n"

    for row_index in range(len(results)):
        insert_str += "\t("
        first: bool = True
        for key in sorted(results.keys()):
            if first:
                first = False
            else:
                insert_str += ", "
            if key != "k_count":
                insert_str += "'"
            insert_str += str(results[key].loc[row_index])
            if key != "k_count":
                insert_str += "'"
        insert_str += "),\n"

    insert_str += "ON CONFLICT DO\nUPDATE SET\n\t"
    insert_str += "k_count = k_count + 1\n"
    insert_str += "WHERE "
    first: bool = True
    for key in results:
        if key == "k_count":
            continue
        if first:
            first = False
        else:
            insert_str += " AND "
        insert_str += str(key) + " = EXCLUDED." + str(key)
    insert_str += ";"

    return insert_str


def bgp_insert_query(
    part: CompValue, results: DataFrame
) -> str:
    insert_str: str = (
        "INSERT INTO " + __encode_table_name(part) + " ("
    )
    first: bool = True
    for key in sorted(results.keys()):
        if first:
            first = False
        else:
            insert_str += ", "
        insert_str += key
    insert_str += ", k_count) VALUES\n"

    for row_index in range(len(results)):
        insert_str += "\t("
        for key in sorted(results.keys()):
            insert_str += (
                "'"
                + str(results[key].loc[row_index])
                + "', "
            )
        insert_str += "1),\n"
    insert_str += "ON CONFLICT DO\nUPDATE SET\n\t"
    insert_str += "k_count = k_count + 1\n"
    insert_str += "WHERE "
    first: bool = True
    for key in results:
        if first:
            first = False
        else:
            insert_str += " AND "
        insert_str += str(key) + " = EXCLUDED." + str(key)
    insert_str += ";"
    return insert_str


def combine_create_table_insert(
    create_str: str, insert_str: str
) -> str:
    combined_str: str = (
        "BEGIN TRANSACTION;\n"
        + create_str
        + "\n"
        + insert_str
        + "\nCOMMIT;"
    )

    return combined_str


def project_table_query(part: CompValue) -> str:
    table_name: str = __encode_table_name(part.p)
    project_str: str = (
        "SELECT "
        + ", ".join(var for var in part.PV)
        + ", k_count FROM "
        + table_name
        + ";"
    )
    return project_str


def select_query(part: CompValue) -> str:
    table_name = __encode_table_name(part.p)
    select_str = "SELECT " + "* FROM " + table_name + ";"
    return select_str


def union_table_query(
    part: CompValue, r1_vars: set[str], r2_vars: set[str]
) -> str:
    """Constructs an SQL query to union two tables together with their k counts.

    Args:
        part (CompValue): Part of the algebra currently calculating
        r1_vars (set[str]): Variables of the left relation.
        r2_vars (set[str]): Variables of the right relation.

    Returns:
        str: The SQL query to union the two tables together.
    """
    table_name1: str = __encode_table_name(part.p1)
    table_name2: str = __encode_table_name(part.p2)

    # Construct union table query
    # FROM clause
    from_clause: str = (
        "FROM "
        + table_name1
        + " AS r1 "
        + "FULL OUTER JOIN "
        + table_name2
        + " AS r2"
        + " ON "
    )
    first: bool = True
    for var1 in r1_vars:
        if var1 in r2_vars:
            if first:
                first = False
            else:
                from_clause += " AND "
            from_clause += "r1." + var1 + " = r2." + var1

    # SELECT clause
    select_clause: str = "SELECT "
    for _var in part.p1._vars.intersection(part.p2._vars):
        select_clause += (
            "(CASE WHEN r1."
            + _var
            + " IS NOT NULL THEN r1."
            + _var
            + " ELSE r2."
            + _var
            + " END) AS "
            + _var
            + ", "
        )
    for _var in part.p1._vars.difference(part.p2._vars):
        select_clause += "r1." + _var + " AS " + _var + ", "
    for _var in part.p2._vars.difference(part.p1._vars):
        select_clause += "r2." + _var + " AS " + _var + ", "
    select_clause += " coalesce(r1.k_count, 0) + coalesce(r2.k_count, 0) as k_count"

    return select_clause + "\n" + from_clause + ";\n"


def build_delta_union_from_clause(
    first_table_name: str,
    second_table_name,
    r1_vars: set[str],
    r2_vars: set[str],
) -> str:
    # Construct union table query
    # FROM clause
    from_clause: str = (
        "FROM "
        + first_table_name
        + " AS r1 "
        + "FULL JOIN "
        + second_table_name
        + " AS r2"
        + " ON "
    )
    first: bool = True
    for var1 in r1_vars:
        if var1 in r2_vars:
            if first:
                first = False
            else:
                from_clause += " AND "
            from_clause += "r1." + var1 + " = r2." + var1

    return from_clause


def delta_union_table_query(
    part: CompValue, r1_vars: set[str], r2_vars: set[str]
) -> tuple[str, str]:
    """Constructs an SQL query to union two tables together with their k counts.

    Args:
        part (CompValue): Part of the algebra currently calculating
        r1_vars (set[str]): Variables of the left relation.
        r2_vars (set[str]): Variables of the right relation.

    Returns:
        str: The SQL query to union the two tables together.
    """
    part1_table_name1: str = "delta_" + __encode_table_name(
        part.p1
    )
    part1_table_name2: str = __encode_table_name(part.p2)

    # First FROM clause
    part1_from_clause: str = build_delta_union_from_clause(
        part1_table_name1,
        part1_table_name2,
        r1_vars,
        r2_vars,
    )

    # Second FROM clause
    part2_table_name1: str = "nu_" + __encode_table_name(
        part.p1
    )
    part2_table_name2: str = "delta_" + __encode_table_name(
        part.p2
    )
    part2_from_clause: str = build_delta_union_from_clause(
        part2_table_name1,
        part2_table_name2,
        r1_vars,
        r2_vars,
    )

    # SELECT clause
    select_clause: str = "SELECT "
    for _var in part.p1._vars.intersection(part.p2._vars):
        select_clause += (
            "(CASE WHEN r1."
            + _var
            + " IS NOT NULL THEN r1."
            + _var
            + " ELSE r2."
            + _var
            + " END) AS "
            + _var
            + ", "
        )
    for _var in part.p1._vars.difference(part.p2._vars):
        select_clause += "r1." + _var + " AS " + _var + ", "
    for _var in part.p2._vars.difference(part.p1._vars):
        select_clause += "r2." + _var + " AS " + _var + ", "
    select_clause += " coalesce(r1.k_count, 0) + coalesce(r2.k_count, 0) as k_count"

    first_query: str = (
        select_clause + "\n" + part1_from_clause + ";\n"
    )
    second_query: str = (
        select_clause + "\n" + part2_from_clause + ";\n"
    )

    return (first_query, second_query)


def filter_expr_part(expr: Expr) -> str:
    """Recursively construct the filter expression part of the query.

    Args:
        expr (Expr): Current expression part of the query

    Returns:
        str: Expression part for the filter query.
    """
    filter_expr = ""
    if type(expr.expr) == Expr:
        filter_expr += filter_expr_part(expr.expr)
        for i in range(len(expr.other)):
            filter_expr += " AND "
            filter_expr += filter_expr_part(expr.other[i])
    else:
        filter_expr += (
            expr.expr + " " + expr.op + " " + expr.other
        )
    return filter_expr


def filter_query(
    part: CompValue, schemas: dict[str, list[list[str]]]
) -> str:
    """Build up the filter queries

    Args:
        part (CompValue): Current part of the query

    Returns:
        str: Query string to get the results of the filter operation
    """
    table_name: str = __encode_table_name(part.p)
    filter_str: str = (
        "SELECT * FROM "
        + table_name
        + " WHERE "
        + filter_expr_part(part.expr)
        + ";"
    )

    part_name: str = __encode_table_name(part)
    schemas[part_name] = list()
    for var_list in schemas[table_name]:
        schemas[part_name].append(var_list)

    return filter_str


def delta_filter_query(part: CompValue) -> str:
    """Build up the incremental delta filter queries.

    Args:
        part (CompValue): Current part of the algebra

    Returns:
        str: Query string to get the results of the delta filter operation
    """
    table_name: str = "delta_" + __encode_table_name(part.p)
    filter_str: str = (
        "SELECT * FROM "
        + table_name
        + " WHERE "
        + filter_expr_part(part.expr)
        + ";"
    )
    return filter_str


def project_query(
    part: CompValue, schemas: dict[str, list[list[str]]]
) -> str:
    """Generate the query string to project the variables from the table.

    Args:
        part (CompValue): Current part of the query

    Returns:
        str: Query string to project the variables from the table.
    """
    table_name: str = __encode_table_name(part.p)

    part_name: str = __encode_table_name(part)
    schemas[part_name] = list()
    for var_list in schemas[table_name]:
        new_var_list: list[str] = list()
        for var in var_list:
            if var in part.PV:
                new_var_list.append(var)
        schemas[part_name].append(new_var_list)

    return (
        "SELECT "
        + ", ".join(var for var in sorted(part.PV))
        + ", SUM(k_count) as k_count FROM "
        + table_name
        + " GROUP BY "
        + ", ".join(var for var in sorted(part.PV))
        + ";"
    )


def leftjoin_query(part: CompValue) -> str:
    """Generate the query string to left join the tables

    Args:
        part (CompValue): Current part of the query

    Returns:
        str: Query string to left join the tables
    """
    leftjoin_query: str = (
        "SELECT "
        + ", ".join(
            var
            for var in sorted(part.p1._vars)
            if var != "k_count"
        )
        + ", "
        + ", ".join(
            var
            for var in sorted(part.p2._vars)
            if var != "k_count"
        )
        + ", r1.k_count as k_count\nFROM "
        + __encode_table_name(part.p1)
        + " AS r1 LEFT JOIN "
        + __encode_table_name(part.p2)
        + " AS r2"
    )
    if part.p1._vars.intersection(part.p2._vars) != set():
        leftjoin_query += " ON "
        leftjoin_query += " AND ".join(
            f"r1.{var} = r2.{var}"
            for var in part.p1._vars.intersection(
                part.p2._vars
            )
        )
    else:
        leftjoin_query += " ON TRUE"
    leftjoin_query += ";"
    return leftjoin_query


def minus_query(
    part: CompValue,
    schemas: dict[str, list[list[str]]],
    multiple_schemas: bool = False,
) -> str:
    """Minus query string for the algebra

    Args:
        part (CompValue): Current part of the algebra

    Returns:
        str: Query string for the minus operation
    """
    if not multiple_schemas:
        minus_query: str = (
            "SELECT * \nFROM "
            + __encode_table_name(part.p1)
            + " AS r1\n"
        )
        if (
            part.p1._vars.intersection(part.p2._vars)
            != set()
        ):
            minus_query += (
                "WHERE "
                + ", ".join(
                    f"r1.{var}"
                    for var in sorted(
                        part.p1._vars.intersection(
                            part.p2._vars
                        )
                    )
                )
                + " NOT IN (SELECT "
                + ", ".join(
                    f"r2.{var}"
                    for var in sorted(
                        part.p1._vars.intersection(
                            part.p2._vars
                        )
                    )
                )
                + " FROM "
                + __encode_table_name(part.p2)
                + " AS r2);"
            )
        else:
            minus_query += ";"
    else:
        if isdir(__encode_table_name(part.p1)):
            minus_query: str = ""
            for p1_file in listdir(
                __encode_table_name(part.p1)
            ):
                minus_query += (
                    "SELECT * \nFROM "
                    + p1_file
                    + " AS r1\n"
                )
                if isdir(__encode_table_name(part.p2)):
                    pass

    part_name: str = __encode_table_name(part)
    schemas[part_name] = list()
    left_table_name: str = __encode_table_name(part.p1)
    for var_list in schemas[left_table_name]:
        schemas[part_name].append(var_list)

    return minus_query


def union_query(
    part: CompValue, schemas: dict[str, list[list[str]]]
) -> str:
    """Union query string for the algebra

    Args:
        part (CompValue): Current part of the algebra

    Returns:
        str: Query string for the union operation
    """
    union_table_name1: str = __encode_table_name(part.p1)
    union_query_left: str = (
        "SELECT * FROM " + union_table_name1 + "\n"
    )
    union_table_name2: str = __encode_table_name(part.p2)
    union_query_right: str = (
        "SELECT "
        + ", ".join(
            var
            for var in sorted(
                part.p2._vars.intersection(part.p1._vars)
            )
        )
        + ", "
        + ", ".join(
            f"NULL AS {var}"
            for var in sorted(
                part.p1._vars.difference(part.p2._vars)
            )
        )
        + " FROM "
        + union_table_name2
        + ";\n"
    )

    left_table_name: str = __encode_table_name(part.p1)
    right_table_name: str = __encode_table_name(part.p2)
    part_name: str = __encode_table_name(part)
    schemas[part_name] = list()
    for var_list in schemas[left_table_name]:
        schemas[part_name].append(var_list)
    for var_list in schemas[right_table_name]:
        schemas[part_name].append(var_list)
    print(schemas)

    return union_query_left + "UNION \n" + union_query_right
