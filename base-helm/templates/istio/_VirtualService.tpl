{{- define "generic.istio.VirtualService" -}}
{{- $generic := .Generic -}}
{{- $ingress := $generic.ingress | default dict -}}
{{- $service := $generic.service | default dict -}}
{{- $trafficManagement := $generic.trafficManagement | default dict -}}

{{/*
Por defecto se utiliza ingress.host del proyecto.
Para microservicios y APIs que usen host compartido se utiliza
SharedIngressHost, proporcionado por worker.yaml.
*/}}
{{- $virtualServiceHost := $ingress.host | default "" -}}

{{- if and .UseSharedIngressHost .SharedIngressHost -}}
  {{- $virtualServiceHost = .SharedIngressHost -}}
{{- end -}}

{{- if not $virtualServiceHost -}}
  {{- fail (printf
      "Error: ingress.host is required for VirtualService of project '%s'"
      $generic.name
  ) -}}
{{- end -}}

{{- if not $ingress.gateway -}}
  {{- fail (printf
      "Error: ingress.gateway is required for VirtualService of project '%s'"
      $generic.name
  ) -}}
{{- end -}}

{{- if not $trafficManagement.ruleSet -}}
  {{- fail (printf
      "Error: trafficManagement.ruleSet is required for VirtualService of project '%s'"
      $generic.name
  ) -}}
{{- end -}}

apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: {{ printf "%s-virtualservice" $generic.name }}
  namespace: {{ .namespace }}
  labels:
    app: {{ $generic.name }}
spec:
  hosts:
    - {{ $virtualServiceHost | quote }}

  gateways:
    - {{ $ingress.gateway | quote }}

  http:
    {{- range $rule := $trafficManagement.ruleSet }}
    - name: {{ $rule.name | default "default" | quote }}

      {{/*
      prefix y exact se convierten en reglas independientes del array
      match, evitando generar dos veces la clave YAML match.
      */}}
      {{- if or $rule.prefix $rule.exact }}
      match:
        {{- if $rule.prefix }}
        - uri:
            prefix: {{ $rule.prefix | quote }}
        {{- end }}

        {{- if $rule.exact }}
        - uri:
            exact: {{ $rule.exact | quote }}
        {{- end }}
      {{- end }}

      {{- if $rule.urlRewrite }}
      rewrite:
        uri: {{ $rule.urlRewrite | quote }}
      {{- end }}

      route:
        - destination:
            host: {{ printf "%s-service" $generic.name | quote }}
            port:
              number: {{ required
                  "Parameter service.port cannot be empty or null"
                  $service.port
              }}

      {{- if $generic.corsPolicy }}
      corsPolicy:
{{ toYaml $generic.corsPolicy | indent 8 }}
      {{- end }}
    {{- end }}
---
{{ end -}}
