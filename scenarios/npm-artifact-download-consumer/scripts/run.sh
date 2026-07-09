#!/usr/bin/env sh

set -eu

: "${COYOTE_ARTIFACT_URL:?COYOTE_ARTIFACT_URL is required}"

apk add --no-cache curl >/dev/null

mkdir -p downloads artifacts

curl -fsSL "$COYOTE_ARTIFACT_URL" -o downloads/acme-widget-network-smoke-0.4.0.tgz
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