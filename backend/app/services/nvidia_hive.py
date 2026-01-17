"""
NVIDIA Hive Deepfake Detection Service
Uses EfficientNet-B4 + YOLOv8 for face detection and deepfake classification
Cloud API - requires NVIDIA API key
"""
import requests
import base64
import os
import cv2
import numpy as np
import tempfile
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class NvidiaHiveService:
    """
    NVIDIA Hive Deepfake Detection API integration.
    
    Features:
    - EfficientNet-B4 backbone
    - YOLOv8 face detection
    - Per-face deepfake classification
    - Supports both images and video frames
    """
    
    API_URL = "https://ai.api.nvidia.com/v1/cv/hive/deepfake-image-detection"
    MODEL_NAME = "NVIDIA-Hive (EfficientNet-B4)"
    
    def __init__(self):
        self.api_key = os.environ.get("NVIDIA_API_KEY")
        self._available = False
        
    def load(self) -> bool:
        """Initialize the service."""
        if not self.api_key:
            logger.warning("NVIDIA_API_KEY not set - NVIDIA Hive unavailable")
            return False
        
        self._available = True
        logger.info("NVIDIA Hive Deepfake Detection initialized")
        return True
    
    def is_available(self) -> bool:
        return self._available
    
    def _encode_image(self, image_path: str) -> tuple:
        """Encode image file to base64."""
        with open(image_path, "rb") as f:
            image_data = f.read()
        
        ext = os.path.splitext(image_path)[1].lower()
        content_type = {
            ".png": "image/png",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg"
        }.get(ext, "image/jpeg")
        
        image_b64 = base64.b64encode(image_data).decode("utf-8")
        return image_b64, content_type
    
    def _encode_numpy_image(self, image: np.ndarray) -> tuple:
        """Encode numpy array (RGB) to base64 PNG (Lossless)."""
        # Convert RGB to BGR for OpenCV
        bgr_image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        
        # Encode to PNG for maximum quality (lossless)
        # This prevents compression artifacts from affecting detection
        success, buffer = cv2.imencode('.png', bgr_image)
        
        if not success:
            # Fallback to High Quality JPEG if PNG fails
            logger.warning("PNG encoding failed, falling back to JPEG 100")
            _, buffer = cv2.imencode('.jpg', bgr_image, [int(cv2.IMWRITE_JPEG_QUALITY), 100])
            ext = "image/jpeg"
        else:
            ext = "image/png"
            
        image_b64 = base64.b64encode(buffer).decode("utf-8")
        
        return image_b64, ext
    
    def _call_api(self, image_b64: str, content_type: str) -> Dict[str, Any]:
        """Make API request to NVIDIA Hive."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json",
        }
        
        payload = {
            "input": [f"data:{content_type};base64,{image_b64}"]
        }
        
        try:
            response = requests.post(
                self.API_URL,
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"NVIDIA API error: {response.status_code} - {response.text}")
                return {"error": f"API error: {response.status_code}"}
                
        except Exception as e:
            logger.error(f"NVIDIA API request failed: {e}")
            return {"error": str(e)}
    
    def _parse_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Parse API response into standard format."""
        if "error" in response:
            return response
        
        faces = []
        max_deepfake_score = 0.0
        
        if "data" in response:
            for item in response["data"]:
                if "bounding_boxes" in item:
                    for i, bbox in enumerate(item["bounding_boxes"]):
                        vertices = bbox.get("vertices", [])
                        is_deepfake = bbox.get("is_deepfake", 0)
                        bbox_conf = bbox.get("bbox_confidence", 0)
                        
                        # Track highest deepfake score
                        max_deepfake_score = max(max_deepfake_score, is_deepfake)
                        
                        # Extract bbox coordinates
                        if len(vertices) >= 2:
                            x1, y1 = vertices[0].get("x", 0), vertices[0].get("y", 0)
                            x2, y2 = vertices[1].get("x", 0), vertices[1].get("y", 0)
                            bbox_coords = [int(x1), int(y1), int(x2), int(y2)]
                        else:
                            bbox_coords = [0, 0, 0, 0]
                        
                        faces.append({
                            "face_id": i,
                            "bbox": bbox_coords,
                            "detection_confidence": bbox_conf,
                            "deepfake_probability": is_deepfake,
                            "classification": "FAKE" if is_deepfake > 0.5 else "REAL"
                        })
        
        # Overall classification
        fake_prob = max_deepfake_score
        real_prob = 1.0 - fake_prob
        risk_score = fake_prob * 100
        
        if fake_prob >= 0.7:
            classification = "MANIPULATED"
            confidence = "HIGH"
        elif fake_prob >= 0.4:
            classification = "SUSPICIOUS"
            confidence = "MEDIUM"
        else:
            classification = "AUTHENTIC"
            confidence = "HIGH" if fake_prob < 0.1 else "MEDIUM"
        
        return {
            "model": self.MODEL_NAME,
            "faces_detected": len(faces),
            "face_predictions": faces,
            "prediction": {
                "fake_probability": round(fake_prob, 4),
                "real_probability": round(real_prob, 4)
            },
            "risk_score": round(risk_score, 2),
            "classification": classification,
            "confidence": confidence
        }
    
    def analyze_image(self, image_path: str) -> Dict[str, Any]:
        """Analyze image file for deepfake detection."""
        if not self._available:
            return {"error": "NVIDIA Hive not available", "available": False}
        
        try:
            image_b64, content_type = self._encode_image(image_path)
            response = self._call_api(image_b64, content_type)
            return self._parse_response(response)
        except Exception as e:
            logger.error(f"NVIDIA image analysis failed: {e}")
            return {"error": str(e)}
    
    def analyze_frame(self, frame: np.ndarray) -> Dict[str, Any]:
        """Analyze a single video frame (numpy RGB array)."""
        if not self._available:
            return {"error": "NVIDIA Hive not available", "available": False}
        
        try:
            image_b64, content_type = self._encode_numpy_image(frame)
            response = self._call_api(image_b64, content_type)
            return self._parse_response(response)
        except Exception as e:
            logger.error(f"NVIDIA frame analysis failed: {e}")
            return {"error": str(e)}
    
    def analyze_video(self, video_path: str, num_frames: int = 5) -> Dict[str, Any]:
        """
        Analyze video by extracting and analyzing key frames.
        
        Args:
            video_path: Path to video file
            num_frames: Number of frames to analyze (default 5 for API rate limits)
            
        Returns:
            Aggregated analysis results
        """
        if not self._available:
            return {"error": "NVIDIA Hive not available", "available": False}
        
        try:
            cap = cv2.VideoCapture(video_path)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            if total_frames == 0:
                return {"error": "Could not read video"}
            
            # Sample frames uniformly
            indices = np.linspace(0, total_frames - 1, num_frames, dtype=int)
            
            frame_results = []
            deepfake_scores = []
            
            for idx in indices:
                cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
                ret, frame = cap.read()
                
                if ret:
                    # Convert BGR to RGB
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    result = self.analyze_frame(frame_rgb)
                    
                    if "error" not in result:
                        frame_results.append({
                            "frame_index": int(idx),
                            "result": result
                        })
                        deepfake_scores.append(result["prediction"]["fake_probability"])
            
            cap.release()
            
            if not deepfake_scores:
                return {"error": "No frames could be analyzed"}
            
            # Aggregate results (use max score for safety)
            avg_score = np.mean(deepfake_scores)
            max_score = np.max(deepfake_scores)
            
            # Use max score for classification (conservative approach)
            fake_prob = max_score
            risk_score = fake_prob * 100
            
            if fake_prob >= 0.7:
                classification = "MANIPULATED"
                confidence = "HIGH"
            elif fake_prob >= 0.4:
                classification = "SUSPICIOUS"
                confidence = "MEDIUM"
            else:
                classification = "AUTHENTIC"
                confidence = "HIGH" if fake_prob < 0.1 else "MEDIUM"
            
            return {
                "model": self.MODEL_NAME,
                "frames_analyzed": len(frame_results),
                "frame_results": frame_results,
                "prediction": {
                    "fake_probability": round(fake_prob, 4),
                    "real_probability": round(1 - fake_prob, 4),
                    "avg_score": round(avg_score, 4),
                    "max_score": round(max_score, 4)
                },
                "risk_score": round(risk_score, 2),
                "classification": classification,
                "confidence": confidence
            }
            
        except Exception as e:
            logger.error(f"NVIDIA video analysis failed: {e}")
            return {"error": str(e)}


# Singleton
nvidia_hive = NvidiaHiveService()
