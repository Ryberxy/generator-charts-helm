from dataclasses import dataclass


@dataclass(frozen=True)
class ComponentConfiguration:
    """Configuración de un componente individual de PDU."""

    name: str
    project_type: str
    image_name: str
    container_port: int
    application_context_path: str


@dataclass(frozen=True)
class ProjectConfiguration:
    """Configuración común de una release Helm con varios componentes."""

    application_name: str
    application_version: str
    chart_version: str
    registry_path: str
    integration_host: str
    certification_host: str
    replica_count: int
    usage_level: str
    sas_monitoring_enabled: bool
    metrics_path: str
    ingress_enabled: bool
    autoscaling_enabled: bool
    components: tuple[ComponentConfiguration, ...]
