"""Momentary loudness (ITU-R BS.1770 K-weighting, 400 ms windows) and the voice-over-music gap."""
from __future__ import annotations

import numpy as np
from scipy.signal import lfilter

SR = 48000
# BS.1770-4 K-weighting at 48 kHz: high-frequency shelf, then the RLB high-pass.
SHELF = ([1.53512485958697, -2.69169618940638, 1.19839281085285], [1.0, -1.69065929318241, 0.73248077421585])
HIGHPASS = ([1.0, -2.0, 1.0], [1.0, -1.99004745483398, 0.99007225036621])
SILENT = -120.0


def k_weight(x: np.ndarray) -> np.ndarray:
    return lfilter(*HIGHPASS, lfilter(*SHELF, x))


def speaking_windows(spans: list, total_s: float, window_s: float, hop_s: float, cover: float) -> list[float]:
    """Window start times where words (spans in seconds) cover at least `cover` of the window."""
    mask = np.zeros(int(total_s * 1000) + 1, bool)
    for start, end in spans:
        mask[max(0, int(start * 1000)): max(0, int(end * 1000))] = True
    size = int(window_s * 1000)
    out, t = [], 0.0
    while t + window_s <= total_s + 1e-9:
        i = int(round(t * 1000))
        if mask[i: i + size].mean() >= cover:
            out.append(round(t, 3))
        t += hop_s
    return out


def window_levels(weighted: np.ndarray, starts: list[float], window_s: float, sr: int = SR) -> np.ndarray:
    size = int(window_s * sr)
    power = np.concatenate(([0.0], np.cumsum(weighted.astype(np.float64) ** 2)))
    at = np.clip((np.array(starts) * sr).astype(int), 0, max(0, len(weighted) - size))
    mean = (power[at + size] - power[at]) / size
    return np.maximum(-0.691 + 10 * np.log10(mean + 1e-20), SILENT)


def gap(voice: np.ndarray, music: np.ndarray, spans: list, params: dict, sr: int = SR) -> dict:
    """Voice minus music loudness in the windows where I'm speaking: median, worst, and when."""
    if sr != SR:
        raise ValueError("stems must be 48 kHz")
    n = min(len(voice), len(music))
    starts = speaking_windows(spans, n / sr, params["window_s"], params["window_hop_s"], params["window_speech_cover"])
    if not starts:
        raise ValueError("no speaking windows: check the word timings")
    v = window_levels(k_weight(voice[:n]), starts, params["window_s"], sr)
    m = window_levels(k_weight(music[:n]), starts, params["window_s"], sr)
    heard = v > -70                                   # a "speaking" window with no voice says nothing
    if not heard.any():
        raise ValueError("the voice stem is silent where the words say I speak")
    gaps = (v - m)[heard]
    times = np.array(starts)[heard]
    worst = int(np.argmin(gaps))
    return {"windows": int(len(gaps)), "median_db": round(float(np.median(gaps)), 2),
            "worst_db": round(float(gaps[worst]), 2), "worst_at_s": round(float(times[worst]), 2)}
