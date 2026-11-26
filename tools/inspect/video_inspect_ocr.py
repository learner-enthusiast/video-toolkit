# OCR stage for video_inspect.py (PaddleOCR venv). usage: gpu-run vt-ocr-python tools/inspect/video_inspect_ocr.py list.json out.json
import json, sys
from PIL import Image
from paddleocr import PaddleOCR
paths = json.load(open(sys.argv[1]))
ocr = PaddleOCR(lang='en', device='gpu:0', use_doc_orientation_classify=False, use_doc_unwarping=False, use_textline_orientation=False,
                text_detection_model_name='PP-OCRv5_mobile_det', text_recognition_model_name='PP-OCRv5_mobile_rec')
out = {}
for p in paths:
    w, h = Image.open(p).size
    r = ocr.predict(p)[0]
    out[p] = [[t, round(float(s), 3), [round(b[0] / w, 3), round(b[1] / h, 3), round(b[2] / w, 3), round(b[3] / h, 3)]]
              for t, s, b in zip(r['rec_texts'], r['rec_scores'], r['rec_boxes']) if s >= 0.6]
json.dump(out, open(sys.argv[2], 'w'))
print('ocr frames', len(out))
