#!/usr/bin/env sh

set -eu

mkdir -p output/manifests
cat > output/manifests/fanout-summary.json << 'EOF'
{
  "scenario": "parallel-artifacts-fanout",
  "parallel_steps": ["backend", "frontend", "docs"],
  "expected_artifact_roots": ["output/backend", "output/frontend", "output/docs"]
}
EOF

echo "wrote fanout summary"