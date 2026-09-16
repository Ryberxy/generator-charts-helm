import shutil
from pathlib import Path


EXCLUDED_TEMPLATE_DIRECTORIES = {
    ".git",
    "projects",
    "report",
    "validation-output",
}

EXCLUDED_TEMPLATE_FILES = {
    "render.yaml",
    "injectValues_PRE.yaml",
    "injectValues_PRO.yaml",
}


def validate_template_structure(template_directory: Path) -> list[str]:
    errors: list[str] = []

    required_files = [
        "Chart.yaml",
        "injectValues_INT.yaml",
        "injectValues_CER.yaml",
    ]

    for required_file in required_files:
        file_path = template_directory / required_file

        if not file_path.is_file():
            errors.append(
                f"La plantilla no contiene {required_file}."
            )

    templates_directory = template_directory / "templates"

    if not templates_directory.is_dir():
        errors.append(
            "La plantilla no contiene el directorio templates/."
        )

    return errors


def copy_template(
    template_directory: Path,
    output_directory: Path,
) -> None:
    """
    Copia la plantilla Helm a output_directory.

    No copia:
    - .git
    - projects existentes
    - directorios de reportes
    - renderizados temporales
    """

    if output_directory.exists():
        shutil.rmtree(output_directory)

    output_directory.mkdir(parents=True, exist_ok=True)

    for source_path in template_directory.iterdir():
        if source_path.name in EXCLUDED_TEMPLATE_DIRECTORIES:
            continue

        if source_path.name in EXCLUDED_TEMPLATE_FILES:
            continue

        destination_path = output_directory / source_path.name

        if source_path.is_dir():
            shutil.copytree(
                source_path,
                destination_path,
                dirs_exist_ok=True,
            )
        else:
            shutil.copy2(source_path, destination_path)

    (output_directory / "projects").mkdir(
        parents=True,
        exist_ok=True,
    )
