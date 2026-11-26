# usage: gpu-run vt-python tools/captions/ctc_window.py wav start end [start end ...] -> greedy CTC text per window (fp32)
import sys, numpy as np, soundfile as sf, torch
from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor
M="facebook/wav2vec2-large-960h-lv60-self"
p=Wav2Vec2Processor.from_pretrained(M); m=Wav2Vec2ForCTC.from_pretrained(M).cuda().eval()
x,sr=sf.read(sys.argv[1]); x=x if x.ndim==1 else x.mean(1)
import scipy.signal as ss
a=sys.argv[2:]
for i in range(0,len(a),2):
    s,e=float(a[i]),float(a[i+1]); seg=x[int(s*sr):int(e*sr)]
    seg=ss.resample_poly(seg,1,3).astype(np.float32)
    iv=p(seg,sampling_rate=16000,return_tensors="pt").input_values.cuda()
    with torch.no_grad(): ids=m(iv).logits.argmax(-1)[0]
    print(f"{s}-{e}: {p.decode(ids)}")
