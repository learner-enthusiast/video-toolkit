# Job results (compact)

**Goal:** Claude reads a short JSON summary; full logs stay on disk.

## Heavy jobs

After reading `work/jobs/<NN>-<job>.status`, prefer:

```bash
vt-python tools/job_report.py projects/<name>/work/jobs/<NN>-<job>.status
```

Example:

```json
{
  "job": "01-render",
  "status": "failed",
  "exit_code": 1,
  "duration_seconds": 412,
  "output": "out/main.mp4",
  "log": "projects/<name>/work/jobs/01-render.log",
  "summary": "CUDA out of memory"
}
```

## Delegation CLIs

Low-stakes tasks still log to `work/delegation/<NN>-<tool>-<task>.log`. Report: exit code, last 20 lines, whether output file exists — do not paste the whole log.

## Validation

```bash
vt-python tools/validate/vt_validate.py projects/<name> --check project --check stage
```

Failures return exit 1 and a JSON `errors[]` with `code`, `message`, `file`.

## Video inspect cache

Before a full inspect run on an unchanged deliverable:

```bash
vt-python tools/inspect_cache.py lookup projects/<name> out/main.mp4 --mode thorough
```

On cache hit, `restore` copies `report.json` only; re-run inspect when the script version, mode, or video bytes change.