{{- define "generic.Secret" }}
apiVersion: v1
kind: Secret
metadata:
  name: {{ .Generic.name }}-secret
  namespace: {{ .namespace }}
type: Opaque
stringData:
  {{- range $key, $val := .Generic.environment.secrets }}
  {{ $key }}: {{ $val | quote }}
  {{- end }}
---
{{ end }}