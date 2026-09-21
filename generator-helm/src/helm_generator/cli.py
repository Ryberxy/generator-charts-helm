import argparse
import sys
from pathlib import Path

from .conventions import validate_configuration
from .generator import (
    write_chart_metadata,
    write_environment_values,
    write_project_definitions,
    write_readme,
)
from .models import (
    ComponentConfiguration,
    ProjectConfiguration,
)
from .template import (
    copy_template,
    validate_template_structure,
)
from .validator import validate_generated_project


def bool_from_string(value: str) -> bool:
    normalized_value = value.strip().lower()

    if normalized_value in {"true", "1", "yes", "y"}:
        return True

    if normalized_value in {"false", "0", "no", "n"}:
        return False

    raise argparse.ArgumentTypeError(
        f"Valor booleano no válido: {value}"
    )


def parse_component_list(value: str) -> list[str]:
    """Convierte una lista CSV en una lista de nombres."""

    return [
        component.strip()
        for component in value.split(",")
        if component.strip()
    ]


def add_project_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--application-name",
        required=True,
        help="Nombre técnico global del proyecto. Ejemplo: pdu.",
    )

    parser.add_argument(
        "--application-version",
        required=True,
        help="Versión de las imágenes. Ejemplo: 1.0.0.",
    )

    parser.add_argument(
        "--chart-version",
        default="0.1.0",
        help="Versión del chart Helm.",
    )

    parser.add_argument(
        "--fronts",
        default="",
        help=(
            "Componentes front separados por comas. Ejemplo: "
            "catalogo-alertas-api,gestor-snapshot."
        ),
    )

    parser.add_argument(
        "--apis",
        default="",
        help=(
            "Componentes API separados por comas. Ejemplo: "
            "consulta-personas,gestion-expedientes."
        ),
    )

    parser.add_argument(
        "--microservicios",
        default="",
        help=(
            "Microservicios separados por comas. Ejemplo: "
            "notificador,procesador-ficheros."
        ),
    )

    parser.add_argument(
        "--backend-container-port",
        type=int,
        default=8080,
        help="Puerto por defecto de APIs y microservicios.",
    )

    parser.add_argument(
        "--front-container-port",
        type=int,
        default=80,
        help="Puerto por defecto de frontales.",
    )

    parser.add_argument(
        "--registry-path",
        default="",
        help=(
            "Path común dentro del registry. Por defecto se usa "
            "application-name."
        ),
    )

    parser.add_argument(
        "--dns-suffix",
        required=True,
        help=(
            "Sufijo DNS base para construir los hosts de INT y CER. "
            "Ejemplo: 10.200.201.76.nip.io. A partir de él se "
            "generan automáticamente front-<project>-integration."
            "<sufijo>, api-<project>-integration.<sufijo> y sus "
            "equivalentes -certification."
        ),
    )

    parser.add_argument(
        "--replica-count",
        type=int,
        default=1,
        help="Réplicas iniciales de cada componente.",
    )

    parser.add_argument(
        "--usage-level",
        choices=["low", "medium", "high"],
        default="low",
        help="Perfil inicial de recursos.",
    )

    parser.add_argument(
        "--sas-monitoring-enabled",
        type=bool_from_string,
        default=False,
        help="Habilita métricas SAS.",
    )

    parser.add_argument(
        "--metrics-path",
        default="/metrics",
        help="Ruta de métricas.",
    )

    parser.add_argument(
        "--ingress-enabled",
        type=bool_from_string,
        default=True,
        help="Habilita Ingress, Gateway y VirtualServices.",
    )

    parser.add_argument(
        "--autoscaling-enabled",
        type=bool_from_string,
        default=False,
        help="Habilita HPA.",
    )


def build_components(
    arguments: argparse.Namespace,
) -> tuple[ComponentConfiguration, ...]:
    components: list[ComponentConfiguration] = []

    component_groups = (
        (
            "front",
            parse_component_list(arguments.fronts),
            arguments.front_container_port,
        ),
        (
            "api",
            parse_component_list(arguments.apis),
            arguments.backend_container_port,
        ),
        (
            "microservicio",
            parse_component_list(arguments.microservicios),
            arguments.backend_container_port,
        ),
    )

    for project_type, names, port in component_groups:
        for name in names:
            components.append(
                ComponentConfiguration(
                    name=name,
                    project_type=project_type,
                    image_name=name,
                    container_port=port,
                    application_context_path=f"/{name}",
                )
            )

    return tuple(components)


def build_configuration(
    arguments: argparse.Namespace,
) -> ProjectConfiguration:
    application_name = arguments.application_name.strip()

    registry_path = arguments.registry_path.strip()
    if not registry_path:
        registry_path = application_name

    return ProjectConfiguration(
        application_name=application_name,
        application_version=arguments.application_version.strip(),
        chart_version=arguments.chart_version.strip(),
        registry_path=registry_path,
        dns_suffix=arguments.dns_suffix.strip(),
        replica_count=arguments.replica_count,
        usage_level=arguments.usage_level.strip(),
        sas_monitoring_enabled=arguments.sas_monitoring_enabled,
        metrics_path=arguments.metrics_path.strip(),
        ingress_enabled=arguments.ingress_enabled,
        autoscaling_enabled=arguments.autoscaling_enabled,
        components=build_components(arguments),
    )


def build_valid_configuration(
    arguments: argparse.Namespace,
) -> tuple[ProjectConfiguration | None, list[str]]:
    """
    Construye la configuración y la valida en un único paso.

    Devuelve (config, []) si es válida, o (None, errores) en caso
    contrario, evitando repetir el patrón "construir -> validar"
    en cada subcomando de la CLI.
    """

    config = build_configuration(arguments)
    errors = validate_configuration(config)

    if errors:
        return None, errors

    return config, []


def print_errors(errors: list[str]) -> None:
    for error in errors:
        print(f"ERROR: {error}", file=sys.stderr)


def validate_input_command(
    arguments: argparse.Namespace,
) -> int:
    _, errors = build_valid_configuration(arguments)

    if errors:
        print_errors(errors)
        return 1

    print("OK: Parámetros de entrada válidos.")
    return 0


def generate_command(
    arguments: argparse.Namespace,
) -> int:
    config, errors = build_valid_configuration(arguments)

    if errors or config is None:
        print_errors(errors)
        return 1

    template_directory = Path(
        arguments.template_directory
    ).resolve()

    output_directory = Path(
        arguments.output_directory
    ).resolve()

    template_errors = validate_template_structure(
        template_directory
    )

    if template_errors:
        print_errors(template_errors)
        return 1

    copy_template(
        template_directory=template_directory,
        output_directory=output_directory,
    )

    chart_file = write_chart_metadata(
        chart_directory=output_directory,
        config=config,
    )

    int_values_file, cer_values_file = write_environment_values(
        chart_directory=output_directory,
        config=config,
    )

    project_files = write_project_definitions(
        chart_directory=output_directory,
        config=config,
    )

    readme_file = write_readme(
        chart_directory=output_directory,
        config=config,
    )

    print("OK: Chart Helm PDU generado correctamente.")
    print(f"Chart: {output_directory}")
    print(f"Chart metadata: {chart_file}")
    print(f"Valores INT: {int_values_file}")
    print(f"Valores CER: {cer_values_file}")
    print(f"Componentes generados: {len(project_files)}")
    print(f"README: {readme_file}")

    return 0


def validate_chart_command(
    arguments: argparse.Namespace,
) -> int:
    chart_directory = Path(
        arguments.chart_directory
    ).resolve()

    errors = validate_generated_project(
        chart_directory=chart_directory,
    )

    if errors:
        print_errors(errors)
        return 1

    print("OK: Chart y componentes válidos.")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="helm-generator",
        description="Generador de charts Helm transversales.",
    )

    subparsers = parser.add_subparsers(
        dest="command",
        required=True,
    )

    validate_input_parser = subparsers.add_parser(
        "validate-input",
        help="Valida los parámetros de entrada.",
    )

    add_project_arguments(validate_input_parser)
    validate_input_parser.set_defaults(
        handler=validate_input_command,
    )

    generate_parser = subparsers.add_parser(
        "generate",
        help="Genera un chart Helm con múltiples componentes.",
    )

    generate_parser.add_argument(
        "--template-directory",
        required=True,
        help="Directorio de la plantilla Helm base.",
    )

    generate_parser.add_argument(
        "--output-directory",
        required=True,
        help="Directorio de salida del chart.",
    )

    add_project_arguments(generate_parser)
    generate_parser.set_defaults(
        handler=generate_command,
    )

    validate_chart_parser = subparsers.add_parser(
        "validate-chart",
        help="Valida todos los componentes del chart generado.",
    )

    validate_chart_parser.add_argument(
        "--chart-directory",
        required=True,
        help="Directorio del chart Helm generado.",
    )

    validate_chart_parser.set_defaults(
        handler=validate_chart_command,
    )

    return parser


def main() -> None:
    parser = build_parser()
    arguments = parser.parse_args()
    raise SystemExit(arguments.handler(arguments))
