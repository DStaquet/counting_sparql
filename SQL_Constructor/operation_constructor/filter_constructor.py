from SQL_Constructor.base_constructor import (
    __encode_schema_name,
    __encode_table_name,
    create_table_w_select,
)


from rdflib.plugins.sparql.parserutils import (
    CompValue,
    Expr,
)


def filter_expr_part(
    expr: Expr, curr_schema: set[str]
) -> str:
    """Recursively construct the filter expression part of the query.

    Args:
        expr (Expr): Current expression part of the query

    Returns:
        str: Expression part for the filter query.
    """
    filter_expr = ""
    if type(expr.expr) == Expr:
        filter_expr += filter_expr_part(
            expr.expr, curr_schema
        )
        for i in range(len(expr.other)):
            filter_expr += " AND "
            filter_expr += filter_expr_part(
                expr.other[i], curr_schema
            )
    else:
        if expr.op in ["<", ">", "<=", ">="]:
            filter_expr += (
                "CAST("
                + expr.expr
                + " AS INT) "
                + expr.op
                + " CAST("
                + expr.other
                + " AS INT)"
            )
        else:
            filter_expr += (
                expr.expr + " " + expr.op + " " + expr.other
            )
    return filter_expr


def __atLeastOneOverlap(
    schema: set[str], expr_part: Expr
) -> bool:  # type: ignore
    """Checks if there is at least one schema that overlaps with the entire expression.

    Args:
        schemas (list[set[str]]): All schemas
        expr_part (Expr): expr part.

    Returns:
        bool: Checks if schemas overlap.
    """
    if type(expr_part.expr) == Expr:
        for i in range(len(expr_part.other)):
            return False or __atLeastOneOverlap(
                schema, expr_part.other[i]
            )
    else:
        return (expr_part.expr in schema) and (
            expr_part.other in schema
        )


def filter_query(
    part: CompValue, schemas: list[set] = []
) -> str:
    """Generate filter query for the current part of the algebra.

    Args:
        part (CompValue): Current part of the algebra.
        schemas (list, optional): List of schemas to filter on. Defaults to
            an empty list

    Returns:
        str: Query string for the filter operation.
    """
    if len(schemas) <= 1:
        filter_str: str = (
            "SELECT "
            + ", ".join(
                var
                for var in sorted(part._vars)
                if var != "k_count"
            )
            + ", k_count\nFROM "
            + __encode_table_name(part.p)
        )
        if __atLeastOneOverlap(schemas[0], part.expr):
            filter_str_part = (
                " \nWHERE "
                + filter_expr_part(part.expr, schemas[0])
            )
            filter_str += filter_str_part
        filter_str += ";\n"

        return create_table_w_select(
            __encode_table_name(part), filter_str
        )
    else:
        filter_strs: str = ""
        for schema in schemas:
            schema_suffix: str = __encode_schema_name(
                str(sorted(schema))
            )
            filter_str: str = (
                "SELECT "
                + ", ".join(
                    var
                    for var in sorted(schema)
                    if var != "k_count"
                )
                + ", k_count\nFROM "
                + __encode_table_name(part.p)
                + "_"
                + schema_suffix
            )
            if __atLeastOneOverlap(schema, part.expr):
                filter_str_part = (
                    " \nWHERE "
                    + filter_expr_part(part.expr, schema)
                )
                filter_str += filter_str_part
            filter_str += ";\n"

            filter_strs += (
                create_table_w_select(
                    __encode_table_name(part)
                    + "_"
                    + schema_suffix,
                    filter_str,
                )
                + "\n"
            )

    return filter_strs


def delta_filter_query(
    part: CompValue, schemas: list[set[str]] = []
) -> str:
    """Build up the incremental delta filter queries.

    Args:
        part (CompValue): Current part of the algebra

    Returns:
        str: Query string to get the results of the delta filter operation
    """
    table_name: str = "delta_" + __encode_table_name(part.p)
    filter_str: str = (
        "SELECT "
        + ", ".join(
            var
            for var in sorted(part._vars)
            if var != "k_count"
        )
        + ", k_count\nFROM "
        + table_name
        + " \nWHERE "
        + filter_expr_part(part.expr, schemas[0])
        + ";"
    )
    return filter_str
