#!/usr/bin/env sh

set -eu

mkdir -p output/modules/api
printf 'api module build\n' > output/modules/api/api-service.jar
printf '{"module":"api","language":"java"}\n' > output/modules/api/module.json
echo "built api module"