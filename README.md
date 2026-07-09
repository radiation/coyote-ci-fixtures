## Coyote CI Fixtures

This repository stays intentionally small: each fixture is a scenario folder with a `coyote.yml`, a few shell scripts, and tiny generated outputs that are easy to inspect in the Coyote UI.

Authoritative DSL note:

- The pipeline YAML in this repo follows the current parser in `coyote-ci/backend/internal/pipeline/schema.go`.
- Parallel execution uses top-level `group.steps`.
- Typed artifacts use `name`, `path`, and optional `type` values. Valid explicit types today are `docker_image`, `npm_package`, `generic`, and `unknown`.

## Repository Layout

```text
example.coyote.yml
scenarios/
  success-basic/
  failure-exit-1/
  logs-long-running/
  artifacts-basic/
  multi-step-failure/
  artifact-versioned-release-shared-version/
  artifact-pagination-search-catalog/
  parallel-artifacts-fanout/
  monorepo-lite-submodules/
  maven-jar-basic/
  npm-library-package/
  python-uv-managed-image-base/
  python-uv-managed-image-lockfile-bump/
```

Each scenario should keep the same lightweight pattern:

- `scenarios/<name>/coyote.yml`
- `scenarios/<name>/scripts/*.sh`
- small fixture source files only when they improve test value
- generated outputs written under `output/`, `dist/`, `target/`, or `artifacts/`

## Real-Network Smoke Scenarios

These scenarios are opt-in. They are intended for local smoke validation of real worker behavior when a build needs:

- public container image pulls
- package-manager network access
- language runtime/toolchain availability
- cache restore/save visibility in logs
- artifact upload after real dependency work

They are not part of the default tiny fixture set, and normal unit tests should not depend on them.

Current opt-in scenarios:

- `docker-image-pull-smoke`: pull a public image and upload a simple artifact
- `maven-dependency-smoke`: resolve a Maven Central dependency and package a tiny JAR
- `npm-install-cache-smoke`: resolve an npm dependency, exercise the `node` cache preset, and pack a tarball
- `python-pip-install-smoke`: resolve PyPI dependencies and upload a version report
- `missing-tool-failure-smoke`: intentionally fail on an image that does not contain Maven so logs/status can be inspected

## Recommended Scenario Set

### Keep as-is

- `success-basic`: minimal success smoke test
- `failure-exit-1`: minimal failure smoke test
- `logs-long-running`: streaming log smoke test
  Note: this scenario now runs for about 60 seconds total, which makes it suitable for both log streaming smoke checks and manual Workers-page busy visibility checks.
- `multi-step-failure`: sequential failure barrier smoke test

### Keep, but treat as legacy-smoke coverage

- `artifacts-basic`: still useful as the smallest possible artifact collection scenario, but no longer the main artifact browse fixture

### New scenarios

| Scenario | What it tests | Execution | Artifact pattern | Managed-image input files |
| --- | --- | --- | --- | --- |
| `artifact-versioned-release-shared-version` | Stable logical artifact paths across repeated builds, shared release version applied to multiple logical artifacts, obvious version display | Sequential | Fixed logical paths under `releases/` with `release.strategy: template` | none |
| `artifact-pagination-search-catalog` | Pagination, search, filtering, mixed obvious names, many artifact rows in one build | Sequential | 24+ files under `output/catalog/` with readable names and tags | none |
| `parallel-artifacts-fanout` | Parallel `group.steps` producing artifacts from multiple steps plus a downstream summary | Parallel fan-out then sequential summary | Step-level artifacts under `output/backend/`, `output/frontend/`, `output/docs/` | none |
| `monorepo-lite-submodules` | One scenario that feels like a small monorepo without committing to future project/job orchestration | Parallel fan-out then sequential summary | Submodule-style outputs under `modules/api/`, `modules/worker/`, `modules/sdk/` | `package.json`, `package-lock.json`, `pom.xml`, `uv.lock` |
| `maven-jar-basic` | Tiny Java/Maven fixture, obvious JAR artifact, metadata sidecar for browse/version UI | Sequential | `target/demo-app-1.0.0.jar` plus manifest text/json | `pom.xml` |
| `npm-library-package` | Tiny package/library fixture with `dist/` output plus packed tarball | Sequential | `dist/**` and `artifacts/acme-widget-0.3.0.tgz` | `package.json`, `package-lock.json` |
| `python-uv-managed-image-base` | Baseline managed-image dependency inputs for a small FastAPI-style fixture | Sequential | `artifacts/images/fastapi-managed-image.tar` plus input manifest | `pyproject.toml`, `uv.lock`, `Dockerfile` |
| `python-uv-managed-image-lockfile-bump` | Same logical fixture as baseline, but with dependency/lockfile changes intended to trigger managed-image refresh behavior | Sequential | same output paths as baseline with changed metadata | `pyproject.toml`, `uv.lock`, `Dockerfile` |

## Scenario Notes

### Real-network smoke scenarios

These scenarios are intentionally separate from the legacy placeholder-style fixtures above.

- The placeholder fixtures remain useful for browse/version/manual UI coverage without depending on Docker Hub, Maven Central, npm, or PyPI.
- The real-network smoke fixtures are the worker-validation slice for CLI-first troubleshooting and agent workflows.

Queueing helpers:

- `scripts/run-fixtures.sh all` queues only the small default scenarios.
- `scripts/run-fixtures.sh real-network` queues the successful real-network smoke set.
- `scripts/run-fixtures.sh manual-failure` queues the intentional failure fixture.

CLI-first smoke loop after running `scripts/bootstrap_fixture_jobs.py`:

```bash
coyote job run npm-install-cache-smoke --project fixtures --ref main --yes
coyote build watch <build-id>
coyote build logs <build-id>
coyote build artifacts <build-id>
coyote build artifacts download <build-id> --all --output ./artifacts/npm-install-cache-smoke
```

Agent-friendly JSON variant:

```bash
BUILD_ID=$(coyote job run npm-install-cache-smoke --project fixtures --ref main --yes --json | jq -r '.run.build_id')
coyote build watch "$BUILD_ID" --json
coyote build logs "$BUILD_ID" --json
coyote build artifacts "$BUILD_ID" --json
coyote build artifacts download "$BUILD_ID" --all --output ./artifacts/npm-install-cache-smoke --json
```

Recommended local prerequisites before running the real-network scenarios:

- the worker is running with the Docker execution backend
- outbound network access is available from worker step containers
- the host Docker daemon can pull public images
- you are comfortable with the local-dev Docker socket trust model documented in the main repo

For the cache smoke specifically, run the same job twice and inspect `coyote build logs <build-id>` for lines such as:

- `cache lookup: ... hit=false`
- `cache lookup: ... hit=true`
- `cache restore end: ...`
- `cache save end: ...`

For the intentional failure smoke, use `missing-tool-failure-smoke` and confirm that:

- the build reaches `failed`
- the failing step remains distinguishable from timeout/cancel paths
- the logs preserve the shell error showing the missing executable

### `artifact-versioned-release-shared-version`

- Uses `release.strategy: template` with a simple template such as `2.1.{build_number}`.
- Produces multiple logical artifacts that intentionally share the same release version string in one build.
- Keeps logical paths stable so repeated runs create browseable version history.

### `artifact-pagination-search-catalog`

- Generates enough artifacts to force pagination in the artifact UI.
- Names include team, service, channel, and version fragments so search and filtering are visually obvious.
- Mixed file extensions let the backend infer different display types without requiring a complex build.

### `parallel-artifacts-fanout`

- Uses the current grouped-step DSL exactly:

```yaml
steps:
  - group:
      name: fanout
      steps:
        - name: backend
          command: ./scripts/build-backend.sh
        - name: frontend
          command: ./scripts/build-frontend.sh
        - name: docs
          command: ./scripts/build-docs.sh
```

- Each parallel step writes into its own artifact subtree.
- A final sequential step writes a manifest showing all fan-out outputs.

### `monorepo-lite-submodules`

- This is the recommended monorepo-style fixture.
- It keeps a single scenario and a single pipeline, but the repo contents look like multiple submodules.
- It gives Coyote a realistic source tree for browse and artifact tests without deciding whether future orchestration should be whole-repo or multi-job.

### `maven-jar-basic`

- Includes `pom.xml` and a tiny Java source file.
- The script keeps things lightweight by generating a tiny JAR-shaped output and a readable manifest instead of building a real application.

### `npm-library-package`

- Includes `package.json`, `package-lock.json`, and a tiny `src/index.js`.
- Produces both easy-to-browse `dist/` files and an `npm_package` tarball artifact.

### `python-uv-managed-image-base` and `python-uv-managed-image-lockfile-bump`

- Both scenarios model the same tiny FastAPI-style container fixture.
- The pair exists specifically to test whether managed build-image logic notices meaningful dependency input changes.
- Keep the output paths stable and change only dependency inputs plus the generated manifest content.

## Existing Scenario Guidance

### Remain unchanged

- `success-basic`
- `failure-exit-1`
- `logs-long-running`
- `multi-step-failure`

### Worth keeping, but no longer the primary artifact scenario

- `artifacts-basic`

### Redundant only if the repo needs trimming later

- None right now. The current five scenarios are still useful as tiny smoke fixtures, even after the new artifact-focused scenarios land.

## Minimum Viable Refresh

- Add `artifact-versioned-release-shared-version`
- Add `artifact-pagination-search-catalog`
- Add `parallel-artifacts-fanout`
- Add `maven-jar-basic`
- Add `npm-library-package`
- Add `python-uv-managed-image-base`
- Add `python-uv-managed-image-lockfile-bump`

This gives artifact browsing, versioning, pagination, typed outputs, parallel production, and managed-image dependency-input coverage without changing the repo shape.

## Nice-to-Have Follow-up

- Add a small scenario index script later if the main repo wants to queue only the new artifact-focused fixtures
- Add a second pagination fixture only if the UI needs even larger catalogs or different naming patterns

## Basic Pipeline Format

Each scenario includes a `coyote.yml` file describing the pipeline.

```yaml
version: 1

pipeline:
  name: scenario-name
  image: alpine:latest

steps:
  - name: run
    command: ./scripts/run.sh

artifacts:
  paths:
    - output/**
```

## Local Job Bootstrap

Use `scripts/bootstrap_fixture_jobs.py` to recreate one job per fixture scenario after local state resets.

Design:

- discovers every `scenarios/*/coyote.yml`
- ensures a fixtures project exists before syncing jobs
- optionally creates configured users before syncing jobs
- derives one stable job name per scenario from the folder name
- lists existing jobs through `/api/jobs`
- creates missing jobs and updates drifted jobs in place
- skips jobs that already match the desired repo/ref/pipeline-path configuration

Files added for this workflow:

- `scripts/bootstrap_fixture_jobs.py`: bootstrap implementation
- `.env.example`: local config template
- `.gitignore`: ignores local `.env`

Why Python:

- the job bootstrap flow needs HTTP, JSON parsing, pagination, payload comparison, and clear error handling
- Python keeps that logic small with only the standard library and avoids shell quoting problems

Usage:

```bash
cp .env.example .env
python3 scripts/bootstrap_fixture_jobs.py --dry-run
python3 scripts/bootstrap_fixture_jobs.py
python3 scripts/bootstrap_fixture_jobs.py success-basic parallel-artifacts-fanout
```

Configuration lives in `.env` or exported environment variables:

- `COYOTE_BASE_URL`: Coyote server base URL such as `http://localhost:8080`
- `COYOTE_PROJECT_ID`: optional existing project UUID; when unset or non-UUID, the script resolves by slug instead
- `COYOTE_PROJECT_SLUG`: optional project slug to find or create; defaults to `fixtures`
- `COYOTE_PROJECT_NAME`: optional project name used when the script creates the fixtures project; defaults to `Coyote Fixtures`
- `COYOTE_PROJECT_DESCRIPTION`: optional project description used on project creation
- `COYOTE_FIXTURES_REPO_URL`: git URL for this fixtures repository
- `COYOTE_FIXTURES_REF`: default git ref, usually `main`
- `COYOTE_BOOTSTRAP_USERS`: optional JSON array of users to create before syncing jobs; supports either email strings or objects with `email`, optional `display_name`, and optional `global_role`
- `COYOTE_API_TOKEN`: optional Coyote API token sent as `Authorization: Bearer <token>`
- `COYOTE_REQUEST_TIMEOUT`: optional request timeout in seconds

The default local flow is to reuse or create a `fixtures` project slug named `Coyote Fixtures` and place every fixture job there.

When Coyote runs with `AUTH_MODE=oidc` or `AUTH_MODE=header`, programmatic fixture access should use a first-class Coyote API token. Create a token for a user with the required project permissions, then export it before running the script:

```bash
export COYOTE_API_TOKEN=coyote_pat_...
python3 scripts/bootstrap_fixture_jobs.py --dry-run
```

The token inherits the owning user's global and project RBAC permissions. For the default bootstrap flow, use a token owned by a user that can list/create projects and jobs, and can create users if `COYOTE_BOOTSTRAP_USERS` is set. The raw token is shown only once when it is created, so keep it in your local environment or secret manager.

Typical OIDC flow:

1. Log in to Coyote in the browser as the user that should own the token.
2. Create a token with `POST /api/me/tokens` from the logged-in browser session, for example through the Swagger UI at `http://localhost:8080/swagger/`.
3. Copy the returned `data.token` value immediately; it is only returned once.
4. Export it as `COYOTE_API_TOKEN` before running `scripts/bootstrap_fixture_jobs.py`.

Do not export, parse, or scrape browser cookies for this script. `--dry-run` still reads current projects and jobs from the Coyote API, so it also needs `COYOTE_API_TOKEN` when auth is enabled.

Example user bootstrap configuration:

```bash
export COYOTE_BOOTSTRAP_USERS='[
  "viewer@example.com",
  {"email": "admin@example.com", "display_name": "Fixture Admin", "global_role": "admin"}
]'
```

The bootstrap script only creates missing users. It does not update or delete existing users.
