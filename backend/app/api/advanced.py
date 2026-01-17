"""Advanced Analytics API endpoint using HuggingFace and NVIDIA Hive models."""
from fastapi import APIRouter, File, UploadFile, HTTPException, Query
from datetime import datetime
from typing import Optional
import uuid
import time
import tempfile
import os
import logging

from app.services.advanced_analytics import advanced_analytics
from app.services.nvidia_hive import nvidia_hive
from app.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/status")
async def get_advanced_status():
    """Check if Enhanced Detection services are available."""
    from app.services.vera_ai import vera_ai
    return {
        "huggingface_available": advanced_analytics.is_available(),
        "nvidia_hive_available": nvidia_hive.is_available(),
        "nvidia_model": nvidia_hive.MODEL_NAME,
        "hf_image_model": advanced_analytics.IMAGE_MODEL,
        "forensic_available": vera_ai.is_available(),
        "recommended": "nvidia" if nvidia_hive.is_available() else "huggingface"
    }


@router.post("/image/")
async def analyze_image_advanced(file: UploadFile = File(...)):
    """
    Analyze image using Enhanced AI Detection (NVIDIA Hive).
    
    Uses NVIDIA Hive with EfficientNet-B4 + YOLOv8.
    
    - **file**: Image file (JPEG, PNG)
    """
    start_time = time.time()
    
    if not nvidia_hive.is_available():
        raise HTTPException(
            503,
            "Enhanced AI not available. NVIDIA_API_KEY not set."
        )
    
    # Validate file
    if not file.filename:
        raise HTTPException(400, "No filename provided")
    
    ext = '.' + file.filename.rsplit('.', 1)[-1].lower() if '.' in file.filename else ''
    if ext not in ['.jpg', '.jpeg', '.png']:
        raise HTTPException(400, f"Unsupported format. Use JPG or PNG.")
    
    # Read and save temp file
    contents = await file.read()
    if len(contents) > settings.MAX_FILE_SIZE:
        raise HTTPException(413, "File too large")
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
        tmp.write(contents)
        tmp_path = tmp.name
    
    # Grand Ensemble: NVIDIA + HuggingFace + Local
    
    # Imports for local models
    try:
        import cv2
        import numpy as np
        from app.services.visual_detector import visual_detector
        from app.services.forensic_analyzer import forensic_analyzer
        from app.services.fusion_engine import fusion_engine
    except ImportError:
        logger.error("Could not import local services for ensemble")
    
    ensemble_scores = []
    signals = {}
    
    # 1. NVIDIA Hive
    if nvidia_hive.is_available():
        try:
            res_nv = nvidia_hive.analyze_image(tmp_path)
            if 'error' not in res_nv:
                score = res_nv.get('risk_score', 50)
                ensemble_scores.append(score)
                signals['nvidia_hive'] = {
                    'risk_score': score, 
                    'classification': res_nv.get('classification'),
                    'confidence': res_nv.get('confidence')
                }
        except Exception as e:
            logger.error(f"NVIDIA Hive failed in ensemble: {e}")

    # 2. HuggingFace
    if advanced_analytics.is_available():
        try:
            res_hf = advanced_analytics.analyze_image(tmp_path)
            if 'error' not in res_hf:
                score = res_hf.get('risk_score', 50)
                ensemble_scores.append(score)
                signals['huggingface'] = {
                    'risk_score': score,
                    'classification': res_hf.get('classification'),
                    'confidence': res_hf.get('confidence')
                }
        except Exception as e:
            logger.error(f"HF failed in ensemble: {e}")
            
    # 3. Local Models
    try:
        # Load image
        nparr = np.frombuffer(contents, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        vis_res = visual_detector.analyze(image)
        for_res = forensic_analyzer.analyze(image)
        local_fused = fusion_engine.fuse_image_signals(vis_res, for_res)
        
        score = local_fused.get('risk_score', 50)
        ensemble_scores.append(score)
        signals['local_ensemble'] = {
            'risk_score': score,
            'classification': local_fused.get('classification'),
            'confidence': local_fused.get('confidence'),
            'forensic_plots': for_res.get('plots', {}),
            'forensic_details': for_res.get('details', {})
        }
    except Exception as e:
        logger.error(f"Local analysis failed in ensemble: {e}")

    if not ensemble_scores:
        raise HTTPException(500, "All analysis methods failed")

    # Weighted Ensemble: NVIDIA=30%, HuggingFace=35%, Local=35%
    weighted_sum = 0.0
    total_weight = 0.0
    
    if 'nvidia_hive' in signals:
        nvidia_score = signals['nvidia_hive']['risk_score']
        weighted_sum += nvidia_score * 0.30  # 30% weight for NVIDIA
        total_weight += 0.30
    
    if 'huggingface' in signals:
        hf_score = signals['huggingface']['risk_score']
        weighted_sum += hf_score * 0.35  # 35% weight for HuggingFace
        total_weight += 0.35
    
    if 'local_ensemble' in signals:
        local_score = signals['local_ensemble']['risk_score']
        weighted_sum += local_score * 0.35  # 35% weight for Local
        total_weight += 0.35
    
    # Calculate weighted average
    if total_weight > 0:
        avg_risk = weighted_sum / total_weight
    else:
        avg_risk = sum(ensemble_scores) / len(ensemble_scores)
    
    # Classification
    if avg_risk >= 70:
        classification = "MANIPULATED"
    elif avg_risk >= 40:
        classification = "SUSPICIOUS"
    else:
        classification = "AUTHENTIC"
        
    processing_time = int((time.time() - start_time) * 1000)
    
    return {
        "analysis_id": str(uuid.uuid4()),
        "timestamp": datetime.utcnow().isoformat(),
        "media_type": "image",
        "filename": file.filename,
        "mode": "enhanced_ensemble",
        "model": "Ensemble (NVIDIA 30% + HF 35% + Local 35%)",
        "classification": classification,
        "confidence": "HIGH" if len(ensemble_scores) >= 2 else "MEDIUM",
        "risk_score": round(avg_risk, 2),
        "prediction": {
            "fake_probability": avg_risk / 100,
            "real_probability": 1 - (avg_risk / 100)
        },
        "signals": signals,
        "processing_time_ms": processing_time
    }
    
    # Cleanup temp file
    if os.path.exists(tmp_path):
        os.unlink(tmp_path)


@router.post("/compare/")
async def compare_analysis(file: UploadFile = File(...)):
    """
    Run both Basic and Advanced analytics and compare results.
    
    Returns side-by-side comparison of local models vs HuggingFace model.
    """
    start_time = time.time()
    
    # Validate
    if not file.filename:
        raise HTTPException(400, "No filename provided")
    
    ext = '.' + file.filename.rsplit('.', 1)[-1].lower() if '.' in file.filename else ''
    if ext not in settings.SUPPORTED_IMAGE_FORMATS:
        raise HTTPException(400, f"Unsupported format: {ext}")
    
    contents = await file.read()
    
    # Save temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
        tmp.write(contents)
        tmp_path = tmp.name
    
    try:
        import numpy as np
        import cv2
        from app.services.visual_detector import visual_detector
        from app.services.forensic_analyzer import forensic_analyzer
        from app.services.fusion_engine import fusion_engine
        
        # Load image for basic analysis
        nparr = np.frombuffer(contents, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Basic analysis
        visual_result = visual_detector.analyze(image)
        forensic_result = forensic_analyzer.analyze(image)
        basic_fused = fusion_engine.fuse_image_signals(visual_result, forensic_result)
        
        # Advanced analysis (if available)
        advanced_result = None
        if advanced_analytics.is_available():
            advanced_result = advanced_analytics.analyze_image(tmp_path)
        
        processing_time = int((time.time() - start_time) * 1000)
        
        return {
            "analysis_id": str(uuid.uuid4()),
            "timestamp": datetime.utcnow().isoformat(),
            "filename": file.filename,
            "comparison": {
                "basic": {
                    "classification": basic_fused['classification'],
                    "risk_score": basic_fused['risk_score'],
                    "confidence": basic_fused['confidence'],
                    "signals": basic_fused.get('signal_values', {})
                },
                "advanced": {
                    "available": advanced_analytics.is_available(),
                    "classification": advanced_result.get('classification') if advanced_result else None,
                    "risk_score": advanced_result.get('risk_score') if advanced_result else None,
                    "confidence": advanced_result.get('confidence') if advanced_result else None,
                    "model": advanced_analytics.IMAGE_MODEL
                }
            },
            "processing_time_ms": processing_time
        }
        
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)


@router.post("/audio/")
async def analyze_audio_advanced(file: UploadFile = File(...)):
    """
    Analyze audio using Enhanced settings.
    
    Currently uses the Local Audio Detector (DeepFake-Audio-v2) as the primary engine,
    as it provides the most reliable detection for synthetic voices.
    """
    start_time = time.time()
    
    # Imports
    from app.services.audio_detector import audio_detector
    
    # Validate
    if not file.filename:
        raise HTTPException(400, "No filename provided")
    
    ext = '.' + file.filename.rsplit('.', 1)[-1].lower() if '.' in file.filename else ''
    if ext not in settings.SUPPORTED_AUDIO_FORMATS:
        raise HTTPException(400, f"Unsupported format: {ext}")
    
    contents = await file.read()
    if len(contents) > settings.MAX_FILE_SIZE:
        raise HTTPException(413, "File too large")
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
        tmp.write(contents)
        tmp_path = tmp.name
    
    try:
        logger.info(f"Enhanced Audio Analytics (Using Local): {file.filename}")
        
        # Use Local Audio Detector
        if not audio_detector.is_loaded():
             audio_detector.load_model()
             
        result = audio_detector.analyze(tmp_path)
        
        if 'error' in result and not result.get('prediction'):
            raise HTTPException(500, f"Analysis failed: {result['error']}")
            
        prediction = result.get('prediction', {})
        synthetic_prob = prediction.get('synthetic_probability', 0.5)
        risk_score = synthetic_prob * 100
        
        processing_time = int((time.time() - start_time) * 1000)
        
        return {
            "analysis_id": str(uuid.uuid4()),
            "timestamp": datetime.utcnow().isoformat(),
            "media_type": "audio",
            "filename": file.filename,
            "mode": "enhanced_audio",
            "model": "AudioForensics-Local",
            "classification": result.get('classification', 'UNKNOWN'),
            "confidence": result.get('confidence', 'MEDIUM'),
            "risk_score": round(risk_score, 2),
            "prediction": {
                "fake_probability": synthetic_prob,
                "real_probability": 1.0 - synthetic_prob
            },
            "audio_features": result.get('audio_features', {}),
            "processing_time_ms": processing_time
        }
        
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)


@router.post("/video/")
async def analyze_video_advanced(
    file: UploadFile = File(...),
    max_frames: int = Query(5, ge=1, le=10, description="Max frames to analyze")
):
    """
    Analyze video using Enhanced AI Detection (NVIDIA Hive).
    
    Extracts key frames and analyzes each using NVIDIA Hive API.
    
    - **file**: Video file (MP4, AVI, MOV, WebM)
    - **max_frames**: Number of frames to analyze (1-10)
    """
    start_time = time.time()
    
    if not nvidia_hive.is_available():
        raise HTTPException(
            503,
            "Enhanced AI not available. NVIDIA_API_KEY not set."
        )
    
    if not file.filename:
        raise HTTPException(400, "No filename provided")
    
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ['.mp4', '.avi', '.mov', '.webm', '.mkv']:
        raise HTTPException(400, f"Unsupported video format: {ext}")
    
    contents = await file.read()
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
        tmp.write(contents)
        video_path = tmp.name
    
    # Grand Ensemble for Video
    
    # Imports for local models
    try:
        from app.services.temporal_detector import temporal_detector
    except ImportError:
        pass
        
    ensemble_scores = []
    signals = {}
    
    # 1. NVIDIA Hive
    if nvidia_hive.is_available():
        try:
            res_nv = nvidia_hive.analyze_video(video_path, num_frames=max_frames)
            if 'error' not in res_nv:
                score = res_nv.get('risk_score', 50)
                ensemble_scores.append(score)
                signals['nvidia_hive'] = {
                    'risk_score': score,
                    'classification': res_nv.get('classification')
                }
        except Exception as e:
            logger.error(f"NVIDIA Video failed: {e}")
            
    # 2. HuggingFace (Sample 3 frames)
    if advanced_analytics.is_available():
        try:
            import cv2
            import numpy as np
            cap = cv2.VideoCapture(video_path)
            total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            indices = np.linspace(0, total-1, 3, dtype=int)
            
            hf_scores = []
            for i in indices:
                cap.set(cv2.CAP_PROP_POS_FRAMES, i)
                ret, frame = cap.read()
                if ret:
                    # Save frame temp
                    with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tf:
                        cv2.imwrite(tf.name, frame)
                        tf_path = tf.name
                        
                    try:
                        res = advanced_analytics.analyze_image(tf_path)
                        if 'risk_score' in res:
                            hf_scores.append(res['risk_score'])
                    finally:
                        if os.path.exists(tf_path):
                            os.unlink(tf_path)
            cap.release()
            
            if hf_scores:
                avg_hf = sum(hf_scores) / len(hf_scores)
                ensemble_scores.append(avg_hf)
                signals['huggingface'] = {'risk_score': avg_hf, 'frames_sampled': len(hf_scores)}
                
        except Exception as e:
            logger.error(f"HF Video failed: {e}")
            
    # 3. Local Temporal Model
    try:
        res_temp = temporal_detector.analyze(video_path)
        if 'error' not in res_temp:
            score = res_temp.get('risk_score', 50)
            ensemble_scores.append(score)
            signals['local_temporal'] = {
                'risk_score': score,
                'classification': res_temp.get('classification')
            }
    except Exception as e:
        logger.error(f"Local Temporal failed: {e}")
        
    if not ensemble_scores:
        raise HTTPException(500, "All video analysis methods failed")
        
    # Weighted Ensemble: NVIDIA=30%, HuggingFace=35%, Local Temporal=35%
    weighted_sum = 0.0
    total_weight = 0.0
    
    if 'nvidia_hive' in signals:
        nvidia_score = signals['nvidia_hive']['risk_score']
        weighted_sum += nvidia_score * 0.30
        total_weight += 0.30
    
    if 'huggingface' in signals:
        hf_score = signals['huggingface']['risk_score']
        weighted_sum += hf_score * 0.35
        total_weight += 0.35
    
    if 'local_temporal' in signals:
        local_score = signals['local_temporal']['risk_score']
        weighted_sum += local_score * 0.35
        total_weight += 0.35
    
    if total_weight > 0:
        avg_risk = weighted_sum / total_weight
    else:
        avg_risk = sum(ensemble_scores) / len(ensemble_scores)
    
    if avg_risk >= 70:
        classification = "MANIPULATED"
    elif avg_risk >= 40:
        classification = "SUSPICIOUS"
    else:
        classification = "AUTHENTIC"
        
    processing_time = int((time.time() - start_time) * 1000)
    
    # Cleanup
    if os.path.exists(video_path):
        os.unlink(video_path)
        
    return {
        "analysis_id": str(uuid.uuid4()),
        "timestamp": datetime.utcnow().isoformat(),
        "media_type": "video",
        "filename": file.filename,
        "mode": "enhanced_ensemble",
        "model": "Ensemble (NVIDIA 30% + HF 35% + Local 35%)",
        "classification": classification,
        "confidence": "HIGH",
        "risk_score": round(avg_risk, 2),
        "prediction": {
            "fake_probability": avg_risk / 100,
            "real_probability": 1 - (avg_risk / 100)
        },
        "signals": signals,
        "processing_time_ms": processing_time
    }
