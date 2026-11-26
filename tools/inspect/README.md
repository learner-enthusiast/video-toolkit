# video_inspect.py: stages and exact settings

Reference for anyone changing `tools/inspect/video_inspect.py`; no pipeline stage reads it. How to run it and read its report: `pipeline/video-inspect.md`.

| Stage | Tool and exact settings |
|---|---|
| Probe | `ffprobe -v error -show_entries format=duration:stream=codec_type,codec_name,width,height,r_frame_rate,avg_frame_rate,nb_frames,sample_rate,channels -of json` |
| Detectors (one decode) | `ffmpeg -hide_banner -nostats -hwaccel cuda [-ss S -to E] -i V -vf "blackdetect=d=0.03:pix_th=0.10,freezedetect=n=-60dB:d=3" -af "silencedetect=n=-40dB:d=0.6,ebur128=peak=true" -f null -`; parse stderr (`black_start/end`, `lavfi.freezedetect.freeze_start/end`, `silence_start/end`, the ebur128 Summary I / LRA / Peak) |
| Scenes | PySceneDetect API: `detect(V, AdaptiveDetector(adaptive_threshold=3.0, min_scene_len=8), start_time=S, end_time=E)`. CLI for a quick look: `scenedetect -i V detect-adaptive list-scenes -n` |
| Frames | one ffmpeg seek per sample: `ffmpeg -v error -ss T -i V -frames:v 1 -vf scale=960:-2 -q:v 3 out.jpg`. Default: middle of each scene. Thorough: also scene start+2 and end−2 frames, and every 1 s |
| Caption band | `ffmpeg -ss S -to E -i V -vf "fps=2,crop=iw:ih*0.30:0:ih*0.70" cap_%05d.jpg` (fps=6 thorough). Reels: the band from the face track and brand layout, not a fixed crop |
| Transcript | faster-whisper `WhisperModel("large-v3", device="cuda", compute_type="int8_float16")`, `transcribe(wav, language="en", word_timestamps=True, vad_filter=True, best_of=1, condition_on_previous_text=False)` on a 16 kHz mono WAV (`ffmpeg -vn -ac 1 -ar 16000`). Free the model before OCR |
| OCR | PaddleOCR 3.x: `PaddleOCR(lang="en", device="gpu:0", use_doc_orientation_classify=False, use_doc_unwarping=False, use_textline_orientation=False, text_detection_model_name="PP-OCRv5_mobile_det", text_recognition_model_name="PP-OCRv5_mobile_rec")`; `r = ocr.predict(path)[0]` → `rec_texts`, `rec_scores`, `rec_boxes`. Keep score ≥ 0.6. Fallback: `easyocr.Reader(["en"], gpu=True)` |
| Face | MediaPipe Tasks `FaceLandmarker` (`~/.cache/mediapipe/face_landmarker.task`, `output_face_blendshapes=True`, `num_faces=2`), CPU. Per frame: face count, box, `eyeBlinkLeft/Right` |
| VLM | Ollama `POST localhost:11434/api/generate` `{"model":"qwen2.5vl:3b","prompt":"Describe this video frame in one short sentence.","images":[b64 of the 512 px keyframe],"stream":false,"keep_alive":"30s","options":{"temperature":0,"num_predict":40,"num_ctx":2048}}`. After the first call, read `/api/ps` and put `size_vram/size` in `summary.notes` if < 100%. Unload every Ollama model (`keep_alive: 0`) before Whisper and after this stage. A hint only, never a verdict |
| Contact sheet | `ffmpeg [-ss S -to E] -i V -vf "fps=48/DUR,scale=320:-2,drawtext=text='%{pts\:hms\:S}':x=6:y=h-th-6:fontsize=18:fontcolor=white:box=1:boxcolor=black@0.6,tile=8x6" -frames:v 1 -q:v 3 contact_sheet.jpg` (48 tiles, one image, ~1.5k tokens). Portrait: `scale=-2:320` and `tile=12x4` (an 8x6 portrait sheet is ~4k tokens) |
