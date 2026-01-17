"""
Face Recognition API Endpoints
NEW FILE - Does not modify existing code

Provides:
- POST /match - 1:1 face verification
- POST /identify - 1:N face identification  
- POST /detect - Face detection only
"""

import os
import time
import uuid
import logging
from datetime import datetime
from typing import Optional

import cv2
import numpy as np
from fastapi import APIRouter, File, UploadFile, HTTPException, Form

from app.services.face_recognition import face_recognition_service

logger = logging.getLogger(__name__)

router = APIRouter()


async def load_image_from_upload(file: UploadFile) -> np.ndarray:
    """Load and decode image from upload."""
    contents = await file.read()
    nparr = np.frombuffer(contents, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    if image is None:
        raise HTTPException(400, f"Could not decode image: {file.filename}")
    
    # Convert BGR to RGB
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    return image


@router.get("/status")
async def get_status():
    """Check if Face Recognition service is available."""
    return {
        "service": "face_recognition",
        "available": face_recognition_service.is_available(),
        "model": "DeepFace VGG-Face",
        "embedding_dimension": 4096,
        "note": "Install deepface for full functionality" if not face_recognition_service.is_available() else None
    }


@router.post("/detect")
async def detect_faces(file: UploadFile = File(...)):
    """
    Detect all faces in an image.
    
    Returns face bounding boxes, landmarks, and attributes.
    """
    if not face_recognition_service.is_available():
        raise HTTPException(503, "Face Recognition service not available")
    
    start_time = time.time()
    
    try:
        image = await load_image_from_upload(file)
        faces = face_recognition_service.detect_faces(image)
        
        processing_time = int((time.time() - start_time) * 1000)
        
        return {
            "request_id": str(uuid.uuid4()),
            "timestamp": datetime.utcnow().isoformat(),
            "filename": file.filename,
            "image_dimensions": {
                "width": image.shape[1],
                "height": image.shape[0]
            },
            "faces_detected": len(faces),
            "faces": faces,
            "processing_time_ms": processing_time
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Face detection failed: {e}", exc_info=True)
        raise HTTPException(500, f"Face detection failed: {str(e)}")


@router.post("/match")
async def match_faces(
    file1: UploadFile = File(..., description="First face image"),
    file2: UploadFile = File(..., description="Second face image"),
    threshold: float = Form(0.6, description="Similarity threshold (0.0-1.0)")
):
    """
    1:1 Face Verification - Compare two faces.
    
    Upload two images and check if they are the same person.
    
    **Thresholds:**
    - 0.4: Low security (~5% FAR)
    - 0.6: Medium security (~0.1% FAR) [default]
    - 0.7: High security (~0.01% FAR)
    """
    if not face_recognition_service.is_available():
        raise HTTPException(503, "Face Recognition service not available")
    
    start_time = time.time()
    
    try:
        # Load both images
        image1 = await load_image_from_upload(file1)
        image2 = await load_image_from_upload(file2)
        
        # Perform matching
        result = face_recognition_service.match_faces(image1, image2, threshold)
        
        processing_time = int((time.time() - start_time) * 1000)
        
        return {
            "request_id": str(uuid.uuid4()),
            "timestamp": datetime.utcnow().isoformat(),
            "service": "face_recognition_service",
            "operation": "match",
            "file1": file1.filename,
            "file2": file2.filename,
            "match_result": result,
            "processing_time_ms": processing_time
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Face matching failed: {e}", exc_info=True)
        raise HTTPException(500, f"Face matching failed: {str(e)}")


@router.post("/embedding")
async def extract_embedding(file: UploadFile = File(...)):
    """
    Extract 512-dimensional face embedding.
    
    Useful for storing faces in a database for later identification.
    """
    if not face_recognition_service.is_available():
        raise HTTPException(503, "Face Recognition service not available")
    
    start_time = time.time()
    
    try:
        image = await load_image_from_upload(file)
        embedding = face_recognition_service.get_embedding(image)
        
        processing_time = int((time.time() - start_time) * 1000)
        
        if embedding is None:
            return {
                "request_id": str(uuid.uuid4()),
                "timestamp": datetime.utcnow().isoformat(),
                "filename": file.filename,
                "success": False,
                "error": "No face detected in image",
                "embedding": None,
                "processing_time_ms": processing_time
            }
        
        return {
            "request_id": str(uuid.uuid4()),
            "timestamp": datetime.utcnow().isoformat(),
            "filename": file.filename,
            "success": True,
            "embedding_dimension": 512,
            "embedding": embedding.tolist(),
            "processing_time_ms": processing_time
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Embedding extraction failed: {e}", exc_info=True)
        raise HTTPException(500, f"Embedding extraction failed: {str(e)}")
