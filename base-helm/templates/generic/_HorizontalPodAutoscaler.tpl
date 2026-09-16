{{- define "generic.HorizontalPodAutoscaler" }}
apiVersion: autoscaling/v2beta2
kind: HorizontalPodAutoscaler
metadata:
  name: {{ .Generic.name }}-hpa
  namespace: {{ .namespace }}
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: {{ .Generic.name }}-deployment
  {{- if eq .Generic.usage_level "high" }}
  minReplicas: {{ .Generic.usageSpec.high.autoscaling.minReplicas | default 1 }}
  maxReplicas: {{ .Generic.usageSpec.high.autoscaling.maxReplicas | default 1 }}
  {{- else if eq .Generic.usage_level "very_high" }}
  minReplicas: {{ .Generic.usageSpec.very_high.autoscaling.minReplicas | default 1 }}
  maxReplicas: {{ .Generic.usageSpec.very_high.autoscaling.maxReplicas | default 1 }}
  {{- else }}
  minReplicas: {{ .Generic.autoscaling.minReplicas | default 1 }}
  maxReplicas: {{ .Generic.autoscaling.maxReplicas | default 1 }}  
  {{- end}}
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: AverageValue
        {{- if eq .Generic.usage_level "high" }}
        averageValue: {{ required "Parameter .Generic.usageSpec.high.autoscaling.targetCPUUtilizationValue cannot be empty or null" .Generic.usageSpec.high.autoscaling.targetCPUUtilizationValue }}
        {{- else if eq .Generic.usage_level "very_high" }}
        averageValue: {{ required "Parameter .Generic.usageSpec.very_high.autoscaling.targetCPUUtilizationValue cannot be empty or null" .Generic.usageSpec.very_high.autoscaling.targetCPUUtilizationValue }}
        {{- else }}
        averageValue: {{ required "Parameter .Generic.autoscaling.targetCPUUtilizationValue cannot be empty or null" .Generic.autoscaling.targetCPUUtilizationValue }}
        {{- end}}
  - type: Resource
    resource:
      name: memory
      target: 
        type: AverageValue
        {{- if eq .Generic.usage_level "high" }}
        averageValue: {{ required "Parameter .Generic.usageSpec.high.autoscaling.targetMemoryUtilizationValue cannot be empty or null" .Generic.usageSpec.high.autoscaling.targetMemoryUtilizationValue }}
        {{- else if eq .Generic.usage_level "very_high" }}
        averageValue: {{ required "Parameter .Generic.usageSpec.very_high.autoscaling.targetMemoryUtilizationValue cannot be empty or null" .Generic.usageSpec.very_high.autoscaling.targetMemoryUtilizationValue }}
        {{- else }}
        averageValue: {{ required "Parameter .Generic.autoscaling.targetMemoryUtilizationValue cannot be empty or null" .Generic.autoscaling.targetMemoryUtilizationValue }}
        {{- end}}
---
{{ end }}