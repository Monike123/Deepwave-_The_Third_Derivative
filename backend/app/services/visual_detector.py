"""
Visual Detector Service - Vision Transformer (ViT) Based Deepfake Detection
Model: google/vit-base-patch16-224-in21k fine-tuned on prithivMLmods/AI-vs-Deepfake-vs-Real
Classes: Artificial (0), Deepfake (1), Real (2)
"""
import torch
from transformers import AutoImageProcessor, AutoModelForImageClassification
from PIL import Image
import numpy as np
import logging
import os

logger = logging.getLogger(__name__)


class VisualDetector:
    """
    DeepVision Visual Detector - ViT based deepfake detection.
    
    Architecture: ViT-Base (Patch16, 224)
    Input: 224x224 RGB images
    Output: 3 Classes (Artificial, Deepfake, Real)
    
    Training Dataset: prithivMLmods/AI-vs-Deepfake-vs-Real
    Labels (alphabetical order from HuggingFace datasets):
        0: Artificial (AI Generated - Midjourney, DALL-E, etc.)
        1: Deepfake (Face swap on real person)
        2: Real (Authentic photograph)
    """
    
    MODEL_CHECKPOINT = "google/vit-base-patch16-224-in21k"
    MODEL_FILE = "best_deepfake_model.pt"
    
    # CRITICAL: Labels MUST match training dataset order
    # Dataset: prithivMLmods/AI-vs-Deepfake-vs-Real
    # features['label'].names returns alphabetical: ['Artificial', 'Deepfake', 'Real']
    LABELS = {
        0: "Artificial",  # AI Generated
        1: "Deepfake",    # Face swap
        2: "Real"         # Authentic
    }
    
    # Human-readable names for frontend
    DISPLAY_LABELS = {
        0: "AI Generated",
        1: "Deepfake",
        2: "Authentic"
    }

    def __init__(self):
        from app.config import settings
        self.models_dir = settings.MODELS_DIR
        self.model = None
        self.processor = None
        self.device = None
        self._loaded = False
        
        self.load_model()
        
    def load_model(self) -> bool:
        """Load the ViT model and custom-trained weights."""
        try:
            pt_path = os.path.join(self.models_dir, self.MODEL_FILE)
            if not os.path.exists(pt_path):
                logger.error(f"Model file not found: {pt_path}")
                return False

            # Force CPU for stability
            self.device = torch.device("cpu")
            logger.info(f"Loading ViT model on {self.device}...")

            # Initialize Processor (handles resize + normalize)
            # This uses the SAME preprocessing as training
            self.processor = AutoImageProcessor.from_pretrained(self.MODEL_CHECKPOINT)
            
            # Initialize Model Architecture
            self.model = AutoModelForImageClassification.from_pretrained(
                self.MODEL_CHECKPOINT,
                num_labels=3,
                id2label={str(k): v for k, v in self.LABELS.items()},
                label2id={v: str(k) for k, v in self.LABELS.items()},
                ignore_mismatched_sizes=True  # Classifier head size mismatch expected
            )

            # Load Custom Trained Weights
            logger.info(f"Loading weights from {pt_path}...")
            state_dict = torch.load(pt_path, map_location=self.device, weights_only=False)
            
            # Handle wrapped state_dict (e.g., from Trainer)
            if 'state_dict' in state_dict:
                state_dict = state_dict['state_dict']
            elif 'model_state_dict' in state_dict:
                state_dict = state_dict['model_state_dict']
            
            # Load weights (strict=False allows partial load)
            missing, unexpected = self.model.load_state_dict(state_dict, strict=False)
            if missing:
                logger.warning(f"Missing keys (expected for base model): {len(missing)}")
            if unexpected:
                logger.warning(f"Unexpected keys: {len(unexpected)}")
            
            self.model.to(self.device)
            self.model.eval()
            
            self._loaded = True
            logger.info(f"ViT Visual Detector loaded successfully")
            logger.info(f"  Classes: {list(self.LABELS.values())}")
            return True

        except Exception as e:
            logger.error(f"Failed to load ViT model: {e}", exc_info=True)
            return False

    def is_loaded(self) -> bool:
        return self._loaded

    def analyze(self, image: np.ndarray) -> dict:
        """
        Analyze image for deepfake detection using ViT.
        
        Args:
            image: RGB numpy array (H, W, 3) - OpenCV format (uint8)
            
        Returns:
            dict with classification results including:
            - risk_score: 0-100 (higher = more likely fake)
            - classification: 'AUTHENTIC', 'SUSPICIOUS', 'MANIPULATED'
            - detailed_label: 'Authentic', 'AI Generated', 'Deepfake'
            - prediction: probabilities for each class
        """
        if not self.is_loaded():
            logger.error("Model not loaded, returning error result")
            return {
                "error": "Model not loaded",
                "risk_score": 50.0,
                "classification": "UNKNOWN",
                "detailed_label": "Unknown",
                "confidence": "LOW",
                "prediction": {"fake_probability": 0.5, "real_probability": 0.5}
            }

        try:
            # Convert numpy (H, W, C) to PIL Image
            # OpenCV uses BGR, but we receive RGB from load_image_from_upload
            pil_image = Image.fromarray(image)
            
            # Preprocess using HuggingFace processor
            # This matches training: Resize(224) → ToTensor → Normalize
            inputs = self.processor(
                images=pil_image,
                return_tensors="pt",
                do_rescale=True,      # Scale 0-255 to 0-1
                do_normalize=True     # Apply mean/std normalization
            )
            
            # Move to device
            inputs = {k: v.to(self.device) for k, v in inputs.items()}

            # Inference
            with torch.no_grad():
                outputs = self.model(**inputs)
                logits = outputs.logits
                
                # Softmax for probabilities
                probs = torch.nn.functional.softmax(logits, dim=-1)[0]

            # Extract probabilities for each class
            prob_artificial = float(probs[0].cpu().item())  # AI Generated
            prob_deepfake = float(probs[1].cpu().item())    # Deepfake
            prob_real = float(probs[2].cpu().item())        # Real

            # Get predicted class
            predicted_class = int(torch.argmax(probs).cpu().item())
            
            # Calculate Risk Score
            # Risk = probability of NOT being real = prob_artificial + prob_deepfake
            fake_probability = prob_artificial + prob_deepfake
            risk_score = fake_probability * 100.0
            
            # Determine Classification
            if predicted_class == 2:  # Real
                classification = "AUTHENTIC"
                detailed_label = "Authentic"
            elif predicted_class == 0:  # Artificial/AI Generated
                classification = "MANIPULATED"
                detailed_label = "AI Generated"
            else:  # Deepfake
                classification = "MANIPULATED"
                detailed_label = "Deepfake"
            
            # Determine Confidence Level
            max_prob = max(prob_artificial, prob_deepfake, prob_real)
            if max_prob >= 0.85:
                confidence = "HIGH"
            elif max_prob >= 0.60:
                confidence = "MEDIUM"
            else:
                confidence = "LOW"

            logger.info(f"Analysis complete: {detailed_label} ({confidence} confidence, {risk_score:.1f}% risk)")

            return {
                "analysis_type": "vit_base_patch16_224",
                "risk_score": round(risk_score, 2),
                "confidence": confidence,
                "classification": classification,
                "detailed_label": detailed_label,
                "faces_detected": 1,  # ViT analyzes full image
                "prediction": {
                    "fake_probability": round(fake_probability, 4),
                    "real_probability": round(prob_real, 4),
                    "ai_generated_probability": round(prob_artificial, 4),
                    "deepfake_probability": round(prob_deepfake, 4)
                },
                "class_probabilities": {
                    "Artificial": round(prob_artificial, 4),
                    "Deepfake": round(prob_deepfake, 4),
                    "Real": round(prob_real, 4)
                }
            }

        except Exception as e:
            logger.error(f"Analysis failed: {e}", exc_info=True)
            return {
                "error": str(e),
                "risk_score": 50.0,
                "classification": "ERROR",
                "detailed_label": "Error",
                "confidence": "LOW",
                "prediction": {"fake_probability": 0.5, "real_probability": 0.5}
            }


# Singleton instance
visual_detector = VisualDetector()
