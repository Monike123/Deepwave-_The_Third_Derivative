"""Image analysis API endpoint."""
from fastapi import APIRouter, File, UploadFile, HTTPException, Request
from datetime import datetime
import numpy as np
import cv2
import uuid
import time
import logging

from app.services.visual_detector import visual_detector
from app.services.forensic_analyzer import forensic_analyzer
from app.services.fusion_engine import fusion_engine
from app.services.explainer import explainer
from app.models.response import ImageAnalysisResponse, FaceDetection, Explanation
from app.config import settings
from app.database.storage import storage_service

logger = logging.getLogger(__name__)
router = APIRouter()


def validate_image_file(file: UploadFile) -> None:
    """Validate uploaded image file."""
    if not file.filename:
        raise HTTPException(400, "No filename provided")
    
    ext = '.' + file.filename.rsplit('.', 1)[-1].lower() if '.' in file.filename else ''
    if ext not in settings.SUPPORTED_IMAGE_FORMATS:
        raise HTTPException(
            400, 
            f"Unsupported format. Supported: {settings.SUPPORTED_IMAGE_FORMATS}"
        )


async def load_image_from_upload(file: UploadFile) -> tuple:
    """Load image from upload file. Returns (image_array, raw_contents)."""
    contents = await file.read()
    
    if len(contents) > settings.MAX_FILE_SIZE:
        raise HTTPException(413, f"File too large. Max: {settings.MAX_FILE_SIZE // (1024*1024)}MB")
    
    # Decode image
    nparr = np.frombuffer(contents, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    if image is None:
        raise HTTPException(400, "Could not decode image")
    
    # Convert BGR to RGB
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    return image, contents


@router.post("/", response_model=ImageAnalysisResponse)
async def analyze_image(file: UploadFile = File(...), request: Request = None):
    """
    Analyze an image for deepfake detection.
    
    Uses an Ensemble of:
    1. Visual Xception Detector (Spatial RGB Expert)
    2. Forensic Classifier (Frequency Domain Expert)
    """
    start_time = time.time()
    
    # Validate file
    validate_image_file(file)
    
    # Load image (and keep raw contents for storage)
    image, file_contents = await load_image_from_upload(file)
    
    logger.info(f"Analyzing image: {file.filename}, shape: {image.shape}")
    
    # Get session info from request headers (if available)
    session_id = None
    if request:
        session_id = request.headers.get("X-Session-ID")
    
    # Save upload to database (async, non-blocking)
    upload_doc = None
    try:
        upload_doc = await storage_service.save_upload(
            file_content=file_contents,
            filename=file.filename or "unknown",
            content_type=file.content_type or "image/jpeg",
            session_id=session_id
        )
        if upload_doc:
            logger.info(f"Saved upload to database: {upload_doc['_id']}")
    except Exception as e:
        logger.warning(f"Failed to save upload to database: {e}")
    
    # 1. Run Visual Analysis (ViT)
    visual_result = visual_detector.analyze(image)
    
    # 2. Run Forensic Analysis
    forensic_result = forensic_analyzer.analyze(image)
    
    # 3. Fuse signals (Ensemble)
    fused_result = fusion_engine.fuse_image_signals(visual_result, forensic_result)
    
    # Generate explanation
    explanation_result = explainer.explain_image_result(
        visual_result, forensic_result, fused_result
    )
    
    # Build face detections
    face_detections = []
    if 'face_predictions' in visual_result:
        for fp in visual_result.get('face_predictions', []):
            face_detections.append(FaceDetection(
                face_id=fp.get('face_id', 0),
                bbox=fp.get('bbox', [0, 0, 0, 0]),
                detection_confidence=fp.get('detection_confidence', 0.0),
                fake_probability=fp.get('fake_probability')
            ))
    
    # Build signals dict
    signals = {}
    
    # Map fused result to 'local_ensemble' for frontend compatibility
    signals['local_ensemble'] = {
        'risk_score': fused_result['risk_score'],
        'classification': visual_result.get('detailed_label', fused_result['classification']),
        'forensic_plots': forensic_result.get('plots', {}),
        'forensic_details': forensic_result.get('details', {})
    }
    
    # Keep atomic signals if needed for debugging
    if visual_result.get('prediction'):
        signals['visual'] = {
            'score': visual_result['prediction'].get('fake_probability', 0.5),
            'weight': 0.7,
            'faces_detected': visual_result.get('faces_detected', 0),
            'analysis_type': visual_result.get('analysis_type', 'vit_base'),
            'class_probabilities': visual_result.get('class_probabilities', {})
        }
    
    if forensic_result.get('prediction'):
        signals['forensic'] = {
            'score': forensic_result['prediction'].get('fake_probability', 0.5),
            'weight': 0.3,
            'features': forensic_result.get('features', {})
        }
    
    processing_time = int((time.time() - start_time) * 1000)
    
    # Build response
    analysis_id = str(uuid.uuid4())
    
    response_data = {
        "analysis_id": analysis_id,
        "timestamp": datetime.utcnow(),
        "media_type": "image",
        "filename": file.filename or "unknown",
        "classification": fused_result['classification'],
        "confidence": fused_result['confidence'],
        "risk_score": fused_result['risk_score'],
        "prediction": {
            "fake_probability": fused_result['risk_score'] / 100.0,
            "real_probability": 1.0 - (fused_result['risk_score'] / 100.0)
        },
        "signals": signals,
        "face_detections": face_detections,
        "explanation": explanation_result,
        "processing_time_ms": processing_time
    }
    
    # Save analysis result to database
    if upload_doc:
        try:
            await storage_service.save_analysis_result(
                upload_id=upload_doc['_id'],
                result=response_data,
                mode="standard"
            )
            logger.info(f"Saved analysis result for upload: {upload_doc['_id']}")
        except Exception as e:
            logger.warning(f"Failed to save analysis result: {e}")
    
    return ImageAnalysisResponse(
        analysis_id=analysis_id,
        timestamp=response_data["timestamp"],
        media_type="image",
        filename=response_data["filename"],
        classification=response_data["classification"],
        confidence=response_data["confidence"],
        risk_score=response_data["risk_score"],
        prediction=response_data["prediction"],
        signals=signals,
        face_detections=face_detections,
        explanation=Explanation(**explanation_result),
        processing_time_ms=processing_time
    )
