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

import rdflib.graph as graph
from rdflib.plugins.sparql import algebra
from rdflib.plugins.sparql import parser
from rdflib.plugins.sparql.sparql import QueryContext
from rdflib.plugins.sparql.sparql import Query

import sys, os

from eval_incremental import VALUES
from eval_incremental.eval_incremental import (
    constructTablesRec, dropTablesRec
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


def queryParser(size: int, increm_bool: bool, g: graph.Graph, query_abbrev: str) -> None:

    # Query 1 - Incremental
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
    print("Result query 1:\n", result, "\n")

    # Query 2 - Incremental
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
    print("Result query 2:\n", result, "\n")

    # Query 3 - Incremental
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
    print("Result query 3:\n", result, "\n")

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
    print("Result query 4:\n", result, "\n")


def readQueryFile(filename: str) -> str:
    """Read query file.

    Args:
        filename (str): filename to be read.
    """

    with open(filename, "r") as file:
        return file.read()


if __name__ == "__main__":
    """if len(sys.argv) < 2:
        print(
            "Usage: python query_parser.py <queryfile.sparql>"
        )
        exit(1)"""
    # query = readQueryFile(sys.argv[1])

    # data = requests.get("http://localhost:3000/")
    # print(data.text)

    size: int = 100

    with open(f"./data/dataset{size}.nt", "r") as datafile:
        read_nt_data: str = datafile.read()

    # insertParseQuery(query, read_ttl_data)

    g = graph.Graph()
    g.parse(data=read_nt_data)

    samples: list[str] = []
    for file in os.listdir(f"./Queries/berlin_benchmark/{size}/query1_benchmark/"):
        if file.endswith(".sparql"):
            samples.append(file.split("_")[1].split(".")[0])

    for sample in samples:
        print(f"Sample: Product{sample}")
        queryParser(size, True, g, sample)
        print("\n")
