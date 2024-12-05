from typing import (
    Any,
    List,
    Generator,
    Union,
    TYPE_CHECKING,
    Iterable,
    Deque,
    Mapping,
)
import collections
from rdflib.term import Identifier, Variable, URIRef
from rdflib.plugins.sparql import parser
from rdflib.plugins.sparql.parserutils import (
    value,
    CompValue,
)
from rdflib.plugins.sparql.aggregates import Aggregator

from pyparsing import ParseException
import json as j

from pandas import DataFrame

from rdflib.plugins.sparql.sparql import (
    QueryContext,
    AlreadyBound,
    FrozenBindings,
    FrozenDict,
    SPARQLError,
)

from rdflib.plugins.sparql.evalutils import (
    _ebv,
    _join,
    _eval,
    _minus,
    _val,
    _fillTemplate,
)
from rdflib.graph import Graph

from urllib.parse import urlencode
from urllib.request import Request, urlopen

import itertools
import re

from os.path import join

from SQL_Constructor import base_constructor

import SQL_Constructor.operation_constructor.bgp_constructor
from eval_incremental import duckdb_conn

_Triple = tuple[Identifier, Identifier, Identifier]

if TYPE_CHECKING:
    from rdflib.paths import Path

from eval_incremental import VALUES


def delete_all_tables(part: CompValue) -> str:
    """Deletes all data from the tables.

    Args:
        part (CompValue): Current part of the query

    Returns:
        str: Returns the SQL query to delete all data from the tables.
    """
    (
        delete_query,
        delete_delta_query,
        delete_nu_query,
        delete_nu_prep_query,
    ) = base_constructor.delete_all_tables(part)
    (
        delta_table_delete_query,
        delta_prep_table_delete_query,
    ) = base_constructor.delete_delta_table(part)
    return (
        delete_query
        + "\n"
        + delete_delta_query
        + "\n"
        + delete_nu_query
        + "\n"
        + delete_nu_prep_query
        + "\n"
        + delta_table_delete_query
        + "\n"
        + delta_prep_table_delete_query
    )


def drop_all_tables(part) -> str:
    (
        drop_query,
        drop_delta_query,
        drop_nu_query,
        drop_nu_prep_query,
    ) = base_constructor.drop_all_tables(part)
    delta_table_drop_query, delta_prep_table_drop_query = (
        base_constructor.drop_delta_table(part)
    )
    return (
        drop_query
        + "\n"
        + drop_delta_query
        + "\n"
        + drop_nu_query
        + "\n"
        + drop_nu_prep_query
        + "\n"
        + delta_table_drop_query
        + "\n"
        + delta_prep_table_drop_query
    )


def construct_tables(part) -> str:
    (
        table_query,
        table_delta,
        table_delta_prep,
        table_nu,
        table_nu_prep,
    ) = base_constructor.make_tables(part, part._vars)
    return (
        table_query
        + "\n"
        + table_delta
        + "\n"
        + table_delta_prep
        + "\n"
        + table_nu
        + "\n"
        + table_nu_prep
        + "\n"
    )


# TODO: Implement join incrementally
def evalIncremBGP(
    ctx: QueryContext,
    triples: list[_Triple],
    part,
    increm: bool,
) -> None:
    if increm:
        delta_queries: list[str] = list()
        for tripe_index in range(len(triples)):
            delta_queries.append(
                SQL_Constructor.operation_constructor.bgp_constructor.bgp_delta_table_query(
                    part, tripe_index + 1
                )
            )
    bgp_query: str = (
        SQL_Constructor.operation_constructor.bgp_constructor.bgp_table_query(
            part
        )
    )
    bgp_results_handle = duckdb_conn.sql(bgp_query)
    bgp_results: DataFrame = bgp_results_handle.df()
    bgp_insert_query: str = (
        base_constructor.bgp_insert_query(part, bgp_results)
    )
    duckdb_conn.sql(bgp_insert_query)


# TODO: Implement selection incrementally
def evalIncrFilter(ctx: QueryContext, part) -> None:
    pass


def evalIncrLazyJoin(ctx: QueryContext, join) -> None:
    pass


# TODO: Implement join incrementally
def evalIncrJoin(ctx: QueryContext, join) -> None:
    pass


# TODO: Implement left join incrementally
def evalIncrLeftJoin(ctx: QueryContext, join) -> None:
    pass


# TODO: implement incremental graph part
def evalIncrGraph(ctx: QueryContext, part) -> None:
    pass


# TODO: implement incremental union part
def evalIncrUnion(
    ctx: QueryContext, union, increm: bool
) -> None:
    evalIncrPart(ctx, union.p1, increm)
    evalIncrPart(ctx, union.p2, increm)
    union_table_query: str = (
        base_constructor.union_table_query(
            union, union.p1._vars, union.p2._vars
        )
    )
    union_handle = duckdb_conn.sql(union_table_query)
    union_results: DataFrame = union_handle.df()
    union_insert_query: str = base_constructor.insert_query(
        union, union_results
    )
    duckdb_conn.sql(union_insert_query)


# TODO: make incremental
def evalIncrValues(ctx: QueryContext, part) -> None:
    pass


# TODO: make incremental
def evalIncrMultiset(ctx: QueryContext, part) -> None:
    pass


# TODO: make incremental
def evalIncrExtend(ctx: QueryContext, part) -> None:
    pass


# TODO: make incremental
def evalIncrMinus(ctx: QueryContext, part) -> None:
    pass


# TODO: make incremental
def evalIncrProject(
    ctx: QueryContext, part, increm: bool
) -> None:
    evalIncrPart(ctx, part.p, increm)
    project_table_name: str = (
        base_constructor.project_table_query(part)
    )
    project_handle = duckdb_conn.sql(project_table_name)
    project_results: DataFrame = project_handle.df()
    project_insert_query: str = (
        base_constructor.insert_query(part, project_results)
    )
    duckdb_conn.sql(project_insert_query)


# TODO: make incremental
def evalIncrSlice(ctx: QueryContext, part) -> None:
    pass


# TODO: make incremental
def evalIncrDistinct(ctx: QueryContext, part) -> None:
    pass


# TODO: make incremental
def evalIncrReduced(ctx: QueryContext, part) -> None:
    pass


# TODO: make incremental
def evalIncrOrderBy(ctx: QueryContext, part) -> None:
    pass


# TODO: make incremental
def evalIncrGroup(ctx: QueryContext, part) -> None:
    pass


# TODO: make incremental
def evalIncrAggregateJoin(ctx: QueryContext, part) -> None:
    pass


# TODO: make incremental
# TODO: write SQL query that returns the final result
def evalIncrSelectQuery(
    ctx: QueryContext, part, increm: bool
) -> Any:
    result = evalIncrPart(ctx, part.p, increm)
    select_query: str = base_constructor.select_query(part)
    select_handle = duckdb_conn.sql(select_query)
    select_results: DataFrame = select_handle.df()
    return select_results


# TODO: make incremental
def evalIncrAskQuery(ctx: QueryContext, part) -> None:
    pass


# TODO: make incremental
def evalIncrConstructQuery(ctx: QueryContext, part) -> None:
    pass


# TODO: make incremental?
def _buildQueryStringForServiceCall(
    ctx: QueryContext, part
) -> None:
    pass


# TODO: make incremental
def evalIncrServiceQuery(ctx: QueryContext, part) -> None:
    pass


# TODO: make incremental
def evalIncrDescribeQuery(ctx: QueryContext, part) -> None:
    pass


def deleteTablesRec(part: CompValue) -> str:
    """Deletes the tables recursively.

    Args:
        part (CompValue): Current part of the query

    Returns:
        str: Returns the SQL query to delete all data from the tables.
    """
    if part == None:
        return ""
    if "p" in part or part.name == "BGP":
        return deleteTablesRec(part.p) + delete_all_tables(
            part
        )
    elif "p1" in part and "p2" in part:
        return (
            deleteTablesRec(part.p1)
            + deleteTablesRec(part.p2)
            + delete_all_tables(part)
        )
    return ""


def dropTablesRec(part) -> str:
    if part == None:
        return ""
    if "p" in part or part.name == "BGP":
        return dropTablesRec(part.p) + drop_all_tables(part)
    elif "p1" in part and "p2" in part:
        return (
            dropTablesRec(part.p1)
            + dropTablesRec(part.p2)
            + drop_all_tables(part)
        )
    return ""


def constructTablesRec(part) -> str:
    if part == None:
        return ""
    if "p" in part or part.name == "BGP":
        return constructTablesRec(
            part.p
        ) + construct_tables(part)
    elif "p1" in part and "p2" in part:
        return (
            constructTablesRec(part.p1)
            + constructTablesRec(part.p2)
            + construct_tables(part)
        )
    return ""


def get_query_string(
    part: CompValue, input_dir: str, prefix: str = ""
) -> str:
    """Gets the SQL query string for the given part of the query.

    Args:
        part (CompValue): Current part of the query
        input_dir (str): Where to read the SQL queries from.

    Returns:
        str: Query string
    """
    query_file_path: str = join(
        input_dir,
        prefix
        + base_constructor.get_table_name(part)
        + ".sql",
    )
    with open(query_file_path, "r") as query_file:
        return query_file.read()


def evalPremIncrPart(
    part: CompValue, input_dir: str, increm: bool = False
) -> DataFrame | None:
    """Goes through the algebra, executing each given SQL query.

    Args:
        part (CompValue): Current part of the query
        input_dir (str): Where to read the SQL queries from.
    """
    if "p" in part:
        evalPremIncrPart(part.p, input_dir, increm)
    elif "p1" in part and "p2" in part:
        evalPremIncrPart(part.p1, input_dir, increm)
        evalPremIncrPart(part.p2, input_dir, increm)
    if not increm:
        query: str = get_query_string(part, input_dir)
        if part.name == "SelectQuery":
            return duckdb_conn.sql(query).df()
        else:
            duckdb_conn.sql(query)
    else:
        query: str = get_query_string(
            part, input_dir, "delta_"
        )
        duckdb_conn.sql(query)
        query: str = get_query_string(
            part, input_dir, "nu_"
        )
        duckdb_conn.sql(query)


def evalIncrPart(
    ctx: QueryContext, part, increm: bool = False
) -> Any:
    try:
        if part.name == "BGP":
            evalIncremBGP(ctx, part.triples, part, increm)
            return
        elif part.name == "Filter":
            pass
        elif part.name == "Join":
            pass
        elif part.name == "LeftJoin":
            pass
        elif part.name == "Graph":
            pass
        elif part.name == "Union":
            evalIncrUnion(ctx, part, increm)
            return
        elif part.name == "ToMultiSet":
            pass
        elif part.name == "Extend":
            pass
        elif part.name == "Minus":
            pass

        elif part.name == "Project":
            evalIncrProject(ctx, part, increm)
            return
        elif part.name == "Slice":
            pass
        elif part.name == "Distinct":
            pass
        elif part.name == "Reduced":
            pass

        elif part.name == "OrderBy":
            pass
        elif part.name == "Group":
            pass
        elif part.name == "AggregateJoin":
            pass

        elif part.name == "SelectQuery":
            return evalIncrSelectQuery(ctx, part, increm)
        elif part.name == "AskQuery":
            pass
        elif part.name == "ConstructQuery":
            pass

        elif part.name == "ServiceGraphPattern":
            pass

        elif part.name == "DescribeQuery":
            pass
    except NotImplementedError as e:
        raise NotImplementedError(
            "I didn´t implement this yet."
        )

    raise NotImplementedError(
        "I didn´t implement this yet."
    )
