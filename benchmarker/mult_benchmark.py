from duckdb import DuckDBPyConnection
from rdflib import Graph


def run_chain_benchmark(
    query: str,
    query_files_dir: str,
    runs: int,
    duckdb_conn: DuckDBPyConnection,
    data_file: str,
    delta_and_nu_files: list[tuple[tuple[str, str], str]],
) -> None:
    """Runs a chain of benchmarks.

    Args:
        query (str): Query to run on the database.
        query_files_dir (str): Output directory where the query files are stored.
        runs (int): Amount of runs to do for testing.
        duckdb_conn (DuckDBPyConnection): Connection to the database.
        data_file (str): Initial base data file. (In turtle format)
        delta_and_nu_files (list[tuple[str, str]]): List of tuples containing delta and nu files.
        (In NTriples and Turtle format respectively)
    """
    # Read initial data
    base_g = Graph()
    base_g.parse(data_file, format="ttl")

    # Read delta and nu files
    for (ins_file, del_file), nu_file in delta_and_nu_files:
        delta_ins_g = Graph()
        delta_ins_g.parse(ins_file, format="nt")

        delta_del_g = Graph()
        delta_del_g.parse(del_file, format="nt")

        nu_g = Graph()
        nu_g.parse(nu_file, format="ttl")

        base_g += delta_ins_g
        base_g -= delta_del_g

        print(base_g == nu_g)
