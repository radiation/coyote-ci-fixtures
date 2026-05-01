#!/usr/bin/env sh

set -eu

mkdir -p dist artifacts
cat > dist/index.js << 'EOF'
export function widgetLabel() {
  return "acme-widget fixture";
}
EOF

cat > dist/index.d.ts << 'EOF'
export declare function widgetLabel(): string;
EOF

printf 'packed npm tarball placeholder\n' > artifacts/acme-widget-0.3.0.tgz

cat > artifacts/package-manifest.json << 'EOF'
{
  "scenario": "npm-library-package",
  "package": "@fixtures/acme-widget",
  "version": "0.3.0",
  "outputs": ["dist/index.js", "dist/index.d.ts", "artifacts/acme-widget-0.3.0.tgz"]
}
EOF

echo "wrote npm-style artifacts"