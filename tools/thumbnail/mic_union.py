# Person cutout (birefnet-general) + separately segmented mic region, unioned. usage: vt-python tools/thumbnail/mic_union.py photo person_cut.png out.png x0 y0 x1 y1
import sys, numpy as np
from PIL import Image
from rembg import remove, new_session
ph, pc, out = sys.argv[1:4]; x0, y0, x1, y1 = map(int, sys.argv[4:8])
im = Image.open(ph).convert('RGB'); person = np.array(Image.open(pc))[..., 3]
s = new_session('birefnet-general', providers=['CPUExecutionProvider'])
crop = remove(im.crop((x0, y0, x1, y1)), session=s, only_mask=True)
mic = np.zeros_like(person); mic[y0:y1, x0:x1] = np.array(crop)
alpha = np.maximum(person, mic)
rgba = np.dstack([np.array(im), alpha]); Image.fromarray(rgba).save(out)
print('person px', int((person > 40).sum()), 'mic px', int((mic > 40).sum()), 'union', int((alpha > 40).sum()))
