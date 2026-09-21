from dataclasses import replace

from helm_generator.conventions import validate_configuration
from helm_generator.models import (
    ComponentConfiguration,
    ProjectConfiguration,
)


def build_valid_configuration() -> ProjectConfiguration:
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
                project_type="api",
                image_name="gestor-snapshot",
                container_port=8080,
                application_context_path="/gestor-snapshot",
            ),
            ComponentConfiguration(
                name="notificador",
                project_type="microservicio",
                image_name="notificador",
                container_port=8080,
                application_context_path="/notificador",
            ),
        ),
    )


def test_valid_configuration_has_no_errors() -> None:
    configuration = build_valid_configuration()

    assert validate_configuration(configuration) == []


def test_invalid_application_name_returns_error() -> None:
    configuration = build_valid_configuration()

    invalid_configuration = replace(
        configuration,
        application_name="PDU_Proyecto",
    )

    errors = validate_configuration(invalid_configuration)

    assert len(errors) == 1
    assert "application_name" in errors[0]


def test_configuration_requires_at_least_one_component() -> None:
    configuration = build_valid_configuration()

    invalid_configuration = replace(
        configuration,
        components=(),
    )

    errors = validate_configuration(invalid_configuration)

    assert len(errors) == 1
    assert "al menos un componente" in errors[0]


def test_duplicate_component_returns_error() -> None:
    configuration = build_valid_configuration()

    duplicate_component = ComponentConfiguration(
        name="catalogo-alertas-api",
        project_type="microservicio",
        image_name="catalogo-alertas-api",
        container_port=8080,
        application_context_path="/catalogo-alertas-api",
    )

    invalid_configuration = replace(
        configuration,
        components=(
            *configuration.components,
            duplicate_component,
        ),
    )

    errors = validate_configuration(invalid_configuration)

    assert len(errors) == 1
    assert "repetido" in errors[0]


def test_invalid_component_name_returns_error() -> None:
    configuration = build_valid_configuration()

    invalid_component = replace(
        configuration.components[0],
        name="Catalogo_Alertas",
    )

    invalid_configuration = replace(
        configuration,
        components=(
            invalid_component,
            *configuration.components[1:],
        ),
    )

    errors = validate_configuration(invalid_configuration)

    assert len(errors) == 1
    assert "Catalogo_Alertas" in errors[0]


def test_component_context_path_must_start_with_slash() -> None:
    configuration = build_valid_configuration()

    invalid_component = replace(
        configuration.components[0],
        application_context_path="catalogo-alertas-api",
    )

    invalid_configuration = replace(
        configuration,
        components=(
            invalid_component,
            *configuration.components[1:],
        ),
    )

    errors = validate_configuration(invalid_configuration)

    assert len(errors) == 1
    assert "context path" in errors[0]
