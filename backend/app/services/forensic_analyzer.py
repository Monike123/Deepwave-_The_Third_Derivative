"""
Forensic Analyzer Service - Frequency Domain Analysis
"""
import cv2
import numpy as np
import onnxruntime as ort
import os
import joblib
import logging
import base64
from app.config import settings

logger = logging.getLogger(__name__)

class ForensicAnalyzer:
    """
    Analyzes images in the frequency domain (DCT/DFT) to detect
    GAN fingerprints and upsampling artifacts common in deepfakes.
    """
    
    def __init__(self):
        self.model_path = os.path.join(settings.MODELS_DIR, "forensic_classifier.onnx")
        self.scaler_path = os.path.join(settings.MODELS_DIR, "forensic_scaler.pkl")
        self.session = None
        self.scaler = None
        self.input_name = None
        self.output_name = None
        self._load_model()

    def _load_model(self):
        try:
            # Load ONNX model
            if not os.path.exists(self.model_path):
                logger.warning(f"Forensic model not found at {self.model_path}")
                return

            providers = ['CPUExecutionProvider'] # Force CPU for stability
            self.session = ort.InferenceSession(self.model_path, providers=providers)
            self.input_name = self.session.get_inputs()[0].name
            self.output_name = self.session.get_outputs()[0].name
            
            # Load Scaler
            if os.path.exists(self.scaler_path):
                self.scaler = joblib.load(self.scaler_path)
            
            logger.info(f"Forensic analyzer loaded from {self.model_path}")
            
        except Exception as e:
            logger.error(f"Failed to load forensic analyzer: {e}")
            self.session = None

    def load_model(self) -> bool:
        """Public method to load model (called by main.py on startup)."""
        if self.session is None:
            self._load_model()
        return self.session is not None

    def is_loaded(self) -> bool:
        return self.session is not None

    def azimuthalAverage(self, image, center=None):
        """
        Calculate the azimuthally averaged radial profile.
        image - The 2D image
        center - The [x,y] pixel coordinates used as the center. The default is 
             None, which then uses the center of the image
        """
        # Calculate the indices from the image
        y, x = np.indices(image.shape)

        if not center:
            center = np.array([(x.max()-x.min())/2.0, (y.max()-y.min())/2.0])

        r = np.hypot(x - center[0], y - center[1])

        # Get sorted radii
        ind = np.argsort(r.flat)
        r_sorted = r.flat[ind]
        i_sorted = image.flat[ind]

        # Get the integer part of the radii (bin size = 1)
        r_int = r_sorted.astype(int)

        # Find all pixels that fall within each radial bin.
        deltar = r_int[1:] - r_int[:-1]  # Assumes all radii represented
        rind = np.where(deltar)[0]       # location of changed radius
        nr = rind[1:] - rind[:-1]        # number of radius bin
        
        # Cumulative sum to figure out sums for each radius bin
        csim = np.cumsum(i_sorted, dtype=float)
        tbin = csim[rind[1:]] - csim[rind[:-1]]

        radial_prof = tbin / nr

        return radial_prof

    def extract_features(self, img_bgr):
        """Extract frequency domain features from image."""
        try:
            # Convert to grayscale
            img_gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
            
            # Resize
            h, w = img_gray.shape
            min_dim = min(h, w)
            if min_dim > 720: # Cap size for performance
                scale = 720 / min_dim
                img_gray = cv2.resize(img_gray, None, fx=scale, fy=scale)
            
            f = np.fft.fft2(img_gray)
            fshift = np.fft.fftshift(f)
            magnitude_spectrum = 20 * np.log(np.abs(fshift) + 1e-8)
            
            # Azimuthal average
            psd1D = self.azimuthalAverage(magnitude_spectrum)
            
            # Normalize to fixed length (e.g. 300 points)
            target_len = 300
            if len(psd1D) != target_len:
                psd1D = np.interp(np.linspace(0, len(psd1D), target_len), np.arange(len(psd1D)), psd1D)
            
            # Scale if scaler is available
            if self.scaler:
                psd1D = self.scaler.transform([psd1D])[0]
                
            return psd1D.astype(np.float32)
            
        except Exception as e:
            logger.error(f"Feature extraction failed: {e}")
            return None

    def _generate_ela(self, image: np.ndarray, quality: int = 90) -> str:
        """Generate Error Level Analysis (ELA) image."""
        try:
            _, buffer = cv2.imencode('.jpg', image, [cv2.IMWRITE_JPEG_QUALITY, quality])
            ela_img = cv2.imdecode(buffer, cv2.IMREAD_COLOR)
            
            diff = 15 * cv2.absdiff(image, ela_img)
            
            # Enhance contrast
            diff = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
            diff = clahe.apply(diff)
            diff = cv2.applyColorMap(diff, cv2.COLORMAP_JET)
            
            _, buf = cv2.imencode('.jpg', diff)
            return base64.b64encode(buf).decode('utf-8')
        except Exception as e:
            logger.error(f"ELA generation failed: {e}")
            return None

    def _generate_spectrum_plot(self, img_gray: np.ndarray) -> str:
        """Generate visual frequency spectrum plot."""
        try:
            f = np.fft.fft2(img_gray)
            fshift = np.fft.fftshift(f)
            magnitude_spectrum = 20 * np.log(np.abs(fshift) + 1e-8)
            
            # Normalize to 0-255
            mag_norm = cv2.normalize(magnitude_spectrum, None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8U)
            mag_color = cv2.applyColorMap(mag_norm, cv2.COLORMAP_INFERNO)
            
            _, buf = cv2.imencode('.jpg', mag_color)
            return base64.b64encode(buf).decode('utf-8')
        except Exception as e:
            logger.error(f"Spectrum plot failed: {e}")
            return None

    def analyze(self, image: np.ndarray) -> dict:
        """
        Analyze image for frequency anomalies and generate forensic report.
        """
        try:
            # Always generate visualizations
            import base64
            img_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            ela_b64 = self._generate_ela(image)
            spectrum_b64 = self._generate_spectrum_plot(img_gray)
            
            if not self.is_loaded():
                # Return neutral result but valid plots
                return {
                    "risk_score": 50.0,
                    "prediction": { "fake_probability": 0.5, "real_probability": 0.5 },
                    "classification": "UNKNOWN",
                    "method": "Frequency Domain Analysis",
                    "plots": {
                        "ela": ela_b64,
                        "spectrum": spectrum_b64
                    },
                    "details": {
                        "ela_explanation": "Error Level Analysis generated (Model missing for classification).",
                        "spectrum_explanation": "Frequency spectrum generated."
                    }
                }

            # Extract features
            features = self.extract_features(image)
            
            if features is None:
                return {"error": "Feature extraction failed"}
            
            # Add batch dimension
            input_tensor = np.expand_dims(features, axis=0)
            
            # Run inference
            probs = self.session.run(
                [self.output_name],
                {self.input_name: input_tensor}
            )[0][0]
            
            # Helper for probabilities
            if isinstance(probs, np.ndarray) and len(probs) == 2:
                exp_probs = np.exp(probs - np.max(probs))
                probs = exp_probs / exp_probs.sum()
                real_prob = float(probs[0])
                fake_prob = float(probs[1])
            else:
                 fake_prob = float(probs)
                 real_prob = 1.0 - fake_prob
            
            risk_score = fake_prob * 100
            
            return {
                "risk_score": round(risk_score, 2),
                "prediction": {
                    "fake_probability": round(fake_prob, 4),
                    "real_probability": round(real_prob, 4)
                },
                "classification": "MANIPULATED" if risk_score > 50 else "AUTHENTIC",
                "method": "Frequency Domain Analysis",
                "plots": {
                    "ela": ela_b64,
                    "spectrum": spectrum_b64
                },
                "details": {
                    "ela_explanation": "Error Level Analysis shows compression artifact inconsistencies. High contrast areas indicate potential manipulation.",
                    "spectrum_explanation": "Frequency spectrum analysis detects upsampling artifacts common in GAN-generated faces."
                }
            }
            
        except Exception as e:
            logger.error(f"Forensic analysis failed: {e}")
            return {"error": str(e)}

# Singleton
forensic_analyzer = ForensicAnalyzer()
