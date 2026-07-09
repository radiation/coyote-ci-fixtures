#!/usr/bin/env sh

set -eu

npm ci --no-audit --no-fund
npm run build
npm pack --pack-destination artifacts

echo "built npm install cache smoke fixture"
