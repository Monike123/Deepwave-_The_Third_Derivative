import React, { useEffect, useState } from 'react';
import './AnalysisLoading.css';

const AnalysisLoading: React.FC = () => {
    const [status, setStatus] = useState('Initializing Neural Network...');

    useEffect(() => {
        const steps = [
            'Scanning Facial Geometry...',
            'Analyzing Frequency Spectrum...',
            'Detecting Compression Artifacts...',
            'Querying DeepNeural Cluster...',
            'Synthesizing Ensemble Results...'
        ];

        let i = 0;
        const interval = setInterval(() => {
            if (i < steps.length) {
                setStatus(steps[i]);
                i++;
            }
        }, 800);

        return () => clearInterval(interval);
    }, []);

    return (
        <div className="analysis-loading-container">
            <div className="scanner-hud">
                <div className="scanner-frame">
                    <div className="scan-line"></div>
                    <div className="face-wireframe">
                        {/* CSS-based "Face" points */}
                        <div className="node n1"></div>
                        <div className="node n2"></div>
                        <div className="node n3"></div>
                        <div className="node n4"></div>
                        <div className="node n5"></div>
                    </div>
                </div>

                <div className="loading-status">
                    <h2>ANALYZING</h2>
                    <div className="status-text">{status}</div>
                </div>

                <div className="loader-bar">
                    <div className="bar-fill"></div>
                </div>
            </div>
        </div>
    );
};

export default AnalysisLoading;
