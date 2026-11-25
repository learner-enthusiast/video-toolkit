"""Single project log lock — shared by hooks and project_state."""
from __future__ import annotations

import contextlib
import fcntl
import os


def lock_path(project: str) -> str:
    return os.path.join(project, "log.md.lock")


@contextlib.contextmanager
def project_log_lock(project: str):
    """Exclusive lock for all log.md read-modify-write operations."""
    lp = lock_path(project)
    os.makedirs(os.path.dirname(lp) or ".", exist_ok=True)
    with open(lp, "a") as lf:
        fcntl.flock(lf, fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(lf, fcntl.LOCK_UN)