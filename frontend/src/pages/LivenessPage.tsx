import { useState, useRef } from 'react';
import { motion } from 'framer-motion';
import { Upload, Camera, Shield, ArrowLeft, Loader2, CheckCircle, XCircle } from 'lucide-react';
import { Link } from 'react-router-dom';
import axios from 'axios';
import './LivenessPage.css';

export default function LivenessPage() {
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState<any>(null);
    const [error, setError] = useState<string | null>(null);
    const [capturedImage, setCapturedImage] = useState<string | null>(null);
    const [securityLevel, setSecurityLevel] = useState('standard');

    // Webcam refs
    const videoRef = useRef<HTMLVideoElement>(null);
    const canvasRef = useRef<HTMLCanvasElement>(null);
    const streamRef = useRef<MediaStream | null>(null);
    const [webcamOn, setWebcamOn] = useState(false);

    // Start webcam
    const startWebcam = async () => {
        try {
            let stream = await navigator.mediaDevices.getUserMedia({ video: true });

            const devices = await navigator.mediaDevices.enumerateDevices();
            const usbCam = devices.find(d => d.kind === 'videoinput' && d.label.includes('USB'));

            if (usbCam) {
                stream.getTracks().forEach(t => t.stop());
                stream = await navigator.mediaDevices.getUserMedia({
                    video: { deviceId: usbCam.deviceId, width: 640, height: 480 }
                });
            }

            streamRef.current = stream;
            if (videoRef.current) {
                videoRef.current.srcObject = stream;
            }
            setWebcamOn(true);
        } catch (err) {
            setError('Could not access webcam');
        }
    };

    // Stop webcam
    const stopWebcam = () => {
        if (streamRef.current) {
            streamRef.current.getTracks().forEach(t => t.stop());
            streamRef.current = null;
        }
        setWebcamOn(false);
    };

    // Capture and analyze
    const captureAndAnalyze = async () => {
        if (!videoRef.current || !canvasRef.current) return;

        const video = videoRef.current;
        const canvas = canvasRef.current;
        canvas.width = video.videoWidth || 640;
        canvas.height = video.videoHeight || 480;

        const ctx = canvas.getContext('2d');
        if (!ctx) return;

        ctx.drawImage(video, 0, 0);
        const imageData = canvas.toDataURL('image/jpeg', 0.9);
        setCapturedImage(imageData);

        canvas.toBlob(async (blob) => {
            if (!blob) return;
            const file = new File([blob], 'capture.jpg', { type: 'image/jpeg' });
            await analyzeImage(file);
        }, 'image/jpeg', 0.9);
    };

    // Handle upload
    const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (!file) return;

        setCapturedImage(URL.createObjectURL(file));
        await analyzeImage(file);
    };

    // Analyze
    const analyzeImage = async (file: File) => {
        setLoading(true);
        setError(null);
        setResult(null);

        const formData = new FormData();
        formData.append('file', file);
        formData.append('security_level', securityLevel);

        try {
            const response = await axios.post(
                'http://localhost:8000/api/v1/analyze/liveness/detect',
                formData
            );
            setResult(response.data);
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Liveness detection failed');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="liveness-page">
            <div className="container">
                <motion.div className="page-header" initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
                    <Link to="/" className="back-link">
                        <ArrowLeft size={20} /> Back
                    </Link>
                    <h1><Shield /> Liveness Detection</h1>
                </motion.div>

                <div className="main-content">
                    {/* Upload */}
                    <div className="upload-box">
                        <h3>📁 Upload Image</h3>
                        <label className="upload-area">
                            <input type="file" accept="image/*" onChange={handleUpload} hidden />
                            <Upload size={40} />
                            <span>Click to upload</span>
                        </label>

                        <div className="security-selector">
                            <label>Security Level</label>
                            <select value={securityLevel} onChange={e => setSecurityLevel(e.target.value)}>
                                <option value="standard">Standard</option>
                                <option value="high">High</option>
                                <option value="banking_kyc">Banking KYC</option>
                            </select>
                        </div>
                    </div>

                    {/* Webcam */}
                    <div className="webcam-box">
                        <h3>📷 Webcam</h3>
                        <div className="video-area">
                            <video ref={videoRef} autoPlay playsInline muted />
                            <canvas ref={canvasRef} style={{ display: 'none' }} />
                        </div>
                        <div className="webcam-controls">
                            {!webcamOn ? (
                                <button onClick={startWebcam} className="btn-start">
                                    <Camera size={18} /> Start Camera
                                </button>
                            ) : (
                                <>
                                    <button onClick={captureAndAnalyze} className="btn-capture">
                                        📸 Capture
                                    </button>
                                    <button onClick={stopWebcam} className="btn-stop">
                                        Stop
                                    </button>
                                </>
                            )}
                        </div>
                    </div>

                    {/* Results */}
                    <div className="results-box">
                        <h3>📊 Results</h3>

                        {capturedImage && (
                            <div className="captured-preview">
                                <img src={capturedImage} alt="Captured" />
                            </div>
                        )}

                        {loading && (
                            <div className="loading">
                                <Loader2 className="spin" size={30} />
                                <span>Analyzing...</span>
                            </div>
                        )}

                        {error && <div className="error">{error}</div>}

                        {result && (
                            <div className={`liveness-result ${result.liveness_result?.is_live ? 'live' : 'spoof'}`}>
                                <div className="result-icon">
                                    {result.liveness_result?.is_live ? (
                                        <CheckCircle size={50} />
                                    ) : (
                                        <XCircle size={50} />
                                    )}
                                </div>
                                <div className="result-text">
                                    {result.liveness_result?.is_live ? 'LIVE' : 'SPOOF DETECTED'}
                                </div>
                                <div className="confidence">
                                    Confidence: {((result.liveness_result?.confidence || 0) * 100).toFixed(1)}%
                                </div>
                                {result.liveness_result?.attack_type && (
                                    <div className="attack-type">
                                        Attack: {result.liveness_result.attack_type}
                                    </div>
                                )}
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
}
