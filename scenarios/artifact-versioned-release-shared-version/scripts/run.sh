#!/usr/bin/env sh

set -eu

mkdir -p releases/service-a releases/service-b releases/sdk releases/metadata

printf 'service-a artifact for shared release version\n' > releases/service-a/app.jar
printf 'service-b artifact for shared release version\n' > releases/service-b/app.jar
printf 'sdk bundle for shared release version\n' > releases/sdk/bundle.tgz

cat > releases/metadata/version-summary.json << 'EOF'
{
  "scenario": "artifact-versioned-release-shared-version",
  "shared_release_pattern": "2.1.{build_number}",
  "artifacts": [
    "catalog/service-a",
    "catalog/service-b",
    "catalog/sdk"
  ]
}
EOF

echo "published shared-version artifacts"