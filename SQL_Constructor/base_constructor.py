"""Modules to get SQL queries from SPARQL algebra parts."""

from rdflib.plugins.sparql.sparql import FrozenBindings
from rdflib.plugins.sparql.parserutils import (
    CompValue,
)

from pandas import DataFrame

from SQL_Constructor.table_constructor import (
    create_table_w_select,
    __create_vars,
    __encode_table_name,
    insert_into_w_select,
)


def get_create_vars(variables: set) -> str:
    """Gets the create variables for the SQL table.

    Args:
        variables (set): Set of variables to create in the SQL table.

    Returns:
        str: Variables to create in the SQL table.
    """
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

    select_part = "SELECT "
    select_part += ", ".join(
        f"(CASE WHEN R{index}.{var} NOT NULL THEN "
        + f"R{index}.{var} ELSE R{double_index}.{var} END) AS {var}"
        for var in known_vars
        if var != "k_count"
    )
    select_part += (
        f", (CASE WHEN R{index}.k_count IS NULL THEN R "
        + f"{double_index}.k_count WHEN R{double_index}.k_count IS "
        + f"NULL THEN R{index}.k_count ELSE R{index}.k_count + "
        + f"R{double_index}.k_count END) AS k_count "
    )

    return select_part + from_part + ";"


def count_k_counts_together(
    schema: set[str],
    to_table: str,
    from_table: str,
    is_delta: bool = False,
) -> str:
    """Counts the k_counts of a already inserted table.

    Args:
        schemas (list[set[str]]): Schemas of the part
        to_table (str): Table to insert into
        from_table (str): Table to select from

    Returns:
        str: Summed k_counts query
    """
    curr_count_query: str = "SELECT "
    if schema:
        curr_count_query += (
            ", ".join(f"r1.{var}" for var in sorted(schema))
            + ", SUM(r1.k_count) as k_count\n"
        )
    else:
        curr_count_query += "SUM(r1.k_count) as k_count\n"
    curr_count_query += "FROM " + from_table + " AS r1\n"
    if schema:
        curr_count_query += "GROUP BY " + ", ".join(
            f"r1.{var}" for var in sorted(schema)
        )
        if is_delta:
            curr_count_query += (
                " HAVING SUM(r1.k_count) != 0"
            )
        else:
            curr_count_query += (
                " HAVING SUM(r1.k_count) > 0"
            )
    curr_count_query += ";\n"

    return create_table_w_select(to_table, curr_count_query)


def schema_in_key(key: str, schema: set[str]) -> bool:
    """Checks if the schema is in the key.

    Args:
        key (str): The key to check
        schema (list[set[str]]): The schema to check

    Returns:
        bool: True if the schema is in the key, False otherwise.
    """
    split_schema_check = key.split("_schema_")[-1]
    return (
        "schema_" + split_schema_check
        == __encode_schema_name(str(sorted(schema)))
    )


def __get_schema(
    schemas: list[set[str]], key: str, is_select: bool
) -> set[str]:
    """Gets the schema for the given key.

    Args:
        schemas (list[set[str]]): List of schemas to check
        key (str): Key to check the schema for
        is_select (bool): Bool to indicate if it is a select query

    Returns:
        set[str]: Current schema for the key.
    """
    if len(schemas) == 1:
        curr_schema = schemas[0]
    elif is_select:
        curr_schema = set()
        for schema in schemas:
            curr_schema = curr_schema.union(schema)
    else:
        for schema in schemas:
            if schema_in_key(key, schema):
                curr_schema = schema

    return curr_schema


def make_join(
    tables_to_make: dict[str, list[str]],
    schemas: list[set[str]],
    is_delta: bool = False,
    is_select: bool = False,
    select_schema: set[str] | None = None,
    new_table_name: str | None = None,
) -> str:
    """Generates the join query string.

    Args:
        tables_to_make (dict[str, list[str]]): The dictionary with tables to make.
        schemas (list[set[str]]): Schemas of the part
        is_delta (bool, optional): Bool to indicate it is a delta. Defaults to False.
        is_select (bool, optional): Bool to indicate it is a select. Defaults to False.
        select_schema (set[str] | None, optional): Selection schema. Defaults to None.

    Returns:
        str: Join query string.
    """
    if select_schema is None:
        select_schema = set()

    print(schemas, tables_to_make)
    if (
        len(schemas) == 1
        and len(tables_to_make) == 1
        and len(
            tables_to_make[list(tables_to_make.keys())[0]]
        )
        == 2
    ):
        if new_table_name is not None:
            return final_outer_join_query(
                list(tables_to_make.keys())[0][0],
                list(tables_to_make.keys())[0][1],
                schemas[0],
                "nu_ " + new_table_name,
                is_delta=is_delta,
                is_select=is_select,
            )

    all_queries: str = ""
    for key in tables_to_make:
        curr_schema = __get_schema(schemas, key, is_select)

        last_made_temp_query: str = ""
        for q_index in range(len(tables_to_make[key])):
            if len(tables_to_make[key]) == 1:
                temp_prefix = ""
                key_suffix = ""
            else:
                temp_prefix = " TEMP "
                key_suffix = "_" + str(q_index)
            all_queries += create_table_w_select(
                key + key_suffix,
                tables_to_make[key][q_index],
                temp_prefix=temp_prefix,
            )
            if len(tables_to_make[key]) == 1:
                continue
            if (
                q_index == 1
                and len(tables_to_make[key]) > 1
                and q_index < len(tables_to_make[key]) - 1
            ):
                all_queries += outer_join_queries(
                    key + "_temp_" + str(q_index),
                    key + "_" + str(q_index - 1),
                    key + "_" + str(q_index),
                    curr_schema,
                )
                last_made_temp_query = (
                    key + "_temp_" + str(q_index)
                )
            elif (
                q_index > 1
                and q_index < len(tables_to_make[key]) - 1
            ):
                all_queries += outer_join_queries(
                    key + "_temp_" + str(q_index),
                    last_made_temp_query,
                    key + "_" + str(q_index),
                    curr_schema,
                )
                last_made_temp_query: str = (
                    key + "_temp_" + str(q_index)
                )
            elif q_index == len(tables_to_make[key]) - 1:
                if select_schema:
                    curr_schema = select_schema
                all_queries += final_outer_join_query(
                    last_made_temp_query,
                    key + "_" + str(q_index),
                    curr_schema,
                    key,
                    is_delta=is_delta,
                    is_select=is_select,
                )
            else:
                last_made_temp_query = (
                    key + "_" + str(q_index)
                )
    return all_queries


def make_group_by(
    tables_to_make: dict[str, list[str]],
    schemas: list[set[str]],
    is_delta: bool = False,
) -> str:
    """Generates the group by query string.

    Args:
        tables_to_make (dict[str, list[set[str]]]): Dictionary with key
        being to table to write to and value being all queries that need
        to be unioned in the table.
        schemas (list[set[Variable]]): List of schemas
        to use for group by

    Returns:
        str: Minus query string with group by.
    """
    all_queries: str = ""
    for key in tables_to_make:
        queries_seen_count = 0
        prep_prefix = ""
        for query in tables_to_make[key]:
            if len(tables_to_make[key]) == 1:
                temp_prefix = ""
                prep_prefix = ""
            else:
                temp_prefix = " TEMP "
                prep_prefix = "prep_"

            if queries_seen_count == 0:
                all_queries += create_table_w_select(
                    prep_prefix + key,
                    query,
                    temp_prefix=temp_prefix,
                )
            else:
                curr_schema = None
                for schema in schemas:
                    if (
                        schema_in_key(key, schema)
                        or len(schemas) == 1
                    ):
                        curr_schema = list(schema)
                all_queries += insert_into_w_select(
                    prep_prefix + key,
                    query,
                    curr_schema,
                )
            queries_seen_count += 1
        if len(tables_to_make[key]) == 1:
            continue
        for schema in schemas:
            if (
                schema_in_key(key, schema)
                or len(schemas) == 1
            ):
                all_queries += count_k_counts_together(
                    schema, key, prep_prefix + key, is_delta
                )
    return all_queries


def combine_dict_queries(
    diff_queries1: dict[str, list[str]],
    diff_queries2: dict[str, list[str]],
) -> dict[str, list[str]]:
    """Combines two dictionaries of queries.

    Args:
        diff_queries1 (dict[str, list[str]]): First dictionary of queries.
        diff_queries2 (dict[str, list[str]]): Second dictionary of queries.

    Returns:
        str: Combined dictionary of queries.
    """
    for key, value in diff_queries2.items():
        if key in diff_queries1:
            diff_queries1[key] += value
        else:
            diff_queries1[key] = value
    return diff_queries1


def add_table_to_dict(
    new_table_name: str,
    query: str,
    dict_queries: dict[str, list[str]],
) -> dict[str, list[str]]:
    """Adds a table to the dictionary of queries.

    Args:
        new_table_name (str): Key of the dictionary.
        query (str): Query to add.
        dict_queries (dict[str, list[str]]): Dictionary containing all queries
        related to the table name.

    Returns:
        dict[str, list[str]]: Dictionary with table added.
    """
    if new_table_name in dict_queries:
        dict_queries[new_table_name].append(query)
    else:
        dict_queries[new_table_name] = [query]
    return dict_queries


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


def add_on_conflict_insert_clause(
    solution_mapping: FrozenBindings,
    sorted_variables: list,
) -> str:
    """Adds the ON CONFLICT clause to the insert query.

    Args:
        solution_mapping (FrozenBindings): Given solution mapping
        sorted_variables (list): Sorted variables to use in the ON CONFLICT clause.

    Returns:
        str: ON CONFLICT clause to add to the insert query.
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
    """Constructs the BGP insert query for the given part.

    Args:
        part (CompValue): Current part of the algebra
        filled_in_triples (list[tuple[str, str, str]]): Filled in triples to insert.

    Returns:
        str: Query to insert the filled in triples into the BGP table.
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
            f"{var}" for var in sorted(part.get("vars"))
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
            f"{var}" for var in sorted(part.get("vars"))
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
                for var in sorted(part.get("vars"))
                if var != "k_count"
            )
            + ")"
        )


def final_outer_join_query(
    left_query: str,
    right_query: str,
    schema: set[str],
    new_table_name: str,
    is_delta: bool = False,
    is_select: bool = False,
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
    join_query: str = ""
    if not is_select:
        join_query += (
            "CREATE TABLE " + new_table_name + " AS "
        )
    join_query += "SELECT "
    if schema:
        join_query += ", ".join(
            f"(CASE WHEN R1.{var} NOT NULL THEN R1.{var} ELSE R2.{var} END) AS {var}"
            for var in schema
            if var != "k_count"
        )
        join_query += ", "
    join_query += (
        "(CASE WHEN R1.k_count IS NULL THEN R2.k_count"
        + " WHEN R2.k_count IS NULL THEN R1.k_count ELSE"
        + " R1.k_count + R2.k_count END) AS k_count "
    )
    join_query += f"FROM {left_query} AS R1 FULL OUTER JOIN {right_query} AS R2"
    if schema:
        join_query += " ON "
        join_query += " AND ".join(
            f"R1.{var} = R2.{var}"
            for var in schema
            if var != "k_count"
        )
        if is_delta:
            join_query += " WHERE coalesce(R1.k_count, 0) + coalesce(R2.k_count, 0) != 0"
        else:
            join_query += " WHERE coalesce(R1.k_count, 0) + coalesce(R2.k_count, 0) > 0"
    join_query += ";\n"
    return join_query


def outer_join_queries(
    delta_table_name: str,
    left_query: str,
    right_query: str,
    known_vars: set[str],
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
    join_query += (
        ", (CASE WHEN R1.k_count IS NULL THEN R2.k_count"
        + " WHEN R2.k_count IS NULL THEN R1.k_count ELSE R1.k_count"
        + " + R2.k_count END) AS k_count "
    )
    join_query += f"FROM {left_query} AS R1 FULL OUTER JOIN {right_query} AS R2 ON "
    join_query += " AND ".join(
        f"R1.{var} = R2.{var}"
        for var in known_vars
        if var != "k_count"
    )
    join_query += ";"
    return join_query


def insert_delta_query(
    part: CompValue,
    results: DataFrame,
    increm_table_name_part: str = "",
) -> str:
    """Inserts the results into the delta table.

    Args:
        part (CompValue): Current part of the query
        results (DataFrame): Results to insert into the delta table
        increm_table_name_part (str, optional): Incremental table name. Defaults to "".

    Returns:
        str: Query string
    """
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
    """Inserts the results into the table.

    Args:
        part (CompValue): Current part of the query
        results (DataFrame): Results to insert into the table
        increm_table_name_part (str, optional): Incremental table name. Defaults to "".

    Returns:
        str: Query string
    """
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
    """Insert BGP results into the table.

    Args:
        part (CompValue): Current part of the query
        results (DataFrame): Results to insert into the table

    Returns:
        str: Query string to insert the results into the BGP table.
    """
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


def project_table_query(part: CompValue) -> str:
    """Projects the table based on the given part.

    Args:
        part (CompValue): Current part of the query

    Returns:
        str: Query to project the table.
    """
    table_name: str = __encode_table_name(part.p)
    project_str: str = (
        "SELECT "
        + ", ".join(var for var in part.PV)
        + ", k_count FROM "
        + table_name
        + ";"
    )
    return project_str


def __final_schema(schemas1: list[set[str]]) -> set[str]:
    """Generates the final schema for the select query part.

    Args:
        schemas1 (list[set[str]]): Given schemas of endresult.

    Returns:
        str: One return schema.
    """
    final_schema: set[str] = set()
    for schema in schemas1:
        final_schema = final_schema.union(schema)
    return final_schema


def __construct_select_query_mult_schemas(
    schema: set[str],
    final_schema: set[str],
    table_name: str,
) -> str:
    """Construct the select query if multiple schemas are present

    Args:
        schema (set[str]): Schema of the current table
        final_schema (set[str]): Final schema of the table
        table_name (str): Name of the table to select from

    Returns:
        str: Query to construct the select query.
    """
    select_str: str = "SELECT "
    for var in sorted(final_schema):
        if var in schema:
            select_str += var + ", "
        else:
            select_str += (
                "CAST(NULL AS VARCHAR) AS " + var + ", "
            )
    select_str += "k_count FROM "
    select_str += table_name + ";"
    return select_str


def select_query(
    part: CompValue,
    schemas: list[set[str]],
    prefix: str = "",
) -> str:
    """Select query for the given part of the algebra.

    Args:
        part (CompValue): Current part of the query
        schemas (list[set[str]]): Current schemas of the part
        prefix (str, optional): Prefix part. Defaults to "".

    Returns:
        str: Selection query for the part.
    """
    table_name = prefix + __encode_table_name(part.p)
    select_table_name = prefix + __encode_table_name(part)

    if len(schemas) == 1:
        return (
            f"CREATE TABLE {select_table_name} AS SELECT "
            + ", ".join(var for var in sorted(schemas[0]))
            + f" FROM {table_name};"
        )
    else:
        final_schema = __final_schema(schemas)
        select_dict: dict[str, list[str]] = dict()
        for schema in schemas:
            new_table_name: str = (
                table_name
                + "_"
                + __encode_schema_name(str(sorted(schema)))
            )
            if select_table_name not in select_dict:
                select_dict[select_table_name] = [
                    __construct_select_query_mult_schemas(
                        schema, final_schema, new_table_name
                    )
                ]
            else:
                select_dict[select_table_name].append(
                    __construct_select_query_mult_schemas(
                        schema, final_schema, new_table_name
                    )
                )

        select_str: str = make_join(
            select_dict,
            schemas,
            is_select=False,
            select_schema=final_schema,
        )
        return select_str


def delta_select_query(
    part: CompValue,
    schemas: list[set[str]],
) -> str:
    """Delta select query for the given part of the algebra.

    Args:
        part (CompValue): Current part of the query
        schemas (list[set[str]]): Schemas of the part

    Returns:
        str: Query string for the delta select query.
    """
    return select_query(part, schemas, "delta_")


def nu_queries(
    part: CompValue, schemas: list[set[str]]
) -> tuple[str, str]:
    """Constructs a query for the nu table.

    Args:
        part (CompValue): Current part of the algebra

    Returns:
        str: Query string for the nu table.
    """

    dict_nu_queries: dict[str, list[str]] = dict()

    if len(schemas) == 1:
        dict_nu_queries = add_table_to_dict(
            "nu_" + __encode_table_name(part),
            f"SELECT * FROM {__encode_table_name(part)};",
            dict_nu_queries,
        )
        dict_nu_queries = add_table_to_dict(
            "nu_" + __encode_table_name(part),
            f"SELECT * FROM delta_{__encode_table_name(part)};",
            dict_nu_queries,
        )
    else:
        for schema in schemas:
            schemas_suffix: str = __encode_schema_name(
                str(sorted(schema))
            )
            curr_table_name = (
                __encode_table_name(part)
                + "_"
                + schemas_suffix
            )
            dict_nu_queries = add_table_to_dict(
                "nu_" + curr_table_name,
                f"SELECT * FROM {curr_table_name};",
                dict_nu_queries,
            )
            dict_nu_queries = add_table_to_dict(
                "nu_" + curr_table_name,
                f"SELECT * FROM delta_{curr_table_name};",
                dict_nu_queries,
            )

    nu_query: str = make_join(
        dict_nu_queries,
        schemas,
        new_table_name="nu_" + __encode_table_name(part),
    )

    nu_query_groupby: str = make_group_by(
        dict_nu_queries,
        schemas,
    )

    return nu_query, nu_query_groupby
