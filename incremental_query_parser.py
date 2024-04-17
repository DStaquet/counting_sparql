"""
import rdflib.plugins.sparql.sparql as ssparql

import rdflib.query as rdfquery
from rdflib.plugins.sparql import algebra
import rdflib.plugin as plugin
from rdflib.plugins.sparql import parser
import sys, requests
from typing import (
    Union,
    Type,
)"""

from time import time

import rdflib.graph as graph
from rdflib.plugins.sparql import algebra
from rdflib.plugins.sparql import parser
from rdflib.plugins.sparql.sparql import QueryContext
from rdflib.plugins.sparql.sparql import Query

import sys, os

from eval_incremental import VALUES
from eval_incremental.eval_incremental import (
    constructTablesRec,
    dropTablesRec,
)
from eval_incremental import delta_inserter
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
    delta_inserter.parseFirstDelta(query.algebra, g)


def insertParseQuery(
    query: str, data: str | None = None
) -> None:

    g = graph.Graph()
    if data == None:
        g.parse(
            "http://fragments.dbpedia.org/", format="ttl"
        )
    else:
        g.parse(data=data)

    query_tree = parser.parseQuery(str(query))
    q_query_object = algebra.translateQuery(query_tree)
    # algebra.pprintAlgebra(q_query_object)

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


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python query_parser.py <output_dir>")
        exit(1)
    else:
        output_file: str = sys.argv[1]
        f = open(output_file, "w")
        f.close()

    f = open("./measurements/results.csv", "w")
    f.write(
        "Data size,Delta size,Sample,Incremental,Query1,Query2,Query3,Query4\n"
    )

    for data_size in [100, 1000, 5000]:
        if data_size == 100:
            extension = "nt"
        else:
            extension = "ttl"
        with open(
            f"./data/dataset{data_size}.{extension}", "r"
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

        g = graph.Graph()
        g.parse(data=read_nt_data)

        for delta_size in ["small", "medium", "large"]:
            print(
                f"Calculating - Data size: {data_size}, Delta size: {delta_size}"
            )

            insert_data_graph.drop_tables()
            insert_data_graph.insert_rdf_into_graph(
                read_nt_data, g
            )
            insert_data_graph.make_tables(
                f"./Queries/berlin_benchmark/{data_size}/{delta_size}_updates.csv",
                f"./Queries/berlin_benchmark/{data_size}/{delta_size}_deletes.csv",
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
                query1_time: float = 0
                query2_time: float = 0
                query3_time: float = 0
                query4_time: float = 0
                queryParser(data_size, False, g, sample)
                query1_time: float = 0
                query2_time: float = 0
                query3_time: float = 0
                query4_time: float = 0
                print(f"Sample: Product{sample}")
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

            insert_data_graph.set_up_nu_table()

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
                query1_time: float = 0
                query2_time: float = 0
                query3_time: float = 0
                query4_time: float = 0
                print(f"Sample: Product{sample}")
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
