"""
Temporal Detector Service - 3D CNN Video Deepfake Detection
Model: SimpleTemporal3D (Custom 3D CNN)
Input: 16 frames, 112x112, RGB, normalized
Output: Binary (Real=0, Fake=1)
"""
import cv2
import numpy as np
import onnxruntime as ort
import os
import logging

from app.config import settings

logger = logging.getLogger(__name__)


class TemporalDetector:
    """
    Temporal Deepfake Detector using 3D CNN.
    
    Architecture: SimpleTemporal3D
    - 3x Conv3D layers with BatchNorm and MaxPool
    - AdaptiveAvgPool3d → Flatten → FC layers
    
    Input Specification:
    - Shape: (1, 3, 16, 112, 112) = (batch, channels, frames, height, width)
    - Frames: 16 uniformly sampled from video
    - Size: 112x112 RGB
    - Normalization: [0, 1] (divide by 255)
    
    Output:
    - Class 0: REAL
    - Class 1: FAKE
    """
    
    # CORRECT model filename
    MODEL_FILE = "Temporal_deepfake_Video.onnx"
    
    # Preprocessing constants (from training)
    NUM_FRAMES = 16
    FRAME_SIZE = (112, 112)  # (width, height)
    
    def __init__(self):
        self.model_path = os.path.join(settings.MODELS_DIR, self.MODEL_FILE)
        self.session = None
        self.input_name = None
        self.output_name = None
        self._loaded = False
        
        self._load_model()
    
    def _load_model(self):
        """Load ONNX model for temporal analysis."""
        try:
            if not os.path.exists(self.model_path):
                logger.error(f"Temporal model not found: {self.model_path}")
                return
            
            # Check for external data file (the ONNX references deepfake_3dcnn_final1.onnx.data)
            expected_data_file = os.path.join(settings.MODELS_DIR, "deepfake_3dcnn_final1.onnx.data")
            if not os.path.exists(expected_data_file):
                logger.error(f"ONNX external data file not found: {expected_data_file}")
                return
            
            # Use CPU only for stability
            providers = ['CPUExecutionProvider']
            
            logger.info(f"Loading Temporal Detector from {self.model_path}...")
            self.session = ort.InferenceSession(self.model_path, providers=providers)
            
            self.input_name = self.session.get_inputs()[0].name
            self.output_name = self.session.get_outputs()[0].name
            
            # Log input shape for verification
            input_shape = self.session.get_inputs()[0].shape
            logger.info(f"Temporal model input shape: {input_shape}")
            logger.info(f"Expected: [1, 3, 16, 112, 112]")
            
            self._loaded = True
            logger.info("Temporal Detector loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load temporal detector: {e}", exc_info=True)
            self.session = None
            self._loaded = False
    
    def load_model(self) -> bool:
        """Public method for startup check."""
        if not self._loaded:
            self._load_model()
        return self._loaded
    
    def is_loaded(self) -> bool:
        return self._loaded
    
    def _extract_frames(self, video_path: str) -> np.ndarray:
        """
        Extract exactly NUM_FRAMES frames uniformly from video.
        
        This matches the EXACT preprocessing from training:
        1. Sample 16 frames uniformly across video duration
        2. Resize to 112x112
        3. Convert BGR to RGB
        4. Normalize to [0, 1]
        5. Transpose to (C, T, H, W)
        6. Add batch dimension
        
        Returns:
            np.ndarray of shape (1, 3, 16, 112, 112)
        """
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            logger.error(f"Cannot open video: {video_path}")
            return None
        
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        if total_frames < self.NUM_FRAMES:
            logger.warning(f"Video has only {total_frames} frames, need {self.NUM_FRAMES}")
            # Will use available frames with repetition
        
        # Uniformly sample frame indices
        indices = np.linspace(0, max(total_frames - 1, 0), self.NUM_FRAMES, dtype=int)
        
        frames = []
        for idx in indices:
            cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
            ret, frame = cap.read()
            
            if not ret:
                # If frame read fails, duplicate last frame
                if frames:
                    frames.append(frames[-1].copy())
                else:
                    frames.append(np.zeros((self.FRAME_SIZE[1], self.FRAME_SIZE[0], 3), dtype=np.uint8))
                continue
            
            # Resize to 112x112
            frame = cv2.resize(frame, self.FRAME_SIZE)
            
            # Convert BGR to RGB
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            frames.append(frame)
        
        cap.release()
        
        # Ensure exactly NUM_FRAMES
        while len(frames) < self.NUM_FRAMES:
            frames.append(frames[-1].copy() if frames else np.zeros((112, 112, 3), dtype=np.uint8))
        
        frames = frames[:self.NUM_FRAMES]
        
        # Stack: (T, H, W, C) = (16, 112, 112, 3)
        video_data = np.array(frames, dtype=np.float32)
        
        # Normalize to [0, 1]
        video_data = video_data / 255.0
        
        # Transpose: (T, H, W, C) → (C, T, H, W) = (3, 16, 112, 112)
        video_data = np.transpose(video_data, (3, 0, 1, 2))
        
        # Add batch dimension: (1, 3, 16, 112, 112)
        video_data = np.expand_dims(video_data, axis=0)
        
        logger.debug(f"Preprocessed video shape: {video_data.shape}")
        
        return video_data
    
    def _stable_softmax(self, logits: np.ndarray) -> np.ndarray:
        """
        Numerically stable softmax (from training test code).
        """
        exp_logits = np.exp(logits - np.max(logits))
        return exp_logits / exp_logits.sum()
    
    def analyze(self, video_path: str) -> dict:
        """
        Analyze video for temporal deepfake detection.
        
        Args:
            video_path: Path to video file
            
        Returns:
            dict with:
            - risk_score: 0-100 (higher = more likely fake)
            - classification: 'AUTHENTIC' or 'MANIPULATED'
            - confidence: 'HIGH', 'MEDIUM', or 'LOW'
            - prediction: probabilities
        """
        if not self.is_loaded():
            logger.error("Temporal detector not loaded")
            return {
                "error": "Model not loaded",
                "risk_score": 50.0,
                "classification": "UNKNOWN",
                "confidence": "LOW",
                "prediction": {"fake_probability": 0.5, "real_probability": 0.5}
            }
        
        try:
            # Preprocess video
            logger.info(f"Preprocessing video for temporal analysis: {video_path}")
            input_tensor = self._extract_frames(video_path)
            
            if input_tensor is None:
                return {
                    "error": "Failed to extract frames",
                    "risk_score": 50.0,
                    "classification": "UNKNOWN"
                }
            
            # Run inference
            logger.info("Running temporal 3D CNN inference...")
            outputs = self.session.run(
                [self.output_name],
                {self.input_name: input_tensor}
            )
            
            # Get logits and apply softmax
            logits = outputs[0][0]  # Shape: (2,)
            probs = self._stable_softmax(logits)
            
            # Extract probabilities
            prob_real = float(probs[0])  # Class 0 = REAL
            prob_fake = float(probs[1])  # Class 1 = FAKE
            
            # Calculate risk score
            risk_score = prob_fake * 100.0
            
            # Determine classification
            if prob_fake > prob_real:
                classification = "MANIPULATED"
            else:
                classification = "AUTHENTIC"
            
            # Determine confidence
            max_prob = max(prob_real, prob_fake)
            if max_prob >= 0.85:
                confidence = "HIGH"
            elif max_prob >= 0.65:
                confidence = "MEDIUM"
            else:
                confidence = "LOW"
            
            logger.info(f"Temporal analysis: {classification} ({confidence}), Risk: {risk_score:.1f}%")
            
            return {
                "analysis_type": "temporal_3dcnn",
                "risk_score": round(risk_score, 2),
                "classification": classification,
                "confidence": confidence,
                "prediction": {
                    "fake_probability": round(prob_fake, 4),
                    "real_probability": round(prob_real, 4)
                },
                "frames_analyzed": self.NUM_FRAMES,
                "method": "3D CNN Temporal Analysis"
            }
            
        except Exception as e:
            logger.error(f"Temporal analysis failed: {e}", exc_info=True)
            return {
                "error": str(e),
                "risk_score": 50.0,
                "classification": "ERROR",
                "confidence": "LOW"
            }


# Singleton instance
temporal_detector = TemporalDetector()
