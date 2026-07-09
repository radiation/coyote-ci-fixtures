#!/usr/bin/env sh

set -eu

mkdir -p output

{
  echo "scenario=docker-image-pull-smoke"
  echo "image=busybox:1.36.1"
  echo "kernel=$(uname -srm)"
  echo "utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
} > output/pull-report.txt

echo "wrote docker pull smoke artifact"
