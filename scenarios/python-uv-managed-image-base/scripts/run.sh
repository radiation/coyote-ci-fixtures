#!/usr/bin/env sh

set -eu

mkdir -p artifacts/images
printf 'managed image placeholder for python-uv baseline\n' > artifacts/images/fastapi-managed-image.tar

cat > artifacts/managed-image-inputs.json << 'EOF'
{
  "scenario": "python-uv-managed-image-base",
  "dependency_inputs": ["pyproject.toml", "uv.lock", "Dockerfile"],
  "lock_signature": "fastapi-0.115.0|uvicorn-0.32.0"
}
EOF

echo "wrote python uv baseline artifacts"