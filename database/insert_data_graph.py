import duckdb
from rdflib.graph import Graph


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


def insert_rdf_into_graph(rdf_data: str, g: Graph) -> None:
    duckdb_conn = duckdb.connect("./k_values.db")
    create_table_str = create_table()
    insert_str = insert_table(rdf_data, g)
    duckdb_conn.execute(create_table_str)
    duckdb_conn.execute(insert_str)


def make_tables() -> None:
    duckdb_conn = duckdb.connect("./k_values.db")
    create_delta_table_str = create_delta_table()
    create_nu_table_str = create_nu_table()
    duckdb_conn.execute(create_delta_table_str)
    duckdb_conn.execute(create_nu_table_str)

    duckdb_conn.execute(simulate_delta_data())
    duckdb_conn.execute(insert_nu_table())


# TODO simulate updates
def simulate_delta_data() -> str:
    return "insert into delta_G (s, p, o, k_count) VALUES ('http://www4.wiwiss.fu-berlin.de/bizer/bsbm/v01/instances/dataFromProducer1/Product30', 'http://www4.wiwiss.fu-berlin.de/bizer/bsbm/v01/vocabulary/productFeature', 'http://www4.wiwiss.fu-berlin.de/bizer/bsbm/v01/instances/ProductFeature2', -1);"


# TODO: correctly update simulations
def insert_nu_table() -> str:
    return "insert into nu_G (s, p, o, k_count) select s, p, o, k_count from (SELECT s, p, o, k_count from G except select s, p, o, k_count from delta_G) as nu_nu_G;"


if __name__ == "__main__":

    with open("../data/dataset.nt") as datafile:
        read_ttl_data: str = datafile.read()

    g: Graph = Graph()
    g.parse(data=read_ttl_data)

    insert_rdf_into_graph(read_ttl_data, g)
    make_tables()
