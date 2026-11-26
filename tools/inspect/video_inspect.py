# video-inspect (pipeline/video-inspect.md).
# usage (from work/): gpu-run vt-python tools/inspect/video_inspect.py VIDEO [--start S --end E] [--thorough] [--glossary ../script.md] [--out-dir inspect]
# --cpu-test is for CI only: FFmpeg detectors and scene detection on the CPU; Whisper, OCR, face and VLM are skipped and the report says so.
import argparse, json, os, re, subprocess, sys, base64, urllib.request
ap = argparse.ArgumentParser(); ap.add_argument('video'); ap.add_argument('--start', type=float, default=0); ap.add_argument('--end', type=float)
ap.add_argument('--thorough', action='store_true'); ap.add_argument('--glossary', default='../script.md')
ap.add_argument('--out-dir', default='inspect'); ap.add_argument('--cpu-test', action='store_true')
ap.add_argument('--language', default='en', help='spoken language for the Whisper transcript (a Hindi twin: hi); OCR stays en')
ap.add_argument('--captions', help='caption timeline.json: check on-screen captions against it instead of Whisper and script.md')
ap.add_argument('--caption-ranges', help='trailer_ranges.json, when --captions is the main timeline and VIDEO is the trailer')
a = ap.parse_args()
ML = not a.cpu_test
if a.cpu_test: print('CPU TEST MODE (CI only): no Whisper/OCR/face/VLM. Not a QA result.', file=sys.stderr)
V = a.video; stem = os.path.splitext(os.path.basename(V))[0]; OUT = f'{a.out_dir}/{stem}'; os.makedirs(f'{OUT}/keyframes', exist_ok=True)
run = lambda cmd: subprocess.run(cmd, capture_output=True, text=True)
# ---- probe
pr = json.loads(run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration:stream=codec_type,width,height,r_frame_rate,nb_frames', '-of', 'json', V]).stdout)
vs = next(s for s in pr['streams'] if s['codec_type'] == 'video'); DUR = float(pr['format']['duration'])
Wd, Hd = vs['width'], vs['height']; S = a.start; E = a.end or DUR; portrait = Hd > Wd
rng = ['-ss', str(S), '-to', str(E)]
# ---- detectors
err = run(['ffmpeg', '-hide_banner', '-nostats', *(['-hwaccel', 'cuda'] if ML else []), *rng, '-i', V, '-vf', 'blackdetect=d=0.03:pix_th=0.10,freezedetect=n=-60dB:d=3', '-af', 'silencedetect=n=-40dB:d=0.6,ebur128=peak=true', '-f', 'null', '-']).stderr
fl = lambda p: [float(x) for x in re.findall(p, err)]
black = list(zip(fl(r'black_start:([\d.]+)'), fl(r'black_end:([\d.]+)')))
fs, fe = fl(r'freeze_start: ([\d.]+)'), fl(r'freeze_end: ([\d.]+)'); fe += [E - S] * (len(fs) - len(fe))
freeze = list(zip(fs, fe))
ss_, se_ = fl(r'silence_start: ([\d.]+)'), fl(r'silence_end: ([\d.]+)'); se_ += [E - S] * (len(ss_) - len(se_))
silence = list(zip(ss_, se_))
summ = err[err.rfind('Summary:'):]
I = re.search(r'I:\s+(-?[\d.]+)', summ); LRA = re.search(r'LRA:\s+([\d.]+)', summ); TP = re.search(r'Peak:\s+(-?[\d.]+)', summ)
# ---- scenes
from scenedetect import detect, AdaptiveDetector
sc = detect(V, AdaptiveDetector(adaptive_threshold=3.0, min_scene_len=8), start_time=S, end_time=E)
scenes = [[round(x[0].get_seconds(), 2), round(x[1].get_seconds(), 2)] for x in sc] or [[S, E]]
# ---- frames
def grab(t, path, w=960):
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', f'{t:.3f}', '-i', V, '-frames:v', '1', '-vf', f'scale={w}:-2', '-q:v', '3', '-update', '1', path])
samples = []
for i, (t0, t1) in enumerate(scenes):
    ts = [(t0 + t1) / 2] + ([t0 + 2 / 30, max(t0, t1 - 2 / 30)] if a.thorough else [])
    for k, t in enumerate(ts):
        p = f'{OUT}/keyframes/s{i:03d}_{k}.jpg'; grab(t, p); samples.append((i, k, t, p))
if a.thorough:
    t = S
    while t < min(E, DUR - 0.1): p = f'{OUT}/keyframes/t{t:07.2f}.jpg'; grab(t, p); samples.append((-1, 9, t, p)); t += 1
# caption band frames
band = f'{OUT}/band'; os.makedirs(band, exist_ok=True)
for f_ in os.listdir(band): os.remove(f'{band}/{f_}')
cf = 6 if a.thorough else 2
crop = 'crop=iw:ih*0.24:0:ih*0.54' if portrait else 'crop=iw:ih*0.30:0:ih*0.70'  # reel: covers the SPLIT strip (y 1040) and FULL lower third (y 1440)
subprocess.run(['ffmpeg', '-v', 'error', *rng, '-i', V, '-vf', f'fps={cf},{crop}', f'{band}/cap_%05d.jpg'])
# ---- transcript (unload ollama first)
def ollama(payload, path='/api/generate'):
    try:
        r = urllib.request.urlopen(urllib.request.Request('http://localhost:11434' + path, data=json.dumps(payload).encode(), headers={'Content-Type': 'application/json'}), timeout=180)
        return json.loads(r.read())
    except Exception as ex: return {'error': str(ex)}
words = []
if ML:
    ollama({'model': 'qwen2.5vl:3b', 'keep_alive': 0})
    wav = f'{OUT}/a16.wav'; subprocess.run(['ffmpeg', '-v', 'error', '-y', *rng, '-i', V, '-vn', '-ac', '1', '-ar', '16000', wav])
    from faster_whisper import WhisperModel
    m = WhisperModel('large-v3', device='cuda', compute_type='int8')
    segs, _ = m.transcribe(wav, language=a.language, word_timestamps=True, vad_filter=True, best_of=1, condition_on_previous_text=False)
    words = [[round(w.start, 2), round(w.end, 2), w.word.strip()] for s_ in segs for w in s_.words]
    del m
    import gc; gc.collect()
# ---- OCR (own venv)
lst = f'{OUT}/ocr_list.json'; bands = sorted(os.listdir(band))
json.dump([p for *_, p in samples] + [f'{band}/{b}' for b in bands], open(lst, 'w'))
ocr = {}
if ML:
    r = run(['vt-ocr-python', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'video_inspect_ocr.py'), lst, f'{OUT}/ocr.json'])
    ocr = json.load(open(f'{OUT}/ocr.json')) if os.path.exists(f'{OUT}/ocr.json') else {}
    if r.returncode: print('OCR failed:', r.stderr[-400:])
# ---- face (CPU, MediaPipe)
if ML:
    import mediapipe as mp, cv2
    from mediapipe.tasks.python import vision, BaseOptions
    fl_ = vision.FaceLandmarker.create_from_options(vision.FaceLandmarkerOptions(base_options=BaseOptions(model_asset_path=os.path.expanduser('~/.cache/mediapipe/face_landmarker.task')), output_face_blendshapes=True, num_faces=2))
def face(p):
    if not ML: return {'n': 0}
    img = cv2.cvtColor(cv2.imread(p), cv2.COLOR_BGR2RGB); res = fl_.detect(mp.Image(image_format=mp.ImageFormat.SRGB, data=img))
    if not res.face_landmarks: return {'n': 0}
    lm = res.face_landmarks[0]; xs = [q.x for q in lm]; ys = [q.y for q in lm]
    bs = {c.category_name: c.score for c in res.face_blendshapes[0]}
    return {'n': len(res.face_landmarks), 'box': [round(min(xs), 3), round(min(ys), 3), round(max(xs), 3), round(max(ys), 3)], 'blink': [round(bs.get('eyeBlinkLeft', 0), 2), round(bs.get('eyeBlinkRight', 0), 2)]}
# ---- VLM (hint only)
notes = [] if ML else ['CPU TEST MODE: Whisper, OCR, face and VLM skipped; not a QA result']
def vlm(p):
    if not ML: return None
    small = p.replace('.jpg', '_512.jpg'); subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', p, '-vf', 'scale=512:-2', '-update', '1', small])
    r_ = ollama({'model': 'qwen2.5vl:3b', 'prompt': 'Describe this video frame in one short sentence.', 'images': [base64.b64encode(open(small, 'rb').read()).decode()], 'stream': False, 'keep_alive': '30s', 'options': {'temperature': 0, 'num_predict': 40, 'num_ctx': 2048}})
    return r_.get('response', '').strip() or None
first = True
scene_out = []
for i, (t0, t1) in enumerate(scenes):
    p = f'{OUT}/keyframes/s{i:03d}_0.jpg'
    d = vlm(p)
    if first and ML:
        ps = ollama({}, '/api/ps') if False else None
        try:
            ps = json.loads(urllib.request.urlopen('http://localhost:11434/api/ps', timeout=10).read())
            mm = ps.get('models', [{}])[0]
            if mm and mm.get('size') and mm.get('size_vram', 0) < mm['size']: notes.append(f"VLM on GPU {100*mm['size_vram']/mm['size']:.0f}% (4 GB card limit)")
        except Exception: pass
        first = False
    scene_out.append({'i': i, 't': [t0, t1], 'kf': p, 'vlm': d, 'ocr': ocr.get(p, []), 'face': face(p)})
if ML: ollama({'model': 'qwen2.5vl:3b', 'keep_alive': 0})
# ---- captions from band OCR
# what captions are compared with: Whisper's words, or the caption timeline itself (times on the inspected range's clock)
if a.captions:
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')))
    from tools.inspect import caption_reference
    ref = [[s - S, e - S, w] for s, e, w in caption_reference.load(a.captions, a.caption_ranges) if S <= s < E]
    notes_ref = [f'caption checks use {os.path.basename(a.captions)}, not Whisper']
else:
    ref, notes_ref = words, []
spoken = [re.sub(r'[^a-z0-9]', '', w[2].lower()) for w in ref]
captions = []
for k, b in enumerate(bands):
    t = S + k / cf
    txt = ' '.join(x[0] for x in ocr.get(f'{band}/{b}', []) if x[1] >= 0.6).strip()
    toks = [re.sub(r'[^a-z0-9]', '', x.lower()) for x in txt.split()]; toks = [x for x in toks if x]
    if len(txt) < 3 or not toks: continue
    near = {spoken[j] for j, w in enumerate(ref) if abs(w[0] - (t - S)) <= 2}
    if sum(x in near for x in toks) / len(toks) < 0.5: continue
    if captions and captions[-1][2] == txt: captions[-1][1] = round(t, 2)
    else: captions.append([round(t, 2), round(t, 2), txt])
# ---- flags
flags = []
def flag(t, typ, detail, frame=None): flags.append({'t': round(t, 2), 'type': typ, 'detail': detail, 'frame': frame})
for b0, b1 in black:
    if b1 - b0 < 0.5 and b0 > 0.2 and b1 < E - S - 0.2: flag(S + b0, 'black_flash', f'{b1-b0:.2f}s')
for t0, t1 in scenes:
    if t1 - t0 < 0.25: flag(t0, 'short_scene', f'{t1-t0:.2f}s')
for f0, f1 in freeze: flag(S + f0, 'static_hold', f'{f1-f0:.2f}s')
for s0, s1 in silence:
    if s0 > 0.3 and s1 < E - S - 0.3: flag(S + s0, 'dead_air', f'{s1-s0:.2f}s')
gloss = set(re.sub(r'[^a-z0-9]', '', x.lower()) for x in re.findall(r"[A-Za-z0-9.'-]+", open(a.glossary).read())) if os.path.exists(a.glossary) else set()
dic = set(x.strip().lower() for x in open('/usr/share/dict/american-english')) if os.path.exists('/usr/share/dict/american-english') else set()
for (i, k, t, p) in samples:
    fc = face(p); boxes = ocr.get(p, [])
    for txt, score, bx in boxes:
        x0, y0, x1, y1 = bx
        if min(x0, y0) < 0.005 or max(x1, y1) > 0.995: flag(t, 'text_cut_off', txt, p)
        elif min(x0, y0) < 0.05 or max(x1, y1) > 0.95: flag(t, 'outside_margin', txt, p)
        if fc.get('n') and fc.get('box'):
            fb = fc['box']
            if x0 < fb[2] and x1 > fb[0] and y0 < fb[3] and y1 > fb[1]: flag(t, 'text_over_face', txt, p)
        if score >= 0.9 and (y1 - y0) >= 0.02:
            for wd in re.findall(r"[A-Za-z]{3,}", txt):
                lw = wd.lower()
                if lw not in dic and lw not in gloss and lw not in spoken and lw.rstrip('s') not in dic: flag(t, 'misspelling', wd, p)
    if fc.get('n') and fc.get('box'):
        fb = fc['box']
        if min(fb[0], fb[1]) < 0.01 or max(fb[2], fb[3]) > 0.99: flag(t, 'face_edge', str(fb), p)
        if fc['blink'][0] > 0.5 and fc['blink'][1] > 0.5: flag(t, 'eyes_closed', str(fc['blink']), p)
for c0, c1, txt in captions:
    t0 = re.sub(r'[^a-z0-9]', '', txt.split()[0].lower())
    cand = [w[0] + S for w in ref if re.sub(r'[^a-z0-9]', '', w[2].lower()) == t0 and abs(w[0] + S - c0) < 2]
    if not cand: continue
    d = c0 - min(cand, key=lambda x: abs(x - c0))
    if d > 0.4 + 1 / cf or d < -0.6 - 1 / cf: flag(c0, 'caption_desync', f'{txt!r} seen {d:+.2f}s vs speech')
flags.sort(key=lambda x: x['t'])
for fl2 in flags:
    if fl2['frame'] and os.path.exists(fl2['frame']):
        dst = f"{OUT}/keyframes/flag_{fl2['t']:07.2f}_{fl2['type']}.jpg"; subprocess.run(['cp', fl2['frame'], dst]); fl2['frame'] = dst
# ---- contact sheet
dur = E - S
vf = (f"fps=48/{dur:.3f},scale=-2:320," if portrait else f"fps=48/{dur:.3f},scale=320:-2,") + "drawtext=text='%{pts\\:hms\\:" + f"{S}" + "}':x=6:y=h-th-6:fontsize=18:fontcolor=white:box=1:boxcolor=black@0.6," + ("tile=12x4" if portrait else "tile=8x6")
subprocess.run(['ffmpeg', '-v', 'error', '-y', *rng, '-i', V, '-vf', vf, '-frames:v', '1', '-q:v', '3', f'{OUT}/contact_sheet.jpg'])
from collections import Counter
rep = {'summary': {'duration': round(DUR, 2), 'range': [S, E], 'resolution': f'{Wd}x{Hd}', 'fps': vs['r_frame_rate'], 'lufs': float(I.group(1)) if I else None, 'tp': float(TP.group(1)) if TP else None, 'lra': float(LRA.group(1)) if LRA else None,
       'scenes': len(scenes), 'flags': dict(Counter(f['type'] for f in flags)), 'notes': notes + notes_ref},
       'scenes': scene_out, 'words': words, 'captions': captions, 'black': black, 'freeze': freeze, 'silence': silence, 'flags': flags}
json.dump(rep, open(f'{OUT}/report.json', 'w'), separators=(',', ':'))
print(json.dumps(rep['summary']))
