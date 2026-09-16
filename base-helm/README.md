### Subdirección de Tecnologías de la Información y Comunicaciones

#### Indice

1. [Datos de proyecto](#1-datos-de-proyecto)
2. [Artefactos generados](#2-artefactos-generados)
3. [Dependencias de Artefactos SAS](#3-dependencias-de-artefactos-sas)
4. [Conjunto de artefactos entregadas necesarias para la compilación de los fuentes](#4-conjunto-de-artefactos-entregadas-necesarias-para-la-compilación-de-los-fuentes)
5. [Navegadores soportados por la aplicación](#5-navegadores-soportados-por-la-aplicación)
6. [Instalación](#6-instalación)
7. [Otros datos de interés](#7-otros-datos-de-interés)
8. [Versión plantilla Readme](#8-versión-plantilla-readme)
----
##### 1. Datos de proyecto
[⇑Indice⇑](#indice)

- **Ámbito:** ```Asistencial```
- **Suite de Aplicaciones:** ```diraya```
- **Aplicación:** ```gestion-centralizada-de-alertas-a-profesionales```
- **Componente:** ```alertas-plataformado-helm```
- **Tipo Aplicación:** ```Plantillas Helm/Administrador paquetes para Kubernetes```
    - **Desplegar en repositorio de artefactos:** ```NO```
    - **Desplegar en repositorio de binarios:** ```SI```
    - **Generar Docker:** ```NO```
- **Firma de Componentes:** ```SI```
- **Tecnología:**
    - **Framework:** ```HELM```
  - **Constructor:** ```npm```
- **Parámetros adicionales:**
    - **Docker:** ```No aplica```
    - **SonarQube:** ```No```
     
- **Descripción de la Aplicación:** ```Paquete Helm de despliegue para los micros de Alertas de catalogo y gestion de estado/consulta.```
- **Observaciones a tener en cuenta:** ```El chart se identifica en Chart.yaml como alertas-plataformado-helm, con versión 0.0.1 y appVersion develop.```

- **Micros incluidos (nomenclatura REPO SAS):**
  - ```motor-evaluador-hechos```
  - ```administrador-tipos-alertas-app-mf```
  - ```catalogo-de-alertas-api```
  - ```motor-evaluacion-eventos```
  - ```compositor-evento-a-hecho-evaluable```
  - ```alertas-a-profesional-app-mf```
  - ```alertas-profesional-bff```
  - ```mapeador-de-alertas-de-profesional```
  - ```controlador-de-estados-alerta-profesional```
  - ```gestor-snapshot-alertas-profesional```
  - ```gestor-estados-alerta-profesional-api```
  - ```registro-de-alertas-centralizado-api```
  - ```gestor-cdv-alertas```
  - ```adaptador-eventos-pruebas-analiticas```
  - ```adaptador-eventos-laboratorio```
  - ```adaptador-eventos-prescripciones```
  - ```proxy-cliente-seguro-maco-rxxi```

- **Correlación nombres antiguos y nombres REPO SAS:**

| **Nombre antiguo / REPO UMANE** | **Nombre nuevo / REPO SAS** |
|:--|:--|
| ```alert-cal-evaluacionhechoalerta-msc``` | ```motor-evaluador-hechos``` |
| ```alert-cca-catalogoalertas-host``` | ```administrador-tipos-alertas-app-mf``` |
| ```alert-cca-gestorcatalogoalertas-msc``` | ```catalogo-de-alertas-api``` |
| ```alert-cha-evaluacondicionesposiblesalerta-msc``` | ```motor-evaluacion-eventos``` |
| ```alert-cha-genhechoevaluablealerta-msc``` | ```compositor-evento-a-hecho-evaluable``` |
| ```alert-eal-usuarioalertas-host``` | ```alertas-a-profesional-app-mf``` |
| ```alert-eal-usuarioalertbff-msc``` | ```alertas-profesional-bff``` |
| ```alert-eap-alertprojection-msc``` | ```mapeador-de-alertas-de-profesional``` |
| ```alert-eap-evaluador-msc``` | ```controlador-de-estados-alerta-profesional``` |
| ```alert-eap-generarsnapshot-msc``` | ```gestor-snapshot-alertas-profesional``` |
| ```alert-eap-manager-msc``` | ```gestor-estados-alerta-profesional-api``` |
| ```alert-gev-consultaalertas-msc``` | ```registro-de-alertas-centralizado-api``` |
| ```alert-gev-gestorestadoversionado-msc``` | ```gestor-cdv-alertas``` |
| ```alert-int-adaptadorsenalesmpa-msc``` | ```adaptador-eventos-pruebas-analiticas``` |
| ```alert-int-adaptadorsenalessil-msc``` | ```adaptador-eventos-laboratorio``` |
| ```alert-int-bdu-acl-msc``` | ```adaptador-eventos-prescripciones``` |
| ```alert-int-rxxi-acl-msc``` | ```proxy-cliente-seguro-maco-rxxi``` |

##### 2. Artefactos generados
[⇑Indice⇑](#indice)

| **Ruta Artefactos** | **Tipo** |
|:----:|:-----:|
| ```Chart.yaml``` | ```Otros (chart Helm)``` |
| ```Jenkinsfile``` | ```Otros (pipeline de despliegue)``` |
| ```injectValues_CER.yaml``` | ```Otros (values de entorno)``` |
| ```injectValues_DES.yaml``` | ```Otros (values de entorno)``` |
| ```injectValues_INT.yaml``` | ```Otros (values de entorno)``` |
| ```injectValues_LOAD.yaml``` | ```Otros (values de entorno)``` |
| ```injectValues_PRE.yaml``` | ```Otros (values de entorno)``` |
| ```injectValues_PRO.yaml``` | ```Otros (values de entorno)``` |
| ```alertas-topics-INT.yaml``` | ```Otros``` |
| ```projects\motor-evaluador-hechos.yaml``` | ```Otros (definición de micro)``` |
| ```projects\administrador-tipos-alertas-app-mf.yaml``` | ```Otros (definición de micro)``` |
| ```projects\catalogo-de-alertas-api.yaml``` | ```Otros (definición de micro)``` |
| ```projects\motor-evaluacion-eventos.yaml``` | ```Otros (definición de micro)``` |
| ```projects\compositor-evento-a-hecho-evaluable.yaml``` | ```Otros (definición de micro)``` |
| ```projects\alertas-a-profesional-app-mf.yaml``` | ```Otros (definición de micro)``` |
| ```projects\alertas-profesional-bff.yaml``` | ```Otros (definición de micro)``` |
| ```projects\mapeador-de-alertas-de-profesional.yaml``` | ```Otros (definición de micro)``` |
| ```projects\controlador-de-estados-alerta-profesional.yaml``` | ```Otros (definición de micro)``` |
| ```projects\gestor-snapshot-alertas-profesional.yaml``` | ```Otros (definición de micro)``` |
| ```projects\gestor-estados-alerta-profesional-api.yaml``` | ```Otros (definición de micro)``` |
| ```projects\registro-de-alertas-centralizado-api.yaml``` | ```Otros (definición de micro)``` |
| ```projects\gestor-cdv-alertas.yaml``` | ```Otros (definición de micro)``` |
| ```projects\adaptador-eventos-pruebas-analiticas.yaml``` | ```Otros (definición de micro)``` |
| ```projects\adaptador-eventos-laboratorio.yaml``` | ```Otros (definición de micro)``` |
| ```projects\adaptador-eventos-prescripciones.yaml``` | ```Otros (definición de micro)``` |
| ```projects\proxy-cliente-seguro-maco-rxxi.yaml``` | ```Otros (definición de micro)``` |
| ```templates\_helpers.tpl``` | ```Otros (template Helm)``` |
| ```templates\configMapFront.yaml``` | ```Otros (template Helm)``` |
| ```templates\gateway.yaml``` | ```Otros (template Helm)``` |
| ```templates\ingress.yaml``` | ```Otros (template Helm)``` |
| ```templates\validation.yaml``` | ```Otros (template Helm)``` |
| ```templates\worker.yaml``` | ```Otros (template Helm)``` |
| ```templates\generic\_ConfigMap.tpl``` | ```Otros (template Helm)``` |
| ```templates\generic\_Deployment.tpl``` | ```Otros (template Helm)``` |
| ```templates\generic\_HorizontalPodAutoscaler.tpl``` | ```Otros (template Helm)``` |
| ```templates\generic\_Secret.tpl``` | ```Otros (template Helm)``` |
| ```templates\generic\_Service.tpl``` | ```Otros (template Helm)``` |
| ```templates\istio\_AuthorizationPolicy.tpl``` | ```Otros (template Helm)``` |
| ```templates\istio\_RequestAuthentication.tpl``` | ```Otros (template Helm)``` |
| ```templates\istio\_VirtualService.tpl``` | ```Otros (template Helm)``` |
| ```templates\resources\secret-kafka-ca.yaml``` | ```Otros (template Helm)``` |
| ```report\validation_report.es.md``` | ```Otros (reporte de validación)``` |
| ```report\validation_report.en.md``` | ```Otros (reporte de validación)``` |
| ```report\validation_report.md``` | ```Otros (reporte de validación)``` |
| ```report\validation_summary.json``` | ```Otros (resumen de validación)``` |
| ```report\renders\des.yaml``` | ```Otros (render Helm)``` |
| ```report\renders\pre.yaml``` | ```Otros (render Helm)``` |
| ```report\renders\pro.yaml``` | ```Otros (render Helm)``` |

##### 3. Dependencias de Artefactos SAS
[⇑Indice⇑](#indice)

| **Artefactos** | **Versión** | **Proyecto SAS** | **Tipo** | **Observaciones** |
|:--------:|:--------:|:------:|:------:|:------:|
| helm | ```No aplica``` | ```Infraestructura de despliegue``` | ```binario``` | ```Necesario para template, install y upgrade del chart``` |
| kubectl | ```No aplica``` | ```Infraestructura de despliegue``` | ```binario``` | ```Necesario para validación de cluster y gestión de namespace en Jenkinsfile``` |
| kubeconfig | ```No aplica``` | ```Credencial de despliegue``` | ```otros``` | ```Jenkinsfile usa withCredentials(file(credentialsId: 'kubeconfig', ...))``` |
| Registro de imágenes de los microservicios desplegados | ```develop-0 / según entorno``` | ```Repositorios de imágenes corporativos``` | ```imagen Docker``` | ```El chart despliega imágenes referenciadas desde los ficheros de projects y values``` |

##### 4. Conjunto de artefactos entregadas necesarias para la compilación de los fuentes
[⇑Indice⇑](#indice)

```Artefactos necesarios para la compilación y se han subido dentro del repositorio (carpeta lib)```

No aplica.

##### 5. Navegadores soportados por la aplicación
[⇑Indice⇑](#indice)

| **Navegador** | **Soportado** | **Versión** |
|:----:|:-----:|:------:|
| Internet Explorer | ```N/A``` | |
| Mozilla | ```N/A``` | |
| Chrome | ```N/A``` | |
| Opera | ```N/A``` | |
| Safari | ```N/A``` | |

##### 6. Instalación
[⇑Indice⇑](#indice)

**Requisitos**
- Helm
- kubectl
- Acceso a un cluster Kubernetes
- Credencial `kubeconfig` disponible para el pipeline
- Fichero de values del entorno correspondiente (`injectValues_DES.yaml`, `injectValues_INT.yaml`, `injectValues_PRE.yaml`, `injectValues_PRO.yaml`, `injectValues_CER.yaml` o `injectValues_LOAD.yaml`)

**Compilación**
```bash
helm template gestor-alertas . -f injectValues_DES.yaml
```

**Ejecución local**
```bash
helm install gestor-alertas . -n <namespace> -f injectValues_DES.yaml
```

**Docker**
```bash
No aplica
```

##### 7. Otros datos de interés
[⇑Indice⇑](#indice)

- El chart Helm es de tipo `application`.


##### 8. Versión plantilla Readme
[⇑Indice⇑](#indice)

```Información de uso interno de las TIC, no modificar```

Versión Plantilla Readme: 1.1.0.2
