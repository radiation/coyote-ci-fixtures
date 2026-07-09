#!/usr/bin/env sh

set -eu

mvn -B -ntp clean package dependency:tree -DoutputFile=target/dependency-tree.txt

cat > target/build-report.json <<'EOF'
{
  "scenario": "maven-dependency-smoke",
  "artifact": "target/dependency-smoke-1.0.0.jar",
  "dependency": "org.apache.commons:commons-lang3:3.17.0",
  "tool": "maven"
}
EOF

echo "built maven dependency smoke fixture"
