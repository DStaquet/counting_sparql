from SQL_Constructor.base_constructor import (
    __encode_schema_name,
    __encode_table_name,
    create_table_w_select,
    insert_into_w_select,
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


def project_query(
    part: CompValue,
    schemas1: list[set] = [],
    is_delta: bool = False,
) -> str:
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

    def projected_variables(schema: set[str]) -> str:
        """Generates the select clause for projected variables."""
        return (
            ", ".join(var for var in sorted(schema)) + ", "
        )

    def projectPVToSchema(
        PV: set[str], schema: set[str]
    ) -> set[str]:
        """Projects the PV to the schema."""
        return PV.intersection(schema)

    if len(schemas1) == 0:
        raise ValueError("No schemas to project on.")
    elif len(schemas1) == 1:
        projected_schema = projectPVToSchema(
            set(part.PV), schemas1[0]
        )
        if projected_schema:
            project_str: str = (
                "SELECT "
                + projected_variables(set(part.PV))
                + " SUM(k_count) AS k_count\nFROM "
                + from_table_name
                + "\nGROUP BY "
                + ", ".join(var for var in sorted(part.PV))
                + ";"
            )
        else:
            project_str: str = (
                "SELECT "
                + " SUM (k_count) AS k_count\nFROM "
                + from_table_name
                + ";"
            )
        return create_table_w_select(
            new_table_name, project_str
        )
    else:
        project_strs: str = ""
        projection_schema = project_schemas(part, schemas1)
        already_seen_projection_schemas = list()
        to_group_schemas = list()
        double_projection_schemas = double_schemas(
            schemas1, projection_schema
        )

        for schema in schemas1:
            projected_schema = projectPVToSchema(
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
                        var
                        for var in sorted(projected_schema)
                    )
                    + ", SUM(k_count) AS k_count\nFROM "
                    + from_table_name
                    + "_"
                    + __encode_schema_name(
                        str(sorted(schema))
                    )
                    + "\nGROUP BY "
                    + ", ".join(
                        var
                        for var in sorted(projected_schema)
                    )
                    + ";"
                )
            else:
                project_str: str = (
                    "SELECT "
                    + " SUM (k_count) AS k_count\nFROM "
                    + from_table_name
                    + "_"
                    + __encode_schema_name(
                        str(sorted(schema))
                    )
                    + ";"
                )

            if (
                projected_schema
                in double_projection_schemas
            ):
                temp_prefix: str = " TEMP "
                prep_prefix: str = "prep_"
            else:
                temp_prefix = ""
                prep_prefix = ""

            if (
                projected_schema
                not in already_seen_projection_schemas
            ):
                already_seen_projection_schemas.append(
                    projected_schema
                )
                project_strs += (
                    create_table_w_select(
                        prep_prefix
                        + new_table_name
                        + schema_suffix,
                        project_str,
                        temp_prefix=temp_prefix,
                    )
                    + "\n"
                )
            else:
                project_strs += (
                    insert_into_w_select(
                        prep_prefix
                        + new_table_name
                        + schema_suffix,
                        project_str,
                        projected_schema,
                    )
                    + "\n"
                )
                to_group_schemas.append(projected_schema)

        for to_group_schema in to_group_schemas:
            project_strs_temp = (
                "SELECT "
                + ", ".join(
                    var for var in sorted(to_group_schema)
                )
                + ", SUM(k_count) AS k_count\nFROM "
                + new_table_name
                + "_"
                + __encode_schema_name(
                    str(sorted(to_group_schema))
                )
                + "\nGROUP BY "
                + ", ".join(
                    var for var in sorted(to_group_schema)
                )
                + ";"
            )
            if len(to_group_schema) == 1:
                schema_suffix = ""
            else:
                schema_suffix = "_" + __encode_schema_name(
                    str(sorted(to_group_schema))
                )
            project_strs += create_table_w_select(
                new_table_name + schema_suffix,
                project_strs_temp,
            )

        return project_strs


def delta_project_query(
    part: CompValue, schemas1: list[set[str]]
) -> str:
    """Build up the incremental delta project queries.

    Args:
        part (CompValue): Current part of the algebra

    Returns:
        str: Query string to get the results of the delta project operation
    """
    project_str: str = project_query(
        part, schemas1, is_delta=True
    )
    return project_str
