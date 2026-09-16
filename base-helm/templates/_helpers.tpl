{{/*
Devuelve el nombre completo del recurso.
Si se define fullnameOverride se utiliza ese valor.
*/}}
{{- define "generic.fullname" -}}
{{- if .Values.fullnameOverride -}}
{{ .Values.fullnameOverride }}
{{- else -}}
{{ .Release.Name }}-{{ .Chart.Name }}
{{- end -}}
{{- end -}}


{{/*
Compatibilidad temporal para templates que aún invoquen mychart.fullname.
Puede eliminarse cuando no existan referencias a dicho helper.
*/}}
{{- define "mychart.fullname" -}}
{{ include "generic.fullname" . }}
{{- end -}}


{{/*
Nombre del Gateway Istio.

Prioridad:
1. global.ingress.gateway
2. <release-name>-gateway
*/}}
{{- define "generic.gatewayName" -}}
{{- $global := .Values.global | default dict -}}
{{- $ingress := $global.ingress | default dict -}}
{{- default (printf "%s-gateway" .Release.Name) $ingress.gateway -}}
{{- end -}}


{{/*
Nombre del ingress compartido.

Prioridad:
1. global.ingress.name
2. <release-name>-ingress
*/}}
{{- define "generic.sharedIngressName" -}}
{{- $global := .Values.global | default dict -}}
{{- $ingress := $global.ingress | default dict -}}
{{- default (printf "%s-ingress" .Release.Name) $ingress.name -}}
{{- end -}}


{{/*
Construye una lista única de hosts de ingress definidos para los tipos
de proyecto soportados: microservicio, front y api.

No añade valores vacíos ni el valor legacy NO_APLICA_EN_ESTA_ITERACION.
*/}}
{{- define "generic.ingressHosts" -}}
{{- $hosts := dict -}}

{{- $microservicio := .Values.microservicio | default dict -}}
{{- $front := .Values.front | default dict -}}
{{- $api := .Values.api | default dict -}}

{{- $microservicioSpec := $microservicio.spec | default dict -}}
{{- $frontSpec := $front.spec | default dict -}}
{{- $apiSpec := $api.spec | default dict -}}

{{- $microservicioIngress := $microservicioSpec.ingress | default dict -}}
{{- $frontIngress := $frontSpec.ingress | default dict -}}
{{- $apiIngress := $apiSpec.ingress | default dict -}}

{{- range $candidate := list
    $microservicioIngress.host
    $frontIngress.host
    $apiIngress.host
-}}
  {{- if and
      $candidate
      (ne $candidate "NO_APLICA_EN_ESTA_ITERACION")
  -}}
    {{- $_ := set $hosts $candidate true -}}
  {{- end -}}
{{- end -}}

{{- range $host := keys $hosts | sortAlpha }}
- {{ $host | quote }}
{{- end -}}
{{- end -}}
