#!/usr/bin/env sh

set -eu

echo "starting long-running logs"
i=1
while [ "$i" -le 6 ]; do
  echo "tick $i"
  sleep 10
  i=$((i + 1))
done
echo "finished long-running logs"