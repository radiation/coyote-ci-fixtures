#!/usr/bin/env sh

set -eu

python -m pip install --disable-pip-version-check --no-input -r requirements.txt
python ./scripts/write_report.py

echo "built python pip install smoke fixture"
