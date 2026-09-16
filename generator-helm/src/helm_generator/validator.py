from pathlib import Path
from typing import Any

import yaml


FORBIDDEN_CONFIGURATION_KEYS = {
    "alertas",
    "audita",
    "authentication",
    "authorization",
    "kafka",
    "keycloak",
}


def is_valid_port(value: Any) -> bool:
    return (
        isinstance(value, int)
        and not isinstance(value, bool)
        and 1 <= value <= 65535
    )


def find_forbidden_keys(
    value: Any,
    path: str = "",
) -> list[str]:
    errors: list[str] = []

    if isinstance(value, dict):
        for key, nested_value in value.items():
            key_as_string = str(key)

            current_path = (
                f"{path}.{key_as_string}"
                if path
                else key_as_string
            )

            if key_as_string.lower() in FORBIDDEN_CONFIGURATION_KEYS:
                errors.append(
                    "Configuración no transversal detectada: "
                    f"'{current_path}'."
                )

            errors.extend(
                find_forbidden_keys(
                    value=nested_value,
                    path=current_path,
                )
            )

    elif isinstance(value, list):
        for index, nested_value in enumerate(value):
            errors.extend(
                find_forbidden_keys(
                    value=nested_value,
                    path=f"{path}[{index}]",
                )
            )

    return errors


def load_yaml_file(
    yaml_file: Path,
) -> tuple[dict[str, Any] | None, list[str]]:
    if not yaml_file.exists():
        return None, [
            f"No existe el fichero requerido: {yaml_file}.",
        ]

    try:
        content = yaml.safe_load(
            yaml_file.read_text(encoding="utf-8")
        )
    except yaml.YAMLError as error:
        return None, [
            f"YAML inválido en '{yaml_file}': {error}.",
        ]

    if not isinstance(content, dict):
        return None, [
            f"El fichero '{yaml_file}' debe contener un objeto YAML.",
        ]

    return content, []


def validate_component_file(
    project_file: Path,
) -> list[str]:
    errors: list[str] = []

    content, loading_errors = load_yaml_file(project_file)

    if loading_errors:
        return loading_errors

    if content is None:
        return [f"No se pudo leer '{project_file}'."]

    errors.extend(find_forbidden_keys(content))

    specification = content.get("spec")

    if not isinstance(specification, dict):
        return errors + [
            f"'{project_file.name}' debe contener 'spec'."
        ]

    name = specification.get("name")

    if not isinstance(name, str) or not name.strip():
        errors.append(
            f"'{project_file.name}': spec.name es obligatorio."
        )

    image = specification.get("image")

    if (
        not isinstance(image, dict)
        or not isinstance(image.get("name"), str)
        or not image["name"].strip()
    ):
        errors.append(
            f"'{project_file.name}': spec.image.name es obligatorio."
        )

    container = specification.get("container")

    if (
        not isinstance(container, dict)
        or not is_valid_port(container.get("port"))
    ):
        errors.append(
            f"'{project_file.name}': "
            "spec.container.port debe ser válido."
        )

    service = specification.get("service")

    if (
        not isinstance(service, dict)
        or not is_valid_port(service.get("port"))
    ):
        errors.append(
            f"'{project_file.name}': "
            "spec.service.port debe ser válido."
        )

    elif (
        isinstance(container, dict)
        and service["port"] != container["port"]
    ):
        errors.append(
            f"'{project_file.name}': "
            "service.port debe coincidir con container.port."
        )

    ingress = specification.get("ingress")

    if not isinstance(ingress, dict):
        errors.append(
            f"'{project_file.name}': spec.ingress es obligatorio."
        )

    else:
        context_path = ingress.get("contextPath")

        if (
            not isinstance(context_path, str)
            or not context_path.startswith("/")
        ):
            errors.append(
                f"'{project_file.name}': "
                "spec.ingress.contextPath debe comenzar por '/'."
            )

    return errors


def validate_generated_project(
    chart_directory: Path,
) -> list[str]:
    """Valida todos los componentes generados en projects/."""

    projects_directory = chart_directory / "projects"

    if not projects_directory.exists():
        return [
            f"No existe el directorio requerido: "
            f"'{projects_directory}'."
        ]

    project_files = sorted(projects_directory.glob("*.yaml"))

    if not project_files:
        return [
            "No se han generado ficheros de componentes en projects/."
        ]

    errors: list[str] = []

    for project_file in project_files:
        errors.extend(
            validate_component_file(project_file)
        )

    return errors
