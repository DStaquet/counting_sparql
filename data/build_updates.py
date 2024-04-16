from rdflib import Graph


def construct_to_delete_tuples(
    product_iri: str,
    producer: str,
    write_file: str,
    g: Graph,
) -> None:
    """
    Construct the triples to delete from the dataset
    """
    query: str = f"""
    PREFIX bsbm-inst: <http://www4.wiwiss.fu-berlin.de/bizer/bsbm/v01/instances/>
    PREFIX bsbm-inst-prod: <http://www4.wiwiss.fu-berlin.de/bizer/bsbm/v01/instances/dataFrom{producer}/>
    PREFIX bsbm: <http://www4.wiwiss.fu-berlin.de/bizer/bsbm/v01/vocabulary/>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

    SELECT ?s ?p ?o
    WHERE {{
        BIND(bsbm-inst-prod:{product_iri} AS ?s)
        ?s ?p ?o .
    }}
    """

    with open(write_file, "a") as f:
        for row in g.query(query):
            f.write(f"{row[0]};{row[1]};{row[2]}\n")  # type: ignore


if __name__ == "__main__":
    # Read dataset
    size = 1000
    with open(f"./data/dataset{size}.ttl", "r") as datafile:
        data = datafile.read()

    g: Graph = Graph()
    g.parse(data=data, format="ttl")
