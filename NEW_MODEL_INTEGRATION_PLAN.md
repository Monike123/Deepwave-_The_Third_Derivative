# New Model Integration Plan: ViT Deepfake Standard Analyser
**Objective**: Replace the current Standard AI (VisualDetector) with the user's new Vision Transformer (ViT) model (`best_deepfake_model.pt`) trained on the "AI-vs-Deepfake-vs-Real" dataset.

## 1. Model & Architecture
*   **Model Source**: `d:\Deepway\Models\best_deepfake_model.pt`
*   **Architecture**: `google/vit-base-patch16-224-in21k` (Vision Transformer)
*   **Classes**: 3-Class Classification
    1.  **Real**
    2.  **Deepfake**
    3.  **AI Generated**
*   **Input Size**: 224x224 (ViT standard)

## 2. Implementation Strategy

### A. Backend Updates (`backend/app/services/visual_detector.py`)
1.  **Dependency Update**: Ensure `transformers` library is installed and imported.
2.  **Model Loading**:
    *   Initialize architecture: `AutoModelForImageClassification.from_pretrained("google/vit-base-patch16-224-in21k", num_labels=3)`
    *   Load Weights: Load state dictionary from `best_deepfake_model.pt`.
    *   **Crucial**: Define `id2label` mapping based on the "AI-vs-Deepfake-vs-Real" dataset.
        *   Likely: `0: "Real", 1: "Deepfake", 2: "AI Generated"` (Will verify or use robust key handling).
3.  **Preprocessing**:
    *   Replace manual OpenCV resizing with `AutoImageProcessor` or `torchvision.transforms` matching the training code:
        *   Resize to (224, 224)
        *   Normalize (Mean/Std of ImageNet/ViT)
4.  **Inference Logic (`predict_frame` / `predict_image`)**:
    *   Run inference.
    *   Apply `Softmax` to logits.
    *   **Risk Score Calculation**:
        *   `Risk = (Prob(Deepfake) + Prob(AiGenerated)) * 100`
    *   **Classification**:
        *   If Risk > 50%: Return "FAKE" (and sub-label "Deepfake" or "AI Generated" in details).
        *   Else: "REAL".
5.  **Device Handling**: Support `cuda` (GPU) checks.

### B. Video Analysis (`backend/app/api/video.py`)
*   The existing frame iteration logic uses `visual_detector.predict_frame()`.
*   This will automatically inherit the new model's capabilities (Real vs Deepfake vs AI).
*   **No changes needed in `video.py`** if `predict_frame` interface remains consistent (returns dict with `risk_score` and `label`).

### C. Frontend Compatibility
*   The Frontend expects:
    *   `risk_score` (0-100)
    *   `classification` ("AUTHENTIC" or "FAKE") -- *Wait, current frontend uses "AUTHENTIC" vs "FAKE"*.
    *   For the 3-class system, we will map:
        *   Real -> AUTHENTIC
        *   Deepfake / AI Generated -> FAKE / ARTIFICIAL
*   **Constraint**: User said "proper reporting should still happen". We will ensure the JSON response includes the detailed prediction ("AI Generated" vs "Deepfake") in the keys for the Detailed Report.

## 3. Execution Steps
1.  **Backup**: Backup current `visual_detector.py`.
2.  **Install Dependencies**: Run `pip install transformers` if missing.
3.  **Update `visual_detector.py`**: Rewire to use ViT and the new `.pt` file.
4.  **Verification**: Test with `test_image.jpg` or via local API.

## 4. Constraint Checklist
- [x] Use `best_deepfake_model.pt`
- [x] Standard AI Only (Do not touch Enhanced/Cloud)
- [x] Handle Images & Split Videos
- [x] Proper Reporting (Risk Score + Class)

---
**Status**: Ready to Implement functionality.
