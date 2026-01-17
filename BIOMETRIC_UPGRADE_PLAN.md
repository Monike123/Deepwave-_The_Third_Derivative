# Deepway Biometric Platform Upgrade
## Detailed Implementation Specifications

---

> **Version**: 2.0.0 (Upgrade)  
> **Created**: January 17, 2026  
> **Type**: ADDITIVE ONLY - No modifications to existing code

---

## 📋 Table of Contents

1. [Upgrade Overview](#upgrade-overview)
2. [New Service Specifications](#new-service-specifications)
3. [Model Downloads Required](#model-downloads-required)
4. [Backend Implementation Details](#backend-implementation-details)
5. [Frontend Implementation Details](#frontend-implementation-details)
6. [Database Schema Additions](#database-schema-additions)
7. [API Specifications](#api-specifications)
8. [Rollback Instructions](#rollback-instructions)
9. [Testing Procedures](#testing-procedures)

---

## 🎯 Upgrade Overview

### What We're Adding

| Service | Model | Purpose | Complexity |
|---------|-------|---------|------------|
| Face Recognition | InsightFace ArcFace | 1:1 verification, 1:N search | Medium |
| Liveness Detection | Silent-Face | Anti-spoofing single image | Medium |
| Age Estimation | DEX VGG-16 | Estimate age from face | Low |
| Photo ID Matching | FaceNet + OCR | KYC identity verification | High |

### What We're NOT Touching

| Component | Status | Reason |
|-----------|--------|--------|
| `visual_detector.py` | PRESERVED | Working ViT deepfake detection |
| `temporal_detector.py` | PRESERVED | Working 3D CNN video analysis |
| `forensic_analyzer.py` | PRESERVED | Working ELA/Spectrum analysis |
| `fusion_engine.py` | PRESERVED | Working signal fusion |
| All existing API endpoints | PRESERVED | Production-ready |
| AnalyzePage.tsx | PRESERVED | Working UI |

---

## 🆕 New Service Specifications

### Service 1: Face Recognition

#### Model Details

```yaml
Model: InsightFace ArcFace (buffalo_l)
Repository: https://github.com/deepinsight/insightface
License: MIT (research), Commercial available
Download: pip install insightface

Architecture:
  - Detection: RetinaFace
  - Recognition: ResNet-100 with ArcFace loss
  
Embedding:
  - Dimension: 512
  - Similarity: Cosine distance
  
Input: 112 × 112 × 3 (RGB)
```

#### Functionality

```python
# 1:1 Face Matching
def match_faces(image1, image2):
    """
    Compare two faces and return similarity score.
    
    Returns:
        similarity: float (0.0 to 1.0)
        is_match: bool (similarity > threshold)
        threshold: typically 0.6
    """

# 1:N Face Identification
def identify_face(query_image, database):
    """
    Search face database for matches.
    
    Returns:
        matches: List[{person_id, similarity, metadata}]
    """

# Face Enrollment
def enroll_face(image, person_id, metadata):
    """
    Add face embedding to database.
    
    Stores:
        - 512-dim embedding vector
        - Person ID
        - Metadata (name, date, etc.)
    """
```

#### Thresholds

| Threshold | Use Case | False Accept Rate |
|-----------|----------|-------------------|
| 0.4 | Low security | ~5% |
| 0.6 | Medium security | ~0.1% |
| 0.7 | High security | ~0.01% |

---

### Service 2: Liveness Detection

#### Model Details

```yaml
Model: Silent-Face Anti-Spoofing
Repository: https://github.com/minivision-ai/Silent-Face-Anti-Spoofing
License: Apache 2.0
Download Size: ~20MB

Architecture: Multi-task CNN with auxiliary supervision
Input: 256 × 256 × 3 (RGB)
Output: [genuine_prob, spoof_prob]
```

#### Attack Types Detected

| Attack Type | Detection Method |
|-------------|------------------|
| Print Attack | Texture analysis, moiré detection |
| Screen Replay | Reflection patterns, color space |
| 3D Mask | Depth cues, skin texture |
| Paper Mask | Edge detection, flatness |

#### Detection Pipeline

```python
def detect_liveness(image):
    """
    Step 1: Face detection (RetinaFace)
    Step 2: Face alignment and crop
    Step 3: Multi-stream analysis:
        - RGB stream: Texture patterns
        - HSV stream: Color anomalies
        - Fourier stream: Frequency artifacts
    Step 4: Score fusion
    
    Returns:
        is_live: bool
        confidence: float
        attack_type: str (if detected)
        method_scores: dict
    """
```

#### Confidence Thresholds

| Level | Threshold | Use Case |
|-------|-----------|----------|
| Standard | 0.7 | General apps |
| High | 0.85 | Financial |
| Banking KYC | 0.95 | Identity verification |

---

### Service 3: Age Estimation

#### Model Details

```yaml
Model: DEX (Deep Expectation)
Paper: "DEX: Deep EXpectation of apparent age from a single image"
Repository: https://data.vision.ee.ethz.ch/cvl/rrothe/imdb-wiki/

Architecture: VGG-16 modified for age classification
Training Data: IMDB-WIKI (500K+ images)
Output: 101-class probability distribution (ages 0-100)
Accuracy: MAE ~3.2 years
```

#### Prediction Method

```python
def estimate_age(image):
    """
    The model outputs probability for each age 0-100.
    Final age = Expected value of distribution.
    
    Example:
        probs = [0.01, 0.02, ..., 0.15, 0.18, 0.12, ...]
                 age0   age1        age33  age34  age35
        
        estimated_age = sum(age * prob for age, prob in enumerate(probs))
        # e.g., 34.2 years
    
    Returns:
        estimated_age: float
        confidence_interval: (lower, upper)
        age_group: str ("20-30", "30-40", etc.)
        distribution: dict (age -> probability)
    """
```

---

### Service 4: Photo ID Matching

#### Pipeline Overview

```
┌─────────────────────────────────────────────────────────┐
│                   ID VERIFICATION PIPELINE               │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌─────────┐         ┌─────────────────────────────┐   │
│  │ Selfie  │         │      ID Document            │   │
│  │  Image  │         │  ┌─────┐ ┌───────────────┐  │   │
│  └────┬────┘         │  │Photo│ │ MRZ/Text Data │  │   │
│       │              │  └──┬──┘ └───────┬───────┘  │   │
│       │              └─────┼────────────┼──────────┘   │
│       │                    │            │              │
│       ▼                    ▼            ▼              │
│  ┌─────────┐         ┌─────────┐  ┌─────────┐         │
│  │ Face    │         │ Face    │  │  OCR    │         │
│  │Embedding│         │Embedding│  │ Extract │         │
│  └────┬────┘         └────┬────┘  └────┬────┘         │
│       │                   │            │              │
│       └───────────────────┼────────────┘              │
│                           ▼                           │
│                    ┌──────────────┐                   │
│                    │   MATCHING   │                   │
│                    │ Face + Data  │                   │
│                    └──────┬───────┘                   │
│                           │                           │
│                           ▼                           │
│                    ┌──────────────┐                   │
│                    │   DECISION   │                   │
│                    │  VERIFIED /  │                   │
│                    │  REJECTED    │                   │
│                    └──────────────┘                   │
└─────────────────────────────────────────────────────────┘
```

#### Components Required

| Component | Model/Tool | Purpose |
|-----------|------------|---------|
| Face Detection | RetinaFace | Find faces |
| Face Recognition | ArcFace | Compare faces |
| Document Detection | YOLOv8 (optional) | Locate ID boundaries |
| OCR | Tesseract 5 | Extract text |
| Liveness | Silent-Face | Verify selfie is live |

---

## 📥 Model Downloads Required

### Download Commands

```powershell
# 1. InsightFace (Face Recognition)
pip install insightface onnxruntime

# 2. Silent-Face (Liveness)
git clone https://github.com/minivision-ai/Silent-Face-Anti-Spoofing
# Copy models to D:\Deepway\Models\liveness\

# 3. DEX Age Estimation
# Download from: https://data.vision.ee.ethz.ch/cvl/rrothe/imdb-wiki/
# File: dex_imdb_wiki.caffemodel → convert to ONNX

# 4. Tesseract OCR
# Download installer from: https://github.com/tesseract-ocr/tesseract
```

### Model File Structure

```
D:\Deepway\Models\
├── best_deepfake_model.pt          # EXISTING - DO NOT TOUCH
├── Temporal_deepfake_Video.onnx    # EXISTING - DO NOT TOUCH
├── deepfake_3dcnn_final1.onnx.data # EXISTING - DO NOT TOUCH
│
├── face_recognition/               # NEW
│   └── buffalo_l/
│       ├── det_10g.onnx
│       └── w600k_r50.onnx
│
├── liveness/                       # NEW
│   ├── 2.7_80x80_MiniFASNetV2.pth
│   └── anti_spoof_models.yaml
│
└── age_estimation/                 # NEW
    └── dex_age.onnx
```

---

## 🔧 Backend Implementation Details

### New Files to Create

#### 1. `backend/app/services/face_recognition.py`

```python
"""
Face Recognition Service using InsightFace ArcFace
NEW FILE - Does not modify existing code
"""

import insightface
from insightface.app import FaceAnalysis
import numpy as np

class FaceRecognitionService:
    def __init__(self):
        self.app = None
        self._loaded = False
    
    def load_model(self):
        """Load InsightFace models"""
        self.app = FaceAnalysis(
            name='buffalo_l',
            providers=['CPUExecutionProvider']
        )
        self.app.prepare(ctx_id=0, det_size=(640, 640))
        self._loaded = True
    
    def get_embedding(self, image) -> np.ndarray:
        """Extract 512-dim face embedding"""
        faces = self.app.get(image)
        if len(faces) == 0:
            return None
        return faces[0].embedding
    
    def compare_faces(self, emb1, emb2) -> float:
        """Calculate cosine similarity"""
        return np.dot(emb1, emb2) / (
            np.linalg.norm(emb1) * np.linalg.norm(emb2)
        )

# Singleton
face_recognition = FaceRecognitionService()
```

#### 2. `backend/app/services/liveness_detector.py`

```python
"""
Liveness Detection Service using Silent-Face
NEW FILE - Does not modify existing code
"""

import torch
import cv2
import numpy as np

class LivenessDetector:
    def __init__(self):
        self.model = None
        self._loaded = False
    
    def load_model(self):
        """Load Silent-Face model"""
        # Model loading code here
        self._loaded = True
    
    def detect(self, image) -> dict:
        """
        Detect if image shows live person.
        
        Returns:
            {
                "is_live": bool,
                "confidence": float,
                "attack_type": str or None,
                "methods": {...}
            }
        """
        pass

# Singleton
liveness_detector = LivenessDetector()
```

#### 3. `backend/app/services/age_estimator.py`

```python
"""
Age Estimation Service using DEX
NEW FILE - Does not modify existing code
"""

import onnxruntime as ort
import numpy as np

class AgeEstimator:
    def __init__(self):
        self.session = None
        self._loaded = False
    
    def estimate(self, image) -> dict:
        """
        Estimate age from face image.
        
        Returns:
            {
                "estimated_age": float,
                "confidence_interval": (float, float),
                "age_group": str,
                "distribution": dict
            }
        """
        pass

# Singleton
age_estimator = AgeEstimator()
```

### New API Endpoints

#### `backend/app/api/face.py`

```python
"""Face Recognition API - NEW FILE"""
from fastapi import APIRouter, File, UploadFile

router = APIRouter()

@router.post("/match")
async def match_faces(
    file1: UploadFile = File(...),
    file2: UploadFile = File(...)
):
    """1:1 Face verification"""
    pass

@router.post("/identify")
async def identify_face(
    file: UploadFile = File(...),
    database_id: str = "default"
):
    """1:N Face identification"""
    pass
```

#### `backend/app/api/liveness.py`

```python
"""Liveness Detection API - NEW FILE"""
from fastapi import APIRouter, File, UploadFile

router = APIRouter()

@router.post("/detect")
async def detect_liveness(
    file: UploadFile = File(...),
    security_level: str = "standard"
):
    """Single image liveness detection"""
    pass
```

#### `backend/app/api/age.py`

```python
"""Age Estimation API - NEW FILE"""
from fastapi import APIRouter, File, UploadFile

router = APIRouter()

@router.post("/estimate")
async def estimate_age(file: UploadFile = File(...)):
    """Estimate age from face"""
    pass
```

### Route Registration

**Modification to `routes.py`** (MINIMAL):

```python
# Add these lines AFTER existing routes
# (Keep all existing router.include_router calls)

from app.api import face, liveness, age

# NEW routes - add at end
router.include_router(face.router, prefix="/face", tags=["Face Recognition"])
router.include_router(liveness.router, prefix="/liveness", tags=["Liveness"])
router.include_router(age.router, prefix="/age", tags=["Age Estimation"])
```

---

## 🎨 Frontend Implementation Details

### New Pages to Create

| File | Route | Purpose |
|------|-------|---------|
| `FaceMatchPage.tsx` | `/face-match` | 1:1 face verification |
| `LivenessPage.tsx` | `/liveness` | Anti-spoofing check |
| `AgeEstimatePage.tsx` | `/age-estimate` | Age prediction |

### Route Updates to App.tsx

```tsx
// ADD these routes (keep existing)
<Route path="/face-match" element={<FaceMatchPage />} />
<Route path="/liveness" element={<LivenessPage />} />
<Route path="/age-estimate" element={<AgeEstimatePage />} />
```

### Updated HomePage with Service Cards

```tsx
// Update features array in HomePage.tsx
const services = [
  // EXISTING - KEEP
  { name: "Deepfake Detection", path: "/analyze", icon: "🔍" },
  
  // NEW - ADD
  { name: "Face Recognition", path: "/face-match", icon: "👤" },
  { name: "Liveness Detection", path: "/liveness", icon: "✓" },
  { name: "Age Estimation", path: "/age-estimate", icon: "🎂" },
];
```

---

## 🗄️ Database Schema Additions

### New Collections (MongoDB)

```javascript
// Face Embeddings - for 1:N search
db.createCollection("face_embeddings", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["person_id", "embedding"],
      properties: {
        person_id: { bsonType: "string" },
        name: { bsonType: "string" },
        embedding: { bsonType: "array" },  // 512 floats
        created_at: { bsonType: "date" },
        metadata: { bsonType: "object" }
      }
    }
  }
});

// Create index for efficient search
db.face_embeddings.createIndex({ "person_id": 1 });

// Liveness Checks
db.createCollection("liveness_checks");

// Age Estimations
db.createCollection("age_estimations");
```

---

## 🔄 Rollback Instructions

### Complete Rollback Procedure

If new services cause issues:

```powershell
# Step 1: Stop everything
taskkill /F /IM python.exe
taskkill /F /IM node.exe

# Step 2: Remove NEW files only (backend)
Remove-Item "D:\Deepway\backend\app\services\face_recognition.py"
Remove-Item "D:\Deepway\backend\app\services\liveness_detector.py"
Remove-Item "D:\Deepway\backend\app\services\age_estimator.py"
Remove-Item "D:\Deepway\backend\app\api\face.py"
Remove-Item "D:\Deepway\backend\app\api\liveness.py"
Remove-Item "D:\Deepway\backend\app\api\age.py"

# Step 3: Remove NEW files only (frontend)
Remove-Item "D:\Deepway\frontend\src\pages\FaceMatchPage.tsx"
Remove-Item "D:\Deepway\frontend\src\pages\LivenessPage.tsx"
Remove-Item "D:\Deepway\frontend\src\pages\AgeEstimatePage.tsx"

# Step 4: Revert routes.py to remove new includes
# (Manual edit required - remove the 3 new router.include_router lines)

# Step 5: Revert App.tsx to remove new routes
# (Manual edit required - remove the 3 new Route elements)

# Step 6: Restart
cd D:\Deepway\backend
python -m uvicorn app.main:app --reload

cd D:\Deepway\frontend
npm run dev
```

### Verify Rollback Success

```powershell
# Test original functionality
cd D:\Deepway\backend
python test_api.py

# Expected: Risk Score for test image should be ~82%
```

---

## ✅ Testing Procedures

### Pre-Implementation Test

```powershell
# Run before adding new code
cd D:\Deepway\backend
python test_api.py
# Record: Risk Score should be ~82%
```

### Post-Implementation Test

```powershell
# Run after adding new services
cd D:\Deepway\backend

# 1. Test original still works
python test_api.py
# Verify: Risk Score still ~82%

# 2. Test new services
python -c "from app.services.face_recognition import face_recognition; print('Face Recognition OK')"
python -c "from app.services.liveness_detector import liveness_detector; print('Liveness OK')"
python -c "from app.services.age_estimator import age_estimator; print('Age Estimator OK')"
```

---

## 📝 Implementation Checklist

### Phase 1: Preparation
- [ ] Backup current working state (git commit)
- [ ] Run pre-implementation tests
- [ ] Download required models

### Phase 2: Face Recognition
- [ ] Create `face_recognition.py`
- [ ] Create `api/face.py`
- [ ] Add route to `routes.py`
- [ ] Create `FaceMatchPage.tsx`
- [ ] Test original deepfake detection still works

### Phase 3: Liveness Detection
- [ ] Create `liveness_detector.py`
- [ ] Create `api/liveness.py`
- [ ] Add route to `routes.py`
- [ ] Create `LivenessPage.tsx`
- [ ] Test original deepfake detection still works

### Phase 4: Age Estimation
- [ ] Create `age_estimator.py`
- [ ] Create `api/age.py`
- [ ] Add route to `routes.py`
- [ ] Create `AgeEstimatePage.tsx`
- [ ] Test original deepfake detection still works

### Phase 5: Integration
- [ ] Update HomePage with new service cards
- [ ] Update navigation
- [ ] Run full test suite
- [ ] Document any issues

---

*This document provides the complete specification for upgrading Deepway while preserving all existing functionality.*
