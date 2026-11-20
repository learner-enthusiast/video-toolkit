#!/usr/bin/env python3
"""Modular, timeline-preserving voice cleanup for video-toolkit.

Stages: input validation -> WPE dereverberation -> DeepFilterNet 3 -> FFmpeg
cleanup/mastering -> measurements -> JSON report. Quality mode (the default and
the only production mode) fails closed: if WPE or DeepFilterNet 3 is missing,
disabled, errors, or produces no verifiable result, the run exits non-zero and
no output is published.
"""
from __future__ import annotations
import argparse, json, math, os, re, shutil, subprocess, sys, tempfile, uuid
from pathlib import Path

PRESETS = {
    "natural": {"dereverb_strength": 0.15, "enhancement_strength": 0.25, "noise_strength": 0.25, "compression_enabled": False},
    "studio": {"dereverb_strength": 0.35, "enhancement_strength": 0.35, "noise_strength": 0.35, "compression_enabled": True},
    "strong-room": {"dereverb_strength": 0.6, "enhancement_strength": 0.45, "noise_strength": 0.45, "compression_enabled": True},
}
KNOWN_SETTINGS = {"dereverb_enabled", "dereverb_strength", "speech_enhancement_enabled", "enhancement_strength",
                  "noise_enabled", "noise_strength", "eq_enabled", "compression_enabled", "deess_enabled", "loudness_enabled"}
STAGES = ("wpe", "deepfilternet3", "mastering")
LOUDNESS_TARGET_LUFS, TRUE_PEAK_CEILING_DBTP = -16.0, -1.5
DURATION_WARN_S, DURATION_FAIL_S = 0.02, 0.10
PROTECTED_DIRS = ("raw", "assets")

DEFAULT_DEEPFILTER_PYTHON = Path.home() / ".local/share/deepfilternet/venv/bin/python"
DEFAULT_DEEPFILTER_CLI = Path.home() / "bin/deep-filter"


class StageError(RuntimeError):
    """A failure attributed to one named processing stage."""
    def __init__(self, stage, message):
        super().__init__(message)
        self.stage = stage


def run(args):
    try:
        p = subprocess.run(args, check=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        tail = [l for l in ((e.stderr or "") + (e.stdout or "")).strip().splitlines() if l.strip()][-6:]
        raise RuntimeError(f"{Path(str(args[0])).name} exited with status {e.returncode}: {' | '.join(tail) or 'no output'}") from e
    return p.stdout + p.stderr


def deepfilter_command(executable=None, interpreter=None):
    """Find the reusable global CLI or its isolated Python interpreter."""
    explicit_cli = executable or os.environ.get("DEEPFILTERNET_EXECUTABLE")
    if explicit_cli:
        path = Path(explicit_cli).expanduser()
        if not path.is_file(): raise FileNotFoundError(f"DeepFilterNet executable not found: {path}")
        return [str(path)], str(path)
    explicit_python = interpreter or os.environ.get("DEEPFILTERNET_PYTHON")
    if explicit_python:
        py = Path(explicit_python).expanduser()
        if not py.is_file(): raise FileNotFoundError(f"DeepFilterNet Python interpreter not found: {py}")
        return [str(py), "-m", "df.enhance"], str(py)
    for name in ("deep-filter", "deepFilter"):
        found = shutil.which(name)
        if found: return [found], found
    if DEFAULT_DEEPFILTER_CLI.is_file():
        return [str(DEFAULT_DEEPFILTER_CLI)], str(DEFAULT_DEEPFILTER_CLI)
    if DEFAULT_DEEPFILTER_PYTHON.is_file():
        return [str(DEFAULT_DEEPFILTER_PYTHON), "-m", "df.enhance"], str(DEFAULT_DEEPFILTER_PYTHON)
    raise FileNotFoundError("DeepFilterNet is not installed. Install it in ~/.local/share/deepfilternet/venv (setup.md) or set DEEPFILTERNET_EXECUTABLE / DEEPFILTERNET_PYTHON.")


def probe(path):
    data = json.loads(run(["ffprobe", "-v", "error", "-select_streams", "a:0", "-show_entries", "stream=sample_rate,channels,channel_layout,duration:format=duration", "-of", "json", str(path)]))
    streams = data.get("streams", [])
    if not streams: raise ValueError(f"No audio stream found: {path}")
    s = streams[0]; duration = float(s.get("duration", data.get("format", {}).get("duration", 0)))
    if duration <= 0: raise ValueError(f"Could not determine audio duration: {path}")
    return {"sample_rate": int(s["sample_rate"]), "channels": int(s["channels"]), "channel_layout": s.get("channel_layout", "unknown"), "duration": duration}


def measure(path):
    text = run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(path), "-af", "ebur128=peak=true", "-f", "null", "-"])
    def val(label):
        found = re.findall(rf"{label}\s*:\s*(-?[\d.]+|\-inf)", text)
        try: return float(found[-1]) if found else None
        except ValueError: return None
    return {"integrated_lufs": val("I"), "loudness_range_lu": val("LRA"), "true_peak_dbtp": val("Peak")}


def _wpe_stft(audio, taps=10, delay=3, iterations=3):
    """Single-channel WPE on 16 kHz audio. Returns the dereverberated signal (same length).

    Raises ValueError when the clip is too short and RuntimeError on any numerical failure;
    it never silently returns the input."""
    import numpy as np
    from scipy.signal import stft, istft
    _, _, y = stft(audio, fs=16000, nperseg=512, noverlap=384, boundary="zeros")
    frames = y.shape[1]; first = delay + taps - 1
    if frames <= first + 2:
        raise ValueError(f"recording too short for WPE ({len(audio) / 16000:.3f} s, {frames} STFT frames; needs more than {first + 2})")
    enhanced = y.copy(); eps = 1e-8
    valid = np.arange(first, frames)
    for f in range(y.shape[0]):
        yf = y[f]
        lam = np.maximum(np.abs(yf) ** 2, eps)
        estimate = yf[valid].copy()
        for it in range(iterations):
            z = np.stack([yf[valid - delay - k] for k in range(taps)], axis=0)
            weights = 1.0 / np.maximum(lam[valid], eps)
            rmat = (z * weights[None, :]) @ z.conj().T
            rhs = z @ (yf[valid].conj() * weights)
            try: filt = np.linalg.solve(rmat + eps * np.eye(taps), rhs)
            except np.linalg.LinAlgError as e:
                raise RuntimeError(f"WPE numerical failure at frequency bin {f}, iteration {it + 1}") from e
            if not np.all(np.isfinite(filt)):
                raise RuntimeError(f"WPE produced non-finite filter coefficients at frequency bin {f}, iteration {it + 1}")
            estimate = yf[valid] - np.conj(filt) @ z
            if not np.all(np.isfinite(estimate)):
                raise RuntimeError(f"WPE produced non-finite enhanced audio at frequency bin {f}, iteration {it + 1}")
            lam[valid] = np.maximum(np.abs(estimate) ** 2, eps)
        enhanced[f, valid] = estimate
    _, restored = istft(enhanced, fs=16000, nperseg=512, noverlap=384, input_onesided=True, boundary=True)
    restored = restored[:len(audio)]
    if len(restored) < len(audio): restored = np.pad(restored, (0, len(audio) - len(restored)))
    if not np.all(np.isfinite(restored)):
        raise RuntimeError("WPE inverse STFT produced non-finite samples")
    return restored


def wpe_dereverb(input_wav, output_wav, strength, taps=10, delay=3, iterations=3):
    """16 kHz-only WPE blend (analysis/regression helper; the pipeline uses wpe_fullband)."""
    import numpy as np
    import soundfile as sf
    from scipy.signal import resample_poly
    audio, sr = sf.read(input_wav, dtype="float64")
    if audio.ndim != 1: audio = audio.mean(axis=1)
    if sr != 16000:
        g = math.gcd(sr, 16000); audio = resample_poly(audio, 16000 // g, sr // g)
    try: restored = _wpe_stft(audio, taps, delay, iterations)
    except ValueError as e:
        sf.write(output_wav, audio, 16000, subtype="PCM_24")
        return {"applied": False, "status": "failed", "reason": str(e)}
    mixed = audio * (1 - strength) + restored * strength
    sf.write(output_wav, mixed, 16000, subtype="FLOAT")
    return {"applied": True, "status": "processed", "algorithm": "single-channel WPE", "taps": taps, "delay_frames": delay, "iterations": iterations, "strength": strength}


def wpe_fullband(input_wav, output_wav, strength, taps=10, delay=3, iterations=3):
    """WPE estimated at 16 kHz, applied to the full-band signal.

    The predicted late reverberation (16 kHz input minus WPE output) is upsampled and
    subtracted at `strength` from the original-rate audio. Below 8 kHz this equals
    blending `(1-strength)*dry + strength*WPE`; above 8 kHz the original is kept, so
    the voice's air and sibilance are not band-limited. Raises on any failure."""
    import numpy as np
    import soundfile as sf
    from scipy.signal import resample_poly
    audio, sr = sf.read(input_wav, dtype="float64")
    if audio.ndim != 1: audio = audio.mean(axis=1)
    g = math.gcd(sr, 16000); up, down = sr // g, 16000 // g
    a16 = resample_poly(audio, down, up) if sr != 16000 else audio
    restored = _wpe_stft(a16, taps, delay, iterations)
    residual16 = a16 - restored
    in_energy, res_energy = float(np.sum(a16 ** 2)), float(np.sum(residual16 ** 2))
    if in_energy <= 0: raise RuntimeError("WPE input is silent; nothing to dereverberate")
    predicted_db = 10 * math.log10(res_energy / in_energy) if res_energy > 0 else -math.inf
    if not math.isfinite(predicted_db) or predicted_db < -90:
        raise RuntimeError(f"WPE produced no measurable change (predicted reverb energy {predicted_db} dB)")
    residual = resample_poly(residual16, up, down)[:len(audio)] if sr != 16000 else residual16
    if len(residual) < len(audio): residual = np.pad(residual, (0, len(audio) - len(residual)))
    out = audio - strength * residual
    if not np.all(np.isfinite(out)): raise RuntimeError("WPE full-band merge produced non-finite samples")
    sf.write(output_wav, out, sr, subtype="FLOAT")
    return {"status": "processed", "applied": True, "algorithm": "single-channel WPE (late-reverberation prediction)",
            "analysis_rate_hz": 16000, "output_rate_hz": sr, "above_8khz": "original passed through (WPE not applied)",
            "taps": taps, "delay_frames": delay, "iterations": iterations, "strength": strength,
            "predicted_reverb_energy_db": round(predicted_db, 2)}


def _rel_diff_db(a_path, b_path):
    """Energy of (b - a) relative to a, in dB, over the common length."""
    import numpy as np
    import soundfile as sf
    a, _ = sf.read(a_path, dtype="float64"); b, _ = sf.read(b_path, dtype="float64")
    if a.ndim > 1: a = a.mean(axis=1)
    if b.ndim > 1: b = b.mean(axis=1)
    n = min(len(a), len(b)); ea = float(np.sum(a[:n] ** 2)); ed = float(np.sum((b[:n] - a[:n]) ** 2))
    if ea <= 0: return None
    return 10 * math.log10(ed / ea) if ed > 0 else -math.inf


HEADROOM_DBFS = -3.0


def _headroom(path, target_dbfs=HEADROOM_DBFS):
    """Scale a float WAV in place so its sample peak is at most `target_dbfs`; return the gain in dB.

    A hot stereo source folded to mono can exceed full scale in float (identical channels add +3 dB).
    DeepFilterNet 0.5.6 saves int16 without clamping, so overs wrap around into loud clicks.
    The final loudnorm restores the level, so this pre-gain never changes the delivered loudness."""
    import numpy as np
    import soundfile as sf
    x, sr = sf.read(path, dtype="float64")
    peak = float(np.max(np.abs(x))) if len(x) else 0.0
    limit = 10 ** (target_dbfs / 20)
    if peak <= limit: return 0.0, peak
    gain = limit / peak
    sf.write(path, x * gain, sr, subtype="FLOAT")
    return 20 * math.log10(gain), peak


def _full_scale_ratio(path):
    """Share of samples at (or wrapped from) full scale, and the largest sample-to-sample jump."""
    import numpy as np
    import soundfile as sf
    x, _ = sf.read(path, dtype="float64")
    if x.ndim > 1: x = x.mean(axis=1)
    if not len(x): return 0.0, 0.0
    return float(np.mean(np.abs(x) >= 0.999)), float(np.max(np.abs(np.diff(x)))) if len(x) > 1 else 0.0


TONE_BANDS = ((80, 300), (300, 1000), (1000, 3000), (3000, 6000), (6000, 10000), (10000, 20000))
TONE_WARN_DB = 6.0


def _tone_shape(path):
    """Per-band energy (dB) relative to the 80 Hz-6 kHz speech-band mean: a level-independent tonal fingerprint."""
    import numpy as np
    import soundfile as sf
    x, sr = sf.read(path, dtype="float64")
    if x.ndim > 1: x = x.mean(axis=1)
    spec = np.abs(np.fft.rfft(x)) ** 2; f = np.fft.rfftfreq(len(x), 1 / sr)
    v = np.array([10 * np.log10(spec[(f >= lo) & (f < min(hi, sr / 2))].sum() + 1e-20) for lo, hi in TONE_BANDS])
    return v - v[:4].mean()


def _settings(preset, config_path, mode, neural):
    settings = dict(PRESETS[preset])
    if config_path:
        overrides = json.loads(Path(config_path).read_text())
        if not isinstance(overrides, dict): raise ValueError("Config must be a JSON object")
        unknown = sorted(set(overrides) - KNOWN_SETTINGS)
        if unknown: raise ValueError(f"Unknown config keys: {', '.join(unknown)} (allowed: {', '.join(sorted(KNOWN_SETTINGS))})")
        settings.update(overrides)
    if mode == "quality":
        if not neural or not settings.get("speech_enhancement_enabled", True):
            raise ValueError("Quality mode requires DeepFilterNet3; speech enhancement cannot be disabled.")
        if not settings.get("dereverb_enabled", True):
            raise ValueError("Quality mode requires WPE dereverberation; dereverberation cannot be disabled.")
        if float(settings.get("dereverb_strength", .35)) <= 0:
            raise ValueError("Quality mode requires dereverb_strength > 0; a zero WPE blend is a disabled stage.")
        if float(settings.get("enhancement_strength", .35)) <= 0:
            raise ValueError("Quality mode requires enhancement_strength > 0; a zero DeepFilterNet3 blend is a disabled stage.")
    elif mode == "balanced":
        settings["speech_enhancement_enabled"] = False
    elif mode == "performance":
        settings["speech_enhancement_enabled"] = False; settings["dereverb_enabled"] = False
    else:
        raise ValueError(f"Unknown processing mode: {mode}")
    if not neural: settings["speech_enhancement_enabled"] = False
    return settings


def _clean_impl(source, output, preset="studio", config_path=None, report_path=None, neural=True, mode="quality",
                deepfilter_python=None, deepfilter_executable=None, progress=None, run_id=None):
    progress = progress if progress is not None else {s: {"status": "not_attempted"} for s in STAGES}
    if not shutil.which("ffmpeg") or not shutil.which("ffprobe"):
        raise RuntimeError("FFmpeg and ffprobe are required. Install with: sudo apt install ffmpeg")
    if not source.is_file(): raise FileNotFoundError(source)
    settings = _settings(preset, config_path, mode, neural)
    if not settings.get("dereverb_enabled", True): progress["wpe"] = {"status": "disabled", "applied": False, "reason": f"{mode} mode or config"}
    if not settings.get("speech_enhancement_enabled", True): progress["deepfilternet3"] = {"status": "disabled", "model": "DeepFilterNet3", "reason": f"{mode} mode or config"}
    strength = max(0., min(1., float(settings.get("dereverb_strength", .35))))
    noise = max(0., min(1., float(settings.get("noise_strength", .35))))
    info = probe(source); output.parent.mkdir(parents=True, exist_ok=True)
    warnings = []
    with tempfile.TemporaryDirectory(prefix="voice-clean-") as td:
        tmp = Path(td); current = tmp / "input.wav"
        run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(source), "-vn", "-ac", "1", "-ar", "48000", "-c:a", "pcm_f32le", str(current)])
        input_gain_db, decoded_peak = _headroom(current)
        decoded = current
        if input_gain_db < 0:
            warnings.append(f"mono decode peaked at {20 * math.log10(decoded_peak):+.2f} dBFS; applied {input_gain_db:.2f} dB headroom before processing (final loudness unaffected)")

        if settings.get("dereverb_enabled", True):
            progress["wpe"] = {"status": "running"}
            try:
                wpe_out = tmp / "wpe.wav"
                report = wpe_fullband(current, wpe_out, strength)
                if report.get("status") != "processed" or not wpe_out.is_file():
                    raise RuntimeError(report.get("reason", "WPE did not report successful processing"))
                current = wpe_out; progress["wpe"] = report
            except Exception as e:
                progress["wpe"] = {"status": "failed", "applied": False, "error": str(e)}
                raise StageError("wpe", f"WPE dereverberation failed: {e}") from e

        engine = "ffmpeg-dsp"
        if settings.get("speech_enhancement_enabled", True):
            progress["deepfilternet3"] = {"status": "running", "model": "DeepFilterNet3"}
            enhancement_strength = max(0., min(1., float(settings.get("enhancement_strength", .35))))
            try:
                command, backend = deepfilter_command(deepfilter_executable, deepfilter_python)
                dfn_dir = tmp / "deepfilternet3"; dfn_dir.mkdir()
                dfn_log = run(command + ["--model-base-dir", "DeepFilterNet3", "--no-suffix", "--output-dir", str(dfn_dir), str(current)])
                device_match = re.search(r"Running on device ([^\r\n]+)", dfn_log)
                time_match = re.search(r"in ([\d.]+)s \(RT factor: ([\d.]+)\)", dfn_log)
                if not time_match:
                    raise RuntimeError("DeepFilterNet did not log a completed enhancement ('Enhanced noisy audio file ... RT factor'); cannot confirm inference ran")
                candidates = sorted(dfn_dir.glob("*.wav"))
                if len(candidates) != 1 or candidates[0].stat().st_size == 0:
                    raise RuntimeError(f"DeepFilterNet ran but produced {len(candidates)} output WAV(s); expected exactly one non-empty file")
                dfo = candidates[0]
                df_delta = probe(dfo)["duration"] - probe(current)["duration"]
                if abs(df_delta) > 0.05:
                    raise RuntimeError(f"DeepFilterNet output duration differs from its input by {df_delta:+.3f} s")
                fs_ratio, max_jump = _full_scale_ratio(dfo)
                if fs_ratio > 1e-4 or max_jump > 1.0:
                    raise RuntimeError(f"DeepFilterNet output is clipped or wrapped ({fs_ratio:.4%} samples at full scale, max sample jump {max_jump:.2f}); input headroom failed")
                change_db = _rel_diff_db(current, dfo)
                if change_db is None or not math.isfinite(change_db) or change_db < -90:
                    raise RuntimeError("DeepFilterNet output is identical to its input; enhancement did not run")
                blend = tmp / "speech_enhanced_blend.wav"
                run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(current), "-i", str(dfo), "-filter_complex", f"[0:a]volume={1-enhancement_strength}[dry];[1:a]volume={enhancement_strength}[wet];[dry][wet]amix=inputs=2:normalize=0", "-ar", "48000", "-ac", "1", "-c:a", "pcm_f32le", str(blend)])
                current, engine = blend, "DeepFilterNet3"
                device = device_match.group(1).strip() if device_match else None
                progress["deepfilternet3"] = {"status": "processed", "enabled": True, "model": "DeepFilterNet3", "backend": backend, "strength": enhancement_strength,
                                              "device": device, "inference_seconds": float(time_match.group(1)), "real_time_factor": float(time_match.group(2)),
                                              "output_change_db": round(change_db, 2)}
                if device is None: warnings.append("DeepFilterNet3 did not report its device")
                elif device.startswith("cpu"): warnings.append("DeepFilterNet3 ran on the CPU (no CUDA device visible); disclose this in the log")
            except Exception as e:
                progress["deepfilternet3"] = {"status": "failed", "model": "DeepFilterNet3", "error": str(e)}
                raise StageError("deepfilternet3", f"DeepFilterNet3 failed during required cleanup: {e}") from e

        # Remaining FFmpeg stages handle residual noise cleanup and mastering.
        filters = ["highpass=f=78"]
        if settings.get("noise_enabled", True) and noise > .01: filters.append(f"afftdn=nr={2+6*noise:.1f}:nf=-45:tn=1")
        if settings.get("eq_enabled", True): filters += ["equalizer=f=260:t=q:w=1:g=-1", "equalizer=f=3200:t=q:w=1:g=0.8"]
        if settings.get("compression_enabled", True): filters.append("acompressor=threshold=0.125:ratio=2.2:attack=18:release=140:makeup=1")
        if settings.get("deess_enabled", True): filters.append("deesser=i=0.15:m=0.35:f=0.5")
        if settings.get("loudness_enabled", True): filters.append(f"loudnorm=I={LOUDNESS_TARGET_LUFS:g}:TP={TRUE_PEAK_CEILING_DBTP:g}:LRA=11:print_format=none")
        progress["mastering"] = {"status": "running"}
        try:
            run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(current), "-af", ",".join(filters), "-ar", "48000", "-ac", "1", "-c:a", "pcm_s24le", "-f", "wav", str(output)])
            if not output.is_file() or output.stat().st_size == 0: raise RuntimeError("no output file written")
            out_info = probe(output)
        except Exception as e:
            progress["mastering"] = {"status": "failed", "error": str(e)}
            raise StageError("mastering", f"FFmpeg mastering failed: {e}") from e
        progress["mastering"] = {"status": "processed", "filters": filters, "sample_rate": out_info["sample_rate"], "channels": out_info["channels"], "codec": "pcm_s24le"}
        # Automated A/B: tonal change of the whole recording versus its own decoded input (catches clicks, hiss, dullness).
        tone = [round(float(d), 1) for d in _tone_shape(output) - _tone_shape(decoded)]
        tone_change = {f"{lo}-{hi}Hz": d for (lo, hi), d in zip(TONE_BANDS, tone)}
        if max(abs(d) for d in tone) > TONE_WARN_DB:
            warnings.append(f"tonal change over ±{TONE_WARN_DB:g} dB versus the input ({tone_change}); listen before use")

    in_meas, out_meas = measure(source), measure(output)
    delta = out_info["duration"] - info["duration"]
    if abs(delta) > DURATION_FAIL_S:
        progress["mastering"] = {"status": "failed", "error": f"duration changed by {delta:+.3f} s"}
        raise StageError("mastering", f"Output duration differs from source by {delta:+.3f} s (> {DURATION_FAIL_S} s); sync would break")
    if abs(delta) > DURATION_WARN_S: warnings.append(f"duration delta {delta:+.3f} s exceeds {DURATION_WARN_S} s; verify start/middle/end sync")
    in_clip = in_meas["true_peak_dbtp"] is not None and in_meas["true_peak_dbtp"] >= -0.1
    out_clip = out_meas["true_peak_dbtp"] is None or out_meas["true_peak_dbtp"] > TRUE_PEAK_CEILING_DBTP + 0.5
    if in_clip: warnings.append("source true peak >= -0.1 dBTP: the recording may be clipped; cleaning cannot restore clipped audio")
    if out_clip: warnings.append(f"output true peak above {TRUE_PEAK_CEILING_DBTP + 0.5} dBTP (or unmeasured)")
    if settings.get("loudness_enabled", True) and (out_meas["integrated_lufs"] is None or abs(out_meas["integrated_lufs"] - LOUDNESS_TARGET_LUFS) > 1.0):
        warnings.append(f"output integrated loudness {out_meas['integrated_lufs']} LUFS is more than 1 LU from {LOUDNESS_TARGET_LUFS}")

    blocking = []
    if mode != "quality": blocking.append(f"mode '{mode}' is not the production quality mode")
    for stage in ("wpe", "deepfilternet3"):
        if progress[stage].get("status") != "processed": blocking.append(f"{stage} status is {progress[stage].get('status')}")
    result = {"run_id": run_id, "status": "succeeded", "input": str(source), "output": str(output), "preset": preset, "mode": mode, "engine": engine,
              "stages": {s: progress[s].get("status") for s in STAGES},
              "dereverberation": progress["wpe"], "speech_enhancement": progress["deepfilternet3"], "mastering": progress["mastering"],
              "input_audio": info, "processing_headroom_gain_db": round(input_gain_db, 2), "tone_change_db": tone_change, "input_measurements": in_meas, "output_measurements": out_meas,
              "input_clipping_suspected": in_clip, "output_clipping_suspected": out_clip,
              "duration_seconds": out_info["duration"], "duration_delta_seconds": delta, "warnings": warnings,
              "production_gate": {"automated_checks_passed": not blocking, "blocking": blocking,
                                  "listening_approval": "required: compare source and output at matched loudness before Whisper (pipeline/voice-cleaning.md)"},
              "reverberation_note": "WPE reduces late reverberation below 8 kHz; it does not remove strong early reflections or slapback. No automatic room-severity score is claimed; compare and listen."}
    if report_path:
        report_path.parent.mkdir(parents=True, exist_ok=True); report_path.write_text(json.dumps(result, indent=2) + "\n")
    return result


def _atomic_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w") as f:
            json.dump(data, f, indent=2); f.write("\n"); f.flush(); os.fsync(f.fileno())
        os.replace(temp_name, path)
    finally:
        if os.path.exists(temp_name): os.unlink(temp_name)


def _owner_input(path):
    """The `input` recorded in an existing report/status JSON, or None."""
    try: return json.loads(path.read_text()).get("input")
    except (OSError, ValueError, AttributeError): return None


def clean(source, output, preset="studio", config_path=None, report_path=None, neural=True, mode="quality", deepfilter_python=None, deepfilter_executable=None):
    source, output = Path(source), Path(output)
    source_resolved, output_resolved = source.resolve(), output.resolve()
    if source_resolved == output_resolved or (output.exists() and os.path.samefile(source, output)):
        raise ValueError(f"Unsafe audio paths: output resolves to the source recording ({source_resolved})")
    report = Path(report_path).resolve() if report_path else None
    if report and report in (source_resolved, output_resolved):
        raise ValueError("Unsafe audio paths: report must be separate from input and output")
    for label, p in (("output", output_resolved), ("report", report)):
        if p and any(part.name in PROTECTED_DIRS for part in p.parents):
            raise ValueError(f"Unsafe audio paths: {label} {p} is inside a protected raw/ or assets/ folder")
    source, output = source_resolved, output_resolved

    run_id = uuid.uuid4().hex
    status_path = output.with_name(output.name + ".run-status.json")
    status_resolved = status_path.resolve()
    if report and report == status_resolved:
        raise ValueError("Unsafe audio paths: report path collides with the run-status file")
    if status_resolved == source_resolved or (status_path.exists() and os.path.samefile(source, status_path)):
        raise ValueError(f"Unsafe audio paths: run-status file aliases the source recording ({source_resolved})")
    for label, p in (("report", report), ("output", status_path)):
        owner = _owner_input(p) if p and p.exists() else None
        if owner and owner != str(source_resolved):
            raise ValueError(f"Unsafe audio paths: existing {label} {p} belongs to another recording ({owner}); give each recording its own ID, WAV and report")
    output.parent.mkdir(parents=True, exist_ok=True)
    if report: report.parent.mkdir(parents=True, exist_ok=True)
    status = {"run_id": run_id, "status": "running", "input": str(source_resolved), "output": str(output_resolved), "report": str(report) if report else None, "mode": mode, "preset": preset,
              "existing_output_at_start": output.exists(), "existing_report_at_start": bool(report and report.exists())}
    _atomic_json(status_path, status)

    def temp_sibling(path, suffix):
        fd, name = tempfile.mkstemp(prefix=f".{path.name}.{run_id}.", suffix=suffix, dir=path.parent)
        os.close(fd); os.unlink(name)
        return Path(name)

    staged_output = temp_sibling(output, ".tmp.wav")
    staged_report = temp_sibling(report, ".tmp.json") if report else None
    output_backup = report_backup = None
    output_published = report_published = False
    progress = {s: {"status": "not_attempted"} for s in STAGES}
    try:
        result = _clean_impl(source, staged_output, preset, config_path, staged_report, neural, mode, deepfilter_python, deepfilter_executable, progress, run_id)
        result["output"] = str(output_resolved)
        if not staged_output.is_file() or staged_output.stat().st_size == 0:
            raise StageError("mastering", "Mastering produced no valid output file")
        probe(staged_output)
        if staged_report:
            staged_report.write_text(json.dumps(result, indent=2) + "\n")

        if output.exists():
            output_backup = output.with_name(output.name + f".previous-{run_id}")
            os.replace(output, output_backup)
        if report and report.exists():
            report_backup = report.with_name(report.name + f".previous-{run_id}")
            os.replace(report, report_backup)
        os.replace(staged_output, output); output_published = True
        if report and staged_report:
            os.replace(staged_report, report); report_published = True
        status.update({"status": "succeeded", "stages": result["stages"], "production_gate": result["production_gate"],
                       "previous_output": str(output_backup) if output_backup else None, "previous_report": str(report_backup) if report_backup else None})
        _atomic_json(status_path, status)
        return result
    except Exception as e:
        if output_published and output.exists(): output.unlink()
        if report_published and report and report.exists(): report.unlink()
        if output_backup and output_backup.exists(): os.replace(output_backup, output)
        if report_backup and report_backup.exists(): os.replace(report_backup, report)
        failed_stage = getattr(e, "stage", None) or ("publish" if output_published else "input_validation")
        for s in STAGES:
            if progress[s].get("status") == "running": progress[s] = {"status": "failed", "error": str(e)}
        stages = {s: progress[s].get("status") for s in STAGES}
        failed_report = None
        if report:
            failed_report = report.with_name(report.name + f".run-{run_id}.failed.json")
            _atomic_json(failed_report, {"run_id": run_id, "status": "failed", "failed_stage": failed_stage, "stages": stages, "stage_details": progress,
                                         "input": str(source_resolved), "output": str(output_resolved), "error": str(e),
                                         "note": "No cleaned output was published by this run. Do not transcribe or edit with any file at the output path."})
        status.update({"status": "failed", "failed_stage": failed_stage, "stages": stages, "error": str(e), "failed_report": str(failed_report) if failed_report else None,
                       "previous_output_preserved": bool(output_backup and output_backup.exists()) or (output.exists() and not output_published),
                       "previous_report_preserved": bool(report_backup and report_backup.exists()) or bool(report and report.exists() and not report_published)})
        _atomic_json(status_path, status)
        e.failed_stage, e.stages, e.status_path = failed_stage, stages, str(status_path)
        raise
    finally:
        for temp_path in (staged_output, staged_report):
            if temp_path and temp_path.exists(): temp_path.unlink()


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter,
                                epilog="Production talking-head cleanup must use --mode quality (the default). balanced (no DeepFilterNet 3) and performance (no WPE, no DeepFilterNet 3) are explicit alternate modes: they never pass the voice-cleaning gate and need the user's explicit approval.")
    p.add_argument("input", type=Path); p.add_argument("output", type=Path)
    p.add_argument("--preset", choices=PRESETS, default="studio")
    p.add_argument("--mode", choices=("quality", "balanced", "performance"), default="quality", help="Processing mode (quality is mandatory for production voice cleanup)")
    p.add_argument("--config", type=Path, help="JSON overrides; quality mode rejects disabling or zeroing WPE / DeepFilterNet 3")
    p.add_argument("--report", type=Path, help="Per-recording JSON report (use a unique path per recording)")
    p.add_argument("--deepfilter-python", help="Override DEEPFILTERNET_PYTHON"); p.add_argument("--deepfilter-executable", help="Override DEEPFILTERNET_EXECUTABLE")
    a = p.parse_args(argv)
    try:
        result = clean(a.input, a.output, a.preset, a.config, a.report, True, a.mode, a.deepfilter_python, a.deepfilter_executable)
    except Exception as e:
        stages = getattr(e, "stages", None)
        print(f"audio cleaning FAILED (stage: {getattr(e, 'failed_stage', 'input_validation')}): {e}", file=sys.stderr)
        if stages: print("stages: " + ", ".join(f"{k}={v}" for k, v in stages.items()), file=sys.stderr)
        if getattr(e, "status_path", None): print(f"run status: {e.status_path}", file=sys.stderr)
        print("No cleaned output was published. Do not transcribe; fix the cause or ask the user before any substitute.", file=sys.stderr)
        return 1
    print(json.dumps(result, indent=2))
    gate = result["production_gate"]
    print(("automated gate: PASSED" if gate["automated_checks_passed"] else "automated gate: NOT PASSED (" + "; ".join(gate["blocking"]) + ")")
          + f" | stages: {', '.join(f'{k}={v}' for k, v in result['stages'].items())} | warnings: {len(result['warnings'])} | listening approval still required", file=sys.stderr)
    return 0


if __name__ == "__main__": raise SystemExit(main())
