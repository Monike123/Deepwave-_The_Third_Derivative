import { useState, useRef } from 'react';
import { Upload, X, AlertTriangle, CheckCircle, Activity } from 'lucide-react';
import './AnalyzePage.css';
import AnalysisLoading from '../components/AnalysisLoading';

interface AnalysisResult {
    classification: string;
    confidence: string;
    risk_score: number;
    prediction: {
        fake_probability: number;
        real_probability: number;
    };
    faces_detected?: number;
    prediction_time?: number;
    filename?: string;
    signals?: {
        nvidia_hive?: {
            risk_score: number;
            classification: string;
        };
        huggingface?: {
            risk_score: number;
            classification: string;
        };
        local_ensemble?: {
            risk_score: number;
            classification: string;
            forensic_plots?: {
                ela?: string;
                spectrum?: string;
            };
            forensic_details?: {
                ela_explanation?: string;
                spectrum_explanation?: string;
            };
        };
        local_temporal?: {
            risk_score: number;
            classification: string;
        };
    };
    audio_features?: any;
    processing_time_ms: number;
}


export default function AnalyzePage() {
    const [file, setFile] = useState<File | null>(null);
    const [preview, setPreview] = useState<string | null>(null);
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState<AnalysisResult | null>(null);
    const [mode, setMode] = useState<'standard' | 'enhanced'>('standard');
    const [error, setError] = useState<string | null>(null);
    const fileInputRef = useRef<HTMLInputElement>(null);

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files[0]) {
            const selectedFile = e.target.files[0];
            setFile(selectedFile);
            setResult(null);
            setError(null);

            // Create preview
            const objectUrl = URL.createObjectURL(selectedFile);
            setPreview(objectUrl);
        }
    };

    const handleDrop = (e: React.DragEvent) => {
        e.preventDefault();
        if (e.dataTransfer.files && e.dataTransfer.files[0]) {
            const selectedFile = e.dataTransfer.files[0];
            setFile(selectedFile);
            setResult(null);
            setError(null);
            const objectUrl = URL.createObjectURL(selectedFile);
            setPreview(objectUrl);
        }
    };

    const clearFile = () => {
        setFile(null);
        setPreview(null);
        setResult(null);
        setError(null);
        if (fileInputRef.current) fileInputRef.current.value = '';
    };

    const analyzeFile = async () => {
        if (!file) return;

        setLoading(true);
        setError(null);
        const formData = new FormData();
        formData.append('file', file);

        try {
            // Determine endpoint based on file type and mode
            const isVideo = file.type.startsWith('video/');
            const isAudio = file.type.startsWith('audio/');

            const baseEndpoint = mode === 'enhanced' ? '/api/v1/analyze/advanced' : '/api/v1/analyze';

            let typeEndpoint = '/image/';
            if (isVideo) typeEndpoint = '/video/';
            if (isAudio) typeEndpoint = '/audio/';

            // Enhanced mode might not support audio directly unless mapped
            if (isAudio && mode === 'enhanced') {
                // If enhanced audio implemented (it is in advanced.py: /audio/)
                typeEndpoint = '/audio/';
            }

            // Use 127.0.0.1 to avoid Windows IPv6 localhost issues
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 30000); // 30s timeout

            const response = await fetch(`http://127.0.0.1:8000${baseEndpoint}${typeEndpoint}`, {
                method: 'POST',
                body: formData,
                signal: controller.signal
            });
            clearTimeout(timeoutId);

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || 'Analysis failed');
            }

            setResult(data);
        } catch (err: any) {
            setError(err.message || 'An error occurred during analysis');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="analyze-page min-h-screen text-white">
            <div className="container mx-auto px-4 py-8">
                <h1 className="page-title glitch-title">DEEPWAY // SIGNAL ANALYSIS</h1>

                {loading ? (
                    <div className="animate-fade-in">
                        <AnalysisLoading />
                    </div>
                ) : (
                    <>
                        <div className="analysis-grid">
                            {/* Upload Section */}
                            <div className="upload-card">
                                <div className="mode-toggle">
                                    <button
                                        className={`mode-btn ${mode === 'standard' ? 'active' : ''}`}
                                        onClick={() => setMode('standard')}
                                    >
                                        Standard (Local)
                                    </button>
                                    <button
                                        className={`mode-btn ${mode === 'enhanced' ? 'active' : ''}`}
                                        onClick={() => setMode('enhanced')}
                                    >
                                        Enhanced (Cloud AI)
                                    </button>
                                </div>

                                {!file ? (
                                    <div
                                        className="dropzone"
                                        onDragOver={(e) => e.preventDefault()}
                                        onDrop={handleDrop}
                                        onClick={() => fileInputRef.current?.click()}
                                    >
                                        <div className="upload-icon-wrapper">
                                            <Upload size={48} className="upload-icon" />
                                        </div>
                                        <h3>Click to upload or drag & drop</h3>
                                        <p>Supports JPG, PNG, MP4, AVI, WAV, MP3 (Max 100MB)</p>
                                        <input
                                            type="file"
                                            ref={fileInputRef}
                                            onChange={handleFileChange}
                                            hidden
                                            accept="image/*,video/*,audio/*"
                                        />
                                    </div>
                                ) : (
                                    <div className="preview-container">
                                        <button className="clear-btn" onClick={clearFile}>
                                            <X size={20} />
                                        </button>
                                        {file.type.startsWith('video/') ? (
                                            <video src={preview!} controls className="file-preview" />
                                        ) : file.type.startsWith('audio/') ? (
                                            <audio src={preview!} controls className="w-full mt-4" />
                                        ) : (
                                            <img src={preview!} alt="Preview" className="file-preview" />
                                        )}
                                        <div className="file-info">
                                            <span className="filename">{file.name}</span>
                                            <span className="filesize">{(file.size / (1024 * 1024)).toFixed(2)} MB</span>
                                        </div>

                                        <button
                                            className="analyze-btn"
                                            onClick={analyzeFile}
                                            disabled={loading}
                                        >
                                            {loading ? (
                                                <>
                                                    <span className="spinner"></span>
                                                    Analyzing...
                                                </>
                                            ) : (
                                                <>
                                                    <Activity size={20} />
                                                    Start Analysis
                                                </>
                                            )}
                                        </button>
                                    </div>
                                )}

                                {error && (
                                    <div className="error-message">
                                        <AlertTriangle size={20} />
                                        {error}
                                    </div>
                                )}
                            </div>

                            {/* Results Section */}
                            {result && (
                                <div className="results-card">
                                    <div className={`result-header ${result.classification.toLowerCase()}`}>
                                        {result.classification === 'AUTHENTIC' ? (
                                            <CheckCircle size={48} />
                                        ) : (
                                            <AlertTriangle size={48} />
                                        )}
                                        <div>
                                            <h2>{result.classification}</h2>
                                            <span className="confidence-badge">
                                                {result.confidence} CONFIDENCE
                                            </span>
                                        </div>
                                    </div>

                                    <div className="score-meter">
                                        <div className="meter-label">
                                            <span>Deepfake Probability</span>
                                            <span>{result.risk_score.toFixed(1)}%</span>
                                        </div>
                                        <div className="meter-track">
                                            <div
                                                className="meter-fill"
                                                style={{
                                                    width: `${result.risk_score}%`,
                                                    backgroundColor: result.risk_score > 50 ? '#ef4444' : '#10b981'
                                                }}
                                            ></div>
                                        </div>
                                    </div>

                                    <div className="details-grid">
                                        <div className="detail-item">
                                            <span className="label">Real Prob</span>
                                            <span className="value">{(result.prediction.real_probability * 100).toFixed(1)}%</span>
                                        </div>
                                        <div className="detail-item">
                                            <span className="label">Fake Prob</span>
                                            <span className="value">{(result.prediction.fake_probability * 100).toFixed(1)}%</span>
                                        </div>
                                        {result.faces_detected !== undefined && (
                                            <div className="detail-item">
                                                <span className="label">Faces Detected</span>
                                                <span className="value">{result.faces_detected}</span>
                                            </div>
                                        )}
                                    </div>
                                </div>
                            )}
                        </div>

                        {/* Detailed Report Section */}
                        {result && (
                            <div className="report-section mt-8">
                                <h2 className="section-title">Detailed Analysis Report</h2>

                                {/* Module Breakdown */}
                                {result.signals && (
                                    <div className="module-breakdown grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
                                        {result.signals.nvidia_hive && (
                                            <div className="report-card">
                                                <h3>Advanced Deep Vision V1</h3>
                                                <div className="score">{result.signals.nvidia_hive.risk_score.toFixed(1)}% Risk</div>
                                                <div className="status">{result.signals.nvidia_hive.classification}</div>
                                            </div>
                                        )}
                                        {result.signals.huggingface && (
                                            <div className="report-card">
                                                <h3>Advanced Deep Vision V2</h3>
                                                <div className="score">{result.signals.huggingface.risk_score.toFixed(1)}% Risk</div>
                                                <div className="status">{result.signals.huggingface.classification}</div>
                                            </div>
                                        )}
                                        {result.signals.local_ensemble && (
                                            <div className="report-card">
                                                <h3>Forensic Core Engine</h3>
                                                <div className="score">{result.signals.local_ensemble.risk_score.toFixed(1)}% Risk</div>
                                                <div className="status">{result.signals.local_ensemble.classification}</div>
                                            </div>
                                        )}
                                        {result.signals.local_temporal && (
                                            <div className="report-card">
                                                <h3>Local Temporal (3D CNN)</h3>
                                                <div className="score">{result.signals.local_temporal.risk_score.toFixed(1)}% Risk</div>
                                                <div className="status">{result.signals.local_temporal.classification}</div>
                                            </div>
                                        )}
                                    </div>
                                )}

                                {/* Forensic Visualizations */}
                                {result.signals?.local_ensemble?.forensic_plots && (
                                    <div className="forensic-viz mb-8">
                                        <h3 className="subsection-title">Forensic Signal Analysis</h3>
                                        <div className="viz-grid grid grid-cols-1 md:grid-cols-2 gap-6">
                                            {/* ELA Plot */}
                                            {result.signals.local_ensemble.forensic_plots.ela && (
                                                <div className="viz-card">
                                                    <h4>Error Level Analysis (ELA)</h4>
                                                    <img
                                                        src={`data:image/jpeg;base64,${result.signals.local_ensemble.forensic_plots.ela}`}
                                                        alt="ELA Analysis"
                                                        className="viz-image"
                                                    />
                                                    <p className="viz-desc">
                                                        {result.signals.local_ensemble.forensic_details?.ela_explanation}
                                                    </p>
                                                </div>
                                            )}

                                            {/* Spectrum Plot */}
                                            {result.signals.local_ensemble.forensic_plots.spectrum && (
                                                <div className="viz-card">
                                                    <h4>Frequency Spectrum Analysis</h4>
                                                    <img
                                                        src={`data:image/jpeg;base64,${result.signals.local_ensemble.forensic_plots.spectrum}`}
                                                        alt="Spectrum Analysis"
                                                        className="viz-image"
                                                    />
                                                    <p className="viz-desc">
                                                        {result.signals.local_ensemble.forensic_details?.spectrum_explanation}
                                                    </p>
                                                </div>
                                            )}
                                        </div>
                                    </div>
                                )}

                                {/* NEW: Enhanced Analysis Report Section */}
                                <div className="enhanced-report-section">
                                    <h3 className="subsection-title">📊 Detailed Analysis Breakdown</h3>

                                    {/* Analysis Summary Card */}
                                    <div className="analysis-summary-card">
                                        <div className="summary-header">
                                            <span className="summary-icon">🔍</span>
                                            <h4>Analysis Summary</h4>
                                        </div>
                                        <div className="summary-content">
                                            <p>
                                                <strong>File Analyzed:</strong> {result.filename || 'Unknown'}<br />
                                                <strong>Processing Time:</strong> {result.processing_time_ms}ms<br />
                                                <strong>Detection Result:</strong> <span className={result.classification === 'AUTHENTIC' ? 'text-green' : 'text-red'}>{result.classification}</span><br />
                                                <strong>Confidence Level:</strong> {result.confidence}
                                            </p>
                                        </div>
                                    </div>

                                    {/* Probability Distribution Chart */}
                                    <div className="probability-chart-section">
                                        <h4 className="chart-title">📈 Class Probability Distribution</h4>
                                        <div className="probability-bars">
                                            <div className="prob-row">
                                                <span className="prob-label">Real / Authentic</span>
                                                <div className="prob-bar-track">
                                                    <div
                                                        className="prob-bar-fill real"
                                                        style={{ width: `${(result.prediction.real_probability * 100)}%` }}
                                                    ></div>
                                                </div>
                                                <span className="prob-value">{(result.prediction.real_probability * 100).toFixed(1)}%</span>
                                            </div>
                                            <div className="prob-row">
                                                <span className="prob-label">Fake / Manipulated</span>
                                                <div className="prob-bar-track">
                                                    <div
                                                        className="prob-bar-fill fake"
                                                        style={{ width: `${(result.prediction.fake_probability * 100)}%` }}
                                                    ></div>
                                                </div>
                                                <span className="prob-value">{(result.prediction.fake_probability * 100).toFixed(1)}%</span>
                                            </div>
                                        </div>
                                    </div>

                                    {/* Detection Methods Used */}
                                    <div className="detection-methods-section">
                                        <h4 className="chart-title">🔬 Detection Methods Used</h4>
                                        <div className="methods-grid">
                                            <div className="method-card">
                                                <div className="method-icon">🧠</div>
                                                <h5>Visual AI (ViT)</h5>
                                                <p>Vision Transformer analyzes visual patterns, textures, and facial features to detect AI-generated content and face swaps.</p>
                                                <span className="method-status active">Active</span>
                                            </div>
                                            <div className="method-card">
                                                <div className="method-icon">📡</div>
                                                <h5>Forensic Analysis</h5>
                                                <p>Frequency domain analysis detects compression artifacts, GAN fingerprints, and upsampling patterns invisible to humans.</p>
                                                <span className="method-status active">Active</span>
                                            </div>
                                            <div className="method-card">
                                                <div className="method-icon">🎯</div>
                                                <h5>ELA Detection</h5>
                                                <p>Error Level Analysis reveals inconsistencies in JPEG compression that indicate edited or spliced regions.</p>
                                                <span className="method-status active">Active</span>
                                            </div>
                                            <div className="method-card">
                                                <div className="method-icon">🔄</div>
                                                <h5>Ensemble Fusion</h5>
                                                <p>Multiple AI models vote together to provide robust, high-confidence detection results.</p>
                                                <span className="method-status active">Active</span>
                                            </div>
                                        </div>
                                    </div>

                                    {/* Technical Details */}
                                    <div className="technical-details-section">
                                        <h4 className="chart-title">⚙️ Technical Details</h4>
                                        <div className="tech-grid">
                                            <div className="tech-item">
                                                <span className="tech-label">Model Architecture</span>
                                                <span className="tech-value">ViT-Base-Patch16-224</span>
                                            </div>
                                            <div className="tech-item">
                                                <span className="tech-label">Forensic Method</span>
                                                <span className="tech-value">FFT + Radial PSD</span>
                                            </div>
                                            <div className="tech-item">
                                                <span className="tech-label">Risk Assessment</span>
                                                <span className="tech-value">{result.risk_score.toFixed(1)}% Risk Score</span>
                                            </div>
                                            <div className="tech-item">
                                                <span className="tech-label">Analysis Type</span>
                                                <span className="tech-value">Multi-Modal Ensemble</span>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        )}
                    </>
                )}
            </div>
        </div>
    );
}
