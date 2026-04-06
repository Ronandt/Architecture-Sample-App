#!/bin/sh
# =============================================================================
# Frontend container entrypoint
#
# This script runs before nginx starts. It:
#   1. Reads environment variables injected by Kubernetes (via the Helm chart).
#   2. Uses `envsubst` to substitute $PLACEHOLDER values in config.js.template.
#   3. Writes the result to config.js, which is served to every browser client.
#   4. Hands off to nginx in the foreground (PID 1).
#
# This is the mechanism that makes the Docker image environment-agnostic:
# the same built image can be deployed to dev, staging, and production by
# changing only the Kubernetes env vars — no rebuild required.
#
# Expected environment variables (all are optional with empty-string fallbacks
# so the container starts even if a value is missing; Helm lint will catch
# omissions at deploy time):
#
#   APP_KEYCLOAK_URL        → window.__APP_CONFIG__.KEYCLOAK_URL
#   APP_KEYCLOAK_REALM      → window.__APP_CONFIG__.KEYCLOAK_REALM
#   APP_KEYCLOAK_CLIENT_ID  → window.__APP_CONFIG__.KEYCLOAK_CLIENT_ID
#   APP_API_URL             → window.__APP_CONFIG__.API_URL
#   APP_ALLOWED_GROUPS      → window.__APP_CONFIG__.ALLOWED_GROUPS
#   APP_ADMIN_ROLE          → window.__APP_CONFIG__.ADMIN_ROLE
#
# The template file and nginx.conf are both mounted from a Kubernetes ConfigMap.
# See: helm/frontend/templates/configmap.yaml
# =============================================================================
set -e

TEMPLATE=/usr/share/nginx/html/config.js.template
OUTPUT=/usr/share/nginx/html/config.js

if [ ! -f "$TEMPLATE" ]; then
  echo "ERROR: $TEMPLATE not found." >&2
  echo "       Ensure the ConfigMap volume is mounted correctly." >&2
  echo "       Check: helm/frontend/templates/deployment.yaml volumeMounts" >&2
  exit 1
fi

# envsubst replaces $PLACEHOLDER tokens in the template.
# Only the listed variables are substituted to avoid accidentally expanding
# any literal $ signs that may appear in the JavaScript template.
envsubst '${APP_KEYCLOAK_URL} ${APP_KEYCLOAK_REALM} ${APP_KEYCLOAK_CLIENT_ID} ${APP_API_URL} ${APP_ALLOWED_GROUPS} ${APP_ADMIN_ROLE}' \
  < "$TEMPLATE" > "$OUTPUT"

echo "config.js written with the following runtime config:"
cat "$OUTPUT"
echo ""

# Start nginx in the foreground so Docker/Kubernetes can manage the process.
exec nginx -g 'daemon off;'
