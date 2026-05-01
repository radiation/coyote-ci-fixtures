#!/usr/bin/env sh

set -eu

mkdir -p output/modules/sdk
printf 'sdk package bundle\n' > output/modules/sdk/sdk-package-0.8.0.tgz
printf '{"module":"sdk","language":"javascript"}\n' > output/modules/sdk/module.json
echo "built sdk module"