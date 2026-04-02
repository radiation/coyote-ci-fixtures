#!/usr/bin/env sh

set -eu

echo "starting long-running logs"
i=1
while [ "$i" -le 4 ]; do
  echo "tick $i"
  sleep 2
  i=$((i + 1))
done
echo "finished long-running logs"