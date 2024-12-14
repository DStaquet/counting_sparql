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
from rdflib.plugins.sparql.parserutils import CompValue
from os.path import join

import sys, os

from build_data import (
    dropTablesRec,
    get_query_input,
    get_query_object,
    readQueryFile,
)
from eval_incremental import VALUES
from eval_incremental.eval_incremental import (
    constructTablesRec,
)
from eval_incremental import delta_inserter
from eval_incremental.eval_incremental import (
    evalIncrPart,
    evalPremIncrPart,
)

from pandas import DataFrame

from eval_incremental import (
    temp_eval_incremental_query1,
    temp_eval_incremental_query2,
    temp_eval_incremental_query3,
    temp_eval_incremental_query4,
)

from database import insert_data_graph

from setup_data import (
    insert_data,
    insert_delete_delta_data,
    insert_nu_data,
    insert_insert_delta_data,
    drop_delta_table,
    create_delta_table,
)

from duckdb import DuckDBPyConnection


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


"""def queryParser(
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
            f.write("\n\n")"""


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


def setup_tables(
    query_input_dir: str,
    duckdb_conn: DuckDBPyConnection,
    increm: bool = False,
) -> None:
    """Sets up the tables in the database

    Args:
        part (CompValue): The query
        input_dir (str): Input directory
    """
    with open(
        join(query_input_dir, "construct_tables.sql"), "r"
    ) as f:
        for line in f.read().split(";\n"):
            command = line + ";"
            duckdb_conn.execute(command)
    if not increm:
        with open(
            join(query_input_dir, "delete_tables.sql"), "r"
        ) as f:
            for line in f.read().split(";"):
                command = line + ";"
                duckdb_conn.execute(command)


def run_query(
    query_str: str,
    data_str: str,
    output_dir: str,
    duckdb_conn: DuckDBPyConnection,
) -> None:
    # g = graph.Graph()
    # g.parse(data_str)

    q_query_object = get_query_object(query_str)
    algebra.pprintAlgebra(q_query_object)

    query_input_dir: str = get_query_input(
        output_dir, q_query_object
    )

    setup_tables(query_input_dir, duckdb_conn)

    df: DataFrame | None = evalPremIncrPart(
        q_query_object.algebra, query_input_dir
    )
    df = evalPremIncrPart(
        q_query_object.algebra, query_input_dir, True
    )
    """output: DataFrame = evalIncrPart(
        QueryContext(g), q_query_object.algebra, True
    )

    with open(f"{output_dir}/output.txt", "w") as f:
        f.write(str(output))"""


if __name__ == "__main__":
    hashseed = os.getenv("PYTHONHASHSEED")
    if not hashseed:
        os.environ["PYTHONHASHSEED"] = "0"
        os.execv(
            sys.executable, [sys.executable] + sys.argv
        )

    if len(sys.argv) < 5:
        print(
            "Usage: python query_parser.py <query_file> <data_file> <output_dir> <delete_data_file>"
        )
        exit(1)
    else:
        query_str: str = sys.argv[1]
        data_str: str = sys.argv[2]
        output_dir: str = sys.argv[3]
        delete_data_str: str = sys.argv[4]
        # f = open(output_file, "w")
        # f.close()

    """f = open("./measurements/results.csv", "w")
    f.write(
        "Data size,Delta size,Sample,Incremental,Query1,Query2,Query3,Query4\n"
    )

    for data_size in [100, 1000, 5000]:
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

        g = graph.Graph()
        g.parse(data=read_nt_data)

        for delta_size in ["small", "medium", "large"]:
            print(
                f"Calculating - Data size: {data_size}, Delta size: {delta_size}"
            )

            insert_data_graph.drop_tables(duckdb_conn)
            insert_data_graph.insert_rdf_into_graph(
                read_nt_data, g, duckdb_conn
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
                query1_time: float = 0
                query2_time: float = 0
                query3_time: float = 0
                query4_time: float = 0
                queryParser(data_size, False, g, sample)
                query1_time: float = 0
                query2_time: float = 0
                query3_time: float = 0
                query4_time: float = 0
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
                query1_time: float = 0
                query2_time: float = 0
                query3_time: float = 0
                query4_time: float = 0
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
    

    f.close()"""

    duckdb_conn = DuckDBPyConnection(":memory:")

    data: str = readQueryFile(data_str)
    insert_data(duckdb_conn, data)
    delete_data: str = readQueryFile(delete_data_str)
    insert_delete_delta_data(duckdb_conn, delete_data)
    insert_nu_data(duckdb_conn)

    query: str = readQueryFile(query_str)
    run_query(query, data_str, output_dir, duckdb_conn)
