"""
Liveness Detection API Endpoints
NEW FILE - Does not modify existing code

Provides:
- POST /detect - Single image liveness detection
"""

import time
import uuid
import logging
from datetime import datetime
from typing import Tuple

import cv2
import numpy as np
from fastapi import APIRouter, File, UploadFile, HTTPException, Form

from app.services.liveness_detector import liveness_detector
from app.database.storage import storage_service

logger = logging.getLogger(__name__)

router = APIRouter()


async def load_image_from_upload(file: UploadFile) -> Tuple[np.ndarray, bytes]:
    """Load and decode image from upload. Returns (image_array, raw_bytes)."""
    contents = await file.read()
    nparr = np.frombuffer(contents, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    if image is None:
        raise HTTPException(400, f"Could not decode image: {file.filename}")
    
    # Convert BGR to RGB
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    return image, contents


@router.get("/status")
async def get_status():
    """Check if Liveness Detection service is available."""
    return {
        "service": "liveness_detection",
        "available": liveness_detector.is_available(),
        "methods": ["texture_analysis", "color_analysis", "moire_detection", "reflection_analysis"],
        "security_levels": ["standard", "high", "banking_kyc"]
    }


@router.post("/detect")
async def detect_liveness(
    file: UploadFile = File(..., description="Face image to analyze"),
    security_level: str = Form("standard", description="Security level: standard, high, banking_kyc")
):
    """
    Single Image Liveness Detection.
    
    Analyzes an image to determine if it shows a live person or a spoofed 
    representation (photo, screen, mask).
    
    **Security Levels:**
    - standard: General applications (threshold 0.5)
    - high: Financial services (threshold 0.65)
    - banking_kyc: Identity verification (threshold 0.8)
    """
    if not liveness_detector.is_available():
        raise HTTPException(503, "Liveness Detection service not available")
    
    start_time = time.time()
    
    try:
        image, raw_bytes = await load_image_from_upload(file)
        result = liveness_detector.detect(image, security_level)
        
        processing_time = int((time.time() - start_time) * 1000)
        
        response = {
            "request_id": str(uuid.uuid4()),
            "timestamp": datetime.utcnow().isoformat(),
            "service": "liveness_detection",
            "filename": file.filename,
            "liveness_result": result,
            "processing_time_ms": processing_time
        }
        
        # Save to MongoDB (async, don't wait)
        await storage_service.save_biometric_data(
            service_type="liveness",
            image_bytes=raw_bytes,
            result=response,
            filename=file.filename or "capture.jpg"
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Liveness detection failed: {e}", exc_info=True)
        raise HTTPException(500, f"Liveness detection failed: {str(e)}")

