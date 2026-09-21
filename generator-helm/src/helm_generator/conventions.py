import re

from .models import ProjectConfiguration


APPLICATION_NAME_PATTERN = re.compile(
    r"^[a-z0-9]([-a-z0-9]*[a-z0-9])?$"
)

SEMVER_PATTERN = re.compile(
    r"^[0-9]+\.[0-9]+\.[0-9]+([\-+][0-9A-Za-z.-]+)?$"
)

VALID_PROJECT_TYPES = {
    "front",
    "api",
    "microservicio",
}

VALID_USAGE_LEVELS = {
    "low",
    "medium",
    "high",
}


def validate_configuration(
    config: ProjectConfiguration,
) -> list[str]:
    """Valida la configuración común y todos los componentes."""

    errors: list[str] = []

    if not config.application_name:
        errors.append("application_name es obligatorio.")

    elif not APPLICATION_NAME_PATTERN.match(config.application_name):
        errors.append(
            "application_name debe contener minúsculas, números y "
            "guiones; debe comenzar y terminar por un carácter "
            "alfanumérico."
        )

    if not config.application_version:
        errors.append("application_version es obligatorio.")

    elif not SEMVER_PATTERN.match(config.application_version):
        errors.append(
            "application_version debe cumplir SemVer. "
            "Ejemplo: 1.0.0."
        )

    if not config.components:
        errors.append(
            "Debe informarse al menos un componente mediante "
            "--fronts, --apis o --microservicios."
        )

    if config.replica_count < 1:
        errors.append(
            "replica_count debe ser mayor o igual que 1."
        )

    if config.usage_level not in VALID_USAGE_LEVELS:
        errors.append(
            "usage_level debe ser uno de: low, medium, high."
        )

    if not config.metrics_path.startswith("/"):
        errors.append(
            "metrics_path debe comenzar por '/'."
        )

    if config.ingress_enabled and not config.dns_suffix:
        errors.append(
            "dns_suffix es obligatorio cuando ingress_enabled=true. "
            "Se usa para construir los hosts front-<project>-<env> "
            "y api-<project>-<env>."
        )

    component_names: set[str] = set()

    for component in config.components:
        if component.name in component_names:
            errors.append(
                f"El componente '{component.name}' está repetido."
            )

        component_names.add(component.name)

        if not APPLICATION_NAME_PATTERN.match(component.name):
            errors.append(
                f"El componente '{component.name}' no es válido. "
                "Use minúsculas, números y guiones."
            )

        if component.project_type not in VALID_PROJECT_TYPES:
            errors.append(
                f"El componente '{component.name}' tiene un tipo "
                f"inválido: '{component.project_type}'."
            )

        if not component.image_name:
            errors.append(
                f"El componente '{component.name}' no tiene imagen."
            )

        if not 1 <= component.container_port <= 65535:
            errors.append(
                f"El componente '{component.name}' tiene un puerto "
                "inválido."
            )

        if (
            not component.application_context_path
            or not component.application_context_path.startswith("/")
        ):
            errors.append(
                f"El context path de '{component.name}' debe "
                "comenzar por '/'."
            )

    return errors
