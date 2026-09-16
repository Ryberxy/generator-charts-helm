# Informe de Validacion Helm InjectValues

- Generado: 2026-04-21 11:16:13
- Renders dir: `C:\PROYECTOS\ALERTAS\plantillas_helm\gestor-alertas-helm\report\renders`
- Logs dir: `C:\PROYECTOS\ALERTAS\plantillas_helm\gestor-alertas-helm\report\logs`

## Checklist automatica (software)

- [x] `helm template` sin errores en todos los entornos
  - DES: OK
  - PRE: OK
  - PRO: OK
- [x] Parseo YAML para DES/PRE/PRO
  - DES: OK
  - PRE: OK
  - PRO: OK
- [x] Formato de variables de entorno en configMap/secrets (`MAYUSCULAS` con `_` opcional)
- [x] Nombres de variables de entorno consistentes en DES/PRE/PRO
- [ ] Templates renderizados similares (permitiendo diferencias por entorno)
  - des-pre: warn
    - diferencias estructurales: 3
      - Service/oc-alert/alert-cca-gestorcatalogoalertas-msc-service
        - detalles:
          - falta en PRE: $.spec.type
          - falta en PRE: $.spec.ports[0].nodePort
          - falta en PRE: $.spec.ports[0].targetPort
      - Service/oc-alert/alert-gev-consultaalerta-msc-service
        - detalles:
          - falta en PRE: $.spec.type
          - falta en PRE: $.spec.ports[0].nodePort
          - falta en PRE: $.spec.ports[0].targetPort
      - Service/oc-alert/alert-gev-gestorestadoversionado-msc-service
        - detalles:
          - falta en PRE: $.spec.type
          - falta en PRE: $.spec.ports[0].nodePort
          - falta en PRE: $.spec.ports[0].targetPort
  - des-pro: warn
    - diferencias estructurales: 3
      - Service/oc-alert/alert-cca-gestorcatalogoalertas-msc-service
        - detalles:
          - falta en PRO: $.spec.type
          - falta en PRO: $.spec.ports[0].nodePort
          - falta en PRO: $.spec.ports[0].targetPort
      - Service/oc-alert/alert-gev-consultaalerta-msc-service
        - detalles:
          - falta en PRO: $.spec.type
          - falta en PRO: $.spec.ports[0].nodePort
          - falta en PRO: $.spec.ports[0].targetPort
      - Service/oc-alert/alert-gev-gestorestadoversionado-msc-service
        - detalles:
          - falta en PRO: $.spec.type
          - falta en PRO: $.spec.ports[0].nodePort
          - falta en PRO: $.spec.ports[0].targetPort
  - pre-pro: ok

## Errores de Construccion

- No se detectaron errores de construccion.

## Checklist del Usuario (validacion manual)

- [ ] Validar gateway en PRE y PRO:
  - Gateway PRE: `alertas-gateway`
  - Gateway PRO: `alertas-gateway`
- [ ] Validar DNS en PRE y PRO:
  - Hosts DNS PRE:
    - microservicio: `api-alertas-pre.sas.junta-andalucia.es`
    - front: `NO_APLICA_EN_ESTA_ITERACION`
    - api: `NO_APLICA_EN_ESTA_ITERACION`
  - Hosts DNS PRO:
    - microservicio: `api-alertas-pro.sas.junta-andalucia.es`
    - front: `NO_APLICA_EN_ESTA_ITERACION`
    - api: `NO_APLICA_EN_ESTA_ITERACION`
- [ ] Validar variables de entorno dependientes de PRE/PRO:
  - Documento PRE: `C:\PROYECTOS\ALERTAS\plantillas_helm\gestor-alertas-helm\injectValues_PRE.yaml`
  - Documento PRO: `C:\PROYECTOS\ALERTAS\plantillas_helm\gestor-alertas-helm\injectValues_PRO.yaml`
  - PRE global.developDeployment: `false`
  - PRO global.developDeployment: `false`
  - ninguno
- [ ] Validar version/imageTag de cada microservicio en PRE y PRO:
  - [PRE] proyectos:
    - [PRE] projects/alert-cca-gestorcatalogoalertas-msc.yaml: `alert-cca-gestorcatalogoalertas-msc:develop-0`
    - [PRE] projects/alert-gev-gestorestadoversionado-msc.yaml: `alert-gev-gestorestadoversionado-msc:develop-0`
    - [PRE] projects/alert-gev-consultaalerta-msc.yaml: `alert-gev-consultaalerta-msc:develop-0`
  - [PRO] proyectos:
    - [PRO] projects/alert-cca-gestorcatalogoalertas-msc.yaml: `alert-cca-gestorcatalogoalertas-msc:develop-0`
    - [PRO] projects/alert-gev-gestorestadoversionado-msc.yaml: `alert-gev-gestorestadoversionado-msc:develop-0`
    - [PRO] projects/alert-gev-consultaalerta-msc.yaml: `alert-gev-consultaalerta-msc:develop-0`

## Recomendaciones de Simplicidad

- Hay alta repeticion de valores (95.1% de hojas iguales). Conviene una base comun y overrides minimos por entorno. (doc: `C:\PROYECTOS\ALERTAS\plantillas_helm\gestor-alertas-helm\injectValues_DES.yaml`)
- DES: se detectan claves sensibles en values (ej: projects[0].spec.environment.secrets.DB_URL). Recomendado mover secretos a Secret manager/ExternalSecret. (doc: `C:\PROYECTOS\ALERTAS\plantillas_helm\gestor-alertas-helm\injectValues_DES.yaml`)

## Mejoras Propuestas (software + informe)

- Integrar en CI y bloquear PR cuando falle parse/template.
- Agregar modo baseline para comparar con snapshots aprobados.
- Agregar allowlist por JSONPath para diferencias esperadas DES-only.
- Mantener salida JSON estructurada para consumo de herramientas.
