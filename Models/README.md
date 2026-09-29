# Model weights

Weight files are not stored in this repository. Place them in this folder before starting the API.

| File | Used by |
| --- | --- |
| `best_deepfake_model.pt` | Visual detector (ViT-Base/16, 3 classes) |
| `forensic_best.pth` | Forensic detector (SRM + EfficientNet-B4) |
| `Temporal_deepfake_Video.onnx` and its `.onnx.data` | Video temporal detector |
| `audio_detector.onnx` and its `.onnx.data` | Synthetic-voice detector |

`MODELS_DIR` can point somewhere else. See `backend/.env.example`.
