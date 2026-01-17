"""
Age Estimation API Endpoints
NEW FILE - Does not modify existing code

Provides:
- POST /estimate - Estimate age from face image
"""

import time
import uuid
import logging
from datetime import datetime
from typing import Tuple

import cv2
import numpy as np
from fastapi import APIRouter, File, UploadFile, HTTPException

from app.services.age_estimator import age_estimator
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
    """Check if Age Estimation service is available."""
    return {
        "service": "age_estimation",
        "available": age_estimator.is_available(),
        "output": "age_probability_distribution"
    }


@router.post("/estimate")
async def estimate_age(file: UploadFile = File(..., description="Face image")):
    """
    Estimate age from facial features.
    
    Analyzes facial features like skin texture and wrinkles to estimate
    apparent age. Returns a probability distribution over possible ages.
    """
    if not age_estimator.is_available():
        raise HTTPException(503, "Age Estimation service not available")
    
    start_time = time.time()
    
    try:
        image, raw_bytes = await load_image_from_upload(file)
        result = age_estimator.estimate(image)
        
        processing_time = int((time.time() - start_time) * 1000)
        
        response = {
            "request_id": str(uuid.uuid4()),
            "timestamp": datetime.utcnow().isoformat(),
            "service": "age_estimation",
            "filename": file.filename,
            "age_result": result,
            "processing_time_ms": processing_time
        }
        
        # Save to MongoDB
        await storage_service.save_biometric_data(
            service_type="age",
            image_bytes=raw_bytes,
            result=response,
            filename=file.filename or "capture.jpg"
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Age estimation failed: {e}", exc_info=True)
        raise HTTPException(500, f"Age estimation failed: {str(e)}")
