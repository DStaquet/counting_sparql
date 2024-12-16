from rdflib.graph import Graph


def readNTriples(file):
    g = Graph()
    g.parse(file, format="nt")
    return g


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
        "output_file",
        help="The output file to use",
    )

    args = parser.parse_args()

    g = readNTriples(args.update_file)

    all_list: list[tuple[str, str, str]] = list()
    for s, p, o in g:
        if "Product" in str(s):
            all_list.append((str(s), str(p), str(o)))

    print(
        sorted(all_list, key=lambda x: x[0].split("/")[-1]),
        len(all_list),
    )
