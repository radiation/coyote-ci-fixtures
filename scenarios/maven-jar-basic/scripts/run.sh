#!/usr/bin/env sh

set -eu

mkdir -p target
printf 'placeholder jar bytes for demo-app\n' > target/demo-app-1.0.0.jar

cat > target/demo-app-build.json << 'EOF'
{
  "scenario": "maven-jar-basic",
  "artifact": "demo-app-1.0.0.jar",
  "pom": "pom.xml",
  "version": "1.0.0"
}
EOF

echo "wrote maven-style artifacts"