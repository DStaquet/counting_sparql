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
        bgp_query = SQL_Constructor.bgp_table_query(part)
        print(bgp_query)
        __write_query_to_output_dir(
            part, output_dir, bgp_query
        )
