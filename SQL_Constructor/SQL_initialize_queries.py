from rdflib.plugins.sparql.parserutils import CompValue
from SQL_Constructor import SQL_Constructor
from os.path import isdir


def create_table() -> str:
    """Create a table in the database"""
    create_str = "CREATE TABLE IF NOT EXISTS G (s TEXT, p TEXT, o TEXT, k_count INT);"
    return create_str


def create_delta_table() -> str:
    create_str = "CREATE TABLE IF NOT EXISTS delta_G (s TEXT, p TEXT, o TEXT, k_count INT);"
    return create_str


def create_nu_table() -> str:
    create_str = "CREATE TABLE IF NOT EXISTS nu_G (s TEXT, p TEXT, o TEXT, k_count INT);"
    return create_str


def __write_query_to_output_dir(
    part: CompValue,
    output_dir: str,
    query: str,
    filename: str,
    append: bool = False,
    name: str = "",
) -> None:
    """Writes the query to the output directory

    Args:
        part (CompValue): Current part of the query
        output_dir (str): Directory to write the SQL queries
        query (str): The query to write
    """
    if not append:
        with open(
            f"{output_dir}/{name}{filename}.sql",
            "w",
        ) as f:
            f.write(query)
    else:
        with open(
            f"{output_dir}/{name}{filename}.sql",
            "a",
        ) as f:
            f.write(query)


def __delta_bgp_queries(part: CompValue) -> list[str]:
    """Builds up the different delta BGP queries for the incremental query.

    Args:
        part (CompValue): Current part of the query

    Returns:
        list[str]: List of the delta queries for the BGP
    """
    delta_queries: list[str] = list()
    for triple_index in range(len(part.triples)):
        delta_queries.append(
            SQL_Constructor.bgp_delta_table_query(
                part, triple_index + 1
            )
        )
    return delta_queries


def build_increm_queries(
    part: CompValue,
    output_dir: str,
    schemas: dict[str, list[list[str]]],
) -> None:
    """Builds up the different incremental queries provided by the query.

    Args:
        part (CompValue): Current part of the query
        output_dir (str): Directory to write the SQL queries
    """
    if "p" in part:
        build_increm_queries(part.p, output_dir, schemas)
    elif "p1" in part and "p2" in part:
        build_increm_queries(part.p1, output_dir, schemas)
        build_increm_queries(part.p2, output_dir, schemas)
    # Construct the SQL query
    match part.name:
        case "BGP":
            bgp_queries: list[str] = __delta_bgp_queries(
                part
            )
            first: bool = True
            for query in bgp_queries:
                if first:
                    __write_query_to_output_dir(
                        part,
                        output_dir,
                        query,
                        SQL_Constructor.get_table_name(
                            part
                        ),
                        name="delta_",
                    )
                    first = False
                else:
                    __write_query_to_output_dir(
                        part,
                        output_dir,
                        query,
                        SQL_Constructor.get_table_name(
                            part
                        ),
                        True,
                        name="delta_",
                    )
        case "Filter":
            filter_delta_query: str = (
                SQL_Constructor.delta_filter_query(part)
            )
            __write_query_to_output_dir(
                part,
                output_dir,
                filter_delta_query,
                SQL_Constructor.get_table_name(part),
                name="delta_",
            )
        case "Project":
            project_delta_query: str = (
                SQL_Constructor.delta_project_query(part)
            )
            __write_query_to_output_dir(
                part,
                output_dir,
                project_delta_query,
                SQL_Constructor.get_table_name(part),
                name="delta_",
            )
        case "LeftJoin":
            leftjoin_delta_queries: list[str] = (
                SQL_Constructor.delta_leftjoin_query(
                    part, schemas
                )
            )
            first = True
            for leftjoin_query in leftjoin_delta_queries:
                if first:
                    __write_query_to_output_dir(
                        part,
                        output_dir,
                        leftjoin_query,
                        SQL_Constructor.get_table_name(
                            part
                        ),
                        name="delta_",
                    )
                    first = False
                else:
                    __write_query_to_output_dir(
                        part,
                        output_dir,
                        leftjoin_query,
                        SQL_Constructor.get_table_name(
                            part
                        ),
                        True,
                        name="delta_",
                    )
        case "Minus":
            minus_delta_query: list[dict[str, str]] = (
                SQL_Constructor.delta_minus_query(
                    part, schemas
                )
            )
            first = True
            for minus_query in minus_delta_query:
                if first:
                    for key in minus_query:
                        __write_query_to_output_dir(
                            part,
                            output_dir,
                            minus_query[key],
                            key,
                            name="delta_",
                        )
                    first = False
                else:
                    for key in minus_query:
                        __write_query_to_output_dir(
                            part,
                            output_dir,
                            minus_query[key],
                            key,
                            True,
                            name="delta_",
                        )
        case "Union":
            union_delta_query: str = (
                SQL_Constructor.delta_union_query(part)
            )
            __write_query_to_output_dir(
                part,
                output_dir,
                union_delta_query,
                SQL_Constructor.get_table_name(part),
                name="delta_",
            )
        case "_":
            print("Didn't implement", part.name)


def build_queries(
    part: CompValue,
    output_dir: str,
    schemas: dict[str, list[list[str]]],
) -> None:
    """Builds up the different queries provided by the query.

    Args:
        part (CompValue): Current part of the query
        output_dir (str): Directory to write the SQL queries
    """
    if "p" in part:
        build_queries(part.p, output_dir, schemas)
    elif "p1" in part and "p2" in part:
        build_queries(part.p1, output_dir, schemas)
        build_queries(part.p2, output_dir, schemas)
    # Construct the SQL query
    if part.name == "BGP":
        bgp_query = SQL_Constructor.bgp_query(part, schemas)
        __write_query_to_output_dir(
            part,
            output_dir,
            bgp_query,
            SQL_Constructor.get_table_name(part),
        )
    elif part.name == "Filter":
        filter_query = SQL_Constructor.filter_query(
            part, schemas
        )
        __write_query_to_output_dir(
            part,
            output_dir,
            filter_query,
            SQL_Constructor.get_table_name(part),
        )
    elif part.name == "Project":
        project_query = SQL_Constructor.project_query(
            part, schemas
        )
        __write_query_to_output_dir(
            part,
            output_dir,
            project_query,
            SQL_Constructor.get_table_name(part),
        )
    elif part.name == "LeftJoin":
        leftjoin_query = SQL_Constructor.leftjoin_query(
            part, schemas
        )
        __write_query_to_output_dir(
            part,
            output_dir,
            leftjoin_query,
            SQL_Constructor.get_table_name(part),
        )
    elif part.name == "Minus":
        minus_query: dict[str, str] = (
            SQL_Constructor.minus_query(part, schemas)
        )
        for key in minus_query:
            __write_query_to_output_dir(
                part, output_dir, minus_query[key], key
            )
    elif part.name == "Union":
        union_query = SQL_Constructor.union_query(
            part, schemas
        )
        __write_query_to_output_dir(
            part,
            output_dir,
            union_query,
            SQL_Constructor.get_table_name(part),
        )
