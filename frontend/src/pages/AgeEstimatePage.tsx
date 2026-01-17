import { useState, useRef } from 'react';
import { motion } from 'framer-motion';
import { Upload, Camera, Cake, ArrowLeft, Loader2 } from 'lucide-react';
import { Link } from 'react-router-dom';
import axios from 'axios';
import './AgeEstimatePage.css';

export default function AgeEstimatePage() {
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState<any>(null);
    const [error, setError] = useState<string | null>(null);
    const [capturedImage, setCapturedImage] = useState<string | null>(null);

    // Webcam refs
    const videoRef = useRef<HTMLVideoElement>(null);
    const canvasRef = useRef<HTMLCanvasElement>(null);
    const streamRef = useRef<MediaStream | null>(null);
    const [webcamOn, setWebcamOn] = useState(false);

    // Start webcam
    const startWebcam = async () => {
        try {
            // Get permission
            let stream = await navigator.mediaDevices.getUserMedia({ video: true });

            // Find USB cam
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

    // Capture from webcam and analyze
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

        // Convert to blob and analyze
        canvas.toBlob(async (blob) => {
            if (!blob) return;
            const file = new File([blob], 'capture.jpg', { type: 'image/jpeg' });
            await analyzeImage(file);
        }, 'image/jpeg', 0.9);
    };

    // Handle file upload
    const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (!file) return;

        setCapturedImage(URL.createObjectURL(file));
        await analyzeImage(file);
    };

    // Analyze image
    const analyzeImage = async (file: File) => {
        setLoading(true);
        setError(null);
        setResult(null);

        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await axios.post(
                'http://localhost:8000/api/v1/analyze/age/estimate',
                formData
            );
            setResult(response.data);
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Age estimation failed');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="age-page">
            <div className="container">
                <motion.div className="page-header" initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
                    <Link to="/" className="back-link">
                        <ArrowLeft size={20} /> Back
                    </Link>
                    <h1><Cake /> Age Estimation</h1>
                </motion.div>

                <div className="main-content">
                    {/* Left: Upload */}
                    <div className="upload-box">
                        <h3>📁 Upload Image</h3>
                        <label className="upload-area">
                            <input type="file" accept="image/*" onChange={handleUpload} hidden />
                            <Upload size={40} />
                            <span>Click to upload</span>
                        </label>
                    </div>

                    {/* Center: Webcam */}
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
                                        📸 Capture & Analyze
                                    </button>
                                    <button onClick={stopWebcam} className="btn-stop">
                                        Stop
                                    </button>
                                </>
                            )}
                        </div>
                    </div>

                    {/* Right: Results */}
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
                            <div className="age-result">
                                <div className="age-number">
                                    {result.age_result?.estimated_age?.toFixed(0) || '?'}
                                </div>
                                <div className="age-label">years old</div>
                                <div className="age-range">
                                    Range: {result.age_result?.confidence_interval_95?.lower_bound?.toFixed(0) || '?'} - {result.age_result?.confidence_interval_95?.upper_bound?.toFixed(0) || '?'}
                                </div>
                                <div className="age-group">
                                    Group: {result.age_result?.age_group || 'N/A'}
                                </div>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
}
