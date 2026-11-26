"""Literal CTC decode (wav2vec2, no LM) of short windows with word times + 10 ms RMS envelope.
usage: gpu-run vt-python tools/captions/ctc_windows.py <wav> <out_txt> <env_npy> a:b [a:b ...]"""
import sys, numpy as np, torch, soundfile as sf
from scipy.signal import resample_poly
from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor

wav, out, envp = sys.argv[1:4]
x, sr = sf.read(wav, dtype='float32')
if x.ndim > 1: x = x.mean(1)
# 10 ms RMS envelope in dBFS (at source sr)
hop = sr // 100
n = len(x) // hop
env = 20 * np.log10(np.sqrt((x[:n * hop].reshape(n, hop) ** 2).mean(1)) + 1e-9)
np.save(envp, env.astype(np.float32))

y = resample_poly(x, 1, sr // 16000) if sr != 16000 else x
name = 'facebook/wav2vec2-large-960h-lv60-self'
proc = Wav2Vec2Processor.from_pretrained(name)
model = Wav2Vec2ForCTC.from_pretrained(name).to('cuda').eval()
vocab = {v: k for k, v in proc.tokenizer.get_vocab().items()}
W = [tuple(map(float, x.split(':'))) for x in sys.argv[4:]]
lines = []
for a, b in W:
    seg = y[int(a * 16000):int(b * 16000)]
    inp = proc(seg, sampling_rate=16000, return_tensors='pt').input_values.to('cuda')
    with torch.no_grad():
        ids = model(inp).logits[0].argmax(-1).cpu().numpy()
    fr = 0.02  # 20 ms per frame
    words, cur, t0, prev = [], '', None, None
    for i, k in enumerate(ids):
        if k == prev: continue
        prev = k
        tok = vocab[int(k)]
        if tok == '<pad>': continue
        if tok == '|':
            if cur: words.append(f'{cur.lower()}@{a + t0:.2f}'); cur = ''
            continue
        if not cur: t0 = i * fr
        cur += tok
    if cur: words.append(f'{cur.lower()}@{a + t0:.2f}')
    lines.append(f'[{a}-{b}] ' + ' '.join(words))
open(out, 'w').write('\n'.join(lines) + '\n')
print('\n'.join(lines))
