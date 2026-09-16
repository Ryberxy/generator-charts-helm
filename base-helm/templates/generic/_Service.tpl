{{- define "generic.Service" }}
apiVersion: v1
kind: Service
metadata:
  name: {{ .Generic.name }}-service
  namespace: {{ .namespace }}
  labels:
    app: {{ .Generic.name }}
    service: {{ .Generic.name }}-service
    sas_monitoring: {{ .Generic.service.sas_monitoring | quote  }}
  {{- if .Generic.service.sas_monitoring }}
  annotations:
    prometheus.io/scrape: "true"
    prometheus.io/path: {{ default "/metrics" .Generic.service.metricsPath | quote }}
    prometheus.io/port: {{ .Generic.container.port | quote }}
  {{- end }}
spec:
  type: ClusterIP
  selector:
    app: {{ .Generic.name }}
  ports:
  - name: "http"
    port: {{ required "Parameter port cannot be empty or null" .Generic.service.port }}
    targetPort: {{ required "Parameter container.port cannot be empty or null" .Generic.container.port }}
---
{{ end }}
