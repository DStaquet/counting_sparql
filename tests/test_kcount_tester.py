import kcount_tester
from eval_incremental import duckdb_conn

import os, sys
import pandas as pd
import numpy as np


def __set_seed() -> None:
    hashseed = os.getenv("PYTHONHASHSEED")
    if not hashseed:
        os.environ["PYTHONHASHSEED"] = "0"
        os.execv(
            sys.executable, [sys.executable] + sys.argv
        )


def test_build_data() -> None:
    __set_seed()

    kcount_tester.build_data(
        "data/dataset100.ttl",
        "output",
        "Queries/berlin_benchmark/100/query3_benchmark/query3_99.sparql",
        duckdb_conn,
        "data/delete_product98.ttl",
        "data/insert_product105.ttl",
    )
    g_data = duckdb_conn.sql("SELECT * FROM G;").df()
    delta_g_data = duckdb_conn.sql(
        "SELECT * FROM delta_G where s = 'http://www4.wiwiss.fu-berlin.de/bizer/bsbm/v01/instances/dataFromProducer3/Product98';"
    ).df()
    assert not delta_g_data.empty
    delta_g_data = duckdb_conn.sql(
        "SELECT * FROM delta_G where s = 'http://www4.wiwiss.fu-berlin.de/bizer/bsbm/v01/instances/dataFromProducer3/Product105';"
    ).df()
    assert not delta_g_data.empty

    nu_g_data = duckdb_conn.sql(
        "SELECT * FROM nu_G WHERE s = 'http://www4.wiwiss.fu-berlin.de/bizer/bsbm/v01/instances/dataFromProducer3/Product98';"
    ).df()
    assert nu_g_data.empty
    nu_g_data = duckdb_conn.sql(
        "SELECT * FROM nu_G WHERE s = 'http://www4.wiwiss.fu-berlin.de/bizer/bsbm/v01/instances/dataFromProducer3/Product105';"
    ).df()
    assert not nu_g_data.empty


def __compare_dataframes(
    g_data: pd.DataFrame, check_df: pd.DataFrame
) -> None:
    for col in g_data.columns:
        for i in range(len(g_data[col])):
            print(
                type(g_data[col][i]), type(check_df[col][i])
            )


def test_run_bgps() -> None:
    __set_seed()
    query_str = "Queries/berlin_benchmark/100/query3_benchmark/query3_99.sparql"
    output_dir = "output"
    kcount_tester.run_bgps(
        query_str, output_dir, duckdb_conn
    )

    g_data = duckdb_conn.sql(
        "SELECT * FROM " + "BGP_4245425749932949804;"
    ).df()

    check_data = {
        "p3": ["470", "967", "302", "227"],
        "product": [
            "http://www4.wiwiss.fu-berlin.de/bizer/bsbm/v01/instances/dataFromProducer3/Product99",
            "http://www4.wiwiss.fu-berlin.de/bizer/bsbm/v01/instances/dataFromProducer1/Product54",
            "http://www4.wiwiss.fu-berlin.de/bizer/bsbm/v01/instances/dataFromProducer1/Product34",
            "http://www4.wiwiss.fu-berlin.de/bizer/bsbm/v01/instances/dataFromProducer3/Product98",
        ],
        "label": [
            "perfumer unbecomingly",
            "chateaus headlands ventilatory",
            "amtrac puckery",
            "spillway coxwain",
        ],
        "p1": ["219", "880", "858", "165"],
        "k_count": np.array([1, 1, 1, 1]).astype("int32"),
    }

    check_df = pd.DataFrame(check_data)

    assert g_data.equals(check_df)


def test_run_filter() -> None:
    __set_seed()
    query_str = "Queries/berlin_benchmark/100/query3_benchmark/query3_99.sparql"
    output_dir = "output"
    kcount_tester.run_filter(
        query_str, output_dir, duckdb_conn
    )

    g_data = duckdb_conn.sql(
        "SELECT * FROM " + "Filter_7141111257548129695;"
    ).df()

    check_data = {
        "label": [
            "amtrac puckery",
            "spillway coxwain",
        ],
        "p1": ["858", "165"],
        "p3": ["302", "227"],
        "product": [
            "http://www4.wiwiss.fu-berlin.de/bizer/bsbm/v01/instances/dataFromProducer1/Product34",
            "http://www4.wiwiss.fu-berlin.de/bizer/bsbm/v01/instances/dataFromProducer3/Product98",
        ],
        "k_count": np.array([1, 1]).astype("int32"),
    }

    assert g_data.equals(pd.DataFrame(check_data))
