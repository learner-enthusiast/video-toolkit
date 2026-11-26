# Adaptive transcription (experimental)

**Status:** not default. The multi-pass workflow in `pipeline/transcribe.md` stays authoritative until benchmarks on this branch show parity.

**Goal:** after the standard initial passes, re-transcribe only uncertain windows and emit a compact discrepancy report.

## Proposed flow

1. Run plain + VAD + disfluency passes (unchanged).
2. Compare against `script.md` paragraphs → flag `MISSING_PARAGRAPH`.
3. Flag low-confidence / cross-pass disagreement windows.
4. Windowed re-transcribe + optional CTC (`tools/captions/align_ctc.py`).
5. Write `work/transcripts/discrepancy-report.json` (compact).

## Benchmark before enable

**Method:** for each representative project, run (A) full multi-pass per `pipeline/transcribe.md` and (B) adaptive draft on the same cleaned WAV; compare with `ctc_window.py` spot-checks and manual correction count. Record wall time, GPU OOMs, and hook-logged session tokens. Store results in `docs/optimization/benchmarks/transcription.json` (create when first run).

Compare old vs adaptive on representative projects: word accuracy, retake detection, caption sync, manual fix count, wall time, and hook-logged tokens. Record results in `docs/optimization/final-report.md`.

## Safe fallback

If adaptive is enabled per project via `project-state.json` → `features.adaptive_transcribe: true`, any failed gate reverts to full multi-pass.