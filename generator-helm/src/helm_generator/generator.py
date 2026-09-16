from pathlib import Path

import yaml

from .models import (
    ComponentConfiguration,
    ProjectConfiguration,
)


def get_project_file_name(
    component: ComponentConfiguration,
) -> str:
    return f"{component.name}.yaml"


def get_gateway_name(
    config: ProjectConfiguration,
) -> str:
    return f"{config.application_name}-gateway"


def get_ingress_name(
    config: ProjectConfiguration,
) -> str:
    return f"{config.application_name}-ingress"


def get_integration_namespace(
    config: ProjectConfiguration,
) -> str:
    return f"{config.application_name}-integration"


def get_certification_namespace(
    config: ProjectConfiguration,
) -> str:
    return f"{config.application_name}-certification"


def get_front_runtime_config_name(
    component: ComponentConfiguration,
) -> str:
    return f"{component.name}-front-runtime-config"


def build_chart_metadata(
    config: ProjectConfiguration,
) -> dict:
    return {
        "apiVersion": "v2",
        "name": f"{config.application_name}-helm",
        "description": (
            f"Chart Helm para el proyecto {config.application_name}"
        ),
        "type": "application",
        "version": config.chart_version,
        "appVersion": str(config.application_version),
    }


def write_chart_metadata(
    chart_directory: Path,
    config: ProjectConfiguration,
) -> Path:
    chart_file = chart_directory / "Chart.yaml"

    yaml.safe_dump(
        build_chart_metadata(config),
        chart_file.open("w", encoding="utf-8"),
        allow_unicode=True,
        default_flow_style=False,
        sort_keys=False,
    )

    return chart_file


def build_usage_spec() -> dict:
    return {
        "low": {
            "resources": {
                "requests": {
                    "cpu": "25m",
                    "memory": "300Mi",
                },
                "limits": {
                    "cpu": "400m",
                    "memory": "350Mi",
                },
            },
        },
        "medium": {
            "resources": {
                "requests": {
                    "cpu": "50m",
                    "memory": "600Mi",
                },
                "limits": {
                    "cpu": "600m",
                    "memory": "700Mi",
                },
            },
        },
        "high": {
            "resources": {
                "requests": {
                    "cpu": "50m",
                    "memory": "400Mi",
                },
                "limits": {
                    "cpu": "1",
                    "memory": "800Mi",
                },
            },
        },
    }


def build_probe(port: int) -> dict:
    return {
        "httpGet": {
            "path": "/health/ready",
            "port": port,
        },
        "initialDelaySeconds": 60,
        "timeoutSeconds": 30,
        "periodSeconds": 60,
        "failureThreshold": 6,
    }


def build_liveness_probe(port: int) -> dict:
    return {
        "httpGet": {
            "path": "/health/live",
            "port": port,
        },
        "initialDelaySeconds": 60,
        "timeoutSeconds": 30,
        "periodSeconds": 60,
        "failureThreshold": 6,
    }


def build_cors_policy() -> dict:
    return {
        "allowCredentials": True,
        "allowHeaders": ["*"],
        "allowOrigins": [{"exact": "*"}],
        "allowMethods": [
            "GET",
            "POST",
            "OPTIONS",
            "HEAD",
            "PUT",
            "DELETE",
        ],
    }


def build_default_type_spec(
    config: ProjectConfiguration,
    ingress_host: str,
) -> dict:
    return {
        "replicaCount": config.replica_count,
        "usage_level": config.usage_level,
        "usageSpec": build_usage_spec(),
        "ingress": {
            "enabled": config.ingress_enabled,
            "host": ingress_host,
            "gateway": get_gateway_name(config),
            "name": get_ingress_name(config),
        },
        "corsPolicy": build_cors_policy(),
        "environment": {
            "configMap": {},
            "secrets": {},
        },
    }


def build_environment_values(
    config: ProjectConfiguration,
    namespace: str,
    registry_dns: str,
    ingress_host: str,
) -> dict:
    type_spec = build_default_type_spec(
        config=config,
        ingress_host=ingress_host,
    )

    projects = []

    for component in config.components:
        projects.append(
            {
                "configFile": (
                    f"projects/{get_project_file_name(component)}"
                ),
                "spec": {
                    "type": component.project_type,
                    "imageTag": config.application_version,
                },
            }
        )

    return {
        "global": {
            "nameSpace": namespace,
            "ingressClassName": (
                "webapprouting.kubernetes.azure.com"
            ),
            "registry": {
                "dns": registry_dns,
                "path": config.registry_path,
            },
            "ingress": {
                "enabled": config.ingress_enabled,
                "gateway": get_gateway_name(config),
                "name": get_ingress_name(config),
            },
            "developDeployment": True,
        },
        "ingress": {
            "annotations": {
                "nginx.ingress.kubernetes.io/ssl-redirect": "false",
            },
            "tls": {
                "enabled": False,
                "entries": [],
            },
        },
        "front": {
            "spec": type_spec,
        },
        "api": {
            "spec": type_spec,
        },
        "microservicio": {
            "spec": type_spec,
        },
        "projects": projects,
    }


def write_environment_values(
    chart_directory: Path,
    config: ProjectConfiguration,
) -> tuple[Path, Path]:
    int_values = build_environment_values(
        config=config,
        namespace=get_integration_namespace(config),
        registry_dns="azudirayacont02.azurecr.io",
        ingress_host=config.integration_host,
    )

    cer_values = build_environment_values(
        config=config,
        namespace=get_certification_namespace(config),
        registry_dns="10.200.201.109:8083",
        ingress_host=config.certification_host,
    )

    int_file = chart_directory / "injectValues_INT.yaml"
    cer_file = chart_directory / "injectValues_CER.yaml"

    for output_file, values in (
        (int_file, int_values),
        (cer_file, cer_values),
    ):
        yaml.safe_dump(
            values,
            output_file.open("w", encoding="utf-8"),
            allow_unicode=True,
            default_flow_style=False,
            sort_keys=False,
        )

    return int_file, cer_file


def build_autoscaling_block(
    config: ProjectConfiguration,
) -> dict:
    """
    Construye el bloque de autoscaling de un componente.

    El template `_HorizontalPodAutoscaler.tpl` requiere, para los
    niveles de uso "low" y "medium" (los únicos que expone hoy la
    CLI), que existan las claves minReplicas/maxReplicas y los
    targets de CPU/memoria dentro de `autoscaling`. Si no se generan
    aquí, `helm template` falla con un `required` sin resolver en
    cuanto `--autoscaling-enabled true` se combina con el nivel de
    uso por defecto.
    """

    autoscaling: dict = {
        "enabled": config.autoscaling_enabled,
    }

    if config.autoscaling_enabled:
        autoscaling.update(
            {
                "minReplicas": config.replica_count,
                "maxReplicas": max(
                    config.replica_count * 2,
                    config.replica_count + 1,
                ),
                "targetCPUUtilizationValue": "700m",
                "targetMemoryUtilizationValue": "600Mi",
            }
        )

    return autoscaling


def build_project_definition(
    config: ProjectConfiguration,
    component: ComponentConfiguration,
) -> dict:
    spec = {
        "name": component.name,
        "image": {
            "name": component.image_name,
        },
        "container": {
            "port": component.container_port,
        },
        "service": {
            "port": component.container_port,
            "sas_monitoring": config.sas_monitoring_enabled,
            "metricsPath": config.metrics_path,
        },
        "gateway": {
            "enabled": config.ingress_enabled,
            "name": get_gateway_name(config),
        },
        "ingress": {
            "enabled": config.ingress_enabled,
            "name": get_ingress_name(config),
            "contextPath": component.application_context_path,
        },
        "trafficManagement": {
            "ruleSet": [
                {
                    "name": "default",
                    "prefix": component.application_context_path,
                },
            ],
        },
        "replicaCount": config.replica_count,
        "autoscaling": build_autoscaling_block(config),
        "environment": {
            "configMap": {},
            "secrets": {},
        },
        "readinessProbe": build_probe(
            component.container_port
        ),
        "livenessProbe": build_liveness_probe(
            component.container_port
        ),
    }

    if component.project_type == "front":
        spec["runtimeConfig"] = {
            "enabled": True,
            "configMapName": get_front_runtime_config_name(
                component
            ),
            "fileName": "config.json",
            "data": {},
        }

        spec["configFile"] = {
            "enabled": True,
            "configMapName": get_front_runtime_config_name(
                component
            ),
            "key": "config.json",
            "mountPath": (
                "/usr/share/nginx/html/assets/config.json"
            ),
        }

    return {
        "spec": spec,
    }


def write_project_definitions(
    chart_directory: Path,
    config: ProjectConfiguration,
) -> list[Path]:
    projects_directory = chart_directory / "projects"
    projects_directory.mkdir(parents=True, exist_ok=True)

    project_files: list[Path] = []

    for component in config.components:
        project_file = (
            projects_directory
            / get_project_file_name(component)
        )

        yaml.safe_dump(
            build_project_definition(config, component),
            project_file.open("w", encoding="utf-8"),
            allow_unicode=True,
            default_flow_style=False,
            sort_keys=False,
        )

        project_files.append(project_file)

    return project_files


def write_readme(
    chart_directory: Path,
    config: ProjectConfiguration,
) -> Path:
    readme_file = chart_directory / "README.md"

    components = "\n".join(
        (
            f"- `{component.name}` "
            f"({component.project_type})"
        )
        for component in config.components
    )

    content = f"""# {config.application_name}-helm

Chart Helm generado para una release con múltiples componentes.

## Componentes

{components}

## Entornos

- `injectValues_INT.yaml`
- `injectValues_CER.yaml`

## Renderizado

```bash
helm lint .

helm template {config.application_name}-int \\
  . \\
  -f injectValues_INT.yaml

helm template {config.application_name}-cer \\
  . \\
  -f injectValues_CER.yaml
```text
"""

    readme_file.write_text(content, encoding="utf-8")
    return readme_file
