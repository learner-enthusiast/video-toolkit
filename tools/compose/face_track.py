# FaceTrackedCrop data (components/FaceTrackedCrop.md): BlazeFace on the upright CFR copy.
# usage (from work/): vt-python tools/compose/face_track.py clips/main.mp4 remotion/public/data/face.json
import sys, json, cv2, numpy as np, mediapipe as mp
from mediapipe.tasks.python import vision, BaseOptions
src, out = sys.argv[1:3]
det = vision.FaceDetector.create_from_options(vision.FaceDetectorOptions(
    base_options=BaseOptions(model_asset_path=f"{__import__('os').path.expanduser('~')}/.cache/mediapipe/blaze_face_short_range.tflite"),
    running_mode=vision.RunningMode.VIDEO, min_detection_confidence=0.5))
cap = cv2.VideoCapture(src); W = int(cap.get(3)); H = int(cap.get(4)); N = int(cap.get(7))
cx = np.full(N, np.nan); cy = np.full(N, np.nan); fw = np.full(N, np.nan)
i = 0
while True:
    ok, fr = cap.read()
    if not ok: break
    if i % 2 == 0:
        small = cv2.resize(fr, (W // 2, H // 2))
        r = det.detect_for_video(mp.Image(image_format=mp.ImageFormat.SRGB, data=cv2.cvtColor(small, cv2.COLOR_BGR2RGB)), int(i * 1000 / 30))
        if r.detections:
            b = max(r.detections, key=lambda d: d.bounding_box.width).bounding_box
            cx[i] = (b.origin_x + b.width / 2) * 2; cy[i] = (b.origin_y + b.height / 2) * 2; fw[i] = b.width * 2
    i += 1
N = i; cx, cy, fw = cx[:N], cy[:N], fw[:N]
ok = ~np.isnan(cx); rate = ok[::2].mean()
idx = np.arange(N)
def fill(a): return np.interp(idx, idx[ok], a[ok])
def smooth(a, k=31):
    from scipy.signal import medfilt
    a = medfilt(a, 15)
    # critically damped follower with dead zone (px)
    o = np.copy(a); v = 0.0; dz = 12
    for t in range(1, len(a)):
        e = a[t] - o[t - 1]
        if abs(e) < dz: e = 0
        v = 0.85 * v + 0.006 * e
        o[t] = o[t - 1] + v
    return o
cxs, cys, fws = smooth(fill(cx)), smooth(fill(cy)), smooth(fill(fw))
json.dump({"w": W, "h": H, "n": N, "rate": round(float(rate), 3),
           "cx": [round(float(v), 1) for v in cxs], "cy": [round(float(v), 1) for v in cys], "fw": [round(float(v), 1) for v in fws]}, open(out, "w"))
print(f"frames={N} detect_rate={rate:.3f} cx[{np.nanmin(cx):.0f},{np.nanmax(cx):.0f}] cy[{np.nanmin(cy):.0f},{np.nanmax(cy):.0f}] fw median={np.nanmedian(fw):.0f}")
