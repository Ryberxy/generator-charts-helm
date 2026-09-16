# cadena del comando final

helm-generator generate \
  --application-name pdu \
  --application-version 1.0.0 \
  --chart-version 0.1.0 \
  --fronts "catalogo-alertas-api,gestor-snapshot,portal-cliente" \
  --apis "consulta-personas,gestion-expedientes,consulta-documentos" \
  --microservicios "notificador,procesador-ficheros,auditoria,workflow,integracion" \
  --integration-host pdu-int.20.8.203.204.nip.io \
  --certification-host pdu-cer.20.8.203.204.nip.io \
  --template-directory /ruta/base-helm \
  --output-directory /ruta/generated-charts
