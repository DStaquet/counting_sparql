from SQL_Constructor.base_constructor import (
    __encode_schema_name,
    __encode_table_name,
    create_table_w_select,
    filter_expr_part,
)


from rdflib.plugins.sparql.parserutils import CompValue


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
            + " \nWHERE "
            + filter_expr_part(part.expr)
            + ";"
        )

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
                + " \nWHERE "
                + filter_expr_part(part.expr)
                + ";"
            )
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
