import duckdb
from rdflib.graph import Graph

import csv


def create_table() -> str:
    create_str = "CREATE TABLE IF NOT EXISTS G (s TEXT, p TEXT, o TEXT, k_count INT);"
    return create_str


def create_delta_table() -> str:
    create_str = "CREATE TABLE IF NOT EXISTS delta_G (s TEXT, p TEXT, o TEXT, k_count INT);"
    return create_str


def create_nu_table() -> str:
    create_str = "CREATE TABLE IF NOT EXISTS nu_G (s TEXT, p TEXT, o TEXT, k_count INT);"
    return create_str


def insert_table(rdf_data: str, g: Graph) -> str:
    rdf_input_data = ""
    known_tuples: dict[tuple[str, str, str], int] = dict()
    for s, p, o in g:
        if (s, p, o) in known_tuples:
            known_tuples[(str(s), str(p), str(o))] += 1
        else:
            known_tuples[(str(s), str(p), str(o))] = 1
    for s, p, o in known_tuples:
        rdf_input_data += f"('{s}', '{p}', '{o}', {known_tuples[(s, p, o)]}),\n"
    insert_str = f"INSERT INTO G VALUES {rdf_input_data};"
    return insert_str


def insert_rdf_into_graph(
    rdf_data: str, g: Graph, duckdb_conn
) -> None:
    create_table_str = create_table()
    insert_str = insert_table(rdf_data, g)
    duckdb_conn.execute(create_table_str)
    duckdb_conn.execute(insert_str)


def make_tables(
    update_file: str, delete_file: str, duckdb_conn
) -> None:
    create_delta_table_str = create_delta_table()
    create_nu_table_str = create_nu_table()
    duckdb_conn.execute(create_delta_table_str)
    duckdb_conn.execute(create_nu_table_str)

    delta_simulation: str = simulate_delta_data(
        update_file, 1
    )
    duckdb_conn.execute(delta_simulation)
    delta_del_simulation: str = simulate_delta_data(
        delete_file, -1
    )
    duckdb_conn.execute(delta_del_simulation)

    duckdb_conn.execute(insert_nu_table())


# TODO simulate updates
def simulate_delta_data(
    update_file: str, delete_or_update: int
) -> str:
    query: str = (
        "insert into delta_G (s, p, o, k_count) VALUES "
    )
    with open(update_file, "r") as f:
        csvreader = csv.reader(f, delimiter=";")
        for line in csvreader:
            s, p, o = line[0], line[1], line[2]
            query += f"('{s}', '{p}', '{o}', {delete_or_update}),\n"

    return query


# TODO: correctly update simulations
def insert_nu_table() -> str:
    return "insert into nu_G (s, p, o, k_count) select r1.s, r1.p, r1.o, coalesce(r1.k_count, 0) + coalesce(r2.k_count, 0) as k_count from G as r1 FULL OUTER JOIN delta_G as r2 ON r1.s = r2.s and r1.p = r2.p and r1.o = r2.o where (coalesce(r1.k_count, 0) + coalesce(r2.k_count, 0)) > 0;"


def set_up_nu_table(duckdb_conn) -> None:
    drop_G = "DROP TABLE IF EXISTS G;"
    duckdb_conn.execute(drop_G)

    create_table_str = create_table()
    duckdb_conn.execute(create_table_str)

    insert_nu_in_g = "INSERT INTO G SELECT * FROM nu_G;"
    duckdb_conn.execute(insert_nu_in_g)


def drop_tables(duckdb_conn) -> None:
    duckdb_conn.execute("DROP TABLE IF EXISTS G;")
    duckdb_conn.execute("DROP TABLE IF EXISTS delta_G;")
    duckdb_conn.execute("DROP TABLE IF EXISTS nu_G;")


if __name__ == "__main__":

    with open("./data/dataset100.nt") as datafile:
        read_ttl_data: str = datafile.read()

    g: Graph = Graph()
    g.parse(data=read_ttl_data, format="ttl")

    size = 100

    duckdb_conn = duckdb.connect()

    set_up_nu_table(duckdb_conn)

    drop_tables(duckdb_conn)

    insert_rdf_into_graph(read_ttl_data, g, duckdb_conn)
    make_tables(
        f"./Queries/berlin_benchmark/{size}/medium_updates.csv",
        f"./Queries/berlin_benchmark/{size}/medium_deletes.csv",
        duckdb_conn,
    )
