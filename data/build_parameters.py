from rdflib.graph import Graph
import random, os

from build_updates import (
    construct_to_delete_tuples,
    construct_to_update_tuples,
)


def get_producer(g: Graph, product_str: str) -> str:
    """
    Get the producer of a product given its IRI
    """
    producer = ""
    query = f"""
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX bsbm: <http://www4.wiwiss.fu-berlin.de/bizer/bsbm/v01/vocabulary/>
    SELECT ?producer ?product
    WHERE {{
        ?product bsbm:producer ?producer .
        FILTER regex(str(?product), "{product_str}")
    }}
    """
    for row in g.query(query):
        if row[1].split("/")[-1] == product_str:  # type: ignore
            producer = row[0]  # type: ignore
    return str(producer)


def get_features_product(
    g: Graph, product_iri: str, producer_iri: str
) -> list[str]:
    """
    Get the features of a product given its IRI
    """
    features: list[str] = []
    query = f"""
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX bsbm: <http://www4.wiwiss.fu-berlin.de/bizer/bsbm/v01/vocabulary/>
    PREFIX bsbm-inst: <http://www4.wiwiss.fu-berlin.de/bizer/bsbm/v01/instances/>
    PREFIX bsbm-producer: <http://www4.wiwiss.fu-berlin.de/bizer/bsbm/v01/instances/dataFrom{producer_iri}/>

    SELECT ?feature
    WHERE {{
        bsbm-producer:{product_iri} bsbm:productFeature ?feature .
    }}
    """

    for row in g.query(query):
        features.append(row[0].split("/")[-1])  # type: ignore

    return features


def get_producttypes_product(
    g: Graph, product_iri: str, producer_iri: str
) -> str:
    """
    Get the product types of a product given its IRI
    """
    product_types: list[str] = []
    query = f"""
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX bsbm: <http://www4.wiwiss.fu-berlin.de/bizer/bsbm/v01/vocabulary/>
    PREFIX bsbm-inst: <http://www4.wiwiss.fu-berlin.de/bizer/bsbm/v01/instances/>
    PREFIX bsbm-producer: <http://www4.wiwiss.fu-berlin.de/bizer/bsbm/v01/instances/dataFrom{producer_iri}/>

    SELECT ?productType
    WHERE {{
        bsbm-producer:{product_iri} a ?productType .
    }}
    """

    for row in g.query(query):
        if row[0].split("/")[-1] != "Product":  # type: ignore
            product_types.append(row[0].split("/")[-1])  # type: ignore

    return product_types[0]


def build_query1(
    feature_list: list[str], product_type: str
) -> str:
    """
    Build the query for the first recommendation
    """
    with open(
        "./Queries/berlin_benchmark/query1_template.sparql",
        "r",
    ) as file:
        query = file.read()

    feature_sample = random.sample(feature_list, 2)

    query = query.replace(
        "%ProductFeature1%",
        "bsbm-inst:" + feature_sample[0],
    )
    query = query.replace(
        "%ProductFeature2%",
        "bsbm-inst:" + feature_sample[1],
    )

    query = query.replace(
        "%ProductType%", "bsbm-inst:" + product_type
    )

    x = random.randint(1, 500)
    query = query.replace("%x%", str(x))

    return query


def build_query2(product_iri: str, producer: str) -> str:
    """Builds up the second query

    Args:
        product_iri (str): Given product IRI

    Returns:
        str: The query itself
    """
    with open(
        "./Queries/berlin_benchmark/query2_template.sparql",
        "r",
    ) as file:
        query = file.read()

    query = query.replace(
        "%ProductXYZ%", "bsbm-inst-prod:" + product_iri
    )
    query = (
        f"PREFIX bsbm-inst-prod: <http://www4.wiwiss.fu-berlin.de/bizer/bsbm/v01/instances/dataFrom{producer}/>\n"
        + query
    )

    return query


def build_query3(
    product_type: str, feature_list: list[str]
) -> str:
    """Builds up the third query

    Args:
        product_iri (str): Given product IRI

    Returns:
        str: The query itself
    """
    with open(
        "./Queries/berlin_benchmark/query3_template.sparql",
        "r",
    ) as file:
        query = file.read()

    feature_sample = random.sample(feature_list, 2)

    query = query.replace(
        "%ProductFeature1%",
        "bsbm-inst:" + feature_sample[0],
    )
    query = query.replace(
        "%ProductFeature2%",
        "bsbm-inst:" + feature_sample[1],
    )

    query = query.replace(
        "%ProductType%", "bsbm-inst:" + product_type
    )

    x = random.randint(1, 500)
    query = query.replace("%x%", str(x))
    y = random.randint(1, 500)
    query = query.replace("%y%", str(y))

    return query


def build_query4(
    product_type: str, feature_list: list[str]
) -> str:
    """Builds up the fourth query

    Args:
        product_iri (str): Given product IRI

    Returns:
        str: The query itself
    """
    with open(
        "./Queries/berlin_benchmark/query4_template.sparql",
        "r",
    ) as file:
        query = file.read()

    feature_sample = random.sample(feature_list, 3)

    query = query.replace(
        "%ProductFeature1%",
        "bsbm-inst:" + feature_sample[0],
    )
    query = query.replace(
        "%ProductFeature2%",
        "bsbm-inst:" + feature_sample[1],
    )
    query = query.replace(
        "%ProductFeature3%",
        "bsbm-inst:" + feature_sample[2],
    )

    query = query.replace(
        "%ProductType%", "bsbm-inst:" + product_type
    )

    x = random.randint(1, 500)
    query = query.replace("%x%", str(x))
    y = random.randint(1, 500)
    query = query.replace("%y%", str(y))

    return query


def del_files_in_dir(dir_path: str):
    """
    Delete all files in a directory
    """
    for file in os.listdir(dir_path):
        os.remove(os.path.join(dir_path, file))


if __name__ == "__main__":
    # Read dataset
    size = 5000
    with open(f"./data/dataset{size}.ttl", "r") as datafile:
        data = datafile.read()

    g: Graph = Graph()
    g.parse(data=data)

    # Get a random sample of 100 triples
    sample: list[int] = random.sample(
        range(1, size + 1), 10
    )

    # Delete all previous instances
    del_files_in_dir(
        "./Queries/berlin_benchmark/query1_benchmark/"
    )
    del_files_in_dir(
        "./Queries/berlin_benchmark/query2_benchmark/"
    )
    del_files_in_dir(
        "./Queries/berlin_benchmark/query3_benchmark/"
    )
    del_files_in_dir(
        "./Queries/berlin_benchmark/query4_benchmark/"
    )

    for type in ["small", "medium", "large"]:
        with open(
            f"./Queries/berlin_benchmark/{size}/{type}_updates.csv",
            "w",
        ) as f:
            pass
        with open(
            f"./Queries/berlin_benchmark/{size}/{type}_deletes.csv",
            "w",
        ) as f:
            pass

    for i in sample:
        producer = get_producer(g, f"Product{i}").split(
            "/"
        )[-1]
        if producer == "":
            print("No producer found.", f"Product{i}")

        feature_list = get_features_product(
            g, f"Product{i}", producer
        )

        product_types = get_producttypes_product(
            g, f"Product{i}", producer
        )

        new_query = build_query1(
            feature_list, product_types
        )
        with open(
            f"./Queries/berlin_benchmark/query1_benchmark/query1_{i}.sparql",
            "w",
        ) as file:
            file.write(new_query)

        new_query = build_query2(f"Product{i}", producer)
        with open(
            f"./Queries/berlin_benchmark/query2_benchmark/query2_{i}.sparql",
            "w",
        ) as file:
            file.write(new_query)

        new_query = build_query3(
            product_types, feature_list
        )
        with open(
            f"./Queries/berlin_benchmark/query3_benchmark/query3_{i}.sparql",
            "w",
        ) as file:
            file.write(new_query)

        new_query = build_query4(
            product_types, feature_list
        )
        with open(
            f"./Queries/berlin_benchmark/query4_benchmark/query4_{i}.sparql",
            "w",
        ) as file:
            file.write(new_query)

    for j in random.sample(sample, int(0.1 * len(sample))):
        producer = get_producer(g, f"Product{j}").split(
            "/"
        )[-1]
        delete_features: list[tuple[str, str]] = (  # type: ignore
            construct_to_delete_tuples(
                f"Product{j}",
                producer,
                f"./Queries/berlin_benchmark/{size}/small_deletes.csv",
                g,
            )
        )
    for j in random.sample(range(1, size + 1), 2):
        producer = get_producer(
            g, f"Product{size + j}"
        ).split("/")[-1]
        construct_to_update_tuples(
            f"Product{j}",
            producer,
            f"./Queries/berlin_benchmark/{size}/small_updates.csv",
            g,
            5,
            delete_features,
        )

    for j in random.sample(sample, int(0.2 * len(sample))):
        producer = get_producer(g, f"Product{j}").split(
            "/"
        )[-1]
        delete_features = construct_to_delete_tuples(  # type: ignore
            f"Product{j}",
            producer,
            f"./Queries/berlin_benchmark/{size}/medium_deletes.csv",
            g,
        )
    for j in random.sample(
        range(1, size + 1), int(0.01 * size)
    ):
        producer = get_producer(
            g, f"Product{size + j}"
        ).split("/")[-1]
        construct_to_update_tuples(
            f"Product{j}",
            producer,
            f"./Queries/berlin_benchmark/{size}/medium_updates.csv",
            g,
            10,
            delete_features,
        )

    for j in random.sample(sample, int(0.4 * len(sample))):
        producer = get_producer(g, f"Product{j}").split(
            "/"
        )[-1]
        delete_features = construct_to_delete_tuples(  # type: ignore
            f"Product{j}",
            producer,
            f"./Queries/berlin_benchmark/{size}/large_deletes.csv",
            g,
        )
    for j in random.sample(
        range(1, size + 1), int(0.1 * size)
    ):
        producer = get_producer(
            g, f"Product{size + j}"
        ).split("/")[-1]
        construct_to_update_tuples(
            f"Product{j}",
            producer,
            f"./Queries/berlin_benchmark/{size}/large_updates.csv",
            g,
            25,
            delete_features,
        )
