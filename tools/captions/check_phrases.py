# check every at("…") phrase in src against timeline.json (pipeline/composition.md)
# usage (from work/remotion/): vt-python tools/captions/check_phrases.py [--timeline public/data/timeline.json] [--src src]
import argparse, json, re, glob
ap = argparse.ArgumentParser(); ap.add_argument('--timeline', default='public/data/timeline.json'); ap.add_argument('--src', default='src')
args = ap.parse_args()
NUM = {'zero':'0','one':'1','two':'2','three':'3','four':'4','five':'5','six':'6','seven':'7','eight':'8','nine':'9','ten':'10','fifteen':'15','million':'million'}
n = lambda s: NUM.get(re.sub(r'[^a-z0-9]', '', s.lower()), re.sub(r'[^a-z0-9]', '', s.lower()))
W = [n(w['raw']) for w in json.load(open(args.timeline))['words']]
src = ''.join(open(f).read() for f in glob.glob(args.src + '/**/*.ts*', recursive=True))
bad = 0
for m in re.finditer(r"""\bat\((['"])(.+?)\1""", src):
    t = [n(x) for x in m.group(2).split() if n(x)]
    hits = sum(1 for i in range(len(W)) if W[i:i+len(t)] == t)
    if hits == 0: print('MISSING', m.group(2)); bad += 1
print('checked; missing =', bad)
