#!/usr/bin/env python3
"""Modular, timeline-preserving voice cleanup for video-toolkit."""
from __future__ import annotations
import argparse, json, re, shutil, subprocess, sys, tempfile
from pathlib import Path

PRESETS = {
    "natural": {"dereverb_strength": 0.15, "enhancement_strength": 0.25, "noise_strength": 0.25, "compression_enabled": False},
    "studio": {"dereverb_strength": 0.35, "enhancement_strength": 0.35, "noise_strength": 0.35, "compression_enabled": True},
    "strong-room": {"dereverb_strength": 0.6, "enhancement_strength": 0.45, "noise_strength": 0.45, "compression_enabled": True},
}

def run(args):
    p = subprocess.run(args, check=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return p.stdout + p.stderr

DEFAULT_DEEPFILTER_PYTHON = Path.home() / ".local/share/deepfilternet/venv/bin/python"
DEFAULT_DEEPFILTER_CLI = Path.home() / "bin/deep-filter"

def deepfilter_command(executable=None, interpreter=None):
    """Find the reusable global CLI or its isolated Python interpreter."""
    import os
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
    raise FileNotFoundError("DeepFilterNet is not installed. Install it in ~/.local/share/deepfilternet/venv or set DEEPFILTERNET_EXECUTABLE / DEEPFILTERNET_PYTHON.")

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

def wpe_dereverb(input_wav, output_wav, strength, taps=10, delay=3, iterations=3):
    """Offline single-channel WPE late-reverb prediction at 16 kHz."""
    import numpy as np
    import soundfile as sf
    from scipy.signal import resample_poly, stft, istft
    audio, sr = sf.read(input_wav, dtype="float64")
    if audio.ndim != 1: audio = audio.mean(axis=1)
    if sr != 16000: audio = resample_poly(audio, 16000, sr)
    _, times, y = stft(audio, fs=16000, nperseg=512, noverlap=384, boundary="zeros")
    frames = y.shape[1]; first = delay + taps - 1
    if frames <= first + 2:
        sf.write(output_wav, audio, 16000, subtype="PCM_24"); return {"applied": False, "reason": "clip too short for WPE"}
    enhanced = y.copy(); eps = 1e-8
    valid = np.arange(first, frames)
    for f in range(y.shape[0]):
        yf = y[f]
        lam = np.maximum(np.abs(yf) ** 2, eps)
        estimate = yf[valid].copy()
        for _ in range(iterations):
            z = np.stack([yf[valid - delay - k] for k in range(taps)], axis=0)
            weights = 1.0 / np.maximum(lam[valid], eps)
            rmat = (z * weights[None, :]) @ z.conj().T
            rhs = z @ (yf[valid].conj() * weights)
            try: filt = np.linalg.solve(rmat + eps * np.eye(taps), rhs)
            except np.linalg.LinAlgError: break
            predicted = np.conj(filt) @ z
            estimate = yf[valid] - predicted
            lam[valid] = np.maximum(np.abs(estimate) ** 2, eps)
        enhanced[f, valid] = estimate
    _, restored = istft(enhanced, fs=16000, nperseg=512, noverlap=384, input_onesided=True, boundary=True)
    restored = restored[:len(audio)]
    if len(restored) < len(audio): restored = np.pad(restored, (0, len(audio)-len(restored)))
    # Conservatively blend the late-reverb estimate with the original signal.
    wet = restored
    mixed = audio * (1-strength) + wet * strength
    sf.write(output_wav, mixed, 16000, subtype="FLOAT")
    return {"applied": True, "algorithm": "single-channel WPE", "taps": taps, "delay_frames": delay, "iterations": iterations, "strength": strength}

def clean(source, output, preset="studio", config_path=None, report_path=None, neural=True, mode="quality", deepfilter_python=None, deepfilter_executable=None):
    if not shutil.which("ffmpeg") or not shutil.which("ffprobe"):
        raise RuntimeError("FFmpeg and ffprobe are required. Install with: sudo apt install ffmpeg")
    if not source.is_file(): raise FileNotFoundError(source)
    settings = dict(PRESETS[preset])
    if config_path: settings.update(json.loads(config_path.read_text()))
    if mode == "balanced": neural = False
    elif mode == "performance":
        neural = False
        settings["dereverb_enabled"] = False
    elif mode != "quality": raise ValueError(f"Unknown processing mode: {mode}")
    strength = max(0., min(1., float(settings.get("dereverb_strength", .55))))
    noise = max(0., min(1., float(settings.get("noise_strength", .35))))
    info = probe(source); output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="voice-clean-") as td:
        tmp = Path(td); current = tmp / "input.wav"
        run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(source), "-vn", "-ac", "1", "-ar", "48000", "-c:a", "pcm_f32le", str(current)])
        dereverb_report = {"applied": False, "reason": "disabled"}
        if settings.get("dereverb_enabled", True):
            try:
                wpe_input, wpe_output = tmp / "pre_wpe.wav", tmp / "wpe.wav"
                run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(current), "-ar", "16000", "-ac", "1", "-c:a", "pcm_f32le", str(wpe_input)])
                dereverb_report = wpe_dereverb(wpe_input, wpe_output, strength)
                if dereverb_report.get("applied"):
                    wpe_back = tmp / "wpe_back.wav"
                    run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(wpe_output), "-ar", "48000", "-ac", "1", "-c:a", "pcm_f32le", str(wpe_back)])
                    current = wpe_back
            except ImportError as e:
                print(f"WPE dereverberation unavailable (install scipy and soundfile): {e}", file=sys.stderr)
                dereverb_report = {"applied": False, "reason": "scipy or soundfile missing"}
        engine = "ffmpeg-dsp"
        enhancement_report = {"enabled": False, "model": "DeepFilterNet3", "status": "disabled"}
        if neural and settings.get("speech_enhancement_enabled", True):
            enhancement_strength = max(0., min(1., float(settings.get("enhancement_strength", .35))))
            try:
                command, backend = deepfilter_command(deepfilter_executable, deepfilter_python)
                dfn_dir = tmp / "deepfilternet3"
                dfn_dir.mkdir()
                dfn_log = run(command + ["--model-base-dir", "DeepFilterNet3", "--no-suffix", "--output-dir", str(dfn_dir), str(current)])
                device_match = re.search(r"Running on device ([^\r\n]+)", dfn_log)
                time_match = re.search(r"in ([\d.]+)s \(RT factor: ([\d.]+)\)", dfn_log)
                candidates = list(dfn_dir.glob("*.wav"))
                if not candidates: raise RuntimeError("DeepFilterNet ran but did not produce an output WAV")
                blend = tmp / "speech_enhanced_blend.wav"
                run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(current), "-i", str(candidates[0]), "-filter_complex", f"[0:a]volume={1-enhancement_strength}[dry];[1:a]volume={enhancement_strength}[wet];[dry][wet]amix=inputs=2:normalize=0", "-ar", "48000", "-ac", "1", "-c:a", "pcm_f32le", str(blend)])
                current, engine = blend, "DeepFilterNet3"
                enhancement_report = {"enabled": True, "model": "DeepFilterNet3", "backend": backend, "strength": enhancement_strength, "status": "processed", "device": device_match.group(1) if device_match else "see CLI log", "inference_seconds": float(time_match.group(1)) if time_match else None, "real_time_factor": float(time_match.group(2)) if time_match else None}
            except (ImportError, RuntimeError, OSError, subprocess.CalledProcessError) as e:
                print(f"DeepFilterNet3 stage unavailable; WPE and FFmpeg stages continue: {e}", file=sys.stderr)
                enhancement_report = {"enabled": True, "model": "DeepFilterNet3", "status": "unavailable", "error": str(e)}
        # Remaining FFmpeg stages handle noise cleanup and mastering.
        filters = ["highpass=f=78"]
        if settings.get("noise_enabled", True) and noise > .01: filters.append(f"afftdn=nr={2+6*noise:.1f}:nf=-45:tn=1")
        if settings.get("eq_enabled", True): filters += ["equalizer=f=260:t=q:w=1:g=-1", "equalizer=f=3200:t=q:w=1:g=0.8"]
        if settings.get("compression_enabled", True): filters.append("acompressor=threshold=0.125:ratio=2.2:attack=18:release=140:makeup=1")
        if settings.get("deess_enabled", True): filters.append("deesser=i=0.15:m=0.35:f=0.5")
        if settings.get("loudness_enabled", True): filters.append("loudnorm=I=-16:TP=-1.5:LRA=11:print_format=none")
        run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(current), "-af", ",".join(filters), "-ar", "48000", "-ac", "1", "-c:a", "pcm_s24le", str(output)])
    out_info = probe(output)
    result = {"input": str(source), "output": str(output), "preset": preset, "mode": mode, "engine": engine, "speech_enhancement": enhancement_report, "dereverberation": dereverb_report, "input_audio": info, "input_measurements": measure(source), "output_measurements": measure(output), "input_clipping_suspected": (measure(source)["true_peak_dbtp"] is not None and measure(source)["true_peak_dbtp"] >= -0.1), "duration_seconds": out_info["duration"], "duration_delta_seconds": out_info["duration"]-info["duration"], "reverberation_note": "No automatic room-severity score is claimed; compare and listen."}
    if report_path:
        report_path.parent.mkdir(parents=True, exist_ok=True); report_path.write_text(json.dumps(result, indent=2)+"\n")
    return result

def main():
    p = argparse.ArgumentParser(description=__doc__); p.add_argument("input", type=Path); p.add_argument("output", type=Path)
    p.add_argument("--preset", choices=PRESETS, default="studio"); p.add_argument("--mode", choices=("quality", "balanced", "performance"), default="quality"); p.add_argument("--config", type=Path); p.add_argument("--report", type=Path); p.add_argument("--no-neural", action="store_true"); p.add_argument("--deepfilter-python", help="Override DEEPFILTERNET_PYTHON"); p.add_argument("--deepfilter-executable", help="Override DEEPFILTERNET_EXECUTABLE")
    a = p.parse_args()
    try: print(json.dumps(clean(a.input, a.output, a.preset, a.config, a.report, not a.no_neural, a.mode, a.deepfilter_python, a.deepfilter_executable), indent=2)); return 0
    except (OSError, ValueError, RuntimeError, subprocess.CalledProcessError) as e: print(f"audio cleaning failed: {e}", file=sys.stderr); return 1

if __name__ == "__main__": raise SystemExit(main())
