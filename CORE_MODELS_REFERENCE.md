# Deepway Core Models Reference
## Complete Technical Documentation for Rollback & Recovery

---

> **Version**: 1.0.0 (Baseline)  
> **Created**: January 17, 2026  
> **Purpose**: Document current working state for safe rollback if needed

---

## 📋 Table of Contents

1. [Current System State](#current-system-state)
2. [Model 1: Visual Detector (ViT)](#model-1-visual-detector-vit)
3. [Model 2: Temporal Detector (3D CNN)](#model-2-temporal-detector-3d-cnn)
4. [Model 3: Forensic Analyzer](#model-3-forensic-analyzer)
5. [Model 4: Fusion Engine](#model-4-fusion-engine)
6. [API Endpoints Reference](#api-endpoints-reference)
7. [Critical File Checksums](#critical-file-checksums)
8. [Rollback Procedures](#rollback-procedures)

---

## 🔒 Current System State

### Working Components (DO NOT MODIFY)

| Component | File | Status | Last Verified |
|-----------|------|--------|---------------|
| Visual Detector | `visual_detector.py` | ✅ Working | 2026-01-17 |
| Temporal Detector | `temporal_detector.py` | ✅ Working | 2026-01-17 |
| Forensic Analyzer | `forensic_analyzer.py` | ✅ Working | 2026-01-17 |
| Fusion Engine | `fusion_engine.py` | ✅ Working | 2026-01-17 |
| Image API | `api/image.py` | ✅ Working | 2026-01-17 |
| Video API | `api/video.py` | ✅ Working | 2026-01-17 |
| Advanced API | `api/advanced.py` | ✅ Working | 2026-01-17 |

### Model Files (NEVER DELETE)

```
D:\Deepway\Models\
├── best_deepfake_model.pt          # ViT weights (327 MB)
├── Temporal_deepfake_Video.onnx    # 3D CNN model
└── deepfake_3dcnn_final1.onnx.data # 3D CNN weights
```

---

## 🧠 Model 1: Visual Detector (ViT)

### Overview

| Property | Value |
|----------|-------|
| **Type** | Vision Transformer |
| **Base Model** | `google/vit-base-patch16-224-in21k` |
| **Input Size** | 224 × 224 × 3 (RGB) |
| **Output Classes** | 3 |
| **Device** | CPU (forced for stability) |

### Label Mapping (CRITICAL)

```python
# Training labels (from Colab notebook)
id2label = {
    0: "Artificial",   # AI-generated images
    1: "Deepfake",     # Face-swapped/manipulated
    2: "Real"          # Authentic images
}

label2id = {
    "Artificial": 0,
    "Deepfake": 1,
    "Real": 2
}
```

### Preprocessing Pipeline

```python
# EXACT steps - DO NOT CHANGE
1. Resize image to 224×224
2. Convert BGR → RGB (if from OpenCV)
3. Normalize:
   - mean = [0.5, 0.5, 0.5]
   - std = [0.5, 0.5, 0.5]
4. Convert to tensor: [B, C, H, W]
```

### Risk Score Calculation

```python
# From visual_detector.py
probabilities = softmax(logits)

# Risk calculation logic
if predicted_class in [0, 1]:  # Artificial or Deepfake
    risk_score = (1.0 - prob_real) * 100.0
    # = (prob_artificial + prob_deepfake) * 100
else:  # Real
    risk_score = (1.0 - prob_real) * 100.0

# Classification thresholds
if risk_score >= 50:
    classification = "MANIPULATED"
else:
    classification = "AUTHENTIC"
```

### Model Loading Code

```python
# EXACT loading sequence - PRESERVED
from transformers import AutoModelForImageClassification, AutoImageProcessor

# 1. Initialize with base config
model = AutoModelForImageClassification.from_pretrained(
    "google/vit-base-patch16-224-in21k",
    num_labels=3,
    id2label=id2label,
    label2id=label2id,
    ignore_mismatched_sizes=True
)

# 2. Load fine-tuned weights
state_dict = torch.load(model_path, map_location='cpu')
model.load_state_dict(state_dict, strict=False)

# 3. Set to eval mode
model.eval()
```

### Output Format

```json
{
  "prediction": {
    "fake_probability": 0.8231,
    "real_probability": 0.1769
  },
  "risk_score": 82.31,
  "classification": "MANIPULATED",
  "confidence": "HIGH",
  "detailed_label": "Deepfake",
  "class_probabilities": {
    "Artificial": 0.12,
    "Deepfake": 0.70,
    "Real": 0.18
  }
}
```

---

## 🎬 Model 2: Temporal Detector (3D CNN)

### Overview

| Property | Value |
|----------|-------|
| **Type** | 3D Convolutional Neural Network |
| **Architecture** | SimpleTemporal3D |
| **Format** | ONNX |
| **Input Shape** | (1, 3, 16, 112, 112) = (B, C, T, H, W) |
| **Output Classes** | 2 (REAL=0, FAKE=1) |

### Label Mapping (CRITICAL)

```python
# From training code
class_labels = {
    0: "REAL",
    1: "FAKE"
}
```

### Preprocessing Pipeline (EXACT)

```python
# Step 1: Extract frames
total_frames = video.frame_count
indices = np.linspace(0, total_frames - 1, 16, dtype=int)

# Step 2: For each frame
for idx in indices:
    frame = read_frame(idx)
    frame = cv2.resize(frame, (112, 112))     # Resize
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # BGR→RGB
    frames.append(frame)

# Step 3: Normalize and reshape
video_data = np.array(frames, dtype=np.float32)
video_data = video_data / 255.0               # Normalize to [0,1]
video_data = np.transpose(video_data, (3, 0, 1, 2))  # (T,H,W,C) → (C,T,H,W)
video_data = np.expand_dims(video_data, axis=0)      # Add batch dim
# Final shape: (1, 3, 16, 112, 112)
```

### Softmax Calculation

```python
# Numerically stable softmax (from training)
def stable_softmax(logits):
    exp_logits = np.exp(logits - np.max(logits))
    return exp_logits / exp_logits.sum()

# Usage
logits = model_output[0][0]  # Shape: (2,)
probs = stable_softmax(logits)
prob_real = probs[0]  # Class 0 = REAL
prob_fake = probs[1]  # Class 1 = FAKE
```

### Risk Score Calculation

```python
risk_score = prob_fake * 100.0

if prob_fake > prob_real:
    classification = "MANIPULATED"
else:
    classification = "AUTHENTIC"

# Confidence levels
max_prob = max(prob_real, prob_fake)
if max_prob >= 0.85:
    confidence = "HIGH"
elif max_prob >= 0.65:
    confidence = "MEDIUM"
else:
    confidence = "LOW"
```

### Output Format

```json
{
  "analysis_type": "temporal_3dcnn",
  "risk_score": 85.23,
  "classification": "MANIPULATED",
  "confidence": "HIGH",
  "prediction": {
    "fake_probability": 0.8523,
    "real_probability": 0.1477
  },
  "frames_analyzed": 16,
  "method": "3D CNN Temporal Analysis"
}
```

---

## 🔬 Model 3: Forensic Analyzer

### Overview

| Property | Value |
|----------|-------|
| **Type** | Signal Processing (No ML) |
| **Analyses** | ELA, Frequency Spectrum |
| **Output** | Plots + Features |

### ELA (Error Level Analysis)

```python
# Algorithm
1. Save image as JPEG at quality=90
2. Reload the compressed image
3. Calculate absolute difference: |original - recompressed|
4. Enhance contrast for visualization
5. Generate heatmap (red = high error = manipulation)

# Interpretation
- Uniform ELA = likely authentic
- Varied ELA regions = possible manipulation
```

### Frequency Spectrum Analysis

```python
# Algorithm
1. Convert to grayscale
2. Apply 2D Fast Fourier Transform (FFT)
3. Shift zero-frequency to center
4. Calculate magnitude spectrum
5. Apply log transform for visualization

# Interpretation
- Natural images have organic frequency distribution
- AI-generated images show unnatural patterns
- GAN artifacts appear as grid patterns
```

### Output Format

```json
{
  "prediction": {
    "fake_probability": 0.5,   // Neutral if no ONNX model
    "real_probability": 0.5
  },
  "plots": {
    "ela": "base64_encoded_jpeg...",
    "spectrum": "base64_encoded_jpeg..."
  },
  "features": {
    "ela_mean": 45.2,
    "ela_std": 23.1,
    "spectrum_energy": 0.87
  },
  "details": {
    "ela_explanation": "ELA shows uniform error levels",
    "spectrum_explanation": "Natural frequency distribution"
  }
}
```

---

## ⚖️ Model 4: Fusion Engine

### Signal Fusion Logic

```python
# Image analysis fusion
def fuse_image_signals(visual_result, forensic_result):
    # Weight configuration
    visual_weight = 0.70    # ViT model (primary)
    forensic_weight = 0.30  # Forensic (secondary)
    
    # Extract scores
    visual_score = visual_result['prediction']['fake_probability']
    forensic_score = forensic_result['prediction']['fake_probability']
    
    # Only include forensic if not neutral (0.5)
    if abs(forensic_score - 0.5) < 0.01:
        # Forensic model not loaded, use visual only
        final_score = visual_score
    else:
        # Weighted average
        final_score = (visual_score * visual_weight) + 
                      (forensic_score * forensic_weight)
    
    risk_score = final_score * 100.0
    return risk_score
```

### Enhanced Mode Weights

```python
# Advanced/Enhanced mode ensemble (advanced.py)
WEIGHTS = {
    "nvidia_hive": 0.30,     # 30%
    "huggingface": 0.35,     # 35%
    "local_ensemble": 0.35   # 35%
}
```

---

## 🌐 API Endpoints Reference

### Standard Endpoints

| Endpoint | Method | Input | Output |
|----------|--------|-------|--------|
| `/api/v1/analyze/image/` | POST | Image file | ImageAnalysisResponse |
| `/api/v1/analyze/video/` | POST | Video file | VideoAnalysisResponse |
| `/api/v1/analyze/audio/` | POST | Audio file | AudioAnalysisResponse |

### Enhanced Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/analyze/advanced/image/` | POST | NVIDIA + HF + Local |
| `/api/v1/analyze/advanced/video/` | POST | NVIDIA + HF + Temporal |
| `/api/v1/analyze/advanced/status` | GET | Check API availability |

---

## 🔐 Critical File Checksums

To verify file integrity before/after changes:

```powershell
# Generate checksums
Get-FileHash -Algorithm SHA256 "D:\Deepway\backend\app\services\visual_detector.py"
Get-FileHash -Algorithm SHA256 "D:\Deepway\backend\app\services\temporal_detector.py"
Get-FileHash -Algorithm SHA256 "D:\Deepway\backend\app\services\forensic_analyzer.py"
Get-FileHash -Algorithm SHA256 "D:\Deepway\backend\app\services\fusion_engine.py"
Get-FileHash -Algorithm SHA256 "D:\Deepway\Models\best_deepfake_model.pt"
```

---

## 🔄 Rollback Procedures

### Scenario 1: New Service Breaks App

**Symptoms**: App crashes, 500 errors, visual_detector not loading

**Fix**:
```powershell
# 1. Stop backend
taskkill /F /IM python.exe

# 2. Remove new service imports from main.py
# (Only remove lines added for new services)

# 3. Remove new route registrations from routes.py
# (Only remove new router.include_router lines)

# 4. Restart
python -m uvicorn app.main:app --reload
```

### Scenario 2: Model File Corrupted

**Symptoms**: Model loading errors, wrong predictions

**Fix**:
```powershell
# Model files are NEVER modified
# Just verify they exist:
Test-Path "D:\Deepway\Models\best_deepfake_model.pt"
Test-Path "D:\Deepway\Models\Temporal_deepfake_Video.onnx"
```

### Scenario 3: Complete Rollback

**To restore to current working state:**

1. **Files to KEEP (core system)**:
   ```
   backend/app/services/
     visual_detector.py
     temporal_detector.py
     forensic_analyzer.py
     fusion_engine.py
     explainer.py
     audio_detector.py
     nvidia_hive.py
     advanced_analytics.py
   
   backend/app/api/
     image.py
     video.py
     audio.py
     advanced.py
     report.py
     routes.py
   
   backend/app/database/
     connection.py
     storage.py
   ```

2. **Files to REMOVE (new additions)**:
   ```
   backend/app/services/
     face_recognition.py     # DELETE
     liveness_detector.py    # DELETE
     age_estimator.py        # DELETE
     id_matcher.py           # DELETE
   
   backend/app/api/
     face.py                 # DELETE
     liveness.py             # DELETE
     age.py                  # DELETE
   
   frontend/src/pages/
     FaceMatchPage.tsx       # DELETE
     LivenessPage.tsx        # DELETE
     AgeEstimatePage.tsx     # DELETE
   ```

3. **Revert routes.py**:
   - Remove any new `router.include_router()` lines
   - Keep original 5 routers only

4. **Revert main.py**:
   - Remove new service imports
   - Remove new initialization code

### Scenario 4: Frontend Only Rollback

**If new pages break navigation:**

```powershell
# 1. Restore App.tsx routes to only include:
#    - "/" → HomePage
#    - "/analyze" → AnalyzePage

# 2. Delete new page files from frontend/src/pages/

# 3. Rebuild
cd frontend
npm run dev
```

---

## ✅ Pre-Upgrade Checklist

Before adding new services, verify:

- [ ] Backend starts without errors
- [ ] Image analysis returns correct results
- [ ] Video analysis returns correct results
- [ ] MongoDB is connected
- [ ] All model files exist in D:\Deepway\Models\

**Test command**:
```powershell
cd D:\Deepway\backend
python test_api.py
# Should output: Risk Score > 80 for test image
```

---

*This document serves as the definitive reference for the current working state. Use it to verify system health and perform rollbacks if needed.*
