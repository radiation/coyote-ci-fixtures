#!/usr/bin/env sh

set -eu

echo "starting success-basic"
echo "writing artifact"
mkdir -p output
echo "hello from success-basic" > output/hello.txt
echo "done"