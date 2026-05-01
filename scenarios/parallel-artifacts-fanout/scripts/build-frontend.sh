#!/usr/bin/env sh

set -eu

mkdir -p output/frontend
printf '<html><body>frontend build placeholder</body></html>\n' > output/frontend/index.html
printf '{"component":"frontend","status":"ok"}\n' > output/frontend/frontend-build.json
echo "built frontend artifacts"