#!/usr/bin/env sh

set -eu

echo "this is stdout"
echo "this is stderr" >&2
exit 1