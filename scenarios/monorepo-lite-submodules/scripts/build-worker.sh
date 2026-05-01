#!/usr/bin/env sh

set -eu

mkdir -p output/modules/worker
printf 'worker module image\n' > output/modules/worker/worker-container-image.tar
printf '{"module":"worker","language":"python"}\n' > output/modules/worker/module.json
echo "built worker module"