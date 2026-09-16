{{- define "generic.ConfigMap" }}
apiVersion: v1
kind: ConfigMap
metadata:
  name: {{ .Generic.name }}-configmap
  namespace: {{ .namespace }}
data:
  {{- range $key, $val := .Generic.environment.configMap }}
  {{ $key }}: {{ $val | quote }}
  {{- end }}
  {{- if .Generic.environment.settings }}
  settings.json: |-
{{ .Generic.environment.settings | toPrettyJson | indent 4 }}
  {{- end }}
---
{{ end }}