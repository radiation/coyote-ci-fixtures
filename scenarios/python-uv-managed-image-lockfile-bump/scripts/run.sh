#!/usr/bin/env sh

set -eu

mkdir -p artifacts/images
printf 'managed image placeholder for python-uv bumped lockfile\n' > artifacts/images/fastapi-managed-image.tar

cat > artifacts/managed-image-inputs.json << 'EOF'
{
  "scenario": "python-uv-managed-image-lockfile-bump",
  "dependency_inputs": ["pyproject.toml", "uv.lock", "Dockerfile"],
  "lock_signature": "fastapi-0.116.0|uvicorn-0.32.1"
}
EOF

echo "wrote python uv bumped-lock artifacts"