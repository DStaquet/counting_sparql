from rdflib.plugins.sparql.parserutils import CompValue
from rdflib.plugins.sparql.sparql import QueryContext
from rdflib.graph import Graph
import rdflib.plugins.sparql.evaluate as evaluate
from rdflib.term import Variable

from eval_incremental import duckdb_conn

from SQL_Constructor.base_constructor import (
    construct_bgp_insert,
)


def return_filled_in_triples(
    ctx: QueryContext, triples: list
) -> list[tuple[str, str, str]]:
    filled_in_triples: list[tuple[str, str, str]] = list()

    for x in evaluate.evalBGP(ctx, triples):
        for triple in triples:
            filled_in_triple: list[str] = list()
            for index in range(len(triple)):
                if type(triple[index]) == Variable:
                    filled_in_triple.append(
                        x[triple[index]]
                    )
                else:
                    filled_in_triple.append(triple[index])
            filled_in_tuple: tuple[str, str, str] = (
                filled_in_triple[0],
                filled_in_triple[1],
                filled_in_triple[2],
            )
            filled_in_triples.append(filled_in_tuple)

    return filled_in_triples


def parseFirstDelta(part: CompValue, g: Graph) -> None:
    if part.name == "BGP":
        ctx: QueryContext = QueryContext(g)
        triples = sorted(
            part.triples,
            key=lambda t: len(
                [n for n in t if ctx[n] is None]
            ),
        )
        filled_in_triples: list[tuple[str, str, str]] = (
            return_filled_in_triples(ctx, triples)
        )
        insert_bgp_str: str = construct_bgp_insert(
            part, filled_in_triples
        )
        duckdb_conn.sql(insert_bgp_str)

    elif "p" in part:
        parseFirstDelta(part.p, g)
    elif "p1" in part and "p2" in part:
        parseFirstDelta(part.p1, g)
        parseFirstDelta(part.p2, g)
    else:
        return
