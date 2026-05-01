#!/usr/bin/env sh

set -eu

mkdir -p output/docs
printf '# fanout docs\nparallel docs artifact\n' > output/docs/README.md
printf '{"component":"docs","status":"ok"}\n' > output/docs/docs-build.json
echo "built docs artifacts"