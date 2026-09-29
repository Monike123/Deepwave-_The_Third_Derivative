"""
Forensic Analyzer Service.

Classification uses forensic_best.pth:
SRM high-pass + EfficientNet-B4 + GeM pooling, binary logit.
ELA and frequency-spectrum plots are always produced, even if the
checkpoint is missing.
"""
import base64
import logging
import os

import cv2
import numpy as np
import torch

from app.config import settings

logger = logging.getLogger(__name__)

# The checkpoint was trained on RGB tensors scaled to [0, 1].
# ImageNet mean/std makes the SRM front-end explode (logits in the tens of thousands).


class ForensicAnalyzer:
    """Frequency-domain plots plus the SRM EfficientNet-B4 classifier."""

    def __init__(self):
        self.model = None
        self.device = torch.device("cpu")
        self.image_size = 380  # EfficientNet-B4 native resolution
        self._loaded = False

    def load_model(self) -> bool:
        """Load forensic_best.pth. A second call does not reload the weights."""
        if self._loaded and self.model is not None:
            return True

        model_path = os.path.join(settings.MODELS_DIR, settings.FORENSIC_MODEL_PATH)
        if not os.path.exists(model_path):
            logger.warning(f"Forensic model not found at {model_path}")
            return False

        try:
            from app.services.forensic_net import ForensicNet

            net = ForensicNet()
            state = torch.load(model_path, map_location="cpu", weights_only=False)
            net.load_state_dict(state, strict=True)
            net.to(self.device)
            net.eval()
            self.model = net
            self._loaded = True
            logger.info(f"Forensic analyzer loaded from {model_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to load forensic analyzer: {e}", exc_info=True)
            self.model = None
            self._loaded = False
            return False

    def is_loaded(self) -> bool:
        return self._loaded and self.model is not None

    def _to_bgr(self, image: np.ndarray) -> np.ndarray:
        """API callers pass RGB uint8. OpenCV plot helpers expect BGR."""
        if image.ndim == 3 and image.shape[2] == 3:
            return cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        return image

    def _generate_ela(self, image_bgr: np.ndarray, quality: int = 90) -> str | None:
        """Generate Error Level Analysis (ELA) image."""
        try:
            _, buffer = cv2.imencode(".jpg", image_bgr, [cv2.IMWRITE_JPEG_QUALITY, quality])
            ela_img = cv2.imdecode(buffer, cv2.IMREAD_COLOR)
            diff = 15 * cv2.absdiff(image_bgr, ela_img)
            diff = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            diff = clahe.apply(diff)
            diff = cv2.applyColorMap(diff, cv2.COLORMAP_JET)
            _, buf = cv2.imencode(".jpg", diff)
            return base64.b64encode(buf).decode("utf-8")
        except Exception as e:
            logger.error(f"ELA generation failed: {e}")
            return None

    def _generate_spectrum_plot(self, img_gray: np.ndarray) -> str | None:
        """Generate visual frequency spectrum plot."""
        try:
            spectrum = np.fft.fftshift(np.fft.fft2(img_gray))
            magnitude = 20 * np.log(np.abs(spectrum) + 1e-8)
            mag_norm = cv2.normalize(magnitude, None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8U)
            mag_color = cv2.applyColorMap(mag_norm, cv2.COLORMAP_INFERNO)
            _, buf = cv2.imencode(".jpg", mag_color)
            return base64.b64encode(buf).decode("utf-8")
        except Exception as e:
            logger.error(f"Spectrum plot failed: {e}")
            return None

    def _predict(self, image_rgb: np.ndarray) -> float:
        """Return fake probability in [0, 1]."""
        resized = cv2.resize(image_rgb, (self.image_size, self.image_size), interpolation=cv2.INTER_AREA)
        tensor = torch.from_numpy(resized.astype(np.float32) / 255.0)
        tensor = tensor.permute(2, 0, 1).unsqueeze(0).to(self.device)
        with torch.no_grad():
            logit = self.model(tensor)
        return float(torch.sigmoid(logit).flatten()[0].item())

    def analyze(self, image: np.ndarray) -> dict:
        """
        Analyze an RGB image.

        Plots are returned even when the classifier checkpoint is missing.
        """
        try:
            image_bgr = self._to_bgr(image)
            img_gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
            ela_b64 = self._generate_ela(image_bgr)
            spectrum_b64 = self._generate_spectrum_plot(img_gray)
            plots = {"ela": ela_b64, "spectrum": spectrum_b64}

            if not self.is_loaded():
                return {
                    "risk_score": 50.0,
                    "prediction": {"fake_probability": 0.5, "real_probability": 0.5},
                    "classification": "UNKNOWN",
                    "method": "SRM + EfficientNet-B4",
                    "plots": plots,
                    "details": {
                        "ela_explanation": "Error Level Analysis generated (model missing for classification).",
                        "spectrum_explanation": "Frequency spectrum generated.",
                    },
                }

            fake_prob = self._predict(image)
            real_prob = 1.0 - fake_prob
            risk_score = fake_prob * 100.0
            return {
                "risk_score": round(risk_score, 2),
                "prediction": {
                    "fake_probability": round(fake_prob, 4),
                    "real_probability": round(real_prob, 4),
                },
                "classification": "MANIPULATED" if risk_score > 50 else "AUTHENTIC",
                "method": "SRM + EfficientNet-B4 + GeM",
                "plots": plots,
                "details": {
                    "ela_explanation": "Error Level Analysis shows compression artifact inconsistencies. High contrast areas indicate potential manipulation.",
                    "spectrum_explanation": "Frequency spectrum analysis detects upsampling artifacts common in GAN-generated faces.",
                },
            }
        except Exception as e:
            logger.error(f"Forensic analysis failed: {e}", exc_info=True)
            return {"error": str(e)}


forensic_analyzer = ForensicAnalyzer()
