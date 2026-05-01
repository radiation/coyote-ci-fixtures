#!/usr/bin/env sh

set -eu

mkdir -p output/manifest
cat > output/manifest/monorepo-lite-summary.json << 'EOF'
{
  "scenario": "monorepo-lite-submodules",
  "submodules": ["api", "worker", "sdk"],
  "purpose": "single pipeline, submodule-style outputs"
}
EOF

echo "wrote monorepo-lite manifest"