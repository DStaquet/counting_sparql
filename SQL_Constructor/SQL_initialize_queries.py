from rdflib.plugins.sparql.parserutils import CompValue
from SQL_Constructor import SQL_Constructor


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
    part: CompValue, output_dir: str, query: str
) -> None:
    """Writes the query to the output directory

    Args:
        part (CompValue): Current part of the query
        output_dir (str): Directory to write the SQL queries
        query (str): The query to write
    """
    with open(
        f"{output_dir}/{SQL_Constructor.get_table_name(part)}.sql",
        "w",
    ) as f:
        f.write(query)


def build_queries(part: CompValue, output_dir: str) -> None:
    """Builds up the different queries provided by the query.

    Args:
        part (CompValue): Current part of the query
        output_dir (str): Directory to write the SQL queries
    """
    if "p" in part:
        build_queries(part.p, output_dir)
    elif "p1" in part and "p2" in part:
        build_queries(part.p1, output_dir)
        build_queries(part.p2, output_dir)
    # Construct the SQL query
    if part.name == "BGP":
        bgp_query = SQL_Constructor.bgp_query(part)
        __write_query_to_output_dir(
            part, output_dir, bgp_query
        )
    elif part.name == "Filter":
        filter_query = SQL_Constructor.filter_query(part)
        __write_query_to_output_dir(
            part, output_dir, filter_query
        )
    elif part.name == "Project":
        project_query = SQL_Constructor.project_query(part)
        __write_query_to_output_dir(
            part, output_dir, project_query
        )
    elif part.name == "LeftJoin":
        leftjoin_query = SQL_Constructor.leftjoin_query(
            part
        )
        __write_query_to_output_dir(
            part, output_dir, leftjoin_query
        )
    elif part.name == "Minus":
        minus_query = SQL_Constructor.minus_query(part)
        __write_query_to_output_dir(
            part, output_dir, minus_query
        )
    elif part.name == "Union":
        union_query = SQL_Constructor.union_query(part)
        __write_query_to_output_dir(
            part, output_dir, union_query
        )
