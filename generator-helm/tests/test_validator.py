from pathlib import Path

from helm_generator.generator import (
    write_project_definitions,
)
from helm_generator.models import (
    ComponentConfiguration,
    ProjectConfiguration,
)
from helm_generator.validator import (
    validate_generated_project,
)


def build_configuration() -> ProjectConfiguration:
    return ProjectConfiguration(
        application_name="pdu",
        application_version="1.0.0",
        chart_version="0.1.0",
        registry_path="pdu",
        dns_suffix="example.local",
        replica_count=1,
        usage_level="low",
        sas_monitoring_enabled=False,
        metrics_path="/metrics",
        ingress_enabled=True,
        autoscaling_enabled=False,
        components=(
            ComponentConfiguration(
                name="catalogo-alertas-api",
                project_type="front",
                image_name="catalogo-alertas-api",
                container_port=80,
                application_context_path="/catalogo-alertas-api",
            ),
            ComponentConfiguration(
                name="gestor-snapshot",
                project_type="microservicio",
                image_name="gestor-snapshot",
                container_port=8080,
                application_context_path="/gestor-snapshot",
            ),
        ),
    )


def test_valid_generated_projects_have_no_errors(
    tmp_path: Path,
) -> None:
    configuration = build_configuration()

    write_project_definitions(
        chart_directory=tmp_path,
        config=configuration,
    )

    errors = validate_generated_project(
        chart_directory=tmp_path,
    )

    assert errors == []
