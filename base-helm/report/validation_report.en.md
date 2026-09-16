# Helm InjectValues Validation Report

- Generated: 2026-04-21 11:16:13
- Renders dir: `C:\PROYECTOS\ALERTAS\plantillas_helm\gestor-alertas-helm\report\renders`
- Logs dir: `C:\PROYECTOS\ALERTAS\plantillas_helm\gestor-alertas-helm\report\logs`

## Automatic Checklist (software)

- [x] `helm template` without errors in all environments
  - DES: OK
  - PRE: OK
  - PRO: OK
- [x] YAML parse for DES/PRE/PRO
  - DES: OK
  - PRE: OK
  - PRO: OK
- [x] Environment variable format in configMap/secrets (`UPPERCASE` with optional `_`)
- [x] Environment variable names are consistent across DES/PRE/PRO
- [ ] Rendered templates are similar (allowing environment-specific differences)
  - des-pre: warn
    - structural diffs: 3
      - Service/oc-alert/alert-cca-gestorcatalogoalertas-msc-service
        - details:
          - missing in PRE: $.spec.type
          - missing in PRE: $.spec.ports[0].nodePort
          - missing in PRE: $.spec.ports[0].targetPort
      - Service/oc-alert/alert-gev-consultaalerta-msc-service
        - details:
          - missing in PRE: $.spec.type
          - missing in PRE: $.spec.ports[0].nodePort
          - missing in PRE: $.spec.ports[0].targetPort
      - Service/oc-alert/alert-gev-gestorestadoversionado-msc-service
        - details:
          - missing in PRE: $.spec.type
          - missing in PRE: $.spec.ports[0].nodePort
          - missing in PRE: $.spec.ports[0].targetPort
  - des-pro: warn
    - structural diffs: 3
      - Service/oc-alert/alert-cca-gestorcatalogoalertas-msc-service
        - details:
          - missing in PRO: $.spec.type
          - missing in PRO: $.spec.ports[0].nodePort
          - missing in PRO: $.spec.ports[0].targetPort
      - Service/oc-alert/alert-gev-consultaalerta-msc-service
        - details:
          - missing in PRO: $.spec.type
          - missing in PRO: $.spec.ports[0].nodePort
          - missing in PRO: $.spec.ports[0].targetPort
      - Service/oc-alert/alert-gev-gestorestadoversionado-msc-service
        - details:
          - missing in PRO: $.spec.type
          - missing in PRO: $.spec.ports[0].nodePort
          - missing in PRO: $.spec.ports[0].targetPort
  - pre-pro: ok

## Build Errors

- No build errors detected.

## User Checklist (manual validation)

- [ ] Validate gateway in PRE and PRO:
  - PRE Gateway: `alertas-gateway`
  - PRO Gateway: `alertas-gateway`
- [ ] Validate DNS in PRE and PRO:
  - PRE DNS hosts:
    - microservicio: `api-alertas-pre.sas.junta-andalucia.es`
    - front: `NO_APLICA_EN_ESTA_ITERACION`
    - api: `NO_APLICA_EN_ESTA_ITERACION`
  - PRO DNS hosts:
    - microservicio: `api-alertas-pro.sas.junta-andalucia.es`
    - front: `NO_APLICA_EN_ESTA_ITERACION`
    - api: `NO_APLICA_EN_ESTA_ITERACION`
- [ ] Validate environment-dependent variables in PRE/PRO:
  - PRE document: `C:\PROYECTOS\ALERTAS\plantillas_helm\gestor-alertas-helm\injectValues_PRE.yaml`
  - PRO document: `C:\PROYECTOS\ALERTAS\plantillas_helm\gestor-alertas-helm\injectValues_PRO.yaml`
  - PRE global.developDeployment: `false`
  - PRO global.developDeployment: `false`
  - none
- [ ] Validate version/imageTag of each microservice in PRE and PRO:
  - [PRE] projects:
    - [PRE] projects/alert-cca-gestorcatalogoalertas-msc.yaml: `alert-cca-gestorcatalogoalertas-msc:develop-0`
    - [PRE] projects/alert-gev-gestorestadoversionado-msc.yaml: `alert-gev-gestorestadoversionado-msc:develop-0`
    - [PRE] projects/alert-gev-consultaalerta-msc.yaml: `alert-gev-consultaalerta-msc:develop-0`
  - [PRO] projects:
    - [PRO] projects/alert-cca-gestorcatalogoalertas-msc.yaml: `alert-cca-gestorcatalogoalertas-msc:develop-0`
    - [PRO] projects/alert-gev-gestorestadoversionado-msc.yaml: `alert-gev-gestorestadoversionado-msc:develop-0`
    - [PRO] projects/alert-gev-consultaalerta-msc.yaml: `alert-gev-consultaalerta-msc:develop-0`

## Simplicity Recommendations

- High value duplication detected (95.1% equal leaf values). Use a shared base and minimal per-environment overrides. (doc: `C:\PROYECTOS\ALERTAS\plantillas_helm\gestor-alertas-helm\injectValues_DES.yaml`)
- DES: sensitive keys detected in values (example: projects[0].spec.environment.secrets.DB_URL). Recommended: move secrets to Secret manager/ExternalSecret. (doc: `C:\PROYECTOS\ALERTAS\plantillas_helm\gestor-alertas-helm\injectValues_DES.yaml`)

## Proposed Improvements (software + report)

- Integrate into CI and block PRs when parse/template fails.
- Add baseline mode to compare against approved snapshots.
- Add JSONPath allowlist for expected DES-only differences.
- Keep structured JSON output for tooling consumption.
