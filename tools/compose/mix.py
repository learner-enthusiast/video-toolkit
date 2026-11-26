"""Offline mix (pipeline/sound.md §7): sfx.wav from sfx_cues*.json, voice laid on the output timeline,
mix = voice + sfx, plus the music bed stem with --music (tools/sound/music_bed.py builds it from the voice).
usage (from work/): vt-python tools/compose/mix.py main|trailer [--music audio/stems/<which>-music.wav]"""
import json, os, subprocess, sys
os.makedirs('scripts', exist_ok=True)
W = '.'; which = sys.argv[1]
if sys.argv[2:] and (len(sys.argv) != 4 or sys.argv[2] != '--music'):
    sys.exit(__doc__)
music = sys.argv[3] if sys.argv[2:] else None
K = 'sfx_cues.json' if which == 'main' else 'sfx_cues_trailer.json'
d = json.load(open(f'audio/{K}')); dur = d['duration']; cues = d['cues']
sfx_out = 'audio/sfx.wav' if which == 'main' else 'audio/sfx_trailer.wav'
voice_out = 'audio/voice_main.wav' if which == 'main' else 'audio/voice_trailer.wav'
mix_out = 'audio/mix.wav' if which == 'main' else 'audio/mix_trailer.wav'
run = lambda a: subprocess.run(a, check=True)
# 1 · sfx track
ins, fl = [], []
for i, c in enumerate(cues):
    ins += ['-i', f'remotion/public/sfx/{c["sound"]}.wav']
    fl.append(f'[{i}]adelay={max(0, round(c["t"] * 1000))}:all=1,volume={c["gain_db"]}dB[s{i}]')
graph = ';'.join(fl) + ';' + ''.join(f'[s{i}]' for i in range(len(cues))) + f'amix=inputs={len(cues)}:normalize=0,apad=whole_dur={dur:.3f},atrim=0:{dur:.3f}[o]'
open(f'scripts/sfx_{which}.fg', 'w').write(graph)
run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', *ins, '-filter_complex_script', f'scripts/sfx_{which}.fg', '-map', '[o]', '-ar', '48000', '-ac', '1', '-c:a', 'pcm_s24le', sfx_out])
# 2 · voice on the output timeline
if which == 'main':
    run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-i', 'audio/voice.wav', '-af', f'apad=whole_dur={dur:.3f},atrim=0:{dur:.3f}', '-ar', '48000', '-ac', '1', '-c:a', 'pcm_s24le', voice_out])
else:
    R = json.load(open('audio/trailer_ranges.json'))['ranges']; tail = dur - sum(b - a for a, b in R) / 30
    parts = [f'[0]atrim=start_sample={a * 1600}:end_sample={b * 1600},asetpts=PTS-STARTPTS,afade=t=in:d=0.012,afade=t=out:st={(b - a) / 30 - 0.012:.3f}:d=0.012[v{i}]' for i, (a, b) in enumerate(R)]
    g = ';'.join(parts) + ';' + ''.join(f'[v{i}]' for i in range(len(R))) + f'concat=n={len(R)}:v=0:a=1,apad=whole_dur={dur:.3f},atrim=0:{dur:.3f}[o]'
    run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-i', 'audio/voice.wav', '-filter_complex', g, '-map', '[o]', '-ar', '48000', '-ac', '1', '-c:a', 'pcm_s24le', voice_out])
# 3 · mix (fade the last 0.5 s with the picture fade)
stems = [voice_out, sfx_out, *([music] if music else [])]   # the voice goes in unchanged; the bed is already leveled
run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', *[a for s in stems for a in ('-i', s)], '-filter_complex', ''.join(f'[{i}]' for i in range(len(stems))) + f'amix=inputs={len(stems)}:normalize=0,afade=t=out:st={dur - 0.5:.3f}:d=0.5[o]', '-map', '[o]', '-ar', '48000', '-c:a', 'pcm_s24le', mix_out])
print(which, 'cues', len(cues), 'dur', round(dur, 3), '->', mix_out)
