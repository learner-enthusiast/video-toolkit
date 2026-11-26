#!/bin/bash
# usage: tools/jobs/gpu_wait.sh <cmd...>  — waits until no python compute job holds the GPU (shared card), then runs; retries 6x on CUDA OOM
for i in 1 2 3 4 5 6; do
  for k in $(seq 1 900); do
    [ "$(nvidia-smi --query-compute-apps=process_name --format=csv,noheader | grep -c python)" = "0" ] && break; sleep 1
  done
  out=$("$@" 2>&1); rc=$?
  if echo "$out" | grep -qi "out of memory"; then echo "OOM try $i, waiting" >&2; sleep 10; continue; fi
  echo "$out" | tail -3; exit $rc
done
echo "gave up after OOM retries"; exit 1
