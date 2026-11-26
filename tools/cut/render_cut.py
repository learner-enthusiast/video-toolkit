# writes filter scripts for the cut voice (1x and sped) and the 720p rough preview (select-based picture, no per-segment buffering)
# usage (from work/): vt-python tools/cut/render_cut.py K [--edl edl.json] [--out-dir scripts]
import argparse, json, os
ap = argparse.ArgumentParser(); ap.add_argument('K', type=float, nargs='?', default=1.05)
ap.add_argument('--edl', default='edl.json'); ap.add_argument('--out-dir', default='scripts')
args = ap.parse_args(); K = args.K; D = args.out_dir; os.makedirs(D, exist_ok=True)
S = json.load(open(args.edl))['segments']
fr = [(round(a*30), round(b*30)) for a, b in S]
A = [f"[0:a]atrim=start_sample={f0*1600}:end_sample={f1*1600},asetpts=PTS-STARTPTS[a{i}]" for i, (f0, f1) in enumerate(fr)]
n = len(fr)
cat = ";\n".join(A) + ";\n" + "".join(f"[a{i}]" for i in range(n)) + f"concat=n={n}:v=0:a=1"
open(f'{D}/voice1x.fg', 'w').write(cat + "[out]")
open(f'{D}/voice.fg', 'w').write(cat + f",atempo={K}[out]")
sel = "+".join(f"between(n\\,{f0}\\,{f1-1})" for f0, f1 in fr)
open(f'{D}/preview.fg', 'w').write(f"[0:v]select='{sel}',setpts=N/(30*TB),setpts=PTS/{K},fps=30,scale=720:1280[vout]")
tot = sum(f1 - f0 for f0, f1 in fr)
print("cut_frames", tot, "out_frames", round(tot / K), "out_s", round(tot / K / 30, 3))
