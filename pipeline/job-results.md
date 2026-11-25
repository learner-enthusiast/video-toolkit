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

# Final QA: lookup ALWAYS misses (run fresh thorough inspect)
vt-python tools/inspect_cache.py lookup projects/<name> out/main.mp4 --mode thorough --for-final
# → {"hit": false, "reason": "final_qa_requires_fresh_run", ...}
```

`restore` copies a bundle for **intermediate** work only. `restore --for-final` is refused (`final_qa_requires_fresh_run`). Cache does not replace Opus vision QA or human approval.

Lookup miss reasons include: `miss`, `hit`, `final_qa_requires_fresh_run`, `incomplete_bundle`, `checksum_mismatch`, `size_mismatch`, `fingerprint_mismatch`, `schema_mismatch`.