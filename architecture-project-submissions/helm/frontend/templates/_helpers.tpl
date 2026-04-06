{{/*
_helpers.tpl — Reusable template fragments for the frontend subchart.

Include these in other templates with:
  {{ include "frontend.<helper>" . }}
*/}}

{{/*
Chart name (defaults to Chart.Name, overridable via .Values.nameOverride).
Truncated to 63 characters — the DNS label length limit.
*/}}
{{- define "frontend.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Fully-qualified resource name: <release-name>-<chart-name>.
If the release name already contains the chart name it is not duplicated.
Truncated to 63 characters.
*/}}
{{- define "frontend.fullname" -}}
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
Standard Kubernetes recommended labels applied to every resource.
https://kubernetes.io/docs/concepts/overview/working-with-objects/common-labels/
*/}}
{{- define "frontend.labels" -}}
helm.sh/chart: {{ printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{ include "frontend.selectorLabels" . }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels — used in Deployment.spec.selector.matchLabels and Service.spec.selector.
Only name + instance are included; adding more labels here would break rolling updates
because Kubernetes does not allow changing selector labels after creation.
*/}}
{{- define "frontend.selectorLabels" -}}
app.kubernetes.io/name: {{ include "frontend.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}
