{{- define "generic.Deployment" -}}
{{- $generic := .Generic -}}
{{- $environment := $generic.environment | default dict -}}
{{- $configFile := $generic.configFile | default dict -}}
{{- $volume := $generic.volume | default dict -}}
{{- $autoscaling := $generic.autoscaling | default dict -}}
{{- $istio := $generic.istio | default dict -}}

{{/*
La inyección del sidecar Istio está habilitada por defecto.
Puede deshabilitarse por aplicación mediante:

istio:
  sidecarInjection: false
*/}}
{{- $sidecarInjection := true -}}
{{- if hasKey $istio "sidecarInjection" -}}
  {{- $sidecarInjection = $istio.sidecarInjection -}}
{{- end -}}

{{- $istioProxyCpu := "50m" -}}
{{- if $istio.proxyCPU -}}
  {{- $istioProxyCpu = $istio.proxyCPU -}}
{{- end -}}

{{- $istioProxyMemory := "50Mi" -}}
{{- if $istio.proxyMemory -}}
  {{- $istioProxyMemory = $istio.proxyMemory -}}
{{- end -}}

apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ $generic.name }}
  namespace: {{ .namespace }}
  labels:
    app: {{ $generic.name }}
  {{- with $generic.deploymentAnnotations }}
  annotations:
{{ toYaml . | indent 4 }}
  {{- end }}
spec:
  selector:
    matchLabels:
      app: {{ $generic.name }}

  {{- if not $autoscaling.enabled }}
  replicas: {{ $generic.replicaCount | default 1 }}
  {{- end }}

  template:
    metadata:
      labels:
        app: {{ $generic.name }}
        version: {{ $generic.version | default "latest" }}
      annotations:
        sidecar.istio.io/inject: {{ $sidecarInjection | quote }}
        sidecar.istio.io/proxyCPU: {{ $istioProxyCpu | quote }}
        sidecar.istio.io/proxyMemory: {{ $istioProxyMemory | quote }}
        {{- with $generic.runtimePodAnnotations }}
{{ toYaml . | indent 8 }}
        {{- end }}
        {{- with $generic.podAnnotations }}
{{ toYaml . | indent 8 }}
        {{- end }}

    spec:
      {{- with $generic.tolerations }}
      tolerations:
{{ toYaml . | indent 8 }}
      {{- end }}

      {{- with $generic.nodeSelector }}
      nodeSelector:
{{ toYaml . | indent 8 }}
      {{- end }}

      {{- with $generic.affinity }}
      affinity:
{{ toYaml . | indent 8 }}
      {{- end }}

      {{- with $generic.hostAliases }}
      hostAliases:
{{ toYaml . | indent 8 }}
      {{- end }}

      containers:
        - name: {{ $generic.name }}
          image: {{ .imagePath | quote }}
          imagePullPolicy: {{ $generic.image.pullPolicy | default "IfNotPresent" }}

          ports:
            - containerPort: {{ required "Parameter container.port cannot be empty or null" $generic.container.port }}

          {{/*
          Volúmenes opcionales de configuración.
          */}}
          {{- $volumeMounts := list -}}

          {{- if and
              $configFile.enabled
              $configFile.mountPath
              $configFile.key
          }}
            {{- $volumeMounts = append $volumeMounts (dict
                "name" "config-volume"
                "mountPath" $configFile.mountPath
                "subPath" $configFile.key
                "readOnly" true
            ) -}}
          {{- end }}

          {{- if and
              $volume.enabled
              $volume.name
              $volume.fileName
              $volume.mountPath
          }}
            {{- $readOnly := true -}}
            {{- if hasKey $volume "readOnly" -}}
              {{- $readOnly = $volume.readOnly -}}
            {{- end -}}

            {{- $volumeMounts = append $volumeMounts (dict
                "name" $volume.name
                "mountPath" $volume.mountPath
                "subPath" $volume.fileName
                "readOnly" $readOnly
            ) -}}
          {{- end }}

          {{- if gt (len $volumeMounts) 0 }}
          volumeMounts:
{{ toYaml $volumeMounts | indent 12 }}
          {{- end }}

          resources:
            {{- if eq $generic.usage_level "low" }}
            requests:
              cpu: {{ $generic.usageSpec.low.resources.requests.cpu }}
              memory: {{ $generic.usageSpec.low.resources.requests.memory }}
            limits:
              cpu: {{ $generic.usageSpec.low.resources.limits.cpu }}
              memory: {{ $generic.usageSpec.low.resources.limits.memory }}

            {{- else if eq $generic.usage_level "medium" }}
            requests:
              cpu: {{ $generic.usageSpec.medium.resources.requests.cpu }}
              memory: {{ $generic.usageSpec.medium.resources.requests.memory }}
            limits:
              cpu: {{ $generic.usageSpec.medium.resources.limits.cpu }}
              memory: {{ $generic.usageSpec.medium.resources.limits.memory }}

            {{- else if eq $generic.usage_level "high" }}
            requests:
              cpu: {{ $generic.usageSpec.high.resources.requests.cpu }}
              memory: {{ $generic.usageSpec.high.resources.requests.memory }}
            limits:
              cpu: {{ $generic.usageSpec.high.resources.limits.cpu }}
              memory: {{ $generic.usageSpec.high.resources.limits.memory }}

            {{- else if eq $generic.usage_level "very_high" }}
            requests:
              cpu: {{ $generic.usageSpec.very_high.resources.requests.cpu }}
              memory: {{ $generic.usageSpec.very_high.resources.requests.memory }}
            limits:
              cpu: {{ $generic.usageSpec.very_high.resources.limits.cpu }}
              memory: {{ $generic.usageSpec.very_high.resources.limits.memory }}

            {{- else }}
            requests:
              cpu: {{ $generic.resources.requests.cpu }}
              memory: {{ $generic.resources.requests.memory }}
            limits:
              cpu: {{ $generic.resources.limits.cpu }}
              memory: {{ $generic.resources.limits.memory }}
            {{- end }}

          {{- if $generic.readinessProbe }}
          {{- $readinessProbe := deepCopy $generic.readinessProbe }}
          {{- if and $readinessProbe.httpGet $generic.container.port }}
            {{- $_ := set $readinessProbe.httpGet "port" $generic.container.port }}
          {{- end }}
          readinessProbe:
{{ toYaml $readinessProbe | indent 12 }}
          {{- end }}

          {{- if $generic.livenessProbe }}
          {{- $livenessProbe := deepCopy $generic.livenessProbe }}
          {{- if and $livenessProbe.httpGet $generic.container.port }}
            {{- $_ := set $livenessProbe.httpGet "port" $generic.container.port }}
          {{- end }}
          livenessProbe:
{{ toYaml $livenessProbe | indent 12 }}
          {{- end }}

          {{- if or $environment.configMap $environment.secrets }}
          envFrom:
            {{- if $environment.configMap }}
            - configMapRef:
                name: {{ printf "%s-configmap" $generic.name }}
            {{- end }}

            {{- if $environment.secrets }}
            - secretRef:
                name: {{ printf "%s-secret" $generic.name }}
            {{- end }}
          {{- end }}

      {{/*
      Volúmenes definidos para ficheros propios de la aplicación.
      */}}
      {{- $volumes := list -}}

      {{- if and
          $configFile.enabled
          $configFile.configMapName
          $configFile.key
      }}
        {{- $volumes = append $volumes (dict
            "name" "config-volume"
            "configMap" (dict
                "name" $configFile.configMapName
                "items" (list (dict
                    "key" $configFile.key
                    "path" $configFile.key
                ))
            )
        ) -}}
      {{- end }}

      {{- if and
          $volume.enabled
          $volume.name
          $volume.configMapName
          $volume.fileName
          (or (not $volume.type) (eq $volume.type "configMap"))
      }}
        {{- $volumes = append $volumes (dict
            "name" $volume.name
            "configMap" (dict
                "name" $volume.configMapName
                "items" (list (dict
                    "key" $volume.fileName
                    "path" $volume.fileName
                ))
            )
        ) -}}
      {{- end }}

      {{- if gt (len $volumes) 0 }}
      volumes:
{{ toYaml $volumes | indent 8 }}
      {{- end }}
---
{{ end -}}
