from rdflib.plugins.sparql.sparql import FrozenBindings
from rdflib.plugins.sparql.parserutils import (
    CompValue,
)


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


def delta_outer_join_long_query(
    part: CompValue, known_vars: set[str]
) -> str:
    """Builds up the query to join the delta tables together fully without
        intermediate tables.

    Args:
        part (CompValue): Current part of the query

    Returns:
        str: Query to join the delta tables together fully.
    """
    index: int = 0
    double_index: str = str(index) + "_" + str(index + 1)

    from_part = " FROM " + __from_clause_long_outer_join(
        part, index
    )

    select_part = f"SELECT "
    select_part += ", ".join(
        f"(CASE WHEN R{index}.{var} NOT NULL THEN R{index}.{var} ELSE R{double_index}.{var} END) AS {var}"
        for var in known_vars
        if var != "k_count"
    )
    select_part += f", (CASE WHEN R{index}.k_count IS NULL THEN R{double_index}.k_count WHEN R{double_index}.k_count IS NULL THEN R{index}.k_count ELSE R{index}.k_count + R{double_index}.k_count END) AS k_count "

    return select_part + from_part + ";"


def countKCountsTogether(
    part: CompValue,
    schemas: list[set[str]],
    to_table: str,
    from_table: str,
) -> str:
    """Counts the k_counts of a already inserted table.

    Args:
        part (CompValue): Current part of the query
        schemas (list[set[str]]): Schemas of the part
        to_table (str): Table to insert into
        from_table (str): Table to select from

    Returns:
        str: Summed k_counts query
    """
    count_queries: str = ""
    for schema in schemas:
        curr_count_query: str = (
            "SELECT "
            + ", ".join(
                f"r1.{var}" for var in sorted(schema)
            )
            + ", SUM(r1.k_count) as k_count\n"
            + "FROM "
            + from_table
            + " AS r1\n"
            + "GROUP BY "
            + ", ".join(
                f"r1.{var}" for var in sorted(schema)
            )
            + ";\n"
        )
        if len(schemas) > 1:
            count_queries += create_table_w_select(
                to_table
                + "_"
                + __encode_schema_name(str(sorted(schema))),
                curr_count_query,
            )
        else:
            count_queries += create_table_w_select(
                to_table, curr_count_query
            )

    return count_queries


def __create_vars(variables: set) -> str:
    var_str: str = ""
    for var in sorted(variables):
        if var == "k_count":
            continue
        var_str += "\t" + var + " VARCHAR(255),\n"
    var_str += "\tk_count INT\n"
    return var_str


def __serialize_to_json(part: CompValue | list[set]) -> str:
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


def __encode_schema_name(part: CompValue | str) -> str:
    """Builds the hash for the schema name.

    Args:
        part (CompValue | str): Current part of the algebra or
            string to hash the schema name.

    Returns:
        str: SQL schema name
    """
    if isinstance(part, str):
        return "schema_" + str(abs(hash(part)))
    else:
        return __encode_table_name(part)


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


def __from_clause_long_outer_join(
    part: CompValue, index: int
) -> str:
    """Recursive part to build the FROM clause for the long outer join query.

    Args:
        part (CompValue): Current part of the query
        index (int): Index to use in the query

    Returns:
        str: From clause for the long outer join query.
    """
    full_outer_join_part_query = (
        "delta_"
        + __encode_table_name(part)
        + "_"
        + str(index + 1)
    )

    if index == len(part.triples) - 1:
        return full_outer_join_part_query
    else:
        double_index: str = (
            str(index) + "_" + str(index + 1)
        )
        return (
            "("
            + full_outer_join_part_query
            + f" AS R{index} FULL OUTER JOIN "
            + __from_clause_long_outer_join(part, index + 1)
            + f" AS R{double_index} ON "
            + " AND ".join(
                f"R{double_index}.{var} = R{index}.{var}"
                for var in sorted(part._vars)
                if var != "k_count"
            )
            + ")"
        )


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
        create_str += ", k_count) AS\n" + select_query
        return create_str


def insert_into_w_select(
    given_table: str,
    select_query: str,
    columns: list[str] | None = None,
    sort: bool = True,
) -> str:
    if columns is None:
        return f"INSERT INTO {given_table}\n{select_query}"
    else:
        if sort:
            sorted_columns: list[str] = sorted(columns)
        else:
            sorted_columns: list[str] = columns
        insert_str: str = (
            f"INSERT INTO {given_table} ("
            + ", ".join(
                key
                for key in sorted_columns
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
    nu_query = create_table_w_select(
        "nu_prep_" + __encode_table_name(part),
        nu_query_original,
        variables,
        temp_prefix="TEMP",
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
    sum_query_w_insert = create_table_w_select(
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
