from rdflib.plugins.sparql.parserutils import CompValue
from SQL_Constructor import SQL_Constructor


def __write_query_to_output_dir(
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


def __delta_bgp_queries(part: CompValue) -> str:
    """Builds up the different delta BGP queries for the incremental query.

    Args:
        part (CompValue): Current part of the query

    Returns:
        list[str]: List of the delta queries for the BGP
    """
    delta_queries: str = ""
    for triple_index in range(len(part.triples)):
        delta_query: str = (
            SQL_Constructor.bgp_delta_table_query(
                part, triple_index + 1
            )
        )
        delta_queries += (
            SQL_Constructor.insert_into_w_select(
                "delta_"
                + SQL_Constructor.get_table_name(part),
                delta_query,
            )
        )
    return delta_queries


def build_increm_queries(
    part: CompValue, output_dir: str
) -> None:
    """Constructs the incremental queries

    Args:
        part (CompValue): Current part of the query
        output_dir (str): Where to write the SQL queries.
    """
    if "p" in part:
        build_increm_queries(part.p, output_dir)
    elif "p1" in part and "p2" in part:
        build_increm_queries(part.p1, output_dir)
        build_increm_queries(part.p2, output_dir)
    # Construct the SQL query
    match part.name:
        case "BGP":
            delta_queries = __delta_bgp_queries(part)
            __write_query_to_output_dir(
                output_dir,
                delta_queries,
                SQL_Constructor.get_table_name(part),
                False,
                "delta_",
            )
        case "Filter":
            filter_query: str = (
                SQL_Constructor.delta_filter_query(part)
            )
            __write_query_to_output_dir(
                output_dir,
                filter_query,
                SQL_Constructor.get_table_name(part),
                name="delta_",
            )
        case "Project":
            project_query: str = (
                SQL_Constructor.delta_project_query(part)
            )
            __write_query_to_output_dir(
                output_dir,
                project_query,
                SQL_Constructor.get_table_name(part),
                name="delta_",
            )
        case "LeftJoin":
            left_join_query: str = (
                SQL_Constructor.delta_left_join_query(part)
            )
            __write_query_to_output_dir(
                output_dir,
                left_join_query,
                SQL_Constructor.get_table_name(part),
                name="delta_",
            )
        case "Minus":
            minus_query: str = (
                SQL_Constructor.delta_minus_query(part)
            )
            __write_query_to_output_dir(
                output_dir,
                minus_query,
                SQL_Constructor.get_table_name(part),
                name="delta_",
            )
        case "Union":
            union_query: str = (
                SQL_Constructor.delta_union_query(part)
            )
            __write_query_to_output_dir(
                output_dir,
                union_query,
                SQL_Constructor.get_table_name(part),
                name="delta_",
            )


def build_queries(part: CompValue, output_dir: str) -> None:
    """Constructs the non_incremental queries

    Args:
        part (CompValue): Current part of the query
        output_dir (str): Where to write the SQL queries
    """
    if "p" in part:
        build_queries(part.p, output_dir)
    elif "p1" in part and "p2" in part:
        build_queries(part.p1, output_dir)
        build_queries(part.p2, output_dir)
    # Construct the SQL query
    match part.name:
        case "BGP":
            bgp_query: str = (
                SQL_Constructor.insert_into_w_select(
                    SQL_Constructor.get_table_name(part),
                    SQL_Constructor.bgp_table_query(part),
                )
            )
            __write_query_to_output_dir(
                output_dir,
                bgp_query,
                SQL_Constructor.get_table_name(part),
            )
        case "Filter":
            filter_query: str = (
                SQL_Constructor.filter_query(part)
            )
            __write_query_to_output_dir(
                output_dir,
                filter_query,
                SQL_Constructor.get_table_name(part),
            )
        case "Project":
            project_query: str = (
                SQL_Constructor.project_query(part)
            )
            __write_query_to_output_dir(
                output_dir,
                project_query,
                SQL_Constructor.get_table_name(part),
            )
        case "LeftJoin":
            left_join_query: str = (
                SQL_Constructor.left_join_query(part)
            )
            __write_query_to_output_dir(
                output_dir,
                left_join_query,
                SQL_Constructor.get_table_name(part),
            )
        case "Minus":
            minus_query: str = SQL_Constructor.minus_query(
                part
            )
            __write_query_to_output_dir(
                output_dir,
                minus_query,
                SQL_Constructor.get_table_name(part),
            )
        case "Union":
            union_query: str = SQL_Constructor.union_query(
                part
            )
            __write_query_to_output_dir(
                output_dir,
                union_query,
                SQL_Constructor.get_table_name(part),
            )
