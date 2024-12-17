from rdflib.graph import Graph
from rdflib import URIRef, Literal
from random import sample, choice
from os.path import join

from tqdm import tqdm


def readNTriples(file):
    print(f"Reading ntriples from {file}.", end="")
    g = Graph()
    g.parse(file, format="nt")
    print(f" Done.")
    return g


def getAllProducts(g: Graph) -> dict[str, list[tuple]]:
    all_dict: dict[str, list[tuple]] = dict()
    for s, p, o in tqdm(g, desc="Getting all products"):
        if "Product" in str(s):
            key = str(s).split("/")[-1]
            if key not in all_dict:
                all_dict[key] = [(s, p, o)]
            else:
                all_dict[key].append((s, p, o))
    # Add random Features to query on
    for key in tqdm(
        all_dict, desc="Adding random features"
    ):
        choices = sample(["FA", "FB", "FC", "FD", "FE"], 2)
        new_tup1 = (
            all_dict[key][0][0],
            URIRef(
                "http://www4.wiwiss.fu-berlin.de/bizer/bsbm/v01/vocabulary/productFeature"
            ),
            URIRef(
                f"http://www4.wiwiss.fu-berlin.de/bizer/bsbm/v01/instances/ProductFeature{choices[0]}"
            ),
        )
        new_tup2 = (
            all_dict[key][0][0],
            URIRef(
                "http://www4.wiwiss.fu-berlin.de/bizer/bsbm/v01/vocabulary/productFeature"
            ),
            URIRef(
                f"http://www4.wiwiss.fu-berlin.de/bizer/bsbm/v01/instances/ProductFeature{choices[1]}"
            ),
        )
        all_dict[key].append(new_tup1)
        all_dict[key].append(new_tup2)

        # Add random productypes for query1
        prodtype_choices = sample(
            ["TA", "TB", "TC", "TD", "TE"], 1
        )
        new_tup3 = (
            all_dict[key][0][0],
            URIRef(
                "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"
            ),
            URIRef(
                f"http://www4.wiwiss.fu-berlin.de/bizer/bsbm/v01/instances/ProductType{prodtype_choices[0]}"
            ),
        )
        all_dict[key].append(new_tup3)
    return all_dict


def getBaseProducts(
    all_product_dict: dict[str, list[tuple]]
) -> tuple[Graph, set[str]]:
    base_g = Graph()

    sample_keys = sample(
        list(all_product_dict.keys()),
        len(all_product_dict.keys()) // 2,
    )

    for key in tqdm(
        sample_keys,
        desc="Getting base case products",
    ):
        for tup in all_product_dict[key]:
            base_g.add(tup)

    return base_g, set(sample_keys)


def getBaseGraph(
    input_file: str, format: str = "ttl"
) -> Graph:
    print(
        f"Constructing base graph in {input_file}.", end=""
    )
    g = Graph()
    g.parse(input_file, format=format)
    print(f" Done.")
    return g


def buildDeltaGs(
    g: Graph,
    all_product_dict: dict[str, list[tuple]],
    S_in_graph: set[str],
    delta_graphs_amount: int,
    insert_amount: int,
    delete_amount: int,
) -> tuple[list[tuple[Graph, Graph, Graph]], set[str]]:
    # List of tuples of graphs containing the respective insert and delete tuples
    delta_Gs: list[tuple[Graph, Graph, Graph]] = list()
    nu_graph = g

    for _ in tqdm(
        range(delta_graphs_amount),
        desc="Building delta graphs",
    ):
        insert_delta_G = Graph()
        delete_delta_G = Graph()

        # Insert
        insert_keys = sample(
            list(all_product_dict.keys() - S_in_graph),
            insert_amount,
        )

        for key in insert_keys:
            for tup in all_product_dict[key]:
                insert_delta_G.add(tup)

        # Delete
        delete_keys = sample(
            list(S_in_graph),
            delete_amount,
        )

        for key in delete_keys:
            for tup in all_product_dict[key]:
                delete_delta_G.add(tup)

        S_in_graph = (S_in_graph - set(delete_keys)) | set(
            insert_keys
        )

        # Nu graph
        nu_graph += insert_delta_G
        nu_graph -= delete_delta_G

        delta_Gs.append(
            (insert_delta_G, delete_delta_G, nu_graph)
        )

    return delta_Gs, S_in_graph


def writeBaseG(
    base_g: Graph,
    output_file: str,
    format: str = "ttl",
) -> None:
    print(f"Writing base graph to {output_file}.", end="")
    base_g.serialize(
        output_file, format=format, encoding="utf-8"
    )
    print(f" Done.")


def writeDeltaGs(
    delta_G_list: list[tuple[Graph, Graph, Graph]],
    output_dir: str,
    format: str = "nt",
    nu_format: str = "ttl",
) -> None:
    for i, (insert_G, delete_G, nu_G) in tqdm(
        enumerate(delta_G_list),
        desc=f"Writing delta graphs to {output_dir}",
    ):
        insert_G.serialize(
            f"{output_dir}/insert_{i}.{format}",
            format=format,
            encoding="utf-8",
        )
        delete_G.serialize(
            f"{output_dir}/delete_{i}.{format}",
            format=format,
            encoding="utf-8",
        )
        nu_G.serialize(
            f"{output_dir}/nu_{i}.{nu_format}",
            format=nu_format,
            encoding="utf-8",
        )


if __name__ == "__main__":
    from argparse import ArgumentParser
    from random import seed

    seed(13)

    parser = ArgumentParser(
        description="Module to construct RDF scenario from Berlin SPARQL Benchmark (BSBM) data to use with incremental view maintenance"
    )
    parser.add_argument(
        "input_file",
        help="The input file to use",
    )
    parser.add_argument(
        "update_file",
        help="The update file to use",
    )
    parser.add_argument(
        "output_dir",
        help="The output directory to use",
    )

    args = parser.parse_args()

    g = readNTriples(args.update_file)
    all_product_dict = getAllProducts(
        readNTriples(args.update_file)
    )

    base_g_products, S_in_graph = getBaseProducts(
        all_product_dict
    )
    base_g = getBaseGraph(args.input_file)
    base_g += base_g_products

    writeBaseG(
        base_g,
        join(args.output_dir, "base.ttl"),
        format="ttl",
    )

    delta_G_list, S_in_graph = buildDeltaGs(
        base_g, all_product_dict, S_in_graph, 10, 1, 1
    )

    writeDeltaGs(
        delta_G_list,
        args.output_dir,
        format="nt",
        nu_format="ttl",
    )
