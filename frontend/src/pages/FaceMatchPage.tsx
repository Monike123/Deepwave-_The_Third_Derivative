import { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { motion, AnimatePresence } from 'framer-motion';
import { Upload, Users, CheckCircle, XCircle, Loader2, ArrowLeft } from 'lucide-react';
import { Link } from 'react-router-dom';
import axios from 'axios';
import './FaceMatchPage.css';

interface MatchResult {
    request_id: string;
    timestamp: string;
    file1: string;
    file2: string;
    match_result: {
        match: boolean;
        verified: boolean;
        similarity_score: number;
        distance: number;
        threshold: number;
        model: string;
        error?: string;
    };
    processing_time_ms: number;
}

export default function FaceMatchPage() {
    const [file1, setFile1] = useState<File | null>(null);
    const [file2, setFile2] = useState<File | null>(null);
    const [preview1, setPreview1] = useState<string | null>(null);
    const [preview2, setPreview2] = useState<string | null>(null);
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState<MatchResult | null>(null);
    const [error, setError] = useState<string | null>(null);
    const [threshold, setThreshold] = useState(0.6);

    const onDrop1 = useCallback((acceptedFiles: File[]) => {
        if (acceptedFiles.length > 0) {
            const file = acceptedFiles[0];
            setFile1(file);
            setPreview1(URL.createObjectURL(file));
            setResult(null);
            setError(null);
        }
    }, []);

    const onDrop2 = useCallback((acceptedFiles: File[]) => {
        if (acceptedFiles.length > 0) {
            const file = acceptedFiles[0];
            setFile2(file);
            setPreview2(URL.createObjectURL(file));
            setResult(null);
            setError(null);
        }
    }, []);

    const { getRootProps: getRootProps1, getInputProps: getInputProps1, isDragActive: isDragActive1 } = useDropzone({
        onDrop: onDrop1,
        accept: { 'image/*': ['.jpeg', '.jpg', '.png', '.webp'] },
        multiple: false
    });

    const { getRootProps: getRootProps2, getInputProps: getInputProps2, isDragActive: isDragActive2 } = useDropzone({
        onDrop: onDrop2,
        accept: { 'image/*': ['.jpeg', '.jpg', '.png', '.webp'] },
        multiple: false
    });

    const handleMatch = async () => {
        if (!file1 || !file2) {
            setError('Please upload both images');
            return;
        }

        setLoading(true);
        setError(null);
        setResult(null);

        const formData = new FormData();
        formData.append('file1', file1);
        formData.append('file2', file2);
        formData.append('threshold', threshold.toString());

        try {
            const response = await axios.post<MatchResult>(
                'http://localhost:8000/api/v1/analyze/face/match',
                formData,
                { headers: { 'Content-Type': 'multipart/form-data' } }
            );
            setResult(response.data);
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Face matching failed');
        } finally {
            setLoading(false);
        }
    };

    const clearAll = () => {
        setFile1(null);
        setFile2(null);
        setPreview1(null);
        setPreview2(null);
        setResult(null);
        setError(null);
    };

    return (
        <div className="face-match-page">
            <div className="container">
                {/* Header */}
                <motion.div
                    className="page-header"
                    initial={{ opacity: 0, y: -20 }}
                    animate={{ opacity: 1, y: 0 }}
                >
                    <Link to="/" className="back-link">
                        <ArrowLeft size={20} />
                        Back to Home
                    </Link>
                    <h1>
                        <Users className="header-icon" />
                        Face Recognition
                    </h1>
                    <p>1:1 Face Verification - Compare two faces to verify identity</p>
                </motion.div>

                {/* Upload Section */}
                <div className="upload-section">
                    <motion.div
                        className="upload-container"
                        initial={{ opacity: 0, x: -30 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: 0.1 }}
                    >
                        <h3>Face 1</h3>
                        <div
                            {...getRootProps1()}
                            className={`dropzone ${isDragActive1 ? 'active' : ''} ${preview1 ? 'has-file' : ''}`}
                        >
                            <input {...getInputProps1()} />
                            {preview1 ? (
                                <img src={preview1} alt="Face 1" className="preview-image" />
                            ) : (
                                <div className="dropzone-content">
                                    <Upload size={40} />
                                    <p>Drop image here or click to upload</p>
                                </div>
                            )}
                        </div>
                    </motion.div>

                    <motion.div
                        className="vs-badge"
                        initial={{ scale: 0 }}
                        animate={{ scale: 1 }}
                        transition={{ delay: 0.2, type: 'spring' }}
                    >
                        VS
                    </motion.div>

                    <motion.div
                        className="upload-container"
                        initial={{ opacity: 0, x: 30 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: 0.1 }}
                    >
                        <h3>Face 2</h3>
                        <div
                            {...getRootProps2()}
                            className={`dropzone ${isDragActive2 ? 'active' : ''} ${preview2 ? 'has-file' : ''}`}
                        >
                            <input {...getInputProps2()} />
                            {preview2 ? (
                                <img src={preview2} alt="Face 2" className="preview-image" />
                            ) : (
                                <div className="dropzone-content">
                                    <Upload size={40} />
                                    <p>Drop image here or click to upload</p>
                                </div>
                            )}
                        </div>
                    </motion.div>
                </div>

                {/* Threshold Slider */}
                <motion.div
                    className="threshold-section"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: 0.3 }}
                >
                    <label>
                        Similarity Threshold: <strong>{threshold.toFixed(2)}</strong>
                    </label>
                    <input
                        type="range"
                        min="0.4"
                        max="0.8"
                        step="0.05"
                        value={threshold}
                        onChange={(e) => setThreshold(parseFloat(e.target.value))}
                        className="threshold-slider"
                    />
                    <div className="threshold-labels">
                        <span>Low Security (0.4)</span>
                        <span>High Security (0.8)</span>
                    </div>
                </motion.div>

                {/* Action Buttons */}
                <motion.div
                    className="action-buttons"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: 0.4 }}
                >
                    <button
                        className="btn-primary"
                        onClick={handleMatch}
                        disabled={!file1 || !file2 || loading}
                    >
                        {loading ? (
                            <>
                                <Loader2 className="spin" size={20} />
                                Matching...
                            </>
                        ) : (
                            <>
                                <Users size={20} />
                                Match Faces
                            </>
                        )}
                    </button>
                    <button className="btn-secondary" onClick={clearAll}>
                        Clear All
                    </button>
                </motion.div>

                {/* Error Message */}
                <AnimatePresence>
                    {error && (
                        <motion.div
                            className="error-message"
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            exit={{ opacity: 0 }}
                        >
                            <XCircle size={20} />
                            {error}
                        </motion.div>
                    )}
                </AnimatePresence>

                {/* Results */}
                <AnimatePresence>
                    {result && (
                        <motion.div
                            className="results-section"
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            exit={{ opacity: 0 }}
                        >
                            <div className={`result-card ${result.match_result?.match ? 'match' : 'no-match'}`}>
                                <div className="result-icon">
                                    {result.match_result?.match ? (
                                        <CheckCircle size={60} />
                                    ) : (
                                        <XCircle size={60} />
                                    )}
                                </div>
                                <h2>{result.match_result?.verified ? 'MATCH' : 'NO MATCH'}</h2>
                                <div className="similarity-score">
                                    <span className="score-value">
                                        {((result.match_result?.similarity_score || 0) * 100).toFixed(1)}%
                                    </span>
                                    <span className="score-label">Similarity</span>
                                </div>
                                <div className="result-details">
                                    <div className="detail-row">
                                        <span>Model</span>
                                        <span className="confidence-badge medium">
                                            {result.match_result?.model || 'DeepFace'}
                                        </span>
                                    </div>
                                    <div className="detail-row">
                                        <span>Threshold Used</span>
                                        <span>{result.match_result?.threshold || threshold}</span>
                                    </div>
                                    <div className="detail-row">
                                        <span>Processing Time</span>
                                        <span>{result.processing_time_ms || 0}ms</span>
                                    </div>
                                </div>
                            </div>
                        </motion.div>
                    )}
                </AnimatePresence>
            </div>
        </div>
    );
}
