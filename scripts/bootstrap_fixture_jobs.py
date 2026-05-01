#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
SCENARIOS_DIR = REPO_ROOT / "scenarios"
ENV_FILE = REPO_ROOT / ".env"
DEFAULT_TIMEOUT_SECONDS = 15
PAGE_LIMIT = 200


@dataclass(frozen=True)
class Config:
    base_url: str
    project_id: str
    fixtures_repo_url: str
    fixtures_ref: str
    auth_token: str | None
    timeout_seconds: int

    @property
    def api_base(self) -> str:
        trimmed = self.base_url.rstrip("/")
        if trimmed.endswith("/api"):
            return trimmed
        return trimmed + "/api"


@dataclass(frozen=True)
class ScenarioSpec:
    scenario_name: str
    pipeline_path: str
    job_name: str

    def create_payload(self, config: Config) -> dict[str, Any]:
        return {
            "project_id": config.project_id,
            "name": self.job_name,
            "repository_url": config.fixtures_repo_url,
            "default_ref": config.fixtures_ref,
            "pipeline_path": self.pipeline_path,
            "push_enabled": False,
            "enabled": True,
        }

    def update_payload(self, config: Config) -> dict[str, Any]:
        return {
            "name": self.job_name,
            "repository_url": config.fixtures_repo_url,
            "default_ref": config.fixtures_ref,
            "default_commit_sha": "",
            "push_enabled": False,
            "push_branch": "",
            "branch_allowlist": [],
            "tag_allowlist": [],
            "pipeline_yaml": "",
            "pipeline_path": self.pipeline_path,
            "enabled": True,
        }


class ApiError(RuntimeError):
    pass


class CoyoteClient:
    def __init__(self, config: Config, dry_run: bool = False) -> None:
        self.config = config
        self.dry_run = dry_run

    def list_jobs(self) -> list[dict[str, Any]]:
        jobs: list[dict[str, Any]] = []
        offset = 0
        while True:
            response = self._request_json(
                "GET",
                f"/jobs?limit={PAGE_LIMIT}&offset={offset}",
            )
            page = response.get("data", {}).get("jobs", [])
            if not isinstance(page, list):
                raise ApiError("unexpected jobs list response shape")
            jobs.extend(page)
            if len(page) < PAGE_LIMIT:
                return jobs
            offset += PAGE_LIMIT

    def create_job(self, payload: dict[str, Any]) -> dict[str, Any]:
        if self.dry_run:
            return {"data": payload}
        return self._request_json("POST", "/jobs", payload)

    def update_job(self, job_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        if self.dry_run:
            return {"data": {"id": job_id, **payload}}
        return self._request_json("PUT", f"/jobs/{job_id}", payload)

    def _request_json(self, method: str, path: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        body: bytes | None = None
        headers = {
            "Accept": "application/json",
        }
        if payload is not None:
            body = json.dumps(payload).encode("utf-8")
            headers["Content-Type"] = "application/json"
        if self.config.auth_token:
            headers["Authorization"] = f"Bearer {self.config.auth_token}"

        request = urllib.request.Request(
            self.config.api_base + path,
            data=body,
            headers=headers,
            method=method,
        )

        try:
            with urllib.request.urlopen(request, timeout=self.config.timeout_seconds) as response:
                raw = response.read().decode("utf-8")
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise ApiError(f"{method} {path} failed with HTTP {exc.code}: {detail}") from exc
        except urllib.error.URLError as exc:
            raise ApiError(f"{method} {path} failed: {exc.reason}") from exc

        try:
            decoded = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise ApiError(f"{method} {path} returned invalid JSON: {raw}") from exc
        if not isinstance(decoded, dict):
            raise ApiError(f"{method} {path} returned unexpected JSON payload")
        return decoded


def load_dotenv(path: Path) -> None:
    if not path.is_file():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


def read_config() -> Config:
    load_dotenv(ENV_FILE)

    base_url = os.getenv("COYOTE_BASE_URL", "").strip()
    project_id = os.getenv("COYOTE_PROJECT_ID", "").strip()
    fixtures_repo_url = os.getenv("COYOTE_FIXTURES_REPO_URL", "").strip()
    fixtures_ref = os.getenv("COYOTE_FIXTURES_REF", "").strip()
    auth_token = os.getenv("COYOTE_AUTH_TOKEN", "").strip() or None

    missing: list[str] = []
    if not base_url:
        missing.append("COYOTE_BASE_URL")
    if not project_id:
        missing.append("COYOTE_PROJECT_ID")
    if not fixtures_repo_url:
        missing.append("COYOTE_FIXTURES_REPO_URL")
    if not fixtures_ref:
        missing.append("COYOTE_FIXTURES_REF")
    if missing:
        raise ApiError("missing required configuration: " + ", ".join(missing))

    timeout_text = os.getenv("COYOTE_REQUEST_TIMEOUT", str(DEFAULT_TIMEOUT_SECONDS)).strip()
    try:
        timeout_seconds = int(timeout_text)
    except ValueError as exc:
        raise ApiError("COYOTE_REQUEST_TIMEOUT must be an integer") from exc
    if timeout_seconds < 1:
        raise ApiError("COYOTE_REQUEST_TIMEOUT must be at least 1 second")

    return Config(
        base_url=base_url,
        project_id=project_id,
        fixtures_repo_url=fixtures_repo_url,
        fixtures_ref=fixtures_ref,
        auth_token=auth_token,
        timeout_seconds=timeout_seconds,
    )


def discover_scenarios(selected_names: list[str]) -> list[ScenarioSpec]:
    wanted = {name.strip() for name in selected_names if name.strip()}
    specs: list[ScenarioSpec] = []

    for pipeline_file in sorted(SCENARIOS_DIR.glob("*/coyote.yml")):
        scenario_name = pipeline_file.parent.name
        if wanted and scenario_name not in wanted:
            continue
        specs.append(
            ScenarioSpec(
                scenario_name=scenario_name,
                pipeline_path=pipeline_file.relative_to(REPO_ROOT).as_posix(),
                job_name=scenario_name,
            )
        )

    if wanted:
        found = {spec.scenario_name for spec in specs}
        missing = sorted(wanted - found)
        if missing:
            raise ApiError("unknown scenario selection: " + ", ".join(missing))

    return specs


def index_jobs_by_name(jobs: list[dict[str, Any]], project_id: str) -> dict[str, list[dict[str, Any]]]:
    indexed: dict[str, list[dict[str, Any]]] = {}
    for job in jobs:
        if str(job.get("project_id", "")).strip() != project_id:
            continue
        name = str(job.get("name", "")).strip()
        if not name:
            continue
        indexed.setdefault(name, []).append(job)
    return indexed


def normalize_job_for_compare(job: dict[str, Any]) -> dict[str, Any]:
    return {
        "name": str(job.get("name", "")).strip(),
        "repository_url": str(job.get("repository_url", "")).strip(),
        "default_ref": str(job.get("default_ref", "")).strip(),
        "default_commit_sha": str(job.get("default_commit_sha") or "").strip(),
        "push_enabled": bool(job.get("push_enabled", False)),
        "push_branch": str(job.get("push_branch") or "").strip(),
        "branch_allowlist": sorted(str(item).strip() for item in job.get("branch_allowlist") or [] if str(item).strip()),
        "tag_allowlist": sorted(str(item).strip() for item in job.get("tag_allowlist") or [] if str(item).strip()),
        "pipeline_yaml": str(job.get("pipeline_yaml", "")).strip(),
        "pipeline_path": str(job.get("pipeline_path") or "").strip(),
        "enabled": bool(job.get("enabled", True)),
    }


def normalize_payload_for_compare(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "name": str(payload.get("name", "")).strip(),
        "repository_url": str(payload.get("repository_url", "")).strip(),
        "default_ref": str(payload.get("default_ref", "")).strip(),
        "default_commit_sha": str(payload.get("default_commit_sha", "")).strip(),
        "push_enabled": bool(payload.get("push_enabled", False)),
        "push_branch": str(payload.get("push_branch", "")).strip(),
        "branch_allowlist": sorted(str(item).strip() for item in payload.get("branch_allowlist", []) if str(item).strip()),
        "tag_allowlist": sorted(str(item).strip() for item in payload.get("tag_allowlist", []) if str(item).strip()),
        "pipeline_yaml": str(payload.get("pipeline_yaml", "")).strip(),
        "pipeline_path": str(payload.get("pipeline_path", "")).strip(),
        "enabled": bool(payload.get("enabled", True)),
    }


def sync_jobs(client: CoyoteClient, config: Config, specs: list[ScenarioSpec]) -> int:
    jobs = client.list_jobs()
    jobs_by_name = index_jobs_by_name(jobs, config.project_id)

    created = 0
    updated = 0
    skipped = 0

    print(f"Discovered {len(specs)} fixture scenarios.")
    print(f"Loaded {len(jobs)} existing jobs from {config.api_base}.")

    for spec in specs:
        existing_matches = jobs_by_name.get(spec.job_name, [])
        if len(existing_matches) > 1:
            raise ApiError(
                f"project {config.project_id} has multiple jobs named {spec.job_name!r}; refusing to continue"
            )

        if not existing_matches:
            payload = spec.create_payload(config)
            print(f"[create] {spec.job_name} -> {spec.pipeline_path}")
            client.create_job(payload)
            created += 1
            continue

        existing = existing_matches[0]
        update_payload = spec.update_payload(config)
        current_state = normalize_job_for_compare(existing)
        desired_state = normalize_payload_for_compare(update_payload)
        if current_state == desired_state:
            print(f"[skip]   {spec.job_name} is already up to date")
            skipped += 1
            continue

        job_id = str(existing.get("id", "")).strip()
        if not job_id:
            raise ApiError(f"existing job {spec.job_name!r} is missing an id")
        print(f"[update] {spec.job_name} -> {spec.pipeline_path}")
        client.update_job(job_id, update_payload)
        updated += 1

    print(f"Summary: created={created} updated={updated} skipped={skipped}")
    return 0


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create or update Coyote fixture jobs for every scenarios/*/coyote.yml pipeline."
    )
    parser.add_argument(
        "scenario",
        nargs="*",
        help="Optional scenario names to bootstrap. Defaults to all discovered scenarios.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the create/update plan without changing the server.",
    )
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    config = read_config()
    specs = discover_scenarios(args.scenario)
    if not specs:
        raise ApiError("no scenarios matched the current selection")
    client = CoyoteClient(config=config, dry_run=args.dry_run)
    return sync_jobs(client, config, specs)


if __name__ == "__main__":
    try:
        raise SystemExit(main(sys.argv[1:]))
    except ApiError as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(1)
    except KeyboardInterrupt:
        print("error: interrupted", file=sys.stderr)
        raise SystemExit(130)
