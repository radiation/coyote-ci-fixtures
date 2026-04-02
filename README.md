## Coyote CI Pipeline Format

Each scenario includes a `coyote.yml` file describing the pipeline.

Basic structure:

```yaml
steps:
  - name: <step-name>
    command: <shell command>

artifacts:
  paths:
    - <glob paths>
