from importlib.metadata import version
from pathlib import Path
import json


def main() -> None:
    artifacts = Path("artifacts")
    artifacts.mkdir(parents=True, exist_ok=True)
    payload = {
        "scenario": "python-pip-install-smoke",
        "dependencies": {
            "fastapi": version("fastapi"),
            "uvicorn": version("uvicorn"),
        },
    }
    artifacts.joinpath("dependency-report.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
