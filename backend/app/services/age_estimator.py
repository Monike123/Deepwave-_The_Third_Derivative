"""
Age Estimation Service using DeepFace pretrained models
NEW FILE - Does not modify existing code

This service provides:
- Age estimation from facial features using pretrained models
- Age probability distribution
- Confidence intervals
"""

import logging
import cv2
import numpy as np
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

# Flag to track if DeepFace is available
DEEPFACE_AVAILABLE = False
analyze_func = None

try:
    from deepface import DeepFace
    DEEPFACE_AVAILABLE = True
    logger.info("✓ DeepFace library loaded for age estimation")
except ImportError:
    logger.warning("DeepFace not installed. Using fallback age estimation.")


class AgeEstimator:
    """
    Age Estimation from facial features.
    
    Uses DeepFace pretrained models (VGG-Face, Age model) for accurate
    age estimation. Falls back to basic CV analysis if DeepFace unavailable.
    """
    
    def __init__(self):
        self._loaded = True
        if DEEPFACE_AVAILABLE:
            logger.info("✓ Age Estimator initialized with DeepFace models")
        else:
            logger.info("✓ Age Estimator initialized with fallback CV methods")
    
    def is_available(self) -> bool:
        """Check if service is available."""
        return self._loaded
    
    def estimate(self, image: np.ndarray) -> Dict[str, Any]:
        """
        Estimate age from facial image using DeepFace pretrained model.
        
        Args:
            image: RGB face image as numpy array
            
        Returns:
            Age estimation with confidence interval
        """
        try:
            if DEEPFACE_AVAILABLE:
                return self._estimate_with_deepface(image)
            else:
                return self._estimate_fallback(image)
                
        except Exception as e:
            logger.error(f"Age estimation failed: {e}")
            return self._estimate_fallback(image)
    
    def _estimate_with_deepface(self, image: np.ndarray) -> Dict[str, Any]:
        """Use DeepFace pretrained model for age estimation."""
        try:
            # DeepFace expects BGR format, convert if RGB
            if len(image.shape) == 3 and image.shape[2] == 3:
                img_bgr = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            else:
                img_bgr = image
            
            # Analyze with DeepFace - uses pretrained age model
            result = DeepFace.analyze(
                img_bgr, 
                actions=['age'],
                enforce_detection=False,
                detector_backend='opencv'
            )
            
            # Handle list or dict result
            if isinstance(result, list):
                result = result[0]
            
            estimated_age = float(result.get('age', 30))
            
            # Generate distribution
            uncertainty = 4.0  # DeepFace is more accurate, ±4 years
            distribution = self._generate_age_distribution(estimated_age, uncertainty)
            
            # Calculate confidence interval (95%)
            lower_bound = max(0, estimated_age - 2 * uncertainty)
            upper_bound = min(100, estimated_age + 2 * uncertainty)
            
            # Determine age group
            age_group = self._get_age_group(estimated_age)
            
            return {
                "estimated_age": round(estimated_age, 1),
                "confidence_interval_95": {
                    "lower_bound": round(lower_bound, 1),
                    "upper_bound": round(upper_bound, 1)
                },
                "age_group": age_group,
                "uncertainty_years": uncertainty,
                "age_distribution": distribution,
                "model": "DeepFace-Age",
                "method": "pretrained_cnn"
            }
            
        except Exception as e:
            logger.warning(f"DeepFace estimation failed, using fallback: {e}")
            return self._estimate_fallback(image)
    
    def _estimate_fallback(self, image: np.ndarray) -> Dict[str, Any]:
        """Fallback estimation using CV techniques."""
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            
            # Simple texture analysis
            edges = cv2.Canny(cv2.GaussianBlur(gray, (3, 3), 0), 50, 150)
            edge_density = np.sum(edges > 0) / edges.size
            
            # Variance analysis
            kernel_size = 5
            mean = cv2.blur(gray.astype(float), (kernel_size, kernel_size))
            sqr_mean = cv2.blur(gray.astype(float)**2, (kernel_size, kernel_size))
            variance = float(np.mean(sqr_mean - mean**2))
            
            # Estimate age (rough approximation)
            base_age = 25.0
            wrinkle_factor = edge_density * 150
            texture_factor = min(variance / 40, 20)
            estimated_age = max(15, min(75, base_age + wrinkle_factor * 0.5 + texture_factor * 0.5))
            
            uncertainty = 8.0  # Higher uncertainty for fallback
            distribution = self._generate_age_distribution(estimated_age, uncertainty)
            
            return {
                "estimated_age": round(estimated_age, 1),
                "confidence_interval_95": {
                    "lower_bound": round(max(0, estimated_age - 2 * uncertainty), 1),
                    "upper_bound": round(min(100, estimated_age + 2 * uncertainty), 1)
                },
                "age_group": self._get_age_group(estimated_age),
                "uncertainty_years": uncertainty,
                "age_distribution": distribution,
                "model": "OpenCV-Fallback",
                "method": "texture_analysis",
                "note": "Install deepface for more accurate results: pip install deepface"
            }
        except Exception as e:
            return {
                "error": str(e),
                "estimated_age": 30.0,
                "age_group": "30-40",
                "model": "fallback_default"
            }
    
    def _generate_age_distribution(self, estimated_age: float, uncertainty: float) -> Dict[int, float]:
        """Generate probability distribution around estimated age."""
        distribution = {}
        for age in range(max(0, int(estimated_age - 15)), min(100, int(estimated_age + 15))):
            prob = np.exp(-0.5 * ((age - estimated_age) / uncertainty) ** 2)
            distribution[age] = round(prob, 4)
        
        total = sum(distribution.values())
        if total > 0:
            distribution = {k: round(v / total, 4) for k, v in distribution.items()}
        return distribution
    
    def _get_age_group(self, age: float) -> str:
        """Determine age group from estimated age."""
        if age < 20:
            return "Under 20"
        elif age < 30:
            return "20-30"
        elif age < 40:
            return "30-40"
        elif age < 50:
            return "40-50"
        elif age < 60:
            return "50-60"
        else:
            return "60+"


# Singleton instance
age_estimator = AgeEstimator()
