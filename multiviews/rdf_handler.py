"""
Submodule of multiviews that handles the logic of reading RDF data.
"""

from rdflib import Graph  # pylint: disable=import-error


def parse_pod_data(
    pod_data: str,
) -> list[tuple[str, str, str, str]]:
    """Parses RDF data from a pod and returns it as a list of tuples.

    Args:
        pod_data (str): The RDF data in string format.
    Returns:
        list[tuple[str, str, str, str]]: A list of tuples
            containing pod_id, subject, predicate, and object.
    """
    g = Graph()
    g.parse(data=pod_data, format="turtle")
    pod_id = "pod_example"  # This should be derived from the pod data or URL
    triples: list[tuple[str, str, str, str]] = []
    for subj, pred, obj in g:
        triples.append((pod_id, str(subj), str(pred), str(obj)))
    return triples
