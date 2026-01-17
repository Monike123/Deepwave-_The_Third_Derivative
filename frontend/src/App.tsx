import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Header from './components/Header';
import HomePage from './pages/HomePage';
import AnalyzePage from './pages/AnalyzePage';
// NEW: Biometric services pages
import FaceMatchPage from './pages/FaceMatchPage';
import LivenessPage from './pages/LivenessPage';
import AgeEstimatePage from './pages/AgeEstimatePage';
import './index.css';

function App() {
    return (
        <Router>
            <div className="app-wrapper">
                <Header />
                <main className="main-content">
                    <Routes>
                        <Route path="/" element={<HomePage />} />
                        <Route path="/analyze" element={<AnalyzePage />} />
                        {/* NEW: Biometric services routes */}
                        <Route path="/face-match" element={<FaceMatchPage />} />
                        <Route path="/liveness" element={<LivenessPage />} />
                        <Route path="/age-estimate" element={<AgeEstimatePage />} />
                    </Routes>
                </main>
            </div>
        </Router>
    );
}

export default App;


