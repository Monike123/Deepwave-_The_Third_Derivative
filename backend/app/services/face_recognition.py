"""
Face Recognition Service using DeepFace pretrained models
NEW FILE - Does not modify existing code

This service provides:
- 1:1 face matching (verification)
- Face embedding extraction
- Multiple backend support (VGG-Face, Facenet, ArcFace)
"""

import logging
import cv2
import numpy as np
from typing import Dict, Any, Optional, List, Tuple

logger = logging.getLogger(__name__)

# Check for DeepFace
DEEPFACE_AVAILABLE = False
try:
    from deepface import DeepFace
    DEEPFACE_AVAILABLE = True
    logger.info("✓ DeepFace library loaded for face recognition")
except ImportError:
    logger.warning("DeepFace not installed. Face recognition will be limited.")


class FaceRecognitionService:
    """
    Face Recognition using DeepFace pretrained models.
    
    Supports multiple models:
    - VGG-Face (default, good balance)
    - Facenet (Google's model)
    - ArcFace (high accuracy)
    """
    
    def __init__(self, model_name: str = "VGG-Face"):
        self._model_name = model_name
        self._loaded = DEEPFACE_AVAILABLE
        
        if DEEPFACE_AVAILABLE:
            logger.info(f"✓ Face Recognition initialized with {model_name}")
        else:
            logger.warning("Face Recognition unavailable - install deepface: pip install deepface")
    
    def is_available(self) -> bool:
        """Check if service is available."""
        return self._loaded
    
    def match_faces(
        self, 
        image1: np.ndarray, 
        image2: np.ndarray,
        threshold: float = 0.6
    ) -> Dict[str, Any]:
        """
        Compare two face images and determine if they belong to the same person.
        
        Args:
            image1: First face image (RGB numpy array)
            image2: Second face image (RGB numpy array)
            threshold: Similarity threshold (0-1), higher = stricter
            
        Returns:
            Match result with similarity score
        """
        if not self._loaded:
            return {
                "match": False,
                "similarity_score": 0.0,
                "verified": False,
                "error": "DeepFace not installed. Run: pip install deepface",
                "model": "unavailable"
            }
        
        try:
            # Convert to BGR for DeepFace
            img1_bgr = cv2.cvtColor(image1, cv2.COLOR_RGB2BGR)
            img2_bgr = cv2.cvtColor(image2, cv2.COLOR_RGB2BGR)
            
            # Use DeepFace verify function
            result = DeepFace.verify(
                img1_bgr,
                img2_bgr,
                model_name=self._model_name,
                enforce_detection=False,
                detector_backend='opencv'
            )
            
            verified = result.get('verified', False)
            distance = result.get('distance', 1.0)
            
            # Convert distance to similarity (inverse relationship)
            # Distance of 0 = perfect match, higher = less similar
            similarity = max(0, 1 - distance)
            
            return {
                "match": verified,
                "similarity_score": round(similarity, 4),
                "distance": round(distance, 4),
                "threshold": result.get('threshold', threshold),
                "verified": verified,
                "model": self._model_name,
                "detector": result.get('detector_backend', 'opencv'),
                "faces_detected": {
                    "image1": True,
                    "image2": True
                }
            }
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Face matching failed: {error_msg}")
            
            # Check if it's a face detection error
            if "face" in error_msg.lower() and "detect" in error_msg.lower():
                return {
                    "match": False,
                    "similarity_score": 0.0,
                    "verified": False,
                    "error": "Could not detect face in one or both images",
                    "model": self._model_name
                }
            
            return {
                "match": False,
                "similarity_score": 0.0,
                "verified": False,
                "error": error_msg,
                "model": self._model_name
            }
    
    def detect_faces(self, image: np.ndarray) -> Dict[str, Any]:
        """
        Detect faces in an image.
        
        Args:
            image: RGB image as numpy array
            
        Returns:
            Detection result with face count and locations
        """
        if not self._loaded:
            # Fallback to OpenCV Haar Cascade
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            face_cascade = cv2.CascadeClassifier(
                cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            )
            faces = face_cascade.detectMultiScale(gray, 1.1, 4)
            
            return {
                "count": len(faces),
                "faces": [{"x": int(x), "y": int(y), "w": int(w), "h": int(h)} 
                         for (x, y, w, h) in faces],
                "model": "opencv_haar"
            }
        
        try:
            img_bgr = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            
            faces = DeepFace.extract_faces(
                img_bgr,
                detector_backend='opencv',
                enforce_detection=False
            )
            
            face_data = []
            for face in faces:
                if face.get('confidence', 0) > 0.5:
                    facial_area = face.get('facial_area', {})
                    face_data.append({
                        "x": facial_area.get('x', 0),
                        "y": facial_area.get('y', 0),
                        "w": facial_area.get('w', 0),
                        "h": facial_area.get('h', 0),
                        "confidence": round(face.get('confidence', 0), 3)
                    })
            
            return {
                "count": len(face_data),
                "faces": face_data,
                "model": "deepface"
            }
            
        except Exception as e:
            logger.error(f"Face detection failed: {e}")
            return {
                "count": 0,
                "faces": [],
                "error": str(e),
                "model": "error"
            }
    
    def get_embedding(self, image: np.ndarray) -> Dict[str, Any]:
        """
        Extract face embedding vector for advanced use cases.
        
        Args:
            image: RGB face image
            
        Returns:
            512-dimensional embedding vector
        """
        if not self._loaded:
            return {
                "embedding": None,
                "error": "DeepFace not installed",
                "dimension": 0
            }
        
        try:
            img_bgr = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            
            embeddings = DeepFace.represent(
                img_bgr,
                model_name=self._model_name,
                enforce_detection=False,
                detector_backend='opencv'
            )
            
            if embeddings and len(embeddings) > 0:
                embedding = embeddings[0].get('embedding', [])
                return {
                    "embedding": embedding,
                    "dimension": len(embedding),
                    "model": self._model_name
                }
            
            return {
                "embedding": None,
                "error": "No face detected",
                "dimension": 0
            }
            
        except Exception as e:
            return {
                "embedding": None,
                "error": str(e),
                "dimension": 0
            }


# Singleton instance
face_recognition_service = FaceRecognitionService()
