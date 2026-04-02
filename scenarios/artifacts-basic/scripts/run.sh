#!/usr/bin/env sh

set -eu

mkdir -p output
echo "alpha" > output/alpha.txt
echo "beta" > output/beta.txt
cat > output/result.json << 'EOF'
{"status":"ok","scenario":"artifacts-basic"}
EOF
echo "wrote artifacts"