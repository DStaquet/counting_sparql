"""Modules to import"""

from rdflib.plugins.sparql.parserutils import CompValue


def values_var(res: list) -> str:
    """Gives the values for a query.

    Args:
        res (list): Vars.

    Returns:
        str: Query string part
    """
    known_vars: set = set()
    var_str: str = ""
    for elem in res:
        for assignment in elem:
            if assignment not in known_vars:
                var_str += "\t" + assignment + " VARCHAR(255),\n\tvalue VARCHAR(255),\n"
                known_vars.add(assignment)
    var_str += "\tPRIMARY KEY(" + "".join(x for x in known_vars) + ")\n"
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
        for var in sorted(part.get("_vars")):
            return_str += str(type(var)) + str(var)
        return (
            part.name
            + "_"
            + str(abs(hash(("".join(ltr for ltr in return_str if ltr.isalnum())))))
        )
    elif part.name == "values":
        return (
            part.name
            + "_"
            + str(abs(hash(("".join(x for x in str(part) if x.isalnum())))))
        )
    elif "PV" in part:
        for var in sorted(part.PV):
            return_str += str(type(var)) + str(var)
        return_str = "".join(x for x in return_str if x.isalnum())
    else:
        for var in sorted(part.get("_vars")):
            return_str += str(type(var)) + str(var)
        return_str = "".join(x for x in return_str if x.isalnum())
    if "p" in part:
        return (
            part.name
            + "_"
            + str(abs(hash((return_str + "__" + __encode_table_name(part.p)))))
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


def delete_all_tables(
    part: CompValue,
) -> tuple[str, str, str, str]:
    """Deletes all rows from the table.

    Args:
        part (CompValue): Current part of the query

    Returns:
        str: Returns the SQL query to delete all rows from the table.
    """
    delete_query: str = "DELETE FROM " + __encode_table_name(part) + ";"
    delete_delta_query: str = "DELETE FROM delta_" + __encode_table_name(part) + ";"
    delete_nu_query: str = "DELETE FROM nu_" + __encode_table_name(part) + ";"
    delete_nu_prep_query: str = "DELETE FROM nu_prep_" + __encode_table_name(part) + ";"

    return (
        delete_query,
        delete_delta_query,
        delete_nu_query,
        delete_nu_prep_query,
    )


def get_table_name(part: CompValue) -> str:
    """Gets the table name for the given part of the algebra.

    Args:
        part (CompValue): Current part of the algebra

    Returns:
        str: Table name
    """
    return __encode_table_name(part)


def __create_vars(variables: set) -> str:
    var_str: str = ""
    for var in sorted(variables):
        if var == "k_count":
            continue
        var_str += "\t" + var + " VARCHAR(255),\n"
    var_str += "\tk_count INT\n"
    return var_str


def make_tables(part, variables: set) -> tuple[str, str, str, str, str]:
    """Makes the SQL tables.

    Args:
        part (_type_): Current part of the algebra
        variables (set): Variables to use in the table

    Returns:
        tuple[str, str, str, str, str]: All different table creation queries.
    """
    if part.name == "BGP":
        # BGP old table
        create_table_str: str = (
            "CREATE TABLE IF NOT EXISTS " + __encode_table_name(part) + " (\n" + "\t"
        )
        for var in variables:
            create_table_str += var + " VARCHAR(255),\n\t"
        create_table_str += "k_count INT);\n"

        # BGP delta table
        create_table_delta_bgp: str = (
            "CREATE TABLE IF NOT EXISTS delta_"
            + __encode_table_name(part)
            + " (\n"
            + "\t"
        )
        for var in variables:
            create_table_delta_bgp += var + " VARCHAR(255),\n\t"
        create_table_delta_bgp += "k_count INT);\n"
        create_table_delta_prep: str = (
            "CREATE TABLE IF NOT EXISTS delta_prep_"
            + __encode_table_name(part)
            + " (\n"
            + "\t"
        )
        for var in variables:
            create_table_delta_prep += var + " VARCHAR(255),\n\t"
        create_table_delta_prep += "k_count INT);\n"
        create_table_nu_prep: str = (
            "CREATE TABLE IF NOT EXISTS nu_prep_"
            + __encode_table_name(part)
            + " (\n"
            + "\t"
        )
        for var in variables:
            create_table_nu_prep += var + " VARCHAR(255),\n\t"
        create_table_nu_prep += "k_count INT);\n"

        # BGP nu table
        create_table_bgp_nu: str = (
            "CREATE TABLE IF NOT EXISTS nu_" + __encode_table_name(part) + " (\n" + "\t"
        )
        for var in variables:
            create_table_bgp_nu += var + " VARCHAR(255),\n\t"
        create_table_bgp_nu += "k_count INT);\n"

    elif part.name == "values" or (
        part.name == "ToMultiSet" and "p" in part and part.p.name == "values"
    ):
        if part.name == "ToMultiSet":
            res: list = part.p.res
        else:
            res: list = part.res
        create_table_str: str = (
            "CREATE TABLE IF NOT EXISTS "
            + __encode_table_name(part)
            + " (\n"
            + values_var(res)
            + ");"
        )

        create_table_delta_bgp: str = (
            "CREATE TABLE IF NOT EXISTS delta_"
            + __encode_table_name(part)
            + " (\n"
            + values_var(res)
            + ");"
        )

        create_table_bgp_nu: str = (
            "CREATE TABLE IF NOT EXISTS nu_"
            + __encode_table_name(part)
            + " (\n"
            + values_var(res)
            + ");"
        )

    elif "PV" in part or (part.name == "Distinct" and "PV" in part.p):
        if part.name == "Distinct":
            variables = part.p.PV
        else:
            variables = part.PV
        create_table_str: str = (
            "CREATE TABLE IF NOT EXISTS "
            + __encode_table_name(part)
            + " (\n"
            + __create_vars(variables)
            + ");"
        )

        create_table_delta_bgp: str = (
            "CREATE TABLE IF NOT EXISTS delta_"
            + __encode_table_name(part)
            + " (\n"
            + __create_vars(variables)
            + ");"
        )
        create_table_delta_prep: str = (
            "CREATE TABLE IF NOT EXISTS delta_prep_"
            + __encode_table_name(part)
            + " (\n"
            + __create_vars(variables)
            + ");"
        )
        create_table_nu_prep: str = (
            "CREATE TABLE IF NOT EXISTS nu_prep_"
            + __encode_table_name(part)
            + " (\n"
            + __create_vars(variables)
            + ");"
        )

        create_table_bgp_nu: str = (
            "CREATE TABLE IF NOT EXISTS nu_"
            + __encode_table_name(part)
            + " (\n"
            + __create_vars(variables)
            + ");"
        )

    else:
        create_table_str: str = (
            "CREATE TABLE IF NOT EXISTS "
            + __encode_table_name(part)
            + " (\n"
            + __create_vars(variables)
            + ");"
        )

        create_table_delta_bgp: str = (
            "CREATE TABLE IF NOT EXISTS delta_"
            + __encode_table_name(part)
            + " (\n"
            + __create_vars(variables)
            + ");"
        )
        create_table_delta_prep: str = (
            "CREATE TABLE IF NOT EXISTS delta_prep_"
            + __encode_table_name(part)
            + " (\n"
            + __create_vars(variables)
            + ");"
        )
        create_table_nu_prep: str = (
            "CREATE TABLE IF NOT EXISTS nu_prep_"
            + __encode_table_name(part)
            + " (\n"
            + __create_vars(variables)
            + ");"
        )

        create_table_bgp_nu: str = (
            "CREATE TABLE IF NOT EXISTS nu_"
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


def delete_delta_table(part: CompValue) -> tuple[str, str]:
    """Deletes the delta table and the delta prep table.

    Args:
        part (CompValue): Current part of the algebra

    Returns:
        tuple[str, str]: Queries to delete the delta table and the delta prep table.
    """
    return (
        f"DELETE FROM delta_{__encode_table_name(part)};",
        f"DELETE FROM delta_prep_{__encode_table_name(part)};",
    )


def drop_delta_table(part: CompValue) -> tuple[str, str]:
    """Drops the delta table and the delta prep table.

    Args:
        part (CompValue): Current part of the algebra

    Returns:
        tuple[str, str]: Queries to drop the delta table and the delta prep table.
    """
    return (
        f"DROP TABLE IF EXISTS delta_{__encode_table_name(part)};",
        f"DROP TABLE IF EXISTS delta_prep_{__encode_table_name(part)};",
    )


def create_table_w_select(
    given_table: str,
    select_query: str,
    columns: list[str] | None = None,
    temp_prefix: str = "",
) -> str:
    """Creates a table with a select query.

    Args:
        given_table (str): _name of the table to create
        select_query (str): Select query to use for the table.
        columns (list[str] | None, optional): Add columns as key if given. Defaults to None.
        temp_prefix (str, optional): Word to set between CREATE and TABLE. Defaults to "".

    Returns:
        str: CREATE TABLE query string.
    """
    if columns is None:
        return f"CREATE {temp_prefix} TABLE {given_table} AS\n{select_query}"
    else:
        create_str: str = f"CREATE {temp_prefix} TABLE {given_table} (" + ", ".join(
            key for key in sorted(columns) if key != "k_count"
        )
        create_str += ", k_count) AS\n" + select_query
        return create_str


def insert_into_w_select(
    given_table: str,
    select_query: str,
    columns: list[str] | None = None,
    sort: bool = True,
) -> str:
    """Inserts into a table with a select query.

    Args:
        given_table (str): Given table to insert into
        select_query (str): Select query to add aftewards
        columns (list[str] | None, optional): Columns to add as keys if given. Defaults to None.
        sort (bool, optional): Indicate if the columns need to be sorted. Defaults to True.

    Returns:
        str: INSERT INTO query string.
    """
    if columns is None:
        return f"INSERT INTO {given_table}\n{select_query}"
    else:
        if sort:
            sorted_columns: list[str] = sorted(columns)
        else:
            sorted_columns: list[str] = columns
        insert_str: str = f"INSERT INTO {given_table} (" + ", ".join(
            key for key in sorted_columns if key != "k_count"
        )
        insert_str += ", k_count)\n" + select_query
        return insert_str


def build_delta_union_from_clause(
    first_table_name: str,
    second_table_name: str,
    r1_vars: set[str],
    r2_vars: set[str],
) -> str:
    """Builds up the FROM clause for the union delta table query.

    Args:
        first_table_name (str): First table name.
        second_table_name (str): Second table name.
        r1_vars (set[str]): Left side variables.
        r2_vars (set[str]): Right side variables.

    Returns:
        str: FROM clause for the union delta table query.
    """
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
    part1_table_name1: str = "delta_" + __encode_table_name(part.p1)
    part1_table_name2: str = __encode_table_name(part.p2)

    # First FROM clause
    part1_from_clause: str = build_delta_union_from_clause(
        part1_table_name1,
        part1_table_name2,
        r1_vars,
        r2_vars,
    )

    # Second FROM clause
    part2_table_name1: str = "nu_" + __encode_table_name(part.p1)
    part2_table_name2: str = "delta_" + __encode_table_name(part.p2)
    part2_from_clause: str = build_delta_union_from_clause(
        part2_table_name1,
        part2_table_name2,
        r1_vars,
        r2_vars,
    )

    # SELECT clause
    select_clause: str = "SELECT "
    # for _var in part.p1._vars.intersection(part.p2._vars):
    for _var in part.p1.get("_vars").intersection(part.p2.get("_vars")):
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
    for _var in part.p1.get("_vars").difference(part.p2.get("_vars")):
        select_clause += "r1." + _var + " AS " + _var + ", "
    for _var in part.p2.get("_vars").difference(part.p1.get("_vars")):
        select_clause += "r2." + _var + " AS " + _var + ", "
    select_clause += " coalesce(r1.k_count, 0) + coalesce(r2.k_count, 0) as k_count"

    first_query: str = select_clause + "\n" + part1_from_clause + ";\n"
    second_query: str = select_clause + "\n" + part2_from_clause + ";\n"

    return (first_query, second_query)


def union_table_query(part: CompValue, r1_vars: set[str], r2_vars: set[str]) -> str:
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
    for _var in part.p1.get("_vars").intersection(part.p2.get("_vars")):
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
    for _var in part.p1.get("_vars").difference(part.p2.get("_vars")):
        select_clause += "r1." + _var + " AS " + _var + ", "
    for _var in part.p2.get("_vars").difference(part.p1.get("_vars")):
        select_clause += "r2." + _var + " AS " + _var + ", "
    select_clause += " coalesce(r1.k_count, 0) + coalesce(r2.k_count, 0) as k_count"

    return select_clause + "\n" + from_clause + ";\n"
