{{- define "generic.istio.AuthorizationPolicy" }}
apiVersion: security.istio.io/v1beta1
kind: AuthorizationPolicy
metadata:
  name: {{ .Generic.name }}-authorization
  namespace: {{ .namespace }}
spec:
  selector:
    matchLabels:
      app: {{ .Generic.name }}
  action: ALLOW
  rules:
  {{- range $policy := .Generic.authorization.policies }}
  - from:
    - source:
        requestPrincipals: ["*"]
    to:
    - operation:
        paths:
        {{- range $path := $policy.paths }}
        - {{ $path | quote }}
        {{- end }}
        methods:
        {{- range $method := $policy.methods }}
        - {{ $method | quote }}
        {{- end }}
    {{- if $policy.scopes }}
    when:
    - key: request.auth.claims[scope]
      values:
      {{- range $scope := $policy.scopes }}
      - {{ $scope | quote }}
      {{- end }}
    {{- end }}
  {{- end }}
  - to:
    - operation:
        paths: 
        - "/health*"
        methods: 
        - "GET"
---
{{- end }}
