from SQL_Constructor.base_constructor import (
    __encode_schema_name,
    __encode_table_name,
    create_table_w_select,
    add_table_to_dict,
    make_group_by,
    make_join,
)


from rdflib.plugins.sparql.parserutils import CompValue


def project_schemas(
    part: CompValue, schemas1: list[set[str]]
) -> list[set[str]]:
    """Generates the schemas for the project part of the query.

    Args:
        part (CompValue): Current part of the query
        schemas1 (list[set[str]]): The schemas of the child part of the query

    Returns:
        list[set[str]]: Schemas of the projection
    """
    new_schema = []
    for schema in schemas1:
        projected_schema = schema.intersection(set(part.PV))
        if projected_schema not in new_schema:
            new_schema.append(projected_schema)
    return new_schema


def double_schemas(
    schemas1: list[set[str]], new_schemas: list[set[str]]
) -> list[set[str]]:
    """Generates all the schemas for the project part that
    add multiple projections.

    Args:
        schemas1 (list[set[str]]): Original schemas
        new_schemas (list[set[str]]): New schemas to add

    Returns:
        list[set[str]]: Double schemas list
    """
    already_seen_projection_schemas = list()
    double_schemas = list()
    for schema in schemas1:
        for new_schema in new_schemas:
            projected_schema = schema.intersection(
                new_schema
            )
            if (
                projected_schema
                not in already_seen_projection_schemas
            ):
                already_seen_projection_schemas.append(
                    projected_schema
                )
            else:
                double_schemas.append(projected_schema)
    return double_schemas


def __projected_variables(schema: set[str]) -> str:
    """Generates the select clause for projected variables."""
    return ", ".join(var for var in sorted(schema)) + ", "


def __projectPVToSchema(
    PV: set[str], schema: set[str]
) -> set[str]:
    """Projects the PV to the schema."""
    return PV.intersection(schema)


def __construct_project_str_one_schema(
    part: CompValue, schema: set[str], from_table_name: str
) -> str:
    """Generates the projection string for only one schema.

    Args:
        part (CompValue): Current part of the query
        schema (set[str]): The schema to project on

    Returns:
        str: The string for the projection
    """
    projected_schema = __projectPVToSchema(
        set(part.PV), schema
    )
    if projected_schema:
        project_str: str = (
            "SELECT "
            + __projected_variables(
                set(part.PV).intersection(schema)
            )
            + " SUM(k_count) AS k_count\nFROM "
            + from_table_name
            + "\nGROUP BY "
            + ", ".join(
                var
                for var in sorted(
                    set(part.PV).intersection(schema)
                )
            )
            + ";"
        )
    else:
        project_str: str = (
            "SELECT "
            + " SUM (k_count) AS k_count\nFROM "
            + from_table_name
            + ";"
        )

    return project_str


def __constructProjectStrMultSchema(
    part: CompValue,
    schemas: list[set[str]],
    from_table_name: str,
    new_table_name: str,
) -> dict[str, list[str]]:
    """Generates the projection strings for multiple schemas.

    Args:
        part (CompValue): Current part of the query
        schema (set[str]): Schema of the child to project on
        from_table_name (str): Name of the table to project on

    Returns:
        str: _description_
    """
    projection_schema = project_schemas(part, schemas)
    projection_dict: dict[str, list[str]] = dict()

    for schema in schemas:
        projected_schema = __projectPVToSchema(
            set(part.PV), schema
        )

        if len(projection_schema) == 1:
            schema_suffix = ""
        else:
            schema_suffix = "_" + __encode_schema_name(
                str(sorted(projected_schema))
            )

        # Returns false if set is empty
        if projected_schema:
            project_str: str = (
                "SELECT "
                + ", ".join(
                    var for var in sorted(projected_schema)
                )
                + ", SUM(k_count) AS k_count\nFROM "
                + from_table_name
                + "_"
                + __encode_schema_name(str(sorted(schema)))
                + "\nGROUP BY "
                + ", ".join(
                    var for var in sorted(projected_schema)
                )
                + ";"
            )
        else:
            project_str: str = (
                "SELECT "
                + " SUM(k_count) AS k_count\nFROM "
                + from_table_name
                + "_"
                + __encode_schema_name(str(sorted(schema)))
                + ";"
            )

        projection_dict = add_table_to_dict(
            new_table_name + schema_suffix,
            project_str,
            projection_dict,
        )

    return projection_dict


def project_query(
    part: CompValue,
    schemas1: list[set[str]] = [],
    is_delta: bool = False,
) -> tuple[str, str] | str:
    """Generate project query for the current part of the algebra.

    Args:
        part (CompValue): Current part of the algebra.
        schemas1 (list[set[str]]): List of schemas to project on.

    Returns:
        str: Query string for the project operation.
    """
    if is_delta:
        from_table_name = "delta_" + __encode_table_name(
            part.p
        )
        new_table_name = "delta_" + __encode_table_name(
            part
        )
    else:
        from_table_name = __encode_table_name(part.p)
        new_table_name = __encode_table_name(part)

    if len(schemas1) == 0:
        raise ValueError("No schemas to project on.")
    elif len(schemas1) == 1:
        project_str: str = (
            __construct_project_str_one_schema(
                part, schemas1[0], from_table_name
            )
        )

        return create_table_w_select(
            new_table_name, project_str
        )
    else:
        project_dict: dict[str, list[str]] = (
            __constructProjectStrMultSchema(
                part,
                schemas1,
                from_table_name,
                new_table_name,
            )
        )

        project_strs: str = make_group_by(
            project_dict,
            project_schemas(part, schemas1),
            is_delta=is_delta,
        )
        project_str_join: str = make_join(
            project_dict, project_schemas(part, schemas1)
        )

        return project_strs, project_str_join


def delta_project_query(
    part: CompValue, schemas1: list[set[str]]
) -> tuple[str, str] | str:
    """Build up the incremental delta project queries.

    Args:
        part (CompValue): Current part of the algebra

    Returns:
        str: Query string to get the results of the delta project operation
    """
    project_str_tuple = project_query(
        part, schemas1, is_delta=True
    )
    return project_str_tuple
