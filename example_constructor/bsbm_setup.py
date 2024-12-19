from rdflib.graph import Graph
from rdflib import URIRef, Literal
from random import sample, choice, seed
from os.path import join, exists
from os import mkdir, makedirs
from copy import deepcopy

from tqdm import tqdm

seed(13)


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
    query_output_dir: str,
) -> set[str]:
    # List of tuples of graphs containing the respective insert and delete tuples
    nu_graph = g

    for j in tqdm(
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

        # Nu graph
        nu_graph += insert_delta_G
        nu_graph -= delete_delta_G

        S_in_graph = (S_in_graph - set(delete_keys)) | set(
            insert_keys
        )

        writeDeltaGs(
            [
                (
                    insert_delta_G,
                    delete_delta_G,
                    nu_graph,
                )
            ],
            query_output_dir,
            format="csv",
            nu_format="csv",
            j=j,
        )

    return S_in_graph


def writeBaseG(
    base_g: Graph,
    output_file: str,
    format: str = "ttl",
) -> None:
    if format == "csv":
        print(
            f"Writing base graph to {output_file}.", end=""
        )
        with open(output_file, "w") as f:
            f.write("s, p, o, k_count\n")
            for s, p, o in base_g:
                f.write(
                    f'"{str(s)}", "{str(p)}", "{str(o)}", 1\n'
                )
        print(f" Done.")
        return
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
    j: int | None = None,
) -> None:
    for i, (insert_G, delete_G, nu_G) in enumerate(
        delta_G_list
    ):
        if j is not None:
            i = j
        if format == "csv":
            with open(
                f"{output_dir}/delta_{i}.{format}", "w"
            ) as f:
                f.write("s, p, o, k_count\n")
                for s, p, o in insert_G:
                    f.write(
                        f'"{str(s)}", "{str(p)}", "{str(o)}", 1\n'
                    )
            with open(
                f"{output_dir}/delta_{i}.{format}", "a"
            ) as f:
                for s, p, o in delete_G:
                    f.write(
                        f'"{str(s)}", "{str(p)}", "{str(o)}", -1\n'
                    )
            with open(
                f"{output_dir}/nu_{i}.{nu_format}", "w"
            ) as f:
                f.write("s, p, o, k_count\n")
                for s, p, o in nu_G:
                    f.write(
                        f'"{str(s)}", "{str(p)}", "{str(o)}", 1\n'
                    )
            continue
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

    # g = readNTriples(args.update_file)
    print("Reading all products.")
    all_product_dict = getAllProducts(
        readNTriples(args.update_file)
    )

    base_g_products, S_in_graph = getBaseProducts(
        all_product_dict
    )
    base_g = getBaseGraph(args.input_file)
    base_g += base_g_products

    if not exists(args.output_dir):
        makedirs(args.output_dir)

    writeBaseG(
        base_g,
        join(args.output_dir, "base.csv"),
        format="csv",
    )

    S_in_graph = buildDeltaGs(
        base_g,
        all_product_dict,
        S_in_graph,
        10,
        1,
        1,
        args.output_dir,
    )

    """ writeDeltaGs(
        delta_G_list,
        args.output_dir,
        format="nt",
        nu_format="ttl",
    ) """
