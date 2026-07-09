#!/usr/bin/env sh

set -eu

echo "expecting mvn to be unavailable in alpine"
mvn -v
