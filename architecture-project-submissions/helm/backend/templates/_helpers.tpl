{{/*
_helpers.tpl — Reusable template fragments for the backend subchart.

Include in other templates with:
  {{ include "backend.<helper>" . }}
*/}}

{{/*
Chart name (defaults to Chart.Name, overridable via .Values.nameOverride).
*/}}
{{- define "backend.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Fully-qualified resource name: <release-name>-<chart-name>.
*/}}
{{- define "backend.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Standard Kubernetes recommended labels.
*/}}
{{- define "backend.labels" -}}
helm.sh/chart: {{ printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{ include "backend.selectorLabels" . }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels — used in Deployment.spec.selector.matchLabels and Service.spec.selector.
*/}}
{{- define "backend.selectorLabels" -}}
app.kubernetes.io/name: {{ include "backend.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Construct the Keycloak internal service URL.

The Bitnami Keycloak chart creates a Service named: <release-name>-keycloak
Port is taken from .Values.keycloak.port (default "80" for HTTP).

This is the cluster-internal address used by the backend to verify JWT tokens.
It is NOT the public Keycloak URL (that is configured in the frontend).
*/}}
{{- define "backend.keycloakUrl" -}}
{{- printf "http://%s-keycloak:%s" .Release.Name .Values.keycloak.port }}
{{- end }}

{{/*
Construct the PostgreSQL DATABASE_URL.

The Bitnami PostgreSQL chart creates a Service named: <release-name>-postgresql
Uses psycopg (v3) driver notation (postgresql+psycopg://...).

The password is embedded in the URL — this value is stored in a Kubernetes
Secret (see secret.yaml), not exposed in the ConfigMap.
*/}}
{{- define "backend.databaseUrl" -}}
{{- printf "postgresql+psycopg://%s:%s@%s-postgresql:%s/%s"
    .Values.database.user
    .Values.database.password
    .Release.Name
    .Values.database.port
    .Values.database.name }}
{{- end }}

{{/*
Construct the MinIO S3 endpoint URL.

The Bitnami MinIO chart creates a Service named: <release-name>-minio
Port is taken from .Values.s3.port (default "9000").

boto3 uses this as the endpoint_url parameter for S3-compatible access.
*/}}
{{- define "backend.s3Endpoint" -}}
{{- printf "http://%s-minio:%s" .Release.Name .Values.s3.port }}
{{- end }}
