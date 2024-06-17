import duckdb
from rdflib.graph import Graph
from pandas import DataFrame


def build_query_string_for_data(
    g: Graph, table_name: str
) -> str:
    """Builds the string for the insertion"""
    rdf_input_data = ""
    known_tuples: dict[tuple[str, str, str], int] = dict()
    for s, p, o in g:
        if (s, p, o) in known_tuples:
            known_tuples[(str(s), str(p), str(o))] += 1
        else:
            known_tuples[(str(s), str(p), str(o))] = 1
    for s, p, o in known_tuples:
        rdf_input_data += f"('{s}', '{p}', '{o}', {known_tuples[(s, p, o)]}),\n"
    insert_str = (
        f"INSERT INTO {table_name} VALUES {rdf_input_data};"
    )
    return insert_str


def insert_data(
    db_conn: duckdb.DuckDBPyConnection, data: str
) -> None:
    """Build up a query string to insert data into a table.


    Args:
        db_conn (duckdb.DuckDBPyConnection): Database connection object.
        data (str): Given data to insert into the table.
    """
    table_name: str = "G"
    g: Graph = Graph().parse(data=data)
    insert_data_query: str = build_query_string_for_data(
        g, table_name
    )

    db_conn.execute(f"DROP TABLE IF EXISTS {table_name};")
    db_conn.execute(
        f"CREATE TABLE IF NOT EXISTS {table_name} (s TEXT, p TEXT, o TEXT, k_count INT);"
    )
    db_conn.execute(insert_data_query)

    df: DataFrame = db_conn.sql(
        f"SELECT * FROM {table_name};"
    ).df()
    print(df)


if __name__ == "__main__":
    from eval_incremental import duckdb_conn
    import sys

    if len(sys.argv) < 2:
        print("Usage: python setup_data.py <data_file>")
        sys.exit(1)

    data_file = sys.argv[1]
    with open(data_file, "r") as f:
        data = f.read()
    insert_data(duckdb_conn, data)
