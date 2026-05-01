#!/usr/bin/env sh

set -eu

mkdir -p output/catalog/packages output/catalog/images output/catalog/reports output/catalog/metadata

for service in api worker web billing search; do
  for channel in stable beta preview; do
    printf '%s %s package\n' "$service" "$channel" > "output/catalog/packages/${service}-${channel}-1.0.0.tgz"
    printf '%s %s image\n' "$service" "$channel" > "output/catalog/images/${service}-${channel}-container-image.tar"
    printf '%s %s report\n' "$service" "$channel" > "output/catalog/reports/${service}-${channel}-summary.txt"
  done
done

cat > output/catalog/metadata/catalog-index.json << 'EOF'
{
  "scenario": "artifact-pagination-search-catalog",
  "artifact_count_hint": 45,
  "search_examples": [
    "api stable",
    "billing beta",
    "container image",
    "summary"
  ]
}
EOF

echo "generated artifact catalog"