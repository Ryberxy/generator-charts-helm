{{- define "generic.istio.RequestAuthentication" }}
apiVersion: security.istio.io/v1beta1
kind: RequestAuthentication
metadata:
  name: {{ .Generic.name }}-requestauthentication
  namespace: {{ .namespace }}
spec:
  selector:
    matchLabels:
      app: {{ .Generic.name }}
---
{{- end }}
