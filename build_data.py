from os.path import exists, join
from duckdb import DuckDBPyConnection
from rdflib.plugins.sparql import algebra, parser
from rdflib.plugins.sparql.parser import parseQuery
from rdflib.plugins.sparql.parserutils import CompValue
from rdflib.plugins.sparql.sparql import Query

from SQL_Constructor import base_constructor
from SQL_Constructor.base_constructor import (
    __encode_schema_name,
    __encode_table_name,
)
from SQL_Constructor.operation_constructor import (
    project_constructor as SQL_project,
    join_constructor as SQL_join,
    leftjoin_constructor as SQL_leftjoin,
    union_constructor as SQL_union,
)

from experiments.experiments import (
    load_table_in_graph,
    load_delta_table_in_graph,
)


def get_query_object(query: str) -> Query:
    query_tree = parseQuery(str(query))
    return algebra.translateQuery(query_tree)


def get_query_input(
    query_file_dir: str, q_query_object: Query
) -> str:
    query_input_dir: str = join(
        query_file_dir,
        "query_"
        + base_constructor.get_table_name(
            q_query_object.algebra
        ),
    )
    return query_input_dir


def readQueryFile(filename: str) -> str:
    """Read query file.

    Args:
        filename (str): filename to be read.
    """

    with open(filename, "r") as file:
        return file.read()


def build_data(
    input_dir: str,
    query: str,
    duckdb_conn: DuckDBPyConnection,
    data_file: str | None = None,
    delf: str | None = None,
    insf: str | None = None,
    delta_file: str | None = None,
    nu_file: str | None = None,
    csv: bool = False,
) -> None:
    """Builds up the data from the data file.

    Args:
        data_file (str): String containing the data file.
    """
    if csv:

        if data_file is None:
            raise ValueError(
                "Data file must be provided when using CSV"
            )
        load_table_in_graph(data_file, duckdb_conn)
        if delta_file is not None and nu_file is not None:
            load_delta_table_in_graph(
                delta_file, duckdb_conn, nu_file
            )

        return

    # import incremental_query_parser as iqp

    """query_input_dir: str = get_query_input(
        input_dir,
        get_query_object(readQueryFile(query)),
    )

    # Set up tables in case they don't exist
    # iqp.setup_tables(query_input_dir, duckdb_conn)

    # Read the data file and put original data into the database
    duckdb_conn.execute(
        f"CREATE TABLE IF NOT EXISTS G (s TEXT, p TEXT, o TEXT, k_count INT);"
    )
    duckdb_conn.execute(f"DELETE FROM G;")
    if data_file is not None:
        data: str = readQueryFile(data_file)
        iqp.insert_data(duckdb_conn, data)

    # Clear the delta G table
    iqp.create_delta_table(duckdb_conn, "delta_G")
    iqp.drop_delta_table(duckdb_conn, "delta_G")

    # Read the deleted data file and put deleted data into the database's delta G table.
    if delf is not None:
        del_data: str = readQueryFile(delf)
        iqp.insert_delete_delta_data(duckdb_conn, del_data)

    # Read the inserted data file and put inserted data into the database's delta G table.
    if insf is not None:
        ins_data: str = readQueryFile(insf)
        iqp.insert_insert_delta_data(duckdb_conn, ins_data)
    # Combine the original and deleted data into the new version of the data.
    iqp.insert_nu_data(duckdb_conn) """


def setup_query_files(
    query_str: str,
    output_dir: str,
) -> None:
    """Constructs the BGP queries and writes them to the output directory.

    Args:
        query_str (str): The query string to construct the BGP queries
        output_dir (str): The output directory to write the BGP queries to
        duckdb_con (DuckDBPyConnection): Connection to the database.
    """
    from SQL_Constructor import (
        SQL_initialize_queries as SQLiq,
    )

    # import incremental_query_parser as iqp
    from setup_queries import (
        get_query_output_dir,
        setup_tables,
    )
    from rdflib.plugins.sparql import algebra

    q_query_object: Query = get_query_object(
        readQueryFile(query_str)
    )
    # algebra.pprintAlgebra(q_query_object)

    # Output directory
    query_output_dir: str = get_query_output_dir(
        output_dir, q_query_object
    )

    SQLiq.build_queries(
        q_query_object.algebra,
        query_output_dir,
    )
    SQLiq.build_increm_queries(
        q_query_object.algebra,
        query_output_dir,
    )

    setup_tables(
        q_query_object.algebra,
        query_output_dir,
    )


def __findDropableTables(
    part_name: str, query_output_dir: str
) -> set[str]:
    """Finds all the tables to drop from build files.

    Args:
        part_name (str): Current part of the query.
        query_output_dir (str): Output directory where the SQL files are stored.

    Returns:
        list[str]: List of all tables to drop.
    """
    final_set: set[str] = set()

    normal_file = join(query_output_dir, part_name + ".sql")
    join_file = join(
        query_output_dir, part_name + "_join.sql"
    )

    # Normal file tables to drop
    def __splitTables(file_name: str) -> set[str]:
        curr_query = readQueryFile(file_name)
        rtn_set: set[str] = set()
        for line in curr_query.split("\n"):
            if "CREATE " in line:
                split_line = line.split()
                for i in range(len(split_line)):
                    if split_line[i] == "TABLE":
                        rtn_set.add(split_line[i + 1])
        return rtn_set

    final_set |= __splitTables(normal_file)

    # Join file tables to drop
    if exists(join_file):
        final_set |= __splitTables(join_file)

    return final_set


def drop_all_tables_str(
    part: CompValue,
    schemas: list[set[str]],
    query_input_dir: str,
) -> tuple[str, str, str]:
    """Generates the drop table queries.

    Args:
        part (CompValue): Current part of the query
        schemas (list[set[str]]): Schemas of this part of the query

    Returns:
        tuple[str, str, str]: All drop table queries for this part.
    """
    drop_queries, drop_delta_queries, drop_nu_queries = (
        "",
        "",
        "",
    )
    for sch in schemas:
        if len(schemas) == 1:
            schema_suffix = ""
        else:
            schema_suffix = "_" + __encode_schema_name(
                str(sorted(sch))
            )

        drop_query: str = (
            "DROP TABLE IF EXISTS "
            + __encode_table_name(part)
            + schema_suffix
            + ";"
        )

        """ drop_delta_query: str = (
            "DROP TABLE IF EXISTS delta_"
            + __encode_table_name(part)
            + schema_suffix
            + ";"
        ) """
        delta_set: set[str] = __findDropableTables(
            "delta_" + __encode_table_name(part),
            query_input_dir,
        )
        drop_delta_query: str = ""
        for table in delta_set:
            drop_delta_query += (
                "DROP TABLE IF EXISTS " + table + ";"
            )

        drop_nu_query: str = (
            "DROP TABLE IF EXISTS nu_"
            + __encode_table_name(part)
            + schema_suffix
            + ";"
        )
        for nu_i in range(2):
            drop_nu_query += (
                "DROP TABLE IF EXISTS nu_"
                + __encode_table_name(part)
                + schema_suffix
                + "_"
                + str(nu_i)
                + ";"
            )

        drop_queries += drop_query + "\n"
        drop_delta_queries += drop_delta_query + "\n"
        drop_nu_queries += drop_nu_query + "\n"

    return (
        drop_queries,
        drop_delta_queries,
        drop_nu_queries,
    )


def drop_all_tables(
    part: CompValue,
    schemas: list[set[str]],
    query_input_dir: str,
) -> tuple[str, str]:
    (
        drop_query,
        drop_delta_query,
        drop_nu_query,
    ) = drop_all_tables_str(part, schemas, query_input_dir)
    """delta_table_drop_query, delta_prep_table_drop_query = (
        base_constructor.drop_delta_table(part)
    ) """
    return (
        drop_query,
        drop_delta_query + "\n" + drop_nu_query,
    )


def dropTablesRec(
    part: CompValue, query_input_dir: str
) -> tuple[str, str, list[set[str]]]:
    """Recursively go through all tables to setup to drop them file.

    Args:
        part (CompValue): Current part of the query.

    Returns:
        tuple[str, list[set[str]]]: Tuple containing the drop queries and the set of schemas
        from the child branch.
    """
    prev_query = ""
    prev_delta_query = ""
    if part is None:
        return prev_query, prev_delta_query, []
    if "p" in part or part.name == "BGP":
        prev_query, prev_delta_query, schemas1 = (
            dropTablesRec(part.p, query_input_dir)
        )
    elif "p1" in part and "p2" in part:
        prev_query1, prev_delta_query1, schemas1 = (
            dropTablesRec(part.p1, query_input_dir)
        )
        prev_query2, prev_delta_query2, schemas2 = (
            dropTablesRec(part.p2, query_input_dir)
        )
        prev_query = prev_query1 + "\n" + prev_query2
        prev_delta_query = (
            prev_delta_query1 + "\n" + prev_delta_query2
        )

    # Return with right schemas
    match part.name:
        case "BGP":
            curr_schemas: list[set[str]] = [part._vars]
        case "Filter":
            curr_schemas = schemas1
        case "Project":
            curr_schemas = SQL_project.project_schemas(
                part, schemas1
            )
        case "Join":
            curr_schemas: list[set[str]] = (
                SQL_join.join_schemas(schemas1, schemas2)
            )
        case "LeftJoin":
            curr_schemas: list[set[str]] = (
                SQL_leftjoin.leftjoin_schemas(
                    schemas1, schemas2
                )
            )
        case "Union":
            curr_schemas: list[set[str]] = (
                SQL_union.union_schemas(schemas1, schemas2)
            )
        case "Minus":
            curr_schemas: list[set[str]] = schemas1
        case "SelectQuery":
            curr_schemas = schemas1
        case _:
            raise NotImplementedError(
                f"Drop tables for {part.name} not implemented"
            )

    # Construct the drop query for the current part
    curr_drop_query, curr_drop_delta_query = (
        drop_all_tables(part, curr_schemas, query_input_dir)
    )
    drop_query = prev_query + "\n" + curr_drop_query
    drop_delta_query = (
        prev_delta_query + "\n" + curr_drop_delta_query
    )

    return drop_query, drop_delta_query, curr_schemas


def getJoinOrNormalFile(query_file_name: str) -> str:
    """Get the join or normal file name.

    Args:
        query_file_name (str): The query file name.

    Returns:
        str: The join or normal file name.
    """
    if exists(query_file_name + "_join.sql"):
        return query_file_name + "_join.sql"
    else:
        return query_file_name + ".sql"


if __name__ == "__main__":
    import sys, os
    import argparse

    hashseed = os.getenv("PYTHONHASHSEED")
    if not hashseed:
        os.environ["PYTHONHASHSEED"] = "0"
        os.execv(
            sys.executable, [sys.executable] + sys.argv
        )

    # Connection to database
    import duckdb

    # Parse the arguments
    parser = argparse.ArgumentParser(
        description="Sets up the data.",
        prog="build_data.py",
        epilog="The program needs a query, data file, insertions and/or deletions file to run properly.",
    )
    parser.add_argument("query", help="The query to test")
    parser.add_argument(
        "output",
        help="The output directory to grab the tables from",
    )
    parser.add_argument(
        "-d",
        "--data",
        dest="data",
        help="The data file",
    )
    parser.add_argument(
        "-dl",
        "--delf",
        dest="deletion_file",
        help="The file containing deletions",
    )
    parser.add_argument(
        "-i",
        "--insf",
        dest="insert_file",
        help="The file containing insertions",
    )
    parser.add_argument(
        "-db",
        "--db",
        dest="db",
        help="The database to connect to",
        default="./database/k_values.db",
    )
    parser.add_argument(
        "-s",
        "--setup",
        action="store_true",
        help="Set up the base graphs",
    )

    args = parser.parse_args()

    setup_query_files(args.query, args.output)

    if args.setup:
        try:
            # Connect to the database
            duckdb_conn = duckdb.connect(args.db)
        except Exception as e:
            print(f"Error connecting to the database: {e}")
            sys.exit(1)

        build_data(
            args.output,
            args.query,
            duckdb_conn,
            args.data,
            args.deletion_file,
            args.insert_file,
        )
