from time import time

import rdflib.graph as graph
from rdflib.plugins.sparql import algebra
from rdflib.plugins.sparql import parser
from rdflib.plugins.sparql.sparql import QueryContext
from rdflib.plugins.sparql.sparql import Query

import sys, os

from eval_incremental.eval_incremental import (
    constructTablesRec,
    dropTablesRec,
)
from eval_incremental import delta_inserter, duckdb_conn
from eval_incremental.eval_incremental import evalIncrPart

from pandas import DataFrame

from eval_incremental import (
    temp_eval_incremental_query1,
    temp_eval_incremental_query2,
    temp_eval_incremental_query3,
    temp_eval_incremental_query4,
)

from database import insert_data_graph


def insertData(g: graph.Graph, query: Query) -> None:
    """Inserts the data in the delta."""
    delta_inserter.parseFirstDelta(query.algebra, g)


def buildGraphFromData(
    data: str | None,
    url: str | None = None,
    format: str | None = None,
) -> graph.Graph:
    """Build th graph from given data or url.

    Args:
        data (str | None): Given data
        url (str | None, optional): Given URL. Defaults to None.
        format (str | None, optional): Given format if applicable. Defaults to None.

    Returns:
        graph.Graph: The parsed graph
    """
    g = graph.Graph()
    if data == None:
        if format == None:
            g.parse(url)
        else:
            g.parse(url, format=format)
    else:
        if format == None:
            g.parse(data=data)
        else:
            g.parse(data=data, format=format)
    return g


def insertParseQuery(
    query: str, data: str | None = None
) -> None:
    """Inserts and parses the query.

    Args:
        query (str): The query to be parsed.
        data (str | None, optional): Data to parse on. Defaults to None.
    """

    g = buildGraphFromData(data)

    query_tree = parser.parseQuery(str(query))
    q_query_object = algebra.translateQuery(query_tree)

    constructTablesRec(q_query_object.algebra)
    output: DataFrame = evalIncrPart(
        QueryContext(g), q_query_object.algebra, True
    )
    print(output)
    # insertData(g, q_query_object)
    # output = g.query(query)  # type: ignore[arg-type]

    """for triple in output.bindings:
        print(triple)"""


def queryParser(
    size: int,
    increm_bool: bool,
    g: graph.Graph,
    query_abbrev: str,
    output_file: str | None = None,
) -> None:
    """Parses the query.

    Args:
        size (int): Size of the data.
        increm_bool (bool): Incremental boolean.
        g (graph.Graph): Graph data.
        query_abbrev (str): Which query to parse.
        output_file (str | None, optional): File to write output to. Defaults to None.
    """

    # Query 1 - Incremental
    start_time = time()
    query = readQueryFile(
        f"./Queries/berlin_benchmark/{str(size)}/query1_benchmark/query1_{query_abbrev}.sparql"
    )
    query_tree = parser.parseQuery(str(query))
    q_query_object = algebra.translateQuery(query_tree)
    # algebra.pprintAlgebra(q_query_object)
    if not increm_bool:
        dropTablesRec(q_query_object.algebra)
    constructTablesRec(q_query_object.algebra)
    result: DataFrame = (
        temp_eval_incremental_query1.evalIncrPart(
            QueryContext(g),
            q_query_object.algebra,
            increm_bool,
        )
    )
    global query1_time
    if query1_time == 0:
        query1_time = time() - start_time
    else:
        query1_time = (
            (time() - start_time) + query1_time
        ) / 2
    # print(f"Time: {time() - start_time} seconds\n")
    if output_file != None:
        with open(output_file, "a") as f:
            f.write(
                f"Query 1 - Time: {time() - start_time} seconds\n"
            )
            f.write("Result query 1:\n")
            f.write(str(result))
            f.write("\n\n")

    # Query 2 - Incremental
    start_time = time()
    query = readQueryFile(
        f"./Queries/berlin_benchmark/{str(size)}/query2_benchmark/query2_{query_abbrev}.sparql"
    )
    query_tree = parser.parseQuery(str(query))
    q_query_object = algebra.translateQuery(query_tree)
    # algebra.pprintAlgebra(q_query_object)
    if not increm_bool:
        dropTablesRec(q_query_object.algebra)
    constructTablesRec(q_query_object.algebra)
    result: DataFrame = (
        temp_eval_incremental_query2.evalIncrPart(
            QueryContext(g),
            q_query_object.algebra,
            increm_bool,
        )
    )
    global query2_time
    if query2_time == 0:
        query2_time = time() - start_time
    else:
        query2_time = (
            (time() - start_time) + query2_time
        ) / 2
    # print(f"Time: {time() - start_time} seconds\n")
    # print("Result query 2:\n", result, "\n")
    if output_file != None:
        with open(output_file, "a") as f:
            f.write(
                f"Query 2 - Time: {time() - start_time} seconds\n"
            )
            f.write("Result query 2:\n")
            f.write(str(result))
            f.write("\n\n")

    # Query 3 - Incremental
    start_time = time()
    query = readQueryFile(
        f"./Queries/berlin_benchmark/{str(size)}/query3_benchmark/query3_{query_abbrev}.sparql"
    )
    query_tree = parser.parseQuery(str(query))
    q_query_object = algebra.translateQuery(query_tree)
    if not increm_bool:
        dropTablesRec(q_query_object.algebra)
    constructTablesRec(q_query_object.algebra)
    result: DataFrame = (
        temp_eval_incremental_query3.evalIncrPart(
            QueryContext(g),
            q_query_object.algebra,
            increm_bool,
        )
    )
    global query3_time
    if query3_time == 0:
        query3_time = time() - start_time
    else:
        query3_time = (
            (time() - start_time) + query3_time
        ) / 2
    # print(f"Time: {time() - start_time} seconds\n")
    # print("Result query 3:\n", result, "\n")
    if output_file != None:
        with open(output_file, "a") as f:
            f.write(
                f"Query 3 - Time: {time() - start_time} seconds\n"
            )
            f.write("Result query 3:\n")
            f.write(str(result))
            f.write("\n\n")

    # Query 4 - Incremental
    query = readQueryFile(
        f"./Queries/berlin_benchmark/{str(size)}/query4_benchmark/query4_{query_abbrev}.sparql"
    )
    query_tree = parser.parseQuery(str(query))
    q_query_object = algebra.translateQuery(query_tree)
    # algebra.pprintAlgebra(q_query_object)
    if not increm_bool:
        dropTablesRec(q_query_object.algebra)
    constructTablesRec(q_query_object.algebra)
    result: DataFrame = (
        temp_eval_incremental_query4.evalIncrPart(
            QueryContext(g),
            q_query_object.algebra,
            increm_bool,
        )
    )
    global query4_time
    if query4_time == 0:
        query4_time = time() - start_time
    else:
        query4_time = (
            (time() - start_time) + query4_time
        ) / 2
    # print(f"Time: {time() - start_time} seconds\n")
    # print("Result query 4:\n", result, "\n")
    if output_file != None:
        with open(output_file, "a") as f:
            f.write(
                f"Query 4 - Time: {time() - start_time} seconds\n"
            )
            f.write("Result query 4:\n")
            f.write(str(result))
            f.write("\n\n")


def readQueryFile(filename: str) -> str:
    """Read query file.

    Args:
        filename (str): filename to be read.
    """

    with open(filename, "r") as file:
        return file.read()


def check_relevancy(
    delta_size: str, data_size: int, sample: str
) -> bool:
    """Checks if the sample is relevant.

    Args:
        delta_size (str): Size of the delta.
        data_size (int): Size of the data.
        sample (str): Used sample.

    Returns:
        bool: True if the sample is relevant, False otherwise.
    """
    with open(
        f"./Queries/berlin_benchmark/{data_size}/relevant_products_{delta_size}.txt",
        "r",
    ) as rel_file:
        relevant_samples: list[str] = rel_file.read().split(
            "\n"
        )[:-1]
        if sample in relevant_samples:
            return True
        else:
            return False


def test_queryParser(
    sizes: list[int], delta_sizes: list[str]
):
    """Test the query parser multiple times using different sizes and delta sizes
    with four different predefined queries.

    Args:
        sizes (list[int]): List of sizes.
        delta_sizes (list[str]): List of delta sizes.
    """
    f = open("./measurements/results.csv", "w")
    f.write(
        "Data size,Delta size,Sample,Incremental,Query1,Query2,Query3,Query4\n"
    )
    global query1_time
    global query2_time
    global query3_time
    global query4_time
    for data_size in sizes:
        with open(
            f"./data/dataset{data_size}.ttl", "r"
        ) as datafile:
            read_nt_data: str = datafile.read()

        samples: list[str] = []
        for file in os.listdir(
            f"./Queries/berlin_benchmark/{data_size}/query1_benchmark/"
        ):
            if file.endswith(".sparql"):
                samples.append(
                    file.split("_")[1].split(".")[0]
                )

        g: graph.Graph = buildGraphFromData(read_nt_data)

        for delta_size in delta_sizes:
            print(
                f"Calculating - Data size: {data_size}, Delta size: {delta_size}"
            )

            insert_data_graph.drop_tables(duckdb_conn)
            insert_data_graph.insert_rdf_into_graph(
                g, duckdb_conn
            )
            insert_data_graph.make_tables(
                f"./Queries/berlin_benchmark/{data_size}/{delta_size}_updates.csv",
                f"./Queries/berlin_benchmark/{data_size}/{delta_size}_deletes.csv",
                duckdb_conn,
            )

            # print("Incremental")
            with open(output_file, "a") as tf:
                tf.write(
                    f"Data size: {data_size}, Delta size: {delta_size} - Incremental\n"
                )
            for sample in samples:
                if not check_relevancy(
                    delta_size, data_size, sample
                ):
                    continue
                query1_time = 0
                query2_time = 0
                query3_time = 0
                query4_time = 0
                queryParser(data_size, False, g, sample)
                query1_time = 0
                query2_time = 0
                query3_time = 0
                query4_time = 0
                # print(f"Sample: Product{sample}")
                for _ in range(10):
                    queryParser(
                        data_size,
                        True,
                        g,
                        sample,
                        output_file,
                    )
                # print(query1_time, query2_time, query3_time, query4_time)
                f.write(
                    f"{data_size},{delta_size},Product{sample},True,{query1_time},{query2_time},{query3_time},{query4_time}\n"
                )

            insert_data_graph.set_up_nu_table(duckdb_conn)

            # print("Non-Incremental")
            with open(output_file, "a") as tf:
                tf.write(
                    f"Data size: {data_size}, Delta size: {delta_size} - Non-Incremental\n"
                )
            for sample in samples:
                if not check_relevancy(
                    delta_size, data_size, sample
                ):
                    continue
                query1_time = 0
                query2_time = 0
                query3_time = 0
                query4_time = 0
                # print(f"Sample: Product{sample}")
                for _ in range(10):
                    queryParser(
                        data_size,
                        False,
                        g,
                        sample,
                        output_file,
                    )
                # print(query1_time, query2_time, query3_time, query4_time)
                f.write(
                    f"{data_size},{delta_size},Product{sample},False,{query1_time},{query2_time},{query3_time},{query4_time}\n"
                )
        print("\n")
    f.close()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python query_parser.py <output_dir>")
        exit(1)
    else:
        output_file: str = sys.argv[1]
        f = open(output_file, "w")
        f.close()

    query1_time: float = 0
    query2_time: float = 0
    query3_time: float = 0
    query4_time: float = 0
    test_queryParser(
        [100, 1000, 5000], ["small", "medium", "large"]
    )
