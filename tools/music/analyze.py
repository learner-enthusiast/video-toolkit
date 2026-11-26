"""Measure a track: length, loudness, true peak, tempo and a loop seam. No models, NumPy only."""
from __future__ import annotations

import re
import subprocess

import numpy as np

SR = 48000
BPM_RANGE = (60, 180)
BEATS_PER_BAR = 4
LOOP_SIMILARITY = 0.92   # the bar after the seam must sound like the bar at the loop start
LOOP_LEVEL_DB = 3.0
SEAM_SEARCH_S = 0.06     # a small tempo error drifts over many bars: line each seam up
BEAT_STRENGTH = 0.3      # beat peak of the onset autocorrelation; noise is ~0.07, rhythm > 0.9
MIN_ONSET = 0.02         # onsets must be this large next to the average spectrum (a drone has none)


def decode(path: str, sr: int = SR, channels: int = 1) -> np.ndarray:
    """Any audio file as float32 via ffmpeg."""
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-vn", "-ac", str(channels), "-ar", str(sr),
                          "-f", "f32le", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).copy()


def loudness(path: str) -> tuple[float, float]:
    """(integrated LUFS, true peak dBTP) from ffmpeg's ebur128."""
    err = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", path, "-vn", "-af", "ebur128=peak=true",
                          "-f", "null", "-"], capture_output=True, text=True, check=True).stderr
    summary = err[err.rfind("Summary:"):]
    integrated = re.search(r"I:\s+(-?[\d.]+)\s+LUFS", summary)
    peak = re.search(r"Peak:\s+(-?[\d.]+|-inf)\s+dBFS", summary)
    if not integrated or not peak:
        raise SystemExit(f"could not measure loudness of {path}")
    return float(integrated[1]), float(peak[1])


def _spectra(x: np.ndarray, size: int, hop: int) -> np.ndarray:
    frames = max(0, 1 + (len(x) - size) // hop)
    window = np.hanning(size)
    return np.array([np.abs(np.fft.rfft(x[i * hop: i * hop + size] * window)) for i in range(frames)])


def tempo(x: np.ndarray, sr: int = SR) -> tuple[float, float] | None:
    """(BPM, first beat in seconds) from the autocorrelation of the spectral-flux onset strength."""
    hop, size = 480, 2048                           # 10 ms
    spec = np.log1p(_spectra(x, size, hop))
    if len(spec) < 400:
        return None
    onset = np.maximum(np.diff(spec, axis=0), 0).sum(1)
    if np.percentile(onset, 99) < MIN_ONSET * spec.sum(1).mean():
        return None
    onset = onset - onset.mean()
    n = len(onset)
    ac = np.fft.irfft(np.abs(np.fft.rfft(onset, 2 * n)) ** 2)[:n]
    lags = np.arange(int(6000 / BPM_RANGE[1]), int(6000 / BPM_RANGE[0]) + 1)
    lags = lags[lags < n - 1]
    if not len(lags) or ac[lags].max() <= BEAT_STRENGTH * ac[0]:
        return None
    # prefer tempos near 110 BPM so a half or double tempo doesn't win a tie
    weight = np.exp(-0.5 * (np.log2(6000 / lags / 110) / 0.9) ** 2)
    k = int(lags[np.argmax(ac[lags] * weight)])
    def peak(i: int) -> float:
        a, b, c = ac[i - 1], ac[i], ac[i + 1]
        return i + (0.5 * (a - c) / (a - 2 * b + c) if a - 2 * b + c else 0.0)

    lag = peak(k)
    for beats in (2, 4, 8, 16):          # the same peak many beats out gives a far finer tempo
        around = int(round(lag * beats))
        if around + 4 >= n // 2:
            break
        i = around - 3 + int(np.argmax(ac[around - 3: around + 4]))
        lag = peak(i) / beats
    phases = np.arange(int(round(lag)))
    strength = [onset[np.round(np.arange(p, n - 1, lag)).astype(int)].sum() for p in phases]
    first = (int(phases[int(np.argmax(strength))]) * hop + size // 2) / sr
    beat_s = lag / 100
    first = (first + 0.06) % beat_s - 0.06   # a beat just before a period is the beat at the start
    return round(60 / beat_s, 2), round(max(first, 0.0), 3)


def _db(x: np.ndarray) -> float:
    return 10 * np.log10(np.mean(x ** 2) + 1e-12)


def loop_seam(x: np.ndarray, bpm: float, first_beat: float, sr: int = SR) -> tuple[float, float] | None:
    """(loop start, seam) seconds: the latest bar boundary whose following bar sounds like the bar at
    the loop start, so jumping from the seam back to the start is inaudible. None if there is none."""
    bar = BEATS_PER_BAR * 60 / bpm
    length = len(x) / sr
    n = int(bar * sr)
    start = int(round(first_beat * sr))
    ref = x[start: start + n]
    if len(ref) < n or n < 4096:
        return None
    probe = min(n, sr // 2)                  # line seams up on the waveform of the first half second
    ref_spec = np.log1p(_spectra(ref, 4096, 1024)).ravel()
    reach = int(SEAM_SEARCH_S * sr)
    best = None
    k = 1
    while first_beat + k * bar + bar <= length + SEAM_SEARCH_S:
        nominal = start + int(round(k * bar * sr))
        k += 1
        if nominal < 0.5 * len(x):
            continue
        lo, hi = max(0, nominal - reach), min(len(x) - n, nominal + reach)
        if hi < lo:
            continue
        window = x[lo: hi + probe]
        seam = lo + int(np.argmax(np.correlate(window, ref[:probe], mode="valid")))
        segment = x[seam: seam + n]
        if len(segment) < n:
            continue
        spec = np.log1p(_spectra(segment, 4096, 1024)).ravel()
        similarity = float(spec @ ref_spec / (np.linalg.norm(spec) * np.linalg.norm(ref_spec) + 1e-12))
        if similarity >= LOOP_SIMILARITY and abs(_db(segment) - _db(ref)) <= LOOP_LEVEL_DB:
            best = (round(start / sr, 3), round(seam / sr, 3))   # keep the latest one that matches
    return best
