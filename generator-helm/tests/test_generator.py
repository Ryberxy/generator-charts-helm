from dataclasses import replace
from pathlib import Path

import yaml

from helm_generator.generator import (
    get_backend_host,
    get_front_host,
    write_environment_values,
    write_project_definitions,
)
from helm_generator.models import (
    ComponentConfiguration,
    ProjectConfiguration,
)


def build_configuration() -> ProjectConfiguration:
    return ProjectConfiguration(
        application_name="pdu",
        application_version="1.0.0",
        chart_version="0.1.0",
        registry_path="pdu",
        dns_suffix="example.local",
        replica_count=2,
        usage_level="medium",
        sas_monitoring_enabled=True,
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
                name="procesador-ficheros",
                project_type="microservicio",
                image_name="procesador-ficheros",
                container_port=8080,
                application_context_path="/procesador-ficheros",
            ),
        ),
    )


def test_generated_project_definitions(tmp_path: Path) -> None:
    configuration = build_configuration()

    project_files = write_project_definitions(
        chart_directory=tmp_path,
        config=configuration,
    )

    assert len(project_files) == 3

    front_file = (
        tmp_path
        / "projects"
        / "catalogo-alertas-api.yaml"
    )

    api_file = (
        tmp_path
        / "projects"
        / "gestor-snapshot.yaml"
    )

    microservice_file = (
        tmp_path
        / "projects"
        / "procesador-ficheros.yaml"
    )

    assert front_file.exists()
    assert api_file.exists()
    assert microservice_file.exists()

    front_content = yaml.safe_load(
        front_file.read_text(encoding="utf-8")
    )

    front_specification = front_content["spec"]

    assert front_specification["name"] == "catalogo-alertas-api"
    assert front_specification["image"]["name"] == (
        "catalogo-alertas-api"
    )
    assert front_specification["container"]["port"] == 80
    assert front_specification["service"]["port"] == 80
    assert front_specification["gateway"]["name"] == "pdu-gateway"
    assert front_specification["ingress"]["name"] == "pdu-ingress"
    assert front_specification["ingress"]["contextPath"] == (
        "/catalogo-alertas-api"
    )
    assert front_specification["service"]["metricsPath"] == "/metrics"

    assert front_specification["runtimeConfig"]["enabled"] is True
    assert front_specification["runtimeConfig"]["configMapName"] == (
        "catalogo-alertas-api-front-runtime-config"
    )

    assert front_specification["configFile"]["enabled"] is True
    assert front_specification["configFile"]["configMapName"] == (
        "catalogo-alertas-api-front-runtime-config"
    )

    assert "kafka" not in front_specification
    assert "keycloak" not in front_specification

    # El bloque de "resources" a nivel raíz era código muerto: el
    # Deployment.tpl solo lo usa para niveles de uso fuera de
    # low/medium/high/very_high, algo que la CLI nunca permite.
    assert "resources" not in front_specification


def test_api_and_microservice_do_not_generate_front_runtime_config(
    tmp_path: Path,
) -> None:
    configuration = build_configuration()

    write_project_definitions(
        chart_directory=tmp_path,
        config=configuration,
    )

    api_file = (
        tmp_path
        / "projects"
        / "gestor-snapshot.yaml"
    )

    microservice_file = (
        tmp_path
        / "projects"
        / "procesador-ficheros.yaml"
    )

    api_content = yaml.safe_load(
        api_file.read_text(encoding="utf-8")
    )

    microservice_content = yaml.safe_load(
        microservice_file.read_text(encoding="utf-8")
    )

    api_specification = api_content["spec"]
    microservice_specification = microservice_content["spec"]

    assert "runtimeConfig" not in api_specification
    assert "configFile" not in api_specification

    assert "runtimeConfig" not in microservice_specification
    assert "configFile" not in microservice_specification


def test_autoscaling_disabled_has_only_enabled_key(
    tmp_path: Path,
) -> None:
    configuration = build_configuration()

    write_project_definitions(
        chart_directory=tmp_path,
        config=configuration,
    )

    project_file = (
        tmp_path / "projects" / "gestor-snapshot.yaml"
    )

    content = yaml.safe_load(
        project_file.read_text(encoding="utf-8")
    )

    autoscaling = content["spec"]["autoscaling"]

    assert autoscaling == {"enabled": False}


def test_autoscaling_enabled_includes_required_hpa_targets(
    tmp_path: Path,
) -> None:
    configuration = replace(
        build_configuration(),
        autoscaling_enabled=True,
        replica_count=3,
    )

    write_project_definitions(
        chart_directory=tmp_path,
        config=configuration,
    )

    project_file = (
        tmp_path / "projects" / "gestor-snapshot.yaml"
    )

    content = yaml.safe_load(
        project_file.read_text(encoding="utf-8")
    )

    autoscaling = content["spec"]["autoscaling"]

    # Estas claves son las que exige `_HorizontalPodAutoscaler.tpl`
    # con "required" para usage_level low/medium. Sin ellas,
    # `helm template` falla.
    assert autoscaling["enabled"] is True
    assert autoscaling["minReplicas"] == 3
    assert autoscaling["maxReplicas"] > autoscaling["minReplicas"]
    assert "targetCPUUtilizationValue" in autoscaling
    assert "targetMemoryUtilizationValue" in autoscaling


def test_front_and_backend_hosts_follow_naming_convention() -> None:
    configuration = build_configuration()

    assert get_front_host(configuration, "integration") == (
        "front-pdu-integration.example.local"
    )
    assert get_backend_host(configuration, "integration") == (
        "api-pdu-integration.example.local"
    )
    assert get_front_host(configuration, "certification") == (
        "front-pdu-certification.example.local"
    )
    assert get_backend_host(configuration, "certification") == (
        "api-pdu-certification.example.local"
    )


def test_front_host_differs_from_backend_host_in_generated_values(
    tmp_path: Path,
) -> None:
    configuration = build_configuration()

    int_file, _ = write_environment_values(
        chart_directory=tmp_path,
        config=configuration,
    )

    values = yaml.safe_load(int_file.read_text(encoding="utf-8"))

    front_host = values["front"]["spec"]["ingress"]["host"]
    api_host = values["api"]["spec"]["ingress"]["host"]
    microservicio_host = values["microservicio"]["spec"]["ingress"][
        "host"
    ]

    assert front_host == "front-pdu-integration.example.local"
    assert api_host == "api-pdu-integration.example.local"

    # api y microservicio siguen compartiendo host (comportamiento
    # ya existente en el chart original de alertas).
    assert api_host == microservicio_host

    # front debe ser distinto del host de api/microservicio: este
    # es el bug que se corrige en este cambio.
    assert front_host != api_host
