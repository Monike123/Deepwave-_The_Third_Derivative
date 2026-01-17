# DeepFake Detection Platform - Project & UI/UX Implementation Plan

## 1. Project Overview
This project is a state-of-the-art Deepfake Detection platform that leverages a **"Grand Ensemble"** of detection technologies to provide the highest possible accuracy for Image, Video, and Audio analysis.

### Core Technologies
- **Frontend:** React, TypeScript, Tailwind CSS (Custom Animated UI).
- **Backend:** FastAPI (Python), OpenCV, PyTorch, ONNX Runtime.
- **AI Models:**
  - **NVIDIA Hive API:** Cloud-based foundation model (EfficientNet-B4 + YOLOv8).
  - **HuggingFace Transformers:** Cloud-based ensemble (DeepVision V2/V3).
  - **Local Models:**
    - **Visual:** EfficientNet-B0 (Tuned for deepfake artifacts).
    - **Temporal:** 3D CNN (ResNext) for video frame consistency.
    - **Forensic:** Frequency Domain Analysis (ELA + Spectrum).
    - **Audio:** AudioForensics-v2 (Local ONNX model).

### "Grand Ensemble" Architecture
For every analysis request, the system queries **ALL** available engines (Cloud + Local), normalizes their scores, and computes a weighted average. This robustness ensures that if one model fails (e.g., missed a subtle artifact), another will catch it.

---

## 2. UI/UX Overhaul Specification (Orange-Purple Theme)

The user interface is being upgraded to a **"Cyber-Forensic"** aesthetic using a vibrant Orange-to-Purple gradient palette (`#FF6B00` to `#7B1FA2`).

### Color Palette
- **Primary Gradient:** `linear-gradient(135deg, #FF6B00 0%, #7B1FA2 100%)`
- **Background:** Deep Void (`#05020A`) with Glassmorphism overlays.
- **Accents:** Neon Orange (`#FF9100`) for warnings/high risk, Neon Purple (`#D500F9`) for AI/Tech vibes.
- **Text:** White (`#FFFFFF`) and Gray-200 (`#E5E7EB`).

### Animations & Transitions
1.  **3D Loading State:** A "Scanning" animation where layer analyzes a wireframe face.
2.  **Page Transitions:** Smooth 3D scale/fade transitions between Home and Analyze pages.
3.  **Hover Effects:** "Holographic" lift effects on cards.
4.  **Glitch Text:** Subtle cyber-glitch effect on titles.

---

## 3. Implementation Steps

### Phase 1: Design System Update
- [ ] Update `index.css` with new CSS Variables.
- [ ] Create `animations.css` for keyframes (Float, Scan, Glitch).

### Phase 2: Component Upgrades
- [ ] **Header:** Glassmorphism with Gradient Border.
- [ ] **Home Page:** Hero section with 3D floating elements.
- [ ] **Analyze Page:**
    - New "Drag & Drop" zone with pulsing holographic border.
    - **Loading Screen:** Custom 3D Scanning animation (replacing simple spinner).
    - **Report Cards:** Glass cards with gradient reveal on hover.

### Phase 3: Verification
- [ ] Verify Mobile responsiveness.
- [ ] Ensure "Detailed Report" plots look good on dark theme.

## 4. Operation & Maintenance

### Running the Project
1.  **Backend:**
    ```bash
    cd backend
    pip install -r requirements.txt
    uvicorn app.main:app --reload
    ```
2.  **Frontend:**
    ```bash
    cd frontend
    npm install
    npm run dev
    ```

### Environment Variables
- `NVIDIA_API_KEY`: Required for Hive models.
- `HF_TOKEN`: Required for HuggingFace models.
- `MODELS_DIR`: Path to local ONNX models.

---

**Status:** Ready for Implementation.
