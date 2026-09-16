# generator-charts-helm
Aplicación desarrollada en Python que permite la generación de Plantillas Helm a partir de una plantilla base, para cualquier proyecto.

# Instalación → Posicionados en el directorio generator-helm
pip -e .

# Uso
Antes que nada es necesario crear la carpeta donde va a ir el chart de helm que se quiere generar, puedes llamarle generated-charts como prueba.

# Generar Chart
helm-generator generate \
  --application-name test \
  --application-version 1.0.0 \
  --chart-version 0.1.0 \
  --fronts "portal-cliente,portal-gestor" \
  --apis "consulta-expedientes" \
  --microservicios "notificador,procesador-ficheros,auditoria,workflow" \
  --integration-host test-int.20.8.203.204.nip.io \
  --certification-host test-cer.20.8.203.204.nip.io \
  --template-directory /ruta/base-helm \
  --output-directory /ruta/generated-charts 
