# helm-generator

Herramienta interna para generar charts Helm de despliegue a partir de una
**plantilla base transversal**. Un equipo describe sus componentes (fronts,
APIs, microservicios) por línea de comandos, y la herramienta genera un
chart Helm completo (`Chart.yaml`, `injectValues_INT.yaml`,
`injectValues_CER.yaml`, `projects/*.yaml`, `README.md`) listo para
`helm template` / `helm install`.

No genera los templates Helm (`.tpl`, `worker.yaml`, etc.) — esos viven en
la **plantilla base** (un directorio Helm ya existente) y se copian tal
cual. Esta herramienta solo genera los **valores** (`values.yaml` /
`injectValues_*.yaml`) y las **definiciones de proyecto**
(`projects/<componente>.yaml`) que esos templates consumen.

---

## 1. Conceptos clave

| Concepto | Qué es |
|---|---|
| **Plantilla base** (`--template-directory`) | Un directorio Helm con `Chart.yaml`, `injectValues_INT.yaml`, `injectValues_CER.yaml` y `templates/`. Es genérica: no conoce microservicios concretos, solo sabe procesar `.Values.projects` (ver `templates/worker.yaml` en la plantilla). |
| **Chart generado** (`--output-directory`) | Copia de la plantilla base + los ficheros que esta herramienta añade/sobreescribe: `Chart.yaml` (metadata), `injectValues_INT.yaml`, `injectValues_CER.yaml`, `projects/*.yaml`, `README.md`. |
| **Componente** | Una pieza desplegable: `front`, `api` o `microservicio`. Se declara con `--fronts`, `--apis` o `--microservicios` (listas separadas por comas). |
| **Entorno** | `integration` (INT) o `certification` (CER). La herramienta genera **ambos** en una sola ejecución de `generate`. |

---

## 2. Flujo de una generación

```
helm-generator generate --application-name pdu ...
        │
        ▼
1. build_configuration()      cli.py       → arguments → ProjectConfiguration
2. validate_configuration()   conventions.py → ProjectConfiguration → [errores]
3. validate_template_structure() template.py → comprueba la plantilla base
4. copy_template()             template.py  → copia la plantilla al output,
                                               EXCLUYENDO projects/, .git/, etc.
5. write_chart_metadata()      generator.py → Chart.yaml
6. write_environment_values()  generator.py → injectValues_INT.yaml
                                               injectValues_CER.yaml
7. write_project_definitions() generator.py → projects/<componente>.yaml
8. write_readme()               generator.py → README.md
```

Si quieres **validar solo los parámetros** sin tocar disco:
`helm-generator validate-input ...` (ejecuta los pasos 1-2).

Si quieres **validar un chart ya generado** (por ejemplo en CI, tras un
`generate`): `helm-generator validate-chart --chart-directory ...` (lee
`projects/*.yaml` del chart generado y comprueba que cada uno tiene lo
mínimo, y que no se ha colado configuración específica de otro proyecto).

---

## 3. Mapa de ficheros — qué mirar primero

Lee en este orden si es la primera vez que tocas el código:

### `src/helm_generator/models.py`
Las dos únicas estructuras de datos de toda la herramienta.

- `ComponentConfiguration`: un componente individual (`name`, `project_type`,
  `image_name`, `container_port`, `application_context_path`).
- `ProjectConfiguration`: la configuración completa de una generación
  (nombre de proyecto, versión, `dns_suffix`, réplicas, nivel de uso,
  lista de componentes...).

Todo el resto de módulos recibe o produce estas dos clases. **Si añades un
campo de configuración nuevo, casi siempre empieza aquí.**

### `src/helm_generator/cli.py`
Punto de entrada (`main()`). Define los 3 subcomandos con `argparse`:

- `validate-input` — valida los parámetros sin generar nada.
- `generate` — genera el chart completo.
- `validate-chart` — valida un chart ya generado.

Funciones relevantes:

- `add_project_arguments()` — declara todos los flags comunes a
  `validate-input` y `generate` (nombre, versión, listas de componentes,
  `--dns-suffix`, réplicas, nivel de uso, etc.).
- `build_components()` — convierte `--fronts/--apis/--microservicios`
  (CSV) en una tupla de `ComponentConfiguration`.
- `build_configuration()` — junta todo en un `ProjectConfiguration`.
- `build_valid_configuration()` — construye y valida en un paso, usado
  por los tres subcomandos para no repetir el patrón.

**Si añades un flag de línea de comandos nuevo, se toca aquí
(`add_project_arguments`) y en `models.py` (el campo correspondiente).**

### `src/helm_generator/conventions.py`
Un único punto de validación: `validate_configuration(config)`, que
devuelve una lista de errores (vacía si todo es correcto). Valida:

- Formato de `application_name` (minúsculas, números, guiones).
- `application_version` en formato SemVer.
- Que haya al menos un componente.
- `replica_count >= 1`, `usage_level` válido, `metrics_path` empieza por `/`.
- `dns_suffix` obligatorio si `ingress_enabled=true`.
- Por cada componente: nombre válido, tipo válido (`front`/`api`/
  `microservicio`), puerto válido, contexto empieza por `/`, sin nombres
  duplicados.

**Si añades una regla de negocio nueva («los nombres no pueden superar
30 caracteres», por ejemplo), se toca aquí.**

### `src/helm_generator/generator.py`
El módulo más grande: construye y escribe todos los ficheros del chart.
Sigue el patrón `build_*` (construye un `dict` en memoria, sin tocar
disco) + `write_*` (llama al `build_*` correspondiente y vuelca a YAML).

Funciones de nombres/convenciones (todas puras, sin efectos secundarios):

- `get_gateway_name`, `get_ingress_name` → `<project>-gateway`,
  `<project>-ingress`.
- `get_integration_namespace`, `get_certification_namespace` →
  `<project>-integration`, `<project>-certification`.
- `get_front_host(config, environment)` →
  `front-<project>-<environment>.<dns_suffix>`. Host **compartido por
  todos los fronts** de un entorno; cada front añade su propio prefijo
  de ruta (`application_context_path`) para convivir en el mismo host.
- `get_backend_host(config, environment)` →
  `api-<project>-<environment>.<dns_suffix>`. Host compartido por **api
  y microservicio** (misma convención que el chart de alertas real).

Funciones de construcción:

- `build_chart_metadata` / `write_chart_metadata` → `Chart.yaml`.
- `build_usage_spec` → perfiles de recursos `low`/`medium`/`high`
  (CPU/memoria de request y limit).
- `build_probe` / `build_liveness_probe` → readiness/liveness probes
  estándar (`/health/ready`, `/health/live`).
- `build_cors_policy` → política CORS por defecto (todo abierto).
- `build_default_type_spec` → el `spec` común que comparten todos los
  componentes de un mismo tipo (`front`, `api`, `microservicio`) en un
  entorno: réplicas, `usageSpec`, ingress (host + gateway), CORS,
  environment vacío.
- `build_environment_values` / `write_environment_values` → arma y
  escribe `injectValues_INT.yaml` e `injectValues_CER.yaml` completos:
  `global`, `ingress`, `front.spec`, `api.spec`, `microservicio.spec` y
  la lista `projects` (qué fichero de `projects/` usa cada componente y
  con qué `imageTag`).
- `build_autoscaling_block` → si `autoscaling_enabled=true`, añade
  `minReplicas`/`maxReplicas`/targets de CPU y memoria (obligatorios
  para que el HPA de la plantilla no falle con `required`).
- `build_project_definition` / `write_project_definitions` → el
  `spec` individual de cada componente (`projects/<nombre>.yaml`):
  imagen, puerto, servicio, gateway/ingress, `trafficManagement.ruleSet`
  (la ruta del componente), autoscaling, probes y, solo si es `front`,
  el bloque `runtimeConfig`/`configFile` para inyectar config al SPA.
- `write_readme` → genera el `README.md` **del chart resultante** (no
  confundir con este README, que documenta la herramienta).

**Si cambias cómo se construye cualquier valor del chart (recursos,
hosts, probes, autoscaling...), se toca aquí.**

### `src/helm_generator/template.py`
Dos responsabilidades, nada más:

- `validate_template_structure(template_directory)` — comprueba que la
  plantilla base tiene `Chart.yaml`, `injectValues_INT.yaml`,
  `injectValues_CER.yaml` y un directorio `templates/`.
- `copy_template(template_directory, output_directory)` — copia la
  plantilla al chart de salida. **Excluye siempre** `.git/`, `projects/`,
  `report/`, `validation-output/`, `render.yaml`,
  `injectValues_PRE.yaml`, `injectValues_PRO.yaml` (esos dos últimos son
  de los entornos de alertas real, no de PDU). `projects/` se recrea
  vacío y lo rellena `write_project_definitions`.

**Los ficheros de `projects/*.yaml` que tenga la plantilla base nunca se
usan como entrada de esta herramienta.** Son irrelevantes para
`generate` — se pueden borrar de la plantilla sin ningún efecto.

### `src/helm_generator/validator.py`
Valida un chart **ya generado** (no los parámetros de entrada). Lo usa
el subcomando `validate-chart`, típicamente en CI tras un `generate`.

- `validate_generated_project(chart_directory)` — recorre
  `projects/*.yaml` y valida cada uno con `validate_component_file`.
- `validate_component_file` — comprueba `spec.name`, `spec.image.name`,
  puertos válidos y coincidentes entre `container.port` y
  `service.port`, y que `spec.ingress.contextPath` empiece por `/`.
- `find_forbidden_keys` — recorre el YAML recursivamente y falla si
  encuentra claves de `FORBIDDEN_CONFIGURATION_KEYS` (`alertas`,
  `kafka`, `keycloak`, `authentication`, `authorization`, `audita`):
  configuración específica de un proyecto concreto que no debería
  colarse en una plantilla transversal.

---

## 4. Uso

### Generar un chart

```bash
helm-generator generate \
  --application-name pdu \
  --application-version 1.0.0 \
  --chart-version 0.1.0 \
  --fronts "portal-cliente,portal-gestor" \
  --apis "consulta-expedientes" \
  --microservicios "notificador,procesador-ficheros,auditoria,workflow" \
  --dns-suffix 10.200.201.76.nip.io \
  --template-directory /ruta/a/la/plantilla-base \
  --output-directory /ruta/de/salida
```

Esto genera, para INT y CER:

| Tipo | Host | Ejemplo de ruta |
|---|---|---|
| `front` | `front-<project>-<env>.<dns-suffix>` | `/portal-cliente` |
| `api` / `microservicio` | `api-<project>-<env>.<dns-suffix>` | `/notificador` |

La ruta de cada componente (`application_context_path`) se calcula por
defecto como `/<nombre-del-componente>`, pero **queda escrita en
`projects/<nombre>.yaml`**, así que después de generar puedes editarla a
mano en ese fichero si necesitas algo distinto — ten en cuenta que
volver a ejecutar `generate` sobreescribe `projects/` desde cero.

### Solo validar los parámetros (sin generar nada)

```bash
helm-generator validate-input \
  --application-name pdu \
  --application-version 1.0.0 \
  --fronts "portal-cliente" \
  --dns-suffix 10.200.201.76.nip.io
```

### Validar un chart ya generado

```bash
helm-generator validate-chart --chart-directory /ruta/de/salida
```

### Flags principales

| Flag | Obligatorio | Descripción |
|---|---|---|
| `--application-name` | sí | Nombre técnico del proyecto (minúsculas, números, guiones). |
| `--application-version` | sí | Versión SemVer, se usa como `imageTag` de todos los componentes. |
| `--chart-version` | no (`0.1.0`) | Versión del chart en `Chart.yaml`. |
| `--fronts` / `--apis` / `--microservicios` | no (vacío) | Listas CSV de nombres de componentes. Al menos uno de los tres es obligatorio. |
| `--dns-suffix` | sí si `--ingress-enabled` (default sí) | Dominio base. Los hosts de front/api/microservicio se derivan de aquí. |
| `--backend-container-port` | no (`8080`) | Puerto por defecto de `api`/`microservicio`. |
| `--front-container-port` | no (`80`) | Puerto por defecto de `front`. |
| `--registry-path` | no (`application-name`) | Path dentro del registry de imágenes. |
| `--replica-count` | no (`1`) | Réplicas iniciales de cada componente. |
| `--usage-level` | no (`low`) | `low` / `medium` / `high`. Perfil de CPU/memoria. |
| `--autoscaling-enabled` | no (`false`) | Habilita HPA (con targets ya calculados). |
| `--sas-monitoring-enabled` | no (`false`) | Anotaciones Prometheus en el `Service`. |
| `--ingress-enabled` | no (`true`) | Genera Gateway/Ingress/VirtualService. |
| `--template-directory` | sí (solo `generate`) | Ruta a la plantilla base Helm. |
| `--output-directory` | sí (solo `generate`) | Ruta de salida del chart generado. |

---

## 5. Tests

```bash
cd generator-helm
PYTHONPATH=src python3 -m pytest tests -v
```

Los tests están organizados igual que el código:

- `tests/test_conventions.py` → valida `conventions.py`.
- `tests/test_generator.py` → valida `generator.py` (definiciones de
  proyecto, autoscaling, hosts front/backend).
- `tests/test_validator.py` → valida `validator.py` contra un chart
  generado de verdad.

Si añades un campo/regla nueva, añade su test en el fichero
correspondiente antes de tocar `generator.py`/`conventions.py`.

---

## 6. Preguntas frecuentes

**¿Por qué `helm lint` se queja de `values.yaml: file does not exist`?**
Es solo informativo. Esta herramienta usa `injectValues_INT.yaml` /
`injectValues_CER.yaml` en vez de `values.yaml`, pasados con `-f` en el
`helm template`/`install`. No afecta al resultado.

**¿Por qué el namespace sale `default` si no paso `-n`?**
Los templates de la plantilla base usan `.Release.Namespace` (el que
fija el flag `-n`/`--namespace` de Helm), no el campo `global.nameSpace`
de los values — ese campo es solo informativo/de referencia. Despliega
siempre con `-n <namespace>` explícito, usando el mismo valor que
`get_integration_namespace`/`get_certification_namespace` calculan
(`<project>-integration` / `<project>-certification`).

**¿Necesito los ficheros de `projects/*.yaml` que trae la plantilla
base?**
No, si la plantilla se usa solo como `--template-directory`: esa carpeta
se excluye siempre al copiar y se regenera desde los flags de
`generate`. Solo son necesarios si ese mismo directorio se despliega
también, aparte, como chart Helm independiente de otro proyecto.# helm-generator

Herramienta interna para generar charts Helm de despliegue a partir de una
**plantilla base transversal**. Un equipo describe sus componentes (fronts,
APIs, microservicios) por línea de comandos, y la herramienta genera un
chart Helm completo (`Chart.yaml`, `injectValues_INT.yaml`,
`injectValues_CER.yaml`, `projects/*.yaml`, `README.md`) listo para
`helm template` / `helm install`.

No genera los templates Helm (`.tpl`, `worker.yaml`, etc.) — esos viven en
la **plantilla base** (un directorio Helm ya existente) y se copian tal
cual. Esta herramienta solo genera los **valores** (`values.yaml` /
`injectValues_*.yaml`) y las **definiciones de proyecto**
(`projects/<componente>.yaml`) que esos templates consumen.

---

## 1. Conceptos clave

| Concepto | Qué es |
|---|---|
| **Plantilla base** (`--template-directory`) | Un directorio Helm con `Chart.yaml`, `injectValues_INT.yaml`, `injectValues_CER.yaml` y `templates/`. Es genérica: no conoce microservicios concretos, solo sabe procesar `.Values.projects` (ver `templates/worker.yaml` en la plantilla). |
| **Chart generado** (`--output-directory`) | Copia de la plantilla base + los ficheros que esta herramienta añade/sobreescribe: `Chart.yaml` (metadata), `injectValues_INT.yaml`, `injectValues_CER.yaml`, `projects/*.yaml`, `README.md`. |
| **Componente** | Una pieza desplegable: `front`, `api` o `microservicio`. Se declara con `--fronts`, `--apis` o `--microservicios` (listas separadas por comas). |
| **Entorno** | `integration` (INT) o `certification` (CER). La herramienta genera **ambos** en una sola ejecución de `generate`. |

---

## 2. Flujo de una generación

```
helm-generator generate --application-name pdu ...
        │
        ▼
1. build_configuration()      cli.py       → arguments → ProjectConfiguration
2. validate_configuration()   conventions.py → ProjectConfiguration → [errores]
3. validate_template_structure() template.py → comprueba la plantilla base
4. copy_template()             template.py  → copia la plantilla al output,
                                               EXCLUYENDO projects/, .git/, etc.
5. write_chart_metadata()      generator.py → Chart.yaml
6. write_environment_values()  generator.py → injectValues_INT.yaml
                                               injectValues_CER.yaml
7. write_project_definitions() generator.py → projects/<componente>.yaml
8. write_readme()               generator.py → README.md
```

Si quieres **validar solo los parámetros** sin tocar disco:
`helm-generator validate-input ...` (ejecuta los pasos 1-2).

Si quieres **validar un chart ya generado** (por ejemplo en CI, tras un
`generate`): `helm-generator validate-chart --chart-directory ...` (lee
`projects/*.yaml` del chart generado y comprueba que cada uno tiene lo
mínimo, y que no se ha colado configuración específica de otro proyecto).

---

## 3. Mapa de ficheros — qué mirar primero

Lee en este orden si es la primera vez que tocas el código:

### `src/helm_generator/models.py`
Las dos únicas estructuras de datos de toda la herramienta.

- `ComponentConfiguration`: un componente individual (`name`, `project_type`,
  `image_name`, `container_port`, `application_context_path`).
- `ProjectConfiguration`: la configuración completa de una generación
  (nombre de proyecto, versión, `dns_suffix`, réplicas, nivel de uso,
  lista de componentes...).

Todo el resto de módulos recibe o produce estas dos clases. **Si añades un
campo de configuración nuevo, casi siempre empieza aquí.**

### `src/helm_generator/cli.py`
Punto de entrada (`main()`). Define los 3 subcomandos con `argparse`:

- `validate-input` — valida los parámetros sin generar nada.
- `generate` — genera el chart completo.
- `validate-chart` — valida un chart ya generado.

Funciones relevantes:

- `add_project_arguments()` — declara todos los flags comunes a
  `validate-input` y `generate` (nombre, versión, listas de componentes,
  `--dns-suffix`, réplicas, nivel de uso, etc.).
- `build_components()` — convierte `--fronts/--apis/--microservicios`
  (CSV) en una tupla de `ComponentConfiguration`.
- `build_configuration()` — junta todo en un `ProjectConfiguration`.
- `build_valid_configuration()` — construye y valida en un paso, usado
  por los tres subcomandos para no repetir el patrón.

**Si añades un flag de línea de comandos nuevo, se toca aquí
(`add_project_arguments`) y en `models.py` (el campo correspondiente).**

### `src/helm_generator/conventions.py`
Un único punto de validación: `validate_configuration(config)`, que
devuelve una lista de errores (vacía si todo es correcto). Valida:

- Formato de `application_name` (minúsculas, números, guiones).
- `application_version` en formato SemVer.
- Que haya al menos un componente.
- `replica_count >= 1`, `usage_level` válido, `metrics_path` empieza por `/`.
- `dns_suffix` obligatorio si `ingress_enabled=true`.
- Por cada componente: nombre válido, tipo válido (`front`/`api`/
  `microservicio`), puerto válido, contexto empieza por `/`, sin nombres
  duplicados.

**Si añades una regla de negocio nueva («los nombres no pueden superar
30 caracteres», por ejemplo), se toca aquí.**

### `src/helm_generator/generator.py`
El módulo más grande: construye y escribe todos los ficheros del chart.
Sigue el patrón `build_*` (construye un `dict` en memoria, sin tocar
disco) + `write_*` (llama al `build_*` correspondiente y vuelca a YAML).

Funciones de nombres/convenciones (todas puras, sin efectos secundarios):

- `get_gateway_name`, `get_ingress_name` → `<project>-gateway`,
  `<project>-ingress`.
- `get_integration_namespace`, `get_certification_namespace` →
  `<project>-integration`, `<project>-certification`.
- `get_front_host(config, environment)` →
  `front-<project>-<environment>.<dns_suffix>`. Host **compartido por
  todos los fronts** de un entorno; cada front añade su propio prefijo
  de ruta (`application_context_path`) para convivir en el mismo host.
- `get_backend_host(config, environment)` →
  `api-<project>-<environment>.<dns_suffix>`. Host compartido por **api
  y microservicio** (misma convención que el chart de alertas real).

Funciones de construcción:

- `build_chart_metadata` / `write_chart_metadata` → `Chart.yaml`.
- `build_usage_spec` → perfiles de recursos `low`/`medium`/`high`
  (CPU/memoria de request y limit).
- `build_probe` / `build_liveness_probe` → readiness/liveness probes
  estándar (`/health/ready`, `/health/live`).
- `build_cors_policy` → política CORS por defecto (todo abierto).
- `build_default_type_spec` → el `spec` común que comparten todos los
  componentes de un mismo tipo (`front`, `api`, `microservicio`) en un
  entorno: réplicas, `usageSpec`, ingress (host + gateway), CORS,
  environment vacío.
- `build_environment_values` / `write_environment_values` → arma y
  escribe `injectValues_INT.yaml` e `injectValues_CER.yaml` completos:
  `global`, `ingress`, `front.spec`, `api.spec`, `microservicio.spec` y
  la lista `projects` (qué fichero de `projects/` usa cada componente y
  con qué `imageTag`).
- `build_autoscaling_block` → si `autoscaling_enabled=true`, añade
  `minReplicas`/`maxReplicas`/targets de CPU y memoria (obligatorios
  para que el HPA de la plantilla no falle con `required`).
- `build_project_definition` / `write_project_definitions` → el
  `spec` individual de cada componente (`projects/<nombre>.yaml`):
  imagen, puerto, servicio, gateway/ingress, `trafficManagement.ruleSet`
  (la ruta del componente), autoscaling, probes y, solo si es `front`,
  el bloque `runtimeConfig`/`configFile` para inyectar config al SPA.
- `write_readme` → genera el `README.md` **del chart resultante** (no
  confundir con este README, que documenta la herramienta).

**Si cambias cómo se construye cualquier valor del chart (recursos,
hosts, probes, autoscaling...), se toca aquí.**

### `src/helm_generator/template.py`
Dos responsabilidades, nada más:

- `validate_template_structure(template_directory)` — comprueba que la
  plantilla base tiene `Chart.yaml`, `injectValues_INT.yaml`,
  `injectValues_CER.yaml` y un directorio `templates/`.
- `copy_template(template_directory, output_directory)` — copia la
  plantilla al chart de salida. **Excluye siempre** `.git/`, `projects/`,
  `report/`, `validation-output/`, `render.yaml`,
  `injectValues_PRE.yaml`, `injectValues_PRO.yaml` (esos dos últimos son
  de los entornos de alertas real, no de PDU). `projects/` se recrea
  vacío y lo rellena `write_project_definitions`.

**Los ficheros de `projects/*.yaml` que tenga la plantilla base nunca se
usan como entrada de esta herramienta.** Son irrelevantes para
`generate` — se pueden borrar de la plantilla sin ningún efecto.

### `src/helm_generator/validator.py`
Valida un chart **ya generado** (no los parámetros de entrada). Lo usa
el subcomando `validate-chart`, típicamente en CI tras un `generate`.

- `validate_generated_project(chart_directory)` — recorre
  `projects/*.yaml` y valida cada uno con `validate_component_file`.
- `validate_component_file` — comprueba `spec.name`, `spec.image.name`,
  puertos válidos y coincidentes entre `container.port` y
  `service.port`, y que `spec.ingress.contextPath` empiece por `/`.
- `find_forbidden_keys` — recorre el YAML recursivamente y falla si
  encuentra claves de `FORBIDDEN_CONFIGURATION_KEYS` (`alertas`,
  `kafka`, `keycloak`, `authentication`, `authorization`, `audita`):
  configuración específica de un proyecto concreto que no debería
  colarse en una plantilla transversal.

---

## 4. Uso

### Generar un chart

```bash
helm-generator generate \
  --application-name pdu \
  --application-version 1.0.0 \
  --chart-version 0.1.0 \
  --fronts "portal-cliente,portal-gestor" \
  --apis "consulta-expedientes" \
  --microservicios "notificador,procesador-ficheros,auditoria,workflow" \
  --dns-suffix 10.200.201.76.nip.io \
  --template-directory /ruta/a/la/plantilla-base \
  --output-directory /ruta/de/salida
```

Esto genera, para INT y CER:

| Tipo | Host | Ejemplo de ruta |
|---|---|---|
| `front` | `front-<project>-<env>.<dns-suffix>` | `/portal-cliente` |
| `api` / `microservicio` | `api-<project>-<env>.<dns-suffix>` | `/notificador` |

La ruta de cada componente (`application_context_path`) se calcula por
defecto como `/<nombre-del-componente>`, pero **queda escrita en
`projects/<nombre>.yaml`**, así que después de generar puedes editarla a
mano en ese fichero si necesitas algo distinto — ten en cuenta que
volver a ejecutar `generate` sobreescribe `projects/` desde cero.

### Solo validar los parámetros (sin generar nada)

```bash
helm-generator validate-input \
  --application-name pdu \
  --application-version 1.0.0 \
  --fronts "portal-cliente" \
  --dns-suffix 10.200.201.76.nip.io
```

### Validar un chart ya generado

```bash
helm-generator validate-chart --chart-directory /ruta/de/salida
```

### Flags principales

| Flag | Obligatorio | Descripción |
|---|---|---|
| `--application-name` | sí | Nombre técnico del proyecto (minúsculas, números, guiones). |
| `--application-version` | sí | Versión SemVer, se usa como `imageTag` de todos los componentes. |
| `--chart-version` | no (`0.1.0`) | Versión del chart en `Chart.yaml`. |
| `--fronts` / `--apis` / `--microservicios` | no (vacío) | Listas CSV de nombres de componentes. Al menos uno de los tres es obligatorio. |
| `--dns-suffix` | sí si `--ingress-enabled` (default sí) | Dominio base. Los hosts de front/api/microservicio se derivan de aquí. |
| `--backend-container-port` | no (`8080`) | Puerto por defecto de `api`/`microservicio`. |
| `--front-container-port` | no (`80`) | Puerto por defecto de `front`. |
| `--registry-path` | no (`application-name`) | Path dentro del registry de imágenes. |
| `--replica-count` | no (`1`) | Réplicas iniciales de cada componente. |
| `--usage-level` | no (`low`) | `low` / `medium` / `high`. Perfil de CPU/memoria. |
| `--autoscaling-enabled` | no (`false`) | Habilita HPA (con targets ya calculados). |
| `--sas-monitoring-enabled` | no (`false`) | Anotaciones Prometheus en el `Service`. |
| `--ingress-enabled` | no (`true`) | Genera Gateway/Ingress/VirtualService. |
| `--template-directory` | sí (solo `generate`) | Ruta a la plantilla base Helm. |
| `--output-directory` | sí (solo `generate`) | Ruta de salida del chart generado. |

---

## 5. Tests

```bash
cd generator-helm
PYTHONPATH=src python3 -m pytest tests -v
```

Los tests están organizados igual que el código:

- `tests/test_conventions.py` → valida `conventions.py`.
- `tests/test_generator.py` → valida `generator.py` (definiciones de
  proyecto, autoscaling, hosts front/backend).
- `tests/test_validator.py` → valida `validator.py` contra un chart
  generado de verdad.

Si añades un campo/regla nueva, añade su test en el fichero
correspondiente antes de tocar `generator.py`/`conventions.py`.

---

## 6. Preguntas frecuentes

**¿Por qué `helm lint` se queja de `values.yaml: file does not exist`?**
Es solo informativo. Esta herramienta usa `injectValues_INT.yaml` /
`injectValues_CER.yaml` en vez de `values.yaml`, pasados con `-f` en el
`helm template`/`install`. No afecta al resultado.

**¿Por qué el namespace sale `default` si no paso `-n`?**
Los templates de la plantilla base usan `.Release.Namespace` (el que
fija el flag `-n`/`--namespace` de Helm), no el campo `global.nameSpace`
de los values — ese campo es solo informativo/de referencia. Despliega
siempre con `-n <namespace>` explícito, usando el mismo valor que
`get_integration_namespace`/`get_certification_namespace` calculan
(`<project>-integration` / `<project>-certification`).

**¿Necesito los ficheros de `projects/*.yaml` que trae la plantilla
base?**
No, si la plantilla se usa solo como `--template-directory`: esa carpeta
se excluye siempre al copiar y se regenera desde los flags de
`generate`. Solo son necesarios si ese mismo directorio se despliega
también, aparte, como chart Helm independiente de otro proyecto.

---

## 7. Cadena para lanzar la generación
helm-generator generate \
  --application-name pdu \
  --application-version 1.0.0 \
  --chart-version 0.1.0 \
  --fronts "portal-cliente,portal-gestor" \
  --apis "consulta-expedientes" \
  --microservicios "notificador,procesador-ficheros,auditoria,workflow" \
  --dns-suffix 10.200.201.76.nip.io \
  --template-directory /ruta/base-helm \
  --output-directory /ruta/generated-charts
