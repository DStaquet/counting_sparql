from eval_incremental import duckdb_conn

from pandas import DataFrame

from rdflib.plugins.sparql.sparql import QueryContext
from rdflib.plugins.sparql.parserutils import CompValue

from typing import Any
from SQL_Constructor.SQL_Constructor import get_table_name
from SQL_Constructor import SQL_Constructor

from rdflib.term import Identifier

_Triple = tuple[Identifier, Identifier, Identifier]


def evalIncrSelectQuery(
    ctx: QueryContext, part: CompValue, increm: bool
) -> Any:
    evalIncrPart(ctx, part.p, increm)
    if increm:
        select_delta_query: str = (
            "SELECT * FROM delta_"
            + get_table_name(part.p)
            + ";"
        )
        select_delta_handle = duckdb_conn.sql(
            select_delta_query
        )
        select_delta_results: DataFrame = (
            select_delta_handle.df()
        )
        select_delta_insert_query: str = (
            SQL_Constructor.insert_delta_query(
                part, select_delta_results, "delta_"
            )
        )
        duckdb_conn.sql(select_delta_insert_query)
        insert_increm_nu_table(part, use_PV=True)
        select_query: str = (
            "SELECT * FROM nu_" + get_table_name(part) + ";"
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
        if not select_results.empty:
            select_insert_query: str = (
                SQL_Constructor.insert_query(
                    part, select_results
                )
            )
            duckdb_conn.sql(select_insert_query)
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
            SQL_Constructor.insert_delta_query(
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
            SQL_Constructor.insert_query(
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
            + ", SUM(k_count) as k_count FROM delta_"
            + get_table_name(part.p.p1)
            + " GROUP BY "
            + ", ".join(var for var in part.PV)
            + ";"
        )
        project_delta_handle = duckdb_conn.sql(
            project_delta_query
        )
        project_delta_results: DataFrame = (
            project_delta_handle.df()
        )
        project_delta_insert_query: str = (
            SQL_Constructor.insert_delta_query(
                part, project_delta_results, "delta_"
            )
        )
        if not project_delta_results.empty:
            duckdb_conn.sql(project_delta_insert_query)
            insert_increm_nu_table(part, use_PV=True)

        project_delta_query: str = (
            "SELECT "
            + ", ".join(var for var in part.PV)
            + ", SUM(k_count) as k_count FROM delta_"
            + get_table_name(part.p.p2)
            + " GROUP BY "
            + ", ".join(var for var in part.PV)
            + ";"
        )
        project_delta_handle = duckdb_conn.sql(
            project_delta_query
        )
        project_delta_results: DataFrame = (
            project_delta_handle.df()
        )
        project_delta_insert_query: str = (
            SQL_Constructor.insert_delta_query(
                part, project_delta_results, "delta_"
            )
        )
        if not project_delta_results.empty:
            duckdb_conn.sql(project_delta_insert_query)
            insert_increm_nu_table(part, use_PV=True)
    else:
        project_table_name: str = get_table_name(part.p.p1)
        project_get_query1: str = (
            "SELECT "
            + ",".join(var for var in sorted(part.PV))
            + ", SUM(k_count) as k_count FROM "
            + project_table_name
            + " GROUP BY "
            + ",".join(var for var in sorted(part.PV))
            + ";"
        )
        project_handle = duckdb_conn.sql(project_get_query1)
        project_results: DataFrame = project_handle.df()
        if not project_results.empty:
            project_insert_query: str = (
                SQL_Constructor.insert_query(
                    part, project_results
                )
            )

            duckdb_conn.sql(project_insert_query)

        project_table_name: str = get_table_name(part.p.p2)
        project_get_query2: str = (
            "SELECT "
            + ",".join(var for var in sorted(part.PV))
            + ", SUM(k_count) as k_count FROM "
            + project_table_name
            + " GROUP BY "
            + ",".join(var for var in sorted(part.PV))
            + ";"
        )
        project_handle = duckdb_conn.sql(project_get_query2)
        project_results: DataFrame = project_handle.df()
        if not project_results.empty:
            project_insert_query: str = (
                SQL_Constructor.insert_query(
                    part, project_results
                )
            )
            duckdb_conn.sql(project_insert_query)


def evalIncrUnion(
    ctx: QueryContext, part: CompValue, increm: bool
) -> None:
    evalIncrPart(ctx, part.p1, increm)
    evalIncrPart(ctx, part.p2, increm)
    if increm:
        # Get both parts
        first_union_delta, second_union_delta = (
            SQL_Constructor.delta_union_table_query(
                part, part.p1._vars, part.p2._vars
            )
        )
        first_union_delta = first_union_delta.replace(
            "FULL JOIN", "LEFT JOIN"
        )
        second_union_delta = second_union_delta.replace(
            "FULL JOIN", "RIGHT JOIN"
        )
        first_union_delta_handle = duckdb_conn.sql(
            first_union_delta
        )
        first_union_delta_results: DataFrame = (
            first_union_delta_handle.df()
        )
        if not first_union_delta_results.empty:
            first_union_delta_insert_query: str = (
                SQL_Constructor.insert_delta_query(
                    part,
                    first_union_delta_results,
                    "delta_",
                )
            )
            duckdb_conn.sql(first_union_delta_insert_query)
        second_union_delta_handle = duckdb_conn.sql(
            second_union_delta
        )
        second_union_delta_results: DataFrame = (
            second_union_delta_handle.df()
        )
        if not second_union_delta_results.empty:
            second_union_delta_insert_query: str = (
                SQL_Constructor.insert_delta_query(
                    part,
                    second_union_delta_results,
                    "delta_",
                )
            )
            duckdb_conn.sql(second_union_delta_insert_query)
        if (
            not first_union_delta_results.empty
            or not second_union_delta_results.empty
        ):
            insert_increm_nu_table(part, union_bool=True)
    else:
        pass
        """union_table_query: str = (
            SQL_Constructor.union_table_query(
                part, part.p1._vars, part.p2._vars
            )
        )

        union_handle = duckdb_conn.sql(union_table_query)
        union_results: DataFrame = union_handle.df()

        union_insert_query: str = (
            SQL_Constructor.insert_query(
                part, union_results
            )
        )
        duckdb_conn.execute(union_insert_query)"""


def insert_increm_nu_table(
    part: CompValue,
    use_PV: bool = False,
    union_bool: bool = False,
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
        + SQL_Constructor.get_create_vars(variables)
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
    )
    nu_query += ", ".join(
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
    if union_bool:
        nu_query += ", (CASE WHEN r1.k_count IS NULL THEN r2.k_count ELSE r1.k_count END) as k_count"
    else:
        nu_query += ", coalesce(r1.k_count, 0) + coalesce(r2.k_count, 0) as k_count"
    nu_query += (
        " from "
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
        filter_query += " WHERE CAST("
        filter_query += part.expr.expr
        filter_query += " AS INT) "
        filter_query += part.expr.op
        filter_query += " "
        filter_query += part.expr.other
        filter_query += ";"
        filter_handle = duckdb_conn.sql(filter_query)
        filter_results: DataFrame = filter_handle.df()
        filter_insert_query: str = (
            SQL_Constructor.insert_delta_query(
                part, filter_results, "delta_"
            )
        )
        if not filter_results.empty:
            duckdb_conn.sql(filter_insert_query)
            insert_increm_nu_table(part)

    else:
        filter_query: str = (
            "SELECT * FROM " + get_table_name(part.p)
        )
        filter_query += (
            " WHERE CAST("
            + part.expr.expr
            + " AS INT) "
            + part.expr.op
            + " "
            + part.expr.other
            + ";"
        )
        filter_handle = duckdb_conn.sql(filter_query)
        filter_results: DataFrame = filter_handle.df()
        if not filter_results.empty:
            filter_insert_query: str = (
                SQL_Constructor.insert_query(
                    part, filter_results
                )
            )
            duckdb_conn.sql(filter_insert_query)


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
                SQL_Constructor.bgp_delta_table_query(
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
                bgp_delta_insert_query: str = (
                    SQL_Constructor.insert_delta_query(
                        part, bgp_delta_results, "delta_"
                    )
                )
                duckdb_conn.sql(bgp_delta_insert_query)
        insert_increm_nu_table(part)
    else:
        bgp_query: str = SQL_Constructor.bgp_table_query(
            part
        )
        bgp_results_handle = duckdb_conn.sql(bgp_query)
        bgp_results: DataFrame = bgp_results_handle.df()
        if not bgp_results.empty:
            bgp_insert_query: str = (
                SQL_Constructor.bgp_insert_query(
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
                SQL_Constructor.insert_delta_query(
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
                SQL_Constructor.insert_delta_query(
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
                SQL_Constructor.insert_query(
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
        # First delta rules of the minus
        minus_delta_query: str = (
            "SELECT r1.*, r2.testVar FROM delta_"
            + get_table_name(part.p1)
            + " as r1 LEFT JOIN "
            + get_table_name(part.p2)
            + " as r2 ON r1.product = r2.product WHERE r2.testVar IS NULL;"
        )
        minus_delta_handle = duckdb_conn.sql(
            minus_delta_query
        )
        minus_delta_results: DataFrame = (
            minus_delta_handle.df()
        )
        if not minus_delta_results.empty:
            minus_delta_insert_query: str = (
                SQL_Constructor.insert_delta_query(
                    part, minus_delta_results, "delta_"
                )
            )
            duckdb_conn.sql(minus_delta_insert_query)
            insert_increm_nu_table(part)

        # Second delta rules of the minus
        minus_delta_query: str = (
            "SELECT r1.*, r2.testVar FROM nu_"
            + get_table_name(part.p1)
            + " as r1 LEFT JOIN delta_"
            + get_table_name(part.p2)
            + " as r2 ON r1.product = r2.product WHERE r2.testVar IS NULL;"
        )
        minus_delta_handle = duckdb_conn.sql(
            minus_delta_query
        )
        minus_delta_results: DataFrame = (
            minus_delta_handle.df()
        )
        if not minus_delta_results.empty:
            minus_delta_insert_query: str = (
                SQL_Constructor.insert_delta_query(
                    part, minus_delta_results, "delta_"
                )
            )
            duckdb_conn.sql(minus_delta_insert_query)
            insert_increm_nu_table(part)
    else:
        minus_query: str = (
            "select r1.*, r2.testVar from "
            + get_table_name(part.p1)
            + " as r1 LEFT JOIN "
            + get_table_name(part.p2)
            + " as r2 ON r1.product = r2.product WHERE r2.testVar IS NULL;"
        )
        minus_handle = duckdb_conn.sql(minus_query)
        minus_results: DataFrame = minus_handle.df()
        if not minus_results.empty:
            minus_insert_query: str = (
                SQL_Constructor.insert_query(
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
