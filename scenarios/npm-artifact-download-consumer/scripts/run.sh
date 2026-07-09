#!/usr/bin/env sh

set -eu

artifact_url="${COYOTE_ARTIFACT_URL:-}"
if [ -z "$artifact_url" ]; then
  api_url="${COYOTE_API_URL:-http://host.docker.internal:8080}"
  : "${COYOTE_TRIGGER_BUILD_ID:?COYOTE_TRIGGER_BUILD_ID is required when COYOTE_ARTIFACT_URL is not set}"
  : "${COYOTE_TRIGGER_ARTIFACT_ID:?COYOTE_TRIGGER_ARTIFACT_ID is required when COYOTE_ARTIFACT_URL is not set}"
  artifact_url="${api_url%/}/api/builds/${COYOTE_TRIGGER_BUILD_ID}/artifacts/${COYOTE_TRIGGER_ARTIFACT_ID}/download"
fi

apk add --no-cache curl >/dev/null

mkdir -p downloads artifacts

curl -fsSL "$artifact_url" -o downloads/acme-widget-network-smoke-0.4.0.tgz
npm install --no-audit --no-fund ./downloads/acme-widget-network-smoke-0.4.0.tgz >/dev/null

node --input-type=module > artifacts/consumer-report.json <<'EOF'
import { readFileSync } from 'node:fs';
import { widgetLabel } from 'acme-widget-network-smoke';

const installedPackage = JSON.parse(
  readFileSync('node_modules/acme-widget-network-smoke/package.json', 'utf8')
);

process.stdout.write(
  JSON.stringify(
    {
      scenario: 'npm-artifact-download-consumer',
      artifact_url: process.env.COYOTE_ARTIFACT_URL || null,
      trigger_type: process.env.COYOTE_TRIGGER_TYPE || null,
      trigger_build_id: process.env.COYOTE_TRIGGER_BUILD_ID || null,
      trigger_artifact_id: process.env.COYOTE_TRIGGER_ARTIFACT_ID || null,
      trigger_artifact_path: process.env.COYOTE_TRIGGER_ARTIFACT_PATH || null,
      trigger_artifact_name: process.env.COYOTE_TRIGGER_ARTIFACT_NAME || null,
      downloaded_package: installedPackage.name,
      downloaded_version: installedPackage.version,
      widget_label: widgetLabel
    },
    null,
    2
  ) + '\n'
);
EOF

echo "consumed downloaded npm package artifact"