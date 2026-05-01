#!/usr/bin/env sh

set -eu

mkdir -p output/backend
printf 'backend binary placeholder\n' > output/backend/backend-linux-amd64.txt
printf '{"component":"backend","status":"ok"}\n' > output/backend/backend-build.json
echo "built backend artifacts"