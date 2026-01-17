# New Temporal Model Integration Plan: 3D CNN Video Analyzer
**Objective**: Replace the current Temporal Detector with the user's new 3D CNN ONNX model (`Temporal_deepfake_Video.onnx`) trained on the "DeepfakeClipDataset".

## 1. Model & Architecture
*   **Model Source**: `d:\Deepway\Models\Temporal_deepfake_Video.onnx`
    *   (Requires `.data` file presence: `d:\Deepway\Models\Temporal_deepfake_Video.onnx.data`)
*   **Architecture**: `SimpleTemporal3D` (Custom 3D CNN)
*   **Classes**: Binary
    *   0: **Real**
    *   1: **Deepfake** (Covers AI Generated/Manipulated)
*   **Input Requirements**:
    *   Shape: `(Batch, Channels, Depth, Height, Width)` -> `(1, 3, 16, 112, 112)`
    *   Sequence: 16 Frames uniformly sampled.
    *   Resize: 112x112 pixels.
    *   Normalization: `pixel / 255.0` (Range 0-1).
    *   Format: RGB.

## 2. Implementation Strategy

### A. Backend Updates (`backend/app/services/temporal_detector.py`)
1.  **Model Loading**:
    *   Update `ONNX_MODEL` path to `Temporal_deepfake_Video.onnx`.
    *   Ensure `onnxruntime` session loads correctly.
2.  **Preprocessing (`preprocess_video`)**:
    *   Current logic might be different (EfficientNet or 3D ResNet defaults).
    *   **New Logic**:
        *   Capture video.
        *   Sample exactly **16 frames** uniformly.
        *   Resize each to **(112, 112)**.
        *   Convert BGR to RGB.
        *   Normalize: `img / 255.0` (Float32).
        *   Transpose to `(Channels, Frames, Height, Width)`.
        *   Add Batch Dimension: `(1, 3, 16, 112, 112)`.
3.  **Inference**:
    *   Run `session.run`.
    *   Apply `Softmax` on logits.
    *   **Risk Score**: `Prob(Fake) * 100`.
    *   **Classification**:
        *   Risk > 50: "FAKE"
        *   Risk <= 50: "AUTHENTIC"

### B. Integration with Video Pipeline (`backend/app/api/video.py`)
*   The `video.py` endpoint already calls `temporal_detector.analyze(video_path)`.
*   It expects a result dict with `risk_score` and `classification`.
*   **No API changes required** if `temporal_detector` maintains the interface.
*   *Note*: The ViT Frame Analysis (implemented previously) will run in parallel on the *same* video (but typically different frame sampling resolution, ViT uses 224x224).
    *   `video.py` handles frame extraction for ViT (`extract_frames` function uses native resolution).
    *   `temporal_detector` will handle its own internal usage of 112x112 frames (handled inside `temporal_detector.analyze`).

## 3. Execution Steps
1.  **Update `temporal_detector.py`**: Rewrite the `analyze` and `_preprocess` methods to match the new 112x112 16-frame logic.
2.  **Verify**: Ensure `d:\Deepway\Models\Temporal_deepfake_Video.onnx` exists.

## 4. Constraint Checklist
- [x] Use `Temporal_deepfake_Video.onnx`
- [x] Standard AI Video Analysis (Do not touch Enhanced)
- [x] Detect Real vs Deepfake (Binary)
- [x] Proper Reporting (Return Risk Score)

---
**Status**: Ready to Implement.
