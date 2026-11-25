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

```bash
# After inspect completes:
vt-python tools/inspect_cache.py store projects/<name> out/main.mp4 work/inspect/main --mode thorough \
  --inspect-script projects/<name>/work/scripts/video_inspect.py

# Before intermediate QA:
vt-python tools/inspect_cache.py lookup projects/<name> out/main.mp4 --mode default

# Final QA: lookup must hit a thorough bundle (or run fresh inspect)
vt-python tools/inspect_cache.py lookup projects/<name> out/main.mp4 --mode thorough --for-final
```

`restore` copies the full bundle to `work/inspect/<deliverable>/`. Cache does not replace Opus vision QA.