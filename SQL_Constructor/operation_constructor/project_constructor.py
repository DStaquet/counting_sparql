from SQL_Constructor.base_constructor import (
    __encode_schema_name,
    __encode_table_name,
    create_table_w_select,
    insert_into_w_select,
    project_schemas,
)


from rdflib.plugins.sparql.parserutils import CompValue


def project_query(
    part: CompValue, schemas1: list[set] = []
) -> str:
    """Generate project query for the current part of the algebra.

    Args:
        part (CompValue): Current part of the algebra.
        schemas1 (list[set[str]]): List of schemas to project on.

    Returns:
        str: Query string for the project operation.
    """

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
                + __encode_table_name(part.p)
                + "\nGROUP BY "
                + ", ".join(var for var in sorted(part.PV))
                + ";"
            )
        else:
            project_str: str = (
                "SELECT "
                + " SUM (k_count) AS k_count\nFROM "
                + __encode_table_name(part.p)
                + ";"
            )
        return create_table_w_select(
            __encode_table_name(part), project_str
        )
    else:
        project_strs: str = ""
        projection_schema = project_schemas(part, schemas1)
        already_seen_projection_schemas = list()
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

            if projected_schema:
                project_str: str = (
                    "SELECT "
                    + ", ".join(
                        var
                        for var in sorted(projected_schema)
                    )
                    + ", SUM(k_count) AS k_count\nFROM "
                    + __encode_table_name(part.p)
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
                    + __encode_table_name(part.p)
                    + "_"
                    + __encode_schema_name(
                        str(sorted(schema))
                    )
                    + ";"
                )
            if (
                projected_schema
                not in already_seen_projection_schemas
            ):
                already_seen_projection_schemas.append(
                    projected_schema
                )
                project_strs += (
                    create_table_w_select(
                        __encode_table_name(part)
                        + schema_suffix,
                        project_str,
                    )
                    + "\n"
                )
            else:
                project_strs += (
                    insert_into_w_select(
                        __encode_table_name(part)
                        + schema_suffix,
                        project_str,
                        projected_schema,
                    )
                    + "\n"
                )
        return project_strs
