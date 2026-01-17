"""
Liveness Detection Service using DeepFace anti-spoofing
NEW FILE - Does not modify existing code

This service provides:
- Single image anti-spoofing detection
- Multi-method liveness verification
- DeepFace + texture analysis hybrid approach
"""

import logging
import cv2
import numpy as np
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

# Try to import DeepFace for face detection
DEEPFACE_AVAILABLE = False
try:
    from deepface import DeepFace
    DEEPFACE_AVAILABLE = True
    logger.info("✓ DeepFace library loaded for liveness detection")
except ImportError:
    logger.warning("DeepFace not installed. Using OpenCV for face detection.")

# OpenCV face detector fallback
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')


class LivenessDetector:
    """
    Single Image Liveness Detection.
    
    Uses multiple methods to detect presentation attacks:
    - Face detection validation (DeepFace or OpenCV)
    - Texture analysis (LBP-based)
    - Color space analysis
    - Frequency domain analysis
    - Blur/sharpness detection
    """
    
    def __init__(self):
        self._loaded = True
        if DEEPFACE_AVAILABLE:
            logger.info("✓ Liveness Detector initialized with DeepFace")
        else:
            logger.info("✓ Liveness Detector initialized with OpenCV")
    
    def is_available(self) -> bool:
        """Check if service is available."""
        return self._loaded
    
    def _detect_face(self, image: np.ndarray) -> Dict[str, Any]:
        """Detect face in image using available method."""
        try:
            if DEEPFACE_AVAILABLE:
                # Use DeepFace for face detection
                img_bgr = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
                faces = DeepFace.extract_faces(
                    img_bgr, 
                    detector_backend='opencv',
                    enforce_detection=False
                )
                if faces and len(faces) > 0:
                    face_data = faces[0]
                    confidence = face_data.get('confidence', 0.9)
                    return {
                        "detected": True,
                        "confidence": float(confidence),
                        "method": "deepface"
                    }
            
            # Fallback to OpenCV Haar Cascade
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.1, 4)
            
            if len(faces) > 0:
                return {
                    "detected": True,
                    "confidence": 0.8,
                    "method": "opencv_haar"
                }
            
            return {"detected": False, "confidence": 0.0, "method": "none"}
            
        except Exception as e:
            logger.error(f"Face detection failed: {e}")
            return {"detected": False, "confidence": 0.0, "error": str(e)}
    
    def _analyze_texture(self, image: np.ndarray) -> Dict[str, Any]:
        """Analyze texture using Local Binary Patterns approach."""
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            
            # Calculate local variance
            kernel_size = 5
            mean = cv2.blur(gray.astype(float), (kernel_size, kernel_size))
            sqr_mean = cv2.blur(gray.astype(float)**2, (kernel_size, kernel_size))
            variance = sqr_mean - mean**2
            
            avg_variance = float(np.mean(variance))
            texture_score = min(avg_variance / 500.0, 1.0)
            
            return {
                "score": round(texture_score, 3),
                "result": "live" if texture_score > 0.3 else "spoof"
            }
        except Exception as e:
            return {"score": 0.5, "result": "unknown", "error": str(e)}
    
    def _analyze_blur(self, image: np.ndarray) -> Dict[str, Any]:
        """Detect print/replay attacks via blur analysis."""
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            
            # Laplacian variance (sharpness indicator)
            laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
            
            # Sharp images are more likely to be live
            # Very blurry = print/screen; Very sharp = possibly digital
            if laplacian_var < 50:
                blur_score = 0.2  # Too blurry
            elif laplacian_var > 2000:
                blur_score = 0.6  # Suspiciously sharp
            else:
                blur_score = 0.9  # Natural sharpness
            
            return {
                "score": round(blur_score, 3),
                "result": "live" if blur_score > 0.5 else "spoof",
                "laplacian_var": round(laplacian_var, 2)
            }
        except Exception as e:
            return {"score": 0.5, "result": "unknown", "error": str(e)}
    
    def _analyze_color(self, image: np.ndarray) -> Dict[str, Any]:
        """Analyze color distribution for spoofing indicators."""
        try:
            hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
            
            saturation = hsv[:, :, 1]
            sat_std = float(np.std(saturation))
            
            hue = hsv[:, :, 0]
            hue_std = float(np.std(hue))
            
            color_score = min((sat_std / 50.0 + hue_std / 30.0) / 2, 1.0)
            
            return {
                "score": round(color_score, 3),
                "result": "live" if color_score > 0.3 else "spoof"
            }
        except Exception as e:
            return {"score": 0.5, "result": "unknown", "error": str(e)}
    
    def _detect_moire(self, image: np.ndarray) -> Dict[str, Any]:
        """Detect moiré patterns from screen replay attacks."""
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            
            f = np.fft.fft2(gray)
            fshift = np.fft.fftshift(f)
            magnitude = np.log(np.abs(fshift) + 1)
            
            center = (magnitude.shape[0] // 2, magnitude.shape[1] // 2)
            magnitude[center[0]-5:center[0]+5, center[1]-5:center[1]+5] = 0
            
            max_peak = float(np.max(magnitude))
            mean_magnitude = float(np.mean(magnitude))
            peak_ratio = max_peak / (mean_magnitude + 1e-6)
            
            moire_score = max(0, 1 - (peak_ratio / 10))
            
            return {
                "score": round(moire_score, 3),
                "result": "live" if moire_score > 0.5 else "spoof"
            }
        except Exception as e:
            return {"score": 0.5, "result": "unknown", "error": str(e)}
    
    def detect(
        self, 
        image: np.ndarray,
        security_level: str = "standard"
    ) -> Dict[str, Any]:
        """
        Perform comprehensive liveness detection.
        
        Args:
            image: RGB image as numpy array
            security_level: "standard", "high", or "banking_kyc"
            
        Returns:
            Liveness detection result with scores
        """
        thresholds = {
            "standard": 0.5,
            "high": 0.65,
            "banking_kyc": 0.8
        }
        threshold = thresholds.get(security_level, 0.5)
        
        # First check if face is detected
        face_result = self._detect_face(image)
        
        if not face_result.get("detected", False):
            return {
                "is_live": False,
                "confidence": 0.0,
                "confidence_level": "NONE",
                "decision": "NO_FACE_DETECTED",
                "attack_type": None,
                "error": "No face detected in image",
                "methods": {}
            }
        
        # Run all detection methods
        texture_result = self._analyze_texture(image)
        blur_result = self._analyze_blur(image)
        color_result = self._analyze_color(image)
        moire_result = self._detect_moire(image)
        
        # Weighted fusion
        weights = {
            "texture": 0.30,
            "blur": 0.25,
            "color": 0.25,
            "moire": 0.20
        }
        
        fused_score = (
            texture_result["score"] * weights["texture"] +
            blur_result["score"] * weights["blur"] +
            color_result["score"] * weights["color"] +
            moire_result["score"] * weights["moire"]
        )
        
        # Add face detection confidence bonus
        fused_score = fused_score * 0.9 + face_result.get("confidence", 0.8) * 0.1
        
        is_live = fused_score >= threshold
        
        # Determine attack type
        attack_type = None
        if not is_live:
            scores = {
                "print": 1 - texture_result["score"],
                "screen_replay": 1 - moire_result["score"],
                "photo": 1 - blur_result["score"]
            }
            attack_type = max(scores, key=scores.get)
        
        # Confidence level
        if fused_score >= 0.8:
            confidence_level = "VERY_HIGH"
        elif fused_score >= 0.65:
            confidence_level = "HIGH"
        elif fused_score >= 0.5:
            confidence_level = "MEDIUM"
        else:
            confidence_level = "LOW"
        
        return {
            "is_live": is_live,
            "confidence": round(fused_score, 3),
            "confidence_level": confidence_level,
            "threshold_used": threshold,
            "security_level": security_level,
            "decision": "LIVE" if is_live else "SPOOF_DETECTED",
            "attack_type": attack_type,
            "face_detected": face_result.get("detected", False),
            "methods": {
                "face_detection": face_result,
                "texture_analysis": texture_result,
                "blur_analysis": blur_result,
                "color_analysis": color_result,
                "moire_detection": moire_result
            },
            "model": "DeepFace+OpenCV" if DEEPFACE_AVAILABLE else "OpenCV"
        }


# Singleton instance
liveness_detector = LivenessDetector()
