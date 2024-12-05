import SQL_Constructor.operation_constructor.bgp_constructor
from eval_incremental import duckdb_conn

from pandas import DataFrame

from rdflib.plugins.sparql.sparql import QueryContext
from rdflib.plugins.sparql.parserutils import CompValue

from typing import Any
from SQL_Constructor.base_constructor import get_table_name
from SQL_Constructor import base_constructor

from rdflib.term import Identifier

_Triple = tuple[Identifier, Identifier, Identifier]


def evalIncrSelectQuery(
    ctx: QueryContext, part: CompValue, increm: bool
) -> Any:
    evalIncrPart(ctx, part.p, increm)
    if increm:

        select_query: str = (
            "SELECT * FROM nu_"
            + get_table_name(part.p)
            + ";"
        )
        select_handle = duckdb_conn.sql(select_query)
        select_results: DataFrame = select_handle.df()
    else:
        select_query: str = (
            "SELECT * FROM " + get_table_name(part.p) + ";"
        )
        # Put into database
        select_handle = duckdb_conn.sql(select_query)
        select_results: DataFrame = select_handle.df()
    return select_results


def evalIncrDistinct(
    ctx: QueryContext, part: CompValue, increm: bool
) -> None:
    evalIncrPart(ctx, part.p, increm)
    if increm:
        distinct_delta_query: str = (
            "SELECT DISTINCT "
            + ", ".join(var for var in part.p.PV)
            + ", k_count FROM delta_"
            + get_table_name(part.p)
            + ";"
        )
        distinct_delta_handle = duckdb_conn.sql(
            distinct_delta_query
        )
        distinct_delta_results: DataFrame = (
            distinct_delta_handle.df()
        )
        distinct_delta_insert_query: str = (
            base_constructor.insert_delta_query(
                part, distinct_delta_results, "delta_"
            )
        )
        duckdb_conn.sql(distinct_delta_insert_query)
        insert_increm_nu_table(part, use_PV=True)
    else:
        distinct_table_name: str = get_table_name(part.p)
        distinct_get_query: str = (
            "SELECT DISTINCT "
            + ", ".join(var for var in part.p.PV)
            + ", k_count FROM "
            + distinct_table_name
            + ";"
        )
        distinct_handle = duckdb_conn.sql(
            distinct_get_query
        )
        distinct_results: DataFrame = distinct_handle.df()
        distinct_insert_query: str = (
            base_constructor.insert_query(
                part, distinct_results
            )
        )
        duckdb_conn.execute(distinct_insert_query)


def evalIncrProject(
    ctx: QueryContext, part: CompValue, increm: bool
) -> None:
    evalIncrPart(ctx, part.p, increm)
    if increm:
        project_delta_query: str = (
            "SELECT "
            + ", ".join(var for var in part.PV)
            + ", k_count FROM delta_"
            + get_table_name(part.p)
            + ";"
        )
        project_delta_handle = duckdb_conn.sql(
            project_delta_query
        )
        project_delta_results: DataFrame = (
            project_delta_handle.df()
        )
        project_delta_insert_query: str = (
            base_constructor.insert_delta_query(
                part, project_delta_results, "delta_"
            )
        )
        if not project_delta_results.empty:
            duckdb_conn.sql(project_delta_insert_query)
        insert_increm_nu_table(part, use_PV=True)
    else:
        project_table_name: str = get_table_name(part.p)
        project_get_query: str = (
            "SELECT "
            + ",".join(var for var in sorted(part.PV))
            + ", k_count FROM "
            + project_table_name
            + ";"
        )
        project_handle = duckdb_conn.sql(project_get_query)
        project_results: DataFrame = project_handle.df()

        if not project_results.empty:
            project_insert_query: str = (
                base_constructor.insert_query(
                    part, project_results
                )
            )

            duckdb_conn.sql(project_insert_query)


def evalIncrUnion(
    ctx: QueryContext, part: CompValue, increm: bool
) -> None:
    evalIncrPart(ctx, part.p1, increm)
    evalIncrPart(ctx, part.p2, increm)
    union_table_query: str = (
        base_constructor.union_table_query(
            part, part.p1._vars, part.p2._vars
        )
    )

    union_handle = duckdb_conn.sql(union_table_query)
    union_results: DataFrame = union_handle.df()

    union_insert_query: str = base_constructor.insert_query(
        part, union_results
    )
    duckdb_conn.execute(union_insert_query)


def insert_increm_nu_table(
    part: CompValue, use_PV: bool = False
) -> None:
    if use_PV:
        if part.PV is None:
            part.PV = part.p.PV
        variables = part.PV
    else:
        variables = part._vars
    drop_table_query: str = (
        "DROP TABLE IF EXISTS nu_"
        + get_table_name(part)
        + ";"
    )
    duckdb_conn.execute(drop_table_query)
    create_table_query: str = (
        f"CREATE TABLE IF NOT EXISTS nu_"
        + get_table_name(part)
        + " (\n"
        + base_constructor.get_create_vars(variables)
        + "\tPRIMARY KEY ("
        + ",".join(
            var for var in variables if var != "k_count"
        )
        + ")\n"
        + ");"
    )
    duckdb_conn.execute(create_table_query)
    nu_query: str = (
        "INSERT INTO nu_"
        + get_table_name(part)
        + "  ("
        + ", ".join(
            var
            for var in sorted(variables)
            if var != "k_count"
        )
        + ", k_count) select "
        + ", ".join(
            "(CASE WHEN r1."
            + var
            + " NOT NULL THEN r1."
            + var
            + " ELSE r2."
            + var
            + " END) as "
            + var
            for var in sorted(variables)
            if var != "k_count"
        )
        + ", coalesce(r1.k_count, 0) + coalesce(r2.k_count, 0) as k_count"
        + " from "
        + get_table_name(part)
        + " AS r1 FULL OUTER JOIN delta_"
        + get_table_name(part)
        + " AS r2 ON "
        + " AND ".join(
            f"r1.{var} = r2.{var}"
            for var in sorted(variables)
            if var != "k_count"
        )
        + " WHERE (coalesce(r1.k_count, 0) + coalesce(r2.k_count, 0)) > 0"
        + ";"
    )
    duckdb_conn.execute(nu_query)


def evalIncrFilter(
    ctx: QueryContext, part: CompValue, increm: bool
) -> None:
    evalIncrPart(ctx, part.p, increm)
    if increm:
        filter_query: str = (
            "SELECT * FROM delta_" + get_table_name(part.p)
        )
        filter_query += (
            " WHERE CAST("
            + part.expr.expr.expr
            + " AS INT) "
            + part.expr.expr.op
            + " "
            + part.expr.expr.other
            + " AND CAST("
            + part.expr.other[0].expr
            + " AS INT) "
            + part.expr.other[0].op
            + " "
            + part.expr.other[0].other
            + ";"
        )
        filter_handle = duckdb_conn.sql(filter_query)
        filter_results: DataFrame = filter_handle.df()
        if not filter_results.empty:
            filter_insert_query: str = (
                base_constructor.insert_delta_query(
                    part, filter_results, "delta_"
                )
            )
            duckdb_conn.sql(filter_insert_query)
        insert_increm_nu_table(part)

    else:
        filter_query: str = (
            "SELECT * FROM " + get_table_name(part.p)
        )
        filter_query += (
            " WHERE CAST("
            + part.expr.expr.expr
            + " AS INT) "
            + part.expr.expr.op
            + " "
            + part.expr.expr.other
            + " AND CAST("
            + part.expr.other[0].expr
            + " AS INT) "
            + part.expr.other[0].op
            + " "
            + part.expr.other[0].other
            + ";"
        )
        filter_handle = duckdb_conn.sql(filter_query)
        filter_results: DataFrame = filter_handle.df()
        if not filter_results.empty:
            filter_insert_query: str = (
                base_constructor.insert_query(
                    part, filter_results
                )
            )
            duckdb_conn.sql(filter_insert_query)


def drop_rebuild_BGP_table(part: CompValue) -> None:
    drop_table_query: str = (
        "DROP TABLE IF EXISTS nu_"
        + get_table_name(part)
        + ";"
    )
    duckdb_conn.execute(drop_table_query)
    create_table_query: str = (
        f"CREATE TABLE IF NOT EXISTS nu_"
        + get_table_name(part)
        + " (\n"
        + base_constructor.get_create_vars(part._vars)
        + "\tPRIMARY KEY ("
        + ",".join(
            var for var in part._vars if var != "k_count"
        )
        + ")\n"
        + ");"
    )
    duckdb_conn.execute(create_table_query)


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
            bgp_delta_query = duckdb_conn.sql(
                delta_queries[len(delta_queries) - 1]
            )
            bgp_delta_results: DataFrame = (
                bgp_delta_query.df()
            )
            if not bgp_delta_results.empty:
                drop_rebuild_BGP_table(part)
                bgp_delta_insert_query: str = (
                    base_constructor.insert_delta_query(
                        part, bgp_delta_results, "delta_"
                    )
                )
                duckdb_conn.sql(bgp_delta_insert_query)
        insert_increm_nu_table(part)
    else:
        bgp_query: str = (
            base_constructor.operation_constructor.bgp_constructor.bgp_table_query(
                part
            )
        )
        bgp_results_handle = duckdb_conn.sql(bgp_query)
        bgp_results: DataFrame = bgp_results_handle.df()
        if not bgp_results.empty:
            bgp_insert_query: str = (
                base_constructor.bgp_insert_query(
                    part, bgp_results
                )
            )
            duckdb_conn.sql(bgp_insert_query)


def evalLeftJoin(
    ctx: QueryContext, part: CompValue, increm: bool
) -> None:
    evalIncrPart(ctx, part.p1, increm)
    evalIncrPart(ctx, part.p2, increm)
    if increm:
        # First delta rules of the left join
        leftjoin_delta_query: str = ""
        leftjoin_delta_query += "SELECT "
        leftjoin_delta_query += ", ".join(
            var for var in part.p1._vars if var != "k_count"
        )
        leftjoin_delta_query += ", "
        leftjoin_delta_query += ", ".join(
            var for var in part.p2._vars if var != "k_count"
        )
        leftjoin_delta_query += ", r1.k_count as k_count"
        leftjoin_delta_query += " FROM delta_"
        leftjoin_delta_query += get_table_name(part.p1)
        leftjoin_delta_query += " AS r1 LEFT OUTER JOIN "
        leftjoin_delta_query += get_table_name(part.p2)
        leftjoin_delta_query += " AS r2"
        leftjoin_delta_query += " ON "
        if (
            part.p1._vars.intersection(part.p2._vars)
            != set()
        ):
            leftjoin_delta_query += " AND ".join(
                f"r1.{var} = r2.{var}"
                for var in part.p1._vars.intersection(
                    part.p2._vars
                )
            )
        else:
            leftjoin_delta_query += (
                "1 = 1 WHERE r1.k_count < 0"
            )
        leftjoin_delta_query += ";"

        leftjoin_delta_handle = duckdb_conn.sql(
            leftjoin_delta_query
        )
        leftjoin_delta_results: DataFrame = (
            leftjoin_delta_handle.df()
        )
        if not leftjoin_delta_results.empty:
            leftjoin_delta_insert_query: str = (
                base_constructor.insert_delta_query(
                    part, leftjoin_delta_results, "delta_"
                )
            )
            duckdb_conn.sql(leftjoin_delta_insert_query)
            insert_increm_nu_table(part)

        # Second delta rules of the left join
        leftjoin_delta_query: str = ""
        leftjoin_delta_query += "SELECT "
        leftjoin_delta_query += ", ".join(
            var for var in part.p1._vars if var != "k_count"
        )
        leftjoin_delta_query += ", "
        leftjoin_delta_query += ", ".join(
            var for var in part.p2._vars if var != "k_count"
        )
        leftjoin_delta_query += ", r2.k_count as k_count"
        leftjoin_delta_query += " FROM nu_"
        leftjoin_delta_query += get_table_name(part.p1)
        leftjoin_delta_query += (
            " AS r1 LEFT OUTER JOIN delta_"
        )
        leftjoin_delta_query += get_table_name(part.p2)
        leftjoin_delta_query += " AS r2"
        leftjoin_delta_query += " ON "
        if (
            part.p1._vars.intersection(part.p2._vars)
            != set()
        ):
            leftjoin_delta_query += " AND ".join(
                f"r1.{var} = r2.{var}"
                for var in part.p1._vars.intersection(
                    part.p2._vars
                )
            )
        else:
            leftjoin_delta_query += (
                "1 = 1 WHERE r2.k_count < 0"
            )
        leftjoin_delta_query += ";"

        leftjoin_delta_handle = duckdb_conn.sql(
            leftjoin_delta_query
        )
        leftjoin_delta_results: DataFrame = (
            leftjoin_delta_handle.df()
        )
        if not leftjoin_delta_results.empty:
            leftjoin_delta_insert_query: str = (
                base_constructor.insert_delta_query(
                    part, leftjoin_delta_results, "delta_"
                )
            )
            duckdb_conn.sql(leftjoin_delta_insert_query)
        insert_increm_nu_table(part)
    else:
        leftjoin_query: str = ""
        leftjoin_query += "SELECT "
        leftjoin_query += ", ".join(
            var for var in part.p1._vars if var != "k_count"
        )
        leftjoin_query += ", "
        leftjoin_query += ", ".join(
            var for var in part.p2._vars if var != "k_count"
        )
        leftjoin_query += ", r1.k_count as k_count"
        leftjoin_query += " FROM "
        leftjoin_query += get_table_name(part.p1)
        leftjoin_query += " AS r1 LEFT OUTER JOIN "
        leftjoin_query += get_table_name(part.p2)
        leftjoin_query += " AS r2"
        leftjoin_query += " ON "
        if (
            part.p1._vars.intersection(part.p2._vars)
            != set()
        ):
            leftjoin_query += " AND ".join(
                f"r1.{var} = r2.{var}"
                for var in part.p1._vars.intersection(
                    part.p2._vars
                )
            )
        else:
            leftjoin_query += "1 = 1"
        leftjoin_query += ";"

        leftjoin_handle = duckdb_conn.sql(leftjoin_query)
        leftjoin_results: DataFrame = leftjoin_handle.df()

        if not leftjoin_results.empty:
            leftjoin_insert_query: str = (
                base_constructor.insert_query(
                    part, leftjoin_results
                )
            )
            duckdb_conn.sql(leftjoin_insert_query)


def evalIncrMinus(
    ctx: QueryContext, part: CompValue, increm: bool
) -> None:
    evalIncrPart(ctx, part.p1, increm)
    evalIncrPart(ctx, part.p2, increm)
    if increm:
        # Pre part
        minus_query_pre_part: str = (
            "SELECT * FROM delta_"
            + get_table_name(part.p1)
            + " as r1"
            + " WHERE r1.product NOT IN (SELECT product FROM "
            + get_table_name(part.p2)
            + ");"
        )
        minus_handle_pre = duckdb_conn.sql(
            minus_query_pre_part
        )
        minus_results_pre: DataFrame = minus_handle_pre.df()
        if not minus_results_pre.empty:
            minus_insert_query_pre: str = (
                base_constructor.insert_delta_query(
                    part, minus_results_pre, "delta_"
                )
            )
            duckdb_conn.sql(minus_insert_query_pre)

        # First delta part
        minus_query_first_part: str = (
            "SELECT DISTINCT F_nu.* FROM nu_"
            + get_table_name(part.p1)
            + " as F_nu, delta_"
            + get_table_name(part.p2)
            + " as delta_P2"
            + " WHERE F_nu.product = delta_P2.product"
            + " AND (delta_P2.product, delta_P2.k_count) IN (SELECT (product, k_count) FROM "
            + get_table_name(part.p2)
            + ");"
        )
        minus_handle_first = duckdb_conn.sql(
            minus_query_first_part
        )
        minus_results_first: DataFrame = (
            minus_handle_first.df()
        )
        if not minus_results_first.empty:
            minus_insert_query_first: str = (
                base_constructor.insert_delta_query(
                    part, minus_results_first, "delta_"
                )
            )
            duckdb_conn.sql(minus_insert_query_first)

        # Second delta part
        minus_query_second_part: str = (
            "SELECT DISTINCT F_nu.product, F_nu.label, F_nu.p1, F_nu.p3, - F_nu.k_count FROM nu_"
            + get_table_name(part.p1)
            + " as F_nu, delta_"
            + get_table_name(part.p2)
            + " as delta_P2"
            + " WHERE F_nu.product = delta_P2.product"
            + " AND (delta_P2.product, delta_P2.k_count) NOT IN (SELECT (product, k_count) FROM "
            + get_table_name(part.p2)
            + ");"
        )
        minus_handle_second = duckdb_conn.sql(
            minus_query_second_part
        )
        minus_results_second: DataFrame = (
            minus_handle_second.df()
        )
        if not minus_results_second.empty:
            minus_insert_query_second: str = (
                base_constructor.insert_delta_query(
                    part, minus_results_second, "delta_"
                )
            )
            duckdb_conn.sql(minus_insert_query_second)

        insert_increm_nu_table(part)
    else:
        minus_query: str = (
            "SELECT * FROM "
            + get_table_name(part.p1)
            + " as r1"
            + " WHERE r1.product NOT IN (SELECT product FROM "
            + get_table_name(part.p2)
            + ");"
        )
        minus_handle = duckdb_conn.sql(minus_query)
        minus_results: DataFrame = minus_handle.df()
        if not minus_results.empty:
            minus_insert_query: str = (
                base_constructor.insert_query(
                    part, minus_results
                )
            )
            duckdb_conn.sql(minus_insert_query)


def evalIncrPart(
    ctx: QueryContext, part, increm: bool = False
) -> Any:
    try:
        if part.name == "BGP":
            evalIncremBGP(ctx, part.triples, part, increm)
            return
        elif part.name == "Filter":
            evalIncrFilter(ctx, part, increm)
            return
        elif part.name == "Join":
            pass
        elif part.name == "LeftJoin":
            evalLeftJoin(ctx, part, increm)
            return
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
            evalIncrMinus(ctx, part, increm)
            return

        elif part.name == "Project":
            evalIncrProject(ctx, part, increm)
            return
        elif part.name == "Slice":
            pass
        elif part.name == "Distinct":
            evalIncrDistinct(ctx, part, increm)
            return
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
