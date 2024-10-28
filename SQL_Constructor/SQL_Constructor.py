from hashlib import sha256

from rdflib.plugins.sparql.sparql import FrozenBindings
from rdflib.plugins.sparql.parserutils import (
    CompValue,
    Expr,
)
from rdflib.term import Variable

from os.path import join

from pandas import DataFrame

import json


def delete_all_tables(
    part: CompValue,
) -> tuple[str, str, str, str]:
    """Deletes all rows from the table.

    Args:
        part (CompValue): Current part of the query

    Returns:
        str: Returns the SQL query to delete all rows from the table.
    """
    delete_query: str = (
        "DELETE FROM " + __encode_table_name(part) + ";"
    )
    delete_delta_query: str = (
        "DELETE FROM delta_"
        + __encode_table_name(part)
        + ";"
    )
    delete_nu_query: str = (
        "DELETE FROM nu_" + __encode_table_name(part) + ";"
    )
    delete_nu_prep_query: str = (
        "DELETE FROM nu_prep_"
        + __encode_table_name(part)
        + ";"
    )

    return (
        delete_query,
        delete_delta_query,
        delete_nu_query,
        delete_nu_prep_query,
    )


def drop_all_tables(part) -> tuple[str, str, str, str]:
    drop_query: str = (
        "DROP TABLE IF EXISTS "
        + __encode_table_name(part)
        + ";"
    )

    drop_delta_query: str = (
        "DROP TABLE IF EXISTS delta_"
        + __encode_table_name(part)
        + ";"
    )

    drop_nu_query: str = (
        "DROP TABLE IF EXISTS nu_"
        + __encode_table_name(part)
        + ";"
    )
    drop_nu_prep_query: str = (
        "DROP TABLE IF EXISTS nu_prep_"
        + __encode_table_name(part)
        + ";"
    )

    return (
        drop_query,
        drop_delta_query,
        drop_nu_query,
        drop_nu_prep_query,
    )


def get_table_name(part: CompValue) -> str:
    return __encode_table_name(part)


def get_create_vars(variables: set) -> str:
    return __create_vars(variables)


def __create_vars(variables: set) -> str:
    var_str: str = ""
    for var in sorted(variables):
        if var == "k_count":
            continue
        var_str += "\t" + var + " VARCHAR(255),\n"
    var_str += "\tk_count INT\n"
    return var_str


def __serialize_to_json(part: CompValue) -> str:
    """Serialize to JSON

    Args:
        part (CompValue): Part to serialize

    Returns:
        str: Serialized part
    """

    def set_default(obj):
        if isinstance(obj, set):
            return list(obj)
        return obj

    return json.dumps(
        part,
        default=set_default,
        indent=4,
    )


def setup_hash_values(
    part: CompValue, output_dir: str
) -> None:
    """Constructs a hash value info file for the query.

    Args:
        part (CompValue): Part of the query
    """
    if part is None:
        return
    hash_value: str = __encode_table_name(part)
    with open(
        join(output_dir, "hash_values.json"), "a"
    ) as hash_file:
        json_part: str = __serialize_to_json(part)
        hash_file.write(
            '"' + hash_value + '": ' + json_part
        )
        hash_file.write("\n")
        if any(key in part for key in ["p", "p1", "p2"]):
            hash_file.write(",\n")
    if "p" in part:
        setup_hash_values(part.p, output_dir)
    elif "p1" in part and "p2" in part:
        setup_hash_values(part.p1, output_dir)
        setup_hash_values(part.p2, output_dir)


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


def delete_delta_table(part: CompValue) -> tuple[str, str]:
    return (
        f"DELETE FROM delta_{__encode_table_name(part)};",
        f"DELETE FROM delta_prep_{__encode_table_name(part)};",
    )


def drop_delta_table(part: CompValue) -> tuple[str, str]:
    return (
        f"DROP TABLE IF EXISTS delta_{__encode_table_name(part)};",
        f"DROP TABLE IF EXISTS delta_prep_{__encode_table_name(part)};",
    )


def make_tables(
    part, variables: set
) -> tuple[str, str, str, str, str]:

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
        create_table_str += "k_count INT);\n"
        """create_table_str += (
            "\tPRIMARY KEY ("
            + ",".join(var for var in variables)
            + ")\n"
            + ");"
        )"""

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
        create_table_delta_bgp += "k_count INT);\n"
        create_table_delta_prep: str = (
            f"CREATE TABLE IF NOT EXISTS delta_prep_"
            + __encode_table_name(part)
            + " (\n"
            + "\t"
        )
        for var in variables:
            create_table_delta_prep += (
                var + " VARCHAR(255),\n\t"
            )
        create_table_delta_prep += "k_count INT);\n"
        create_table_nu_prep: str = (
            f"CREATE TABLE IF NOT EXISTS nu_prep_"
            + __encode_table_name(part)
            + " (\n"
            + "\t"
        )
        for var in variables:
            create_table_nu_prep += (
                var + " VARCHAR(255),\n\t"
            )
        create_table_nu_prep += "k_count INT);\n"
        """create_table_delta_bgp += (
            "\tPRIMARY KEY ("
            + ",".join(var for var in variables)
            + ")\n"
            + ");"
        )"""

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
        create_table_bgp_nu += "k_count INT);\n"
        """create_table_bgp_nu += (
            "\tPRIMARY KEY ("
            + ",".join(var for var in variables)
            + ")\n"
            + ");"
        )"""

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
            + ");"
        )

        create_table_delta_bgp: str = (
            f"CREATE TABLE IF NOT EXISTS delta_"
            + __encode_table_name(part)
            + " (\n"
            + __create_vars(variables)
            + ");"
        )
        create_table_delta_prep: str = (
            f"CREATE TABLE IF NOT EXISTS delta_prep_"
            + __encode_table_name(part)
            + " (\n"
            + __create_vars(variables)
            + ");"
        )
        create_table_nu_prep: str = (
            f"CREATE TABLE IF NOT EXISTS nu_prep_"
            + __encode_table_name(part)
            + " (\n"
            + __create_vars(variables)
            + ");"
        )

        create_table_bgp_nu: str = (
            f"CREATE TABLE IF NOT EXISTS nu_"
            + __encode_table_name(part)
            + " (\n"
            + __create_vars(variables)
            + ");"
        )

    else:
        create_table_str: str = (
            f"CREATE TABLE IF NOT EXISTS "
            + __encode_table_name(part)
            + " (\n"
            + __create_vars(variables)
            + ");"
        )

        create_table_delta_bgp: str = (
            f"CREATE TABLE IF NOT EXISTS delta_"
            + __encode_table_name(part)
            + " (\n"
            + __create_vars(variables)
            + ");"
        )
        create_table_delta_prep: str = (
            f"CREATE TABLE IF NOT EXISTS delta_prep_"
            + __encode_table_name(part)
            + " (\n"
            + __create_vars(variables)
            + ");"
        )
        create_table_nu_prep: str = (
            f"CREATE TABLE IF NOT EXISTS nu_prep_"
            + __encode_table_name(part)
            + " (\n"
            + __create_vars(variables)
            + ");"
        )

        create_table_bgp_nu: str = (
            f"CREATE TABLE IF NOT EXISTS nu_"
            + __encode_table_name(part)
            + " (\n"
            + __create_vars(variables)
            + ");"
        )

    return (
        create_table_str,
        create_table_delta_bgp,
        create_table_delta_prep,
        create_table_bgp_nu,
        create_table_nu_prep,
    )


def add_on_conflict_insert_clause(
    tbl_name: str,
    solution_mapping: FrozenBindings,
    sorted_variables: list,
) -> str:
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


def delta_prep_sum_query(
    part: CompValue, use_pv: bool = False
) -> str:
    """Sums the k_count values in the delta_prep table based upon duplicates in the delta table.

    Args:
        part (CompValue): Current part of the query
        use_pv (bool, optional): Whether to use the PV values. Defaults to False.

    Returns:
        str: The query to sum the k_count values in the delta_prep table.
    """
    update_query: str = "SELECT "
    if use_pv:
        update_query += ", ".join(
            f"{var}" for var in sorted(part.PV)
        )
    else:
        update_query += ", ".join(
            f"{var}" for var in sorted(part._vars)
        )
    update_query += ", SUM(k_count) AS k_count\n"
    update_query += "FROM delta_prep_"
    update_query += __encode_table_name(part)
    update_query += "\nGROUP BY "
    if use_pv:
        update_query += ", ".join(
            f"{var}" for var in sorted(part.PV)
        )
    else:
        update_query += ", ".join(
            f"{var}" for var in sorted(part._vars)
        )
    update_query += ";"

    return update_query


def final_outer_join_query(
    part: CompValue,
    left_query: str,
    right_query: str,
    known_vars: set[str],
) -> str:
    """Generates a query that joins the final tables together.

    Args:
        part (CompValue): Current part of the query
        left_query (str): Left part to fully outer join
        right_query (str): Right part to fully outer join
        known_vars (set[str]): Set of known variables.

    Returns:
        str: Query that joins both tables as a UNION.
    """
    join_query: str = (
        "CREATE TABLE delta_" + __encode_table_name(part)
    )
    join_query += " AS SELECT "
    join_query += ", ".join(
        f"(CASE WHEN R1.{var} NOT NULL THEN R1.{var} ELSE R2.{var} END) AS {var}"
        for var in known_vars
        if var != "k_count"
    )
    join_query += f", (CASE WHEN R1.k_count IS NULL THEN R2.k_count WHEN R2.k_count IS NULL THEN R1.k_count ELSE R1.k_count + R2.k_count END) AS k_count "
    join_query += f"FROM {left_query} AS R1 FULL OUTER JOIN {right_query} AS R2 ON "
    join_query += " AND ".join(
        f"R1.{var} = R2.{var}"
        for var in known_vars
        if var != "k_count"
    )
    join_query += f";"
    return join_query


def outer_join_queries(
    part: CompValue,
    delta_table_name: str,
    left_query: str,
    right_query: str,
    known_vars: set[str],
    index: int,
) -> str:
    """Generates a full outer join query between two tables

    Args:
        left_query (str): Left query to join
        right_query (str): Right query to join
        known_vars (set[str]): Set of known variables of both tables

    Returns:
        str: String with entire full outer join to add to the SQL file
    """
    join_query: str = (
        "CREATE TEMP TABLE " + delta_table_name
    )
    join_query += " AS SELECT "
    join_query += ", ".join(
        f"(CASE WHEN R1.{var} NOT NULL THEN R1.{var} ELSE R2.{var} END) AS {var}"
        for var in known_vars
        if var != "k_count"
    )
    join_query += f", (CASE WHEN R1.k_count IS NULL THEN R2.k_count WHEN R2.k_count IS NULL THEN R1.k_count ELSE R1.k_count + R2.k_count END) AS k_count "
    join_query += f"FROM {left_query} AS R1 FULL OUTER JOIN {right_query} AS R2 ON "
    join_query += " AND ".join(
        f"R1.{var} = R2.{var}"
        for var in known_vars
        if var != "k_count"
    )
    join_query += f";"
    return join_query


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


def create_table_w_select(
    given_table: str,
    select_query: str,
    columns: list[str] | None = None,
    temp_prefix: str = "",
) -> str:
    if columns is None:
        return f"CREATE {temp_prefix} TABLE {given_table} AS\n{select_query}"
    else:
        create_str: str = (
            f"CREATE {temp_prefix} TABLE {given_table} ("
            + ", ".join(
                key
                for key in sorted(columns)
                if key != "k_count"
            )
        )
        create_str += ", k_count INT)\n" + select_query
        return create_str


def insert_into_w_select(
    given_table: str,
    select_query: str,
    columns: list[str] | None = None,
) -> str:
    if columns is None:
        return f"INSERT INTO {given_table}\n{select_query}"
    else:
        insert_str: str = (
            f"INSERT INTO {given_table} ("
            + ", ".join(
                key
                for key in sorted(columns)
                if key != "k_count"
            )
        )
        insert_str += ", k_count)\n" + select_query
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


def delta_select_query(part: CompValue) -> str:
    table_name: str = __encode_table_name(part.p)
    delta_table_name: str = "delta_" + table_name
    select_str: str = (
        "SELECT " + "* FROM " + delta_table_name + ";"
    )
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
        if expr.op in ["=", "<", ">", "<=", ">=", "!="]:
            filter_expr += (
                "CAST("
                + expr.expr
                + " AS INT) "
                + expr.op
                + " CAST("
                + expr.other
                + " AS INT)"
            )
        else:
            filter_expr += (
                expr.expr + " " + expr.op + " " + expr.other
            )
    return filter_expr


def delta_filter_query(part: CompValue) -> str:
    """Build up the incremental delta filter queries.

    Args:
        part (CompValue): Current part of the algebra

    Returns:
        str: Query string to get the results of the delta filter operation
    """
    table_name: str = "delta_" + __encode_table_name(part.p)
    filter_str: str = (
        "INSERT INTO delta_"
        + __encode_table_name(part)
        + "("
        + ", ".join(
            var
            for var in sorted(part._vars)
            if var != "k_count"
        )
        + ", k_count)"
        + "\n"
        + "SELECT "
        + ", ".join(
            var
            for var in sorted(part._vars)
            if var != "k_count"
        )
        + ", k_count\nFROM "
        + table_name
        + " \nWHERE "
        + filter_expr_part(part.expr)
        + ";"
    )
    return filter_str


def delta_project_query(part: CompValue) -> str:
    """Build up the incremental delta project queries.

    Args:
        part (CompValue): Current part of the algebra

    Returns:
        str: Query string to get the results of the delta project operation
    """
    table_name: str = "delta_" + __encode_table_name(part.p)
    project_str: str = (
        "INSERT INTO "
        + "delta_"
        + __encode_table_name(part)
        + "("
        + ", ".join(var for var in sorted(part.PV))
        + ", k_count)\n"
        + "SELECT "
        + ", ".join(var for var in sorted(part.PV))
        + ", SUM(k_count) AS k_count\nFROM "
        + table_name
        + "\nGROUP BY "
        + ", ".join(var for var in sorted(part.PV))
        + ";"
    )
    return project_str


def __delta_diff_sub(part: CompValue) -> str:
    """Generates the minus subquery.

    Args:
        part (CompValue): Current part of the query containing the minus operation.

    Returns:
        str: Query string of the needed minus operation.
    """
    # R1 MINUS delta_R2
    first_query: str = (
        "INSERT INTO delta_"
        + __encode_table_name(part)
        + "\n"
    )
    first_query += "SELECT " + ", ".join(
        var for var in sorted(part.p1._vars)
    )
    if part.p2._vars.difference(part.p1._vars) != set():
        first_query += ", " + ", ".join(
            f"coalesce(p2.{var}, 'UNBOUND')"
            for var in sorted(
                part.p2._vars.difference(part.p1._vars)
            )
        )
    first_query += ", p1.k_count as k_count\n"
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
        + " AND "
        + " AND ".join(
            f"{var} = EXCLUDED.{var}"
            for var in sorted(
                part.p2._vars.difference(part.p1._vars)
            )
        )
    )
    first_query += ";\n"

    # R1_nu MINUS delta_R2 - First part
    second_query_first: str = (
        "INSERT INTO delta_"
        + __encode_table_name(part)
        + "\n"
    )
    first_query += "SELECT " + ", ".join(
        var for var in sorted(part.p1._vars)
    )
    if part.p2._vars.difference(part.p1._vars) != set():
        first_query += ", " + ", ".join(
            f"coalesce(p2.{var}, 'UNBOUND')"
            for var in sorted(
                part.p2._vars.difference(part.p1._vars)
            )
        )
    first_query += ", p1.k_count as k_count\n"
    second_query_first += "FROM "
    second_query_first += (
        "nu_"
        + __encode_table_name(part.p1)
        + " AS p1, delta_"
        + __encode_table_name(part.p2)
        + " AS delta_p2\n"
    )
    if part.p1._vars.intersection(part.p2._vars) != set():
        second_query_first += "WHERE (" + ", ".join(
            f"p1.{var} = delta_p2.{var}"
            for var in sorted(
                part.p1._vars.intersection(part.p2._vars)
            )
        )
        second_query_first += (
            ", -delta_p2.k_count) IN (SELECT "
            + ", ".join(
                f"{var}"
                for var in sorted(
                    part.p1._vars.intersection(
                        part.p2._vars
                    )
                )
            )
            + ", k_count\n"
        )
        second_query_first += (
            "FROM "
            + __encode_table_name(part.p2)
            + " AS p2)\n"
        )
    second_query_first += "ON CONFLICT DO\nUPDATE SET\n\t"
    second_query_first += (
        "k_count = EXCLUDED.k_count + k_count\n"
        + "WHERE "
        + " AND ".join(
            f"{var} = EXCLUDED.{var}"
            for var in sorted(part.p1._vars)
        )
        + " AND "
        + " AND ".join(
            f"{var} = EXCLUDED.{var}"
            for var in sorted(
                part.p2._vars.difference(part.p1._vars)
            )
        )
    )
    second_query_first += ";\n"

    # R1_nu MINUS delta_R2 - Second part
    second_query_second: str = (
        "INSERT INTO delta_"
        + __encode_table_name(part)
        + "\n"
    )
    first_query += "SELECT " + ", ".join(
        var for var in sorted(part.p1._vars)
    )
    if part.p2._vars.difference(part.p1._vars) != set():
        first_query += ", " + ", ".join(
            f"coalesce(p2.{var}, 'UNBOUND')"
            for var in sorted(
                part.p2._vars.difference(part.p1._vars)
            )
        )
    first_query += ", -p1.k_count as k_count\n"
    second_query_second += "FROM "
    second_query_second += (
        "nu_"
        + __encode_table_name(part.p1)
        + " AS p1, delta_"
        + __encode_table_name(part.p2)
        + " AS delta_p2\n"
    )
    if part.p1._vars.intersection(part.p2._vars) != set():
        second_query_second += "WHERE (" + ", ".join(
            f"p1.{var} = delta_p2.{var}"
            for var in sorted(
                part.p1._vars.intersection(part.p2._vars)
            )
        )
        second_query_second += (
            ", k_count) NOT IN (SELECT "
            + ", ".join(
                f"{var}"
                for var in sorted(
                    part.p1._vars.intersection(
                        part.p2._vars
                    )
                )
            )
            + ", k_count\n"
        )
        second_query_second += (
            "FROM "
            + __encode_table_name(part.p2)
            + " AS p2)\n"
        )
    second_query_second += "ON CONFLICT DO\nUPDATE SET\n\t"
    second_query_second += (
        "k_count = EXCLUDED.k_count + k_count\n"
        + "WHERE "
        + " AND ".join(
            f"{var} = EXCLUDED.{var}"
            for var in sorted(part.p1._vars)
        )
        + " AND "
        + " AND ".join(
            f"{var} = EXCLUDED.{var}"
            for var in sorted(
                part.p2._vars.difference(part.p1._vars)
            )
        )
    )
    second_query_second += ";\n"

    second_query: str = (
        second_query_first + second_query_second
    )

    return first_query + second_query


def __delta_join_sub(
    part1: CompValue, part2: CompValue, join_part: CompValue
) -> str:
    """Generates the delta join subquery.

    Args:
        part1 (CompValue): First part of the join.
        part2 (CompValue): Second part of the join.
    """
    # R1 JOIN delta_R2
    first_query: str = (
        "INSERT INTO delta_"
        + __encode_table_name(join_part)
        + "\n"
    )
    first_query += (
        "SELECT "
        + __left_join_select_clause(join_part)
        + ", r1.k_count * r2.k_count as k_count\n"
    )
    first_query += (
        "FROM delta_"
        + __encode_table_name(part1)
        + " AS r1 JOIN "
        + __encode_table_name(part2)
        + " AS r2 "
    )
    first_query += "ON "
    if part1._vars.intersection(part2._vars) != set():
        first_query += " AND ".join(
            f"r1.{var} = r2.{var}"
            for var in part1._vars.intersection(part2._vars)
        )
        first_query += "\n"
    else:
        first_query += "TRUE\n"
    first_query += "ON CONFLICT DO\nUPDATE SET\n\t"
    first_query += (
        "k_count = EXCLUDED.k_count + k_count\n"
        + "WHERE "
        + " AND ".join(
            f"{var} = EXCLUDED.{var}" for var in part1._vars
        )
        + " AND ".join(
            f"{var} = EXCLUDED.{var}"
            for var in part2._vars.difference(part1._vars)
        )
    )
    first_query += ";\n"

    second_query: str = (
        "INSERT INTO delta_"
        + __encode_table_name(join_part)
    )
    second_query += (
        "\nSELECT "
        + __left_join_select_clause(join_part)
        + ", r1.k_count * r2.k_count as k_count\n"
    )
    second_query += (
        "FROM nu_"
        + __encode_table_name(part1)
        + " AS r1 JOIN delta_"
        + __encode_table_name(part2)
        + " AS r2\n"
    )
    second_query += "ON "
    if part1._vars.intersection(part2._vars) != set():
        second_query += " AND ".join(
            f"r1.{var} = r2.{var}"
            for var in part1._vars.intersection(part2._vars)
        )
        second_query += "\n"
    else:
        second_query += "TRUE\n"
    second_query += "ON CONFLICT DO\nUPDATE SET\n\t"
    second_query += (
        "k_count = EXCLUDED.k_count + k_count\n"
        + "WHERE "
        + " AND ".join(
            f"{var} = EXCLUDED.{var}" for var in part1._vars
        )
        + " AND ".join(
            f"{var} = EXCLUDED.{var}"
            for var in part2._vars.difference(part1._vars)
        )
    )
    second_query += ";\n"

    return first_query + second_query


def __left_join_select_clause(part: CompValue) -> str:
    """Returns the lefjoin select clause for the delta rule.

    Args:
        part (CompValue): Current part of the query.

    Returns:
        str: String containing the leftjoin variable clause.
    """
    return_str: str = (
        ", ".join(
            var
            for var in sorted(part.p1._vars)
            if var != "k_count"
        )
        + ", "
        + ", ".join(
            var
            for var in sorted(
                part.p2._vars.difference(part.p1._vars)
            )
            if var != "k_count"
        )
    )
    return return_str


def delta_left_join_query(part: CompValue) -> str:
    # First delta rules of the left join
    # Join deltas
    leftjoin_join_delta_query: str = __delta_join_sub(
        part.p1, part.p2, part
    )
    leftjoin_minus_delta_query: str = __delta_diff_sub(part)

    return (
        leftjoin_join_delta_query
        + leftjoin_minus_delta_query
    )


def delta_minus_query(part: CompValue) -> str:
    """Returns the delta minus query.

    Args:
        part (CompValue): Current part of the query.

    Returns:
        str: Query string for the delta minus operation.
    """
    if part.p1._vars.intersection(part.p2._vars) == set():
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

    return first_query + second_query


def delta_union_query(part: CompValue) -> str:
    """Generates the union delta query.

    Args:
        part (CompValue): Current part of the query.

    Returns:
        str: Query string for the delta union operation.
    """
    union_query: str = (
        "INSERT INTO delta_"
        + __encode_table_name(part)
        + "\n"
    )
    union_query += (
        "SELECT "
        + ", ".join(
            f"(CASE WHEN r1.{var} IS NOT NULL THEN r1.{var} ELSE r2.{var} END) AS {var}"
            for var in sorted(part.p1._vars)
        )
        + ", coalesce(r1.k_count, 0) + coalesce(r2.k_count, 0) as k_count\n"
    )
    union_query += (
        "FROM delta_"
        + __encode_table_name(part.p1)
        + " AS r1 FULL OUTER JOIN "
        + __encode_table_name(part.p2)
        + " AS r2 ON "
    )
    union_query += " AND ".join(
        f"r1.{var} = r2.{var}"
        for var in sorted(
            part.p1._vars.intersection(part.p2._vars)
        )
    )
    union_query += ";\n"

    union_query += (
        "INSERT INTO delta_"
        + __encode_table_name(part)
        + "\n"
    )
    union_query += (
        "SELECT "
        + ", ".join(
            f"(CASE WHEN r1.{var} IS NOT NULL THEN r1.{var} ELSE r2.{var} END) AS {var}"
            for var in sorted(part.p1._vars)
        )
        + ", coalesce(r1.k_count, 0) + coalesce(r2.k_count, 0) as k_count\n"
    )
    union_query += (
        "FROM nu_"
        + __encode_table_name(part.p1)
        + " AS r1 FULL OUTER JOIN delta_"
        + __encode_table_name(part.p2)
        + " AS r2 ON "
    )
    union_query += " AND ".join(
        f"r1.{var} = r2.{var}"
        for var in sorted(
            part.p1._vars.intersection(part.p2._vars)
        )
    )
    union_query += ";\n"

    return union_query


def filter_query(part: CompValue) -> str:
    """Generate filter query for the current part of the algebra.

    Args:
        part (CompValue): Current part of the algebra.

    Returns:
        str: Query string for the filter operation.
    """
    filter_str: str = (
        "INSERT INTO "
        + __encode_table_name(part)
        + "("
        + ", ".join(
            var
            for var in sorted(part._vars)
            if var != "k_count"
        )
        + ", k_count)\n"
        + "SELECT "
        + ", ".join(
            var
            for var in sorted(part._vars)
            if var != "k_count"
        )
        + ", k_count\nFROM "
        + __encode_table_name(part.p)
        + " \nWHERE "
        + filter_expr_part(part.expr)
        + ";"
    )
    return filter_str


def project_query(part: CompValue) -> str:
    """Generate project query for the current part of the algebra.

    Args:
        part (CompValue): Current part of the algebra.

    Returns:
        str: Query string for the project operation.
    """
    project_str: str = (
        "INSERT INTO "
        + __encode_table_name(part)
        + "("
        + ", ".join(var for var in sorted(part.PV))
        + ", k_count)\n"
        + "SELECT "
        + ", ".join(var for var in sorted(part.PV))
        + ", SUM(k_count) AS k_count\nFROM "
        + __encode_table_name(part.p)
        + "\nGROUP BY "
        + ", ".join(var for var in sorted(part.PV))
        + ";"
    )
    return project_str


def __join_query(part: CompValue) -> str:
    """Generates the join query.

    Args:
        part (CompValue): Current part of the query.

    Returns:
        str: Query string for the join operation.
    """
    join_query: str = (
        "INSERT INTO " + __encode_table_name(part) + "\n"
    )
    join_query += "SELECT "
    join_query += __left_join_select_clause(part)
    join_query += ", r1.k_count * r2.k_count as k_count\n"
    join_query += "FROM "
    join_query += __encode_table_name(part.p1)
    join_query += " AS r1 JOIN "
    join_query += __encode_table_name(part.p2)
    join_query += " AS r2 "
    if part.p1._vars.intersection(part.p2._vars) != set():
        join_query += "ON "
        join_query += " AND ".join(
            f"r1.{var} = r2.{var}"
            for var in sorted(
                part.p1._vars.intersection(part.p2._vars)
            )
        )
    join_query += "\nON CONFLICT DO\nUPDATE SET\n\t"
    join_query += (
        "k_count = EXCLUDED.k_count + k_count\n"
        + "WHERE "
        + " AND ".join(
            f"{var} = EXCLUDED.{var}"
            for var in sorted(part.p1._vars)
        )
        + " AND ".join(
            f"{var} = EXCLUDED.{var}"
            for var in sorted(
                part.p2._vars.difference(part.p1._vars)
            )
        )
    )
    join_query += ";\n"
    return join_query


def __diff_query_sub(part: CompValue) -> str:
    """Generates the difference subquery.

    Args:
        part (CompValue): Current part of the query containing the dofference operation.

    Returns:
        str: Query string of the needed difference operation.
    """
    diff_query: str = (
        "INSERT INTO "
        + __encode_table_name(part)
        + "\n"
        + "SELECT "
        + ", ".join(var for var in sorted(part.p1._vars))
    )
    if part.p2._vars.difference(part.p1._vars) != set():
        diff_query += ", " + ", ".join(
            f"coalesce(p2.{var}, 'UNBOUND')"
            for var in sorted(
                part.p2._vars.difference(part.p1._vars)
            )
        )
    diff_query += (
        ", p1.k_count as k_count\n"
        + "FROM "
        + __encode_table_name(part.p1)
        + " AS p1\n"
    )
    diff_query += "WHERE (" + ", ".join(
        f"p1.{var}"
        for var in sorted(
            part.p1._vars.intersection(part.p2._vars)
        )
    )
    diff_query += ") NOT IN (SELECT " + ", ".join(
        f"p2.{var}"
        for var in sorted(
            part.p1._vars.intersection(part.p2._vars)
        )
    )
    diff_query += (
        " FROM "
        + __encode_table_name(part.p2)
        + " AS p2)\n"
    )
    diff_query += "ON CONFLICT DO\nUPDATE SET\n\t"
    diff_query += (
        "k_count = EXCLUDED.k_count + k_count\n"
        + "WHERE "
        + " AND ".join(
            f"{var} = EXCLUDED.{var}"
            for var in sorted(part.p1._vars)
        )
    )
    if part.p2._vars.difference(part.p1._vars) != set():
        diff_query += " AND " + " AND ".join(
            f"{var} = EXCLUDED.{var}"
            for var in sorted(
                part.p2._vars.difference(part.p1._vars)
            )
        )
    diff_query += ";\n"

    return diff_query


def left_join_query(part: CompValue) -> str:
    """Generates the leftjoin query.

    Args:
        part (CompValue): Current part of the query.

    Returns:
        str: Query string for the leftjoin operation.
    """
    leftjoin_join: str = __join_query(part)
    leftjoin_diff: str = __diff_query_sub(part)

    return leftjoin_join + leftjoin_diff


def minus_query(part: CompValue) -> str:
    """Generates the minus query.

    Args:
        part (CompValue): Current part of the query.

    Returns:
        str: Query string for the minus operation.
    """
    if part.p1._vars.intersection(part.p2._vars) == set():
        return (
            "INSERT INTO "
            + __encode_table_name(part)
            + " SELECT * FROM "
            + __encode_table_name(part.p1)
            + ";"
        )
    else:
        return __diff_query_sub(part)


def union_query(part: CompValue) -> str:
    """Generates the union query.

    Args:
        part (CompValue): Current part of the query.

    Returns:
        str: Query string containing the union operation.
    """
    union_query: str = (
        "INSERT INTO "
        + __encode_table_name(part)
        + "\n"
        + "SELECT "
        + ", ".join(
            f"(CASE WHEN r1.{var} IS NOT NULL THEN r1.{var} ELSE r2.{var} END) AS {var}"
            for var in sorted(part.p1._vars)
        )
        + ", coalesce(r1.k_count, 0) + coalesce(r2.k_count, 0) as k_count\n"
        + "FROM "
        + __encode_table_name(part.p1)
        + " AS r1 FULL OUTER JOIN "
        + __encode_table_name(part.p2)
        + " AS r2 ON "
    )
    union_query += " AND ".join(
        f"r1.{var} = r2.{var}"
        for var in sorted(
            part.p1._vars.intersection(part.p2._vars)
        )
    )
    union_query += ";\n"

    return union_query


def nu_queries(
    part: CompValue, use_PV: bool = False
) -> str:
    """Constructs a query for the nu table.

    Args:
        part (CompValue): Current part of the algebra

    Returns:
        str: Query string for the nu table.
    """
    """if use_PV:
        if part.PV is None:
            part.PV = part.p.PV
        variables = part.PV
    else:
        variables = part._vars

    nu_query: str = (
        "INSERT INTO nu_"
        + get_table_name(part)
        + "  ("
        + ", ".join(
            var
            for var in sorted(variables)
            if var != "k_count"
        )
        + ", k_count) select "
    )
    nu_query += ", ".join(
        "(CASE WHEN r1."
        + var
        + " NOT NULL THEN r1."
        + var
        + " ELSE r2."
        + var
        + " END) as "
        + var
        for var in sorted(variables)
        if var != "k_count"
    )
    nu_query += ", coalesce(r1.k_count, 0) + coalesce(r2.k_count, 0) as k_count"
    nu_query += (
        " from "
        + get_table_name(part)
        + " AS r1 FULL OUTER JOIN delta_"
        + get_table_name(part)
        + " AS r2 ON "
        + " AND ".join(
            f"r1.{var} = r2.{var}"
            for var in sorted(variables)
            if var != "k_count"
        )
        + " WHERE (coalesce(r1.k_count, 0) + coalesce(r2.k_count, 0)) > 0"
        + ";"
    )"""
    variables = part._vars
    if use_PV:
        if part.PV is None:
            part.PV = part.p.PV
        variables = part.PV

    nu_query_original: str = (
        " SELECT "
        + ", ".join(var for var in sorted(variables))
        + ", k_count FROM "
        + __encode_table_name(part)
        + ";"
    )
    nu_query = insert_into_w_select(
        "nu_prep_" + __encode_table_name(part),
        nu_query_original,
        variables,
    )

    # Query to add the delta
    nu_query_delta = (
        " SELECT "
        + ", ".join(var for var in sorted(variables))
        + ", k_count FROM delta_"
        + __encode_table_name(part)
        + ";"
    )
    nu_query += insert_into_w_select(
        "nu_prep_" + __encode_table_name(part),
        nu_query_delta,
        variables,
    )

    # Query to sum the k count
    sum_query: str = (
        "SELECT "
        + ", ".join(var for var in sorted(variables))
        + ", SUM(k_count) as k_count FROM nu_prep_"
        + __encode_table_name(part)
        + " GROUP BY "
        + ", ".join(var for var in sorted(variables))
    )
    sum_query_w_insert = insert_into_w_select(
        "nu_" + __encode_table_name(part),
        sum_query,
        variables,
    )
    nu_query += sum_query_w_insert
    nu_query += " HAVING SUM(k_count) > 0;"

    """# Remove unwanted records
    nu_query += (
        "DELETE FROM nu_"
        + __encode_table_name(part)
        + " WHERE k_count <= 0;"
    )"""

    return nu_query
