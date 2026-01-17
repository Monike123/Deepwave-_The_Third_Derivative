import { motion } from 'framer-motion';
import { useState } from 'react';
import { Link } from 'react-router-dom';
import { ArrowRight, Github, Twitter, Linkedin, Mail, Shield, Zap, Video, Cpu, Brain, Lock, Globe, Sparkles, Users, Cake, UserCheck, AlertTriangle, X } from 'lucide-react';
import AnimatedOrbs from '../components/AnimatedOrbs';
import FeatureCard from '../components/FeatureCard';
import StatCard from '../components/StatCard';
import './HomePage.css';

// Animation variants for staggered children
const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
        opacity: 1,
        transition: {
            staggerChildren: 0.1,
            delayChildren: 0.2,
        },
    },
};

const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: {
        opacity: 1,
        y: 0,
        transition: { duration: 0.6, ease: [0.4, 0, 0.2, 1] },
    },
};

// Feature data
const features = [
    {
        icon: Shield,
        title: 'Multi-Layer Forensics',
        description: 'Combines visual artifact detection, frequency domain analysis, and 3D temporal CNNs for robust verification.',
        accent: 'cyan' as const,
    },
    {
        icon: Video,
        title: 'Video & Image Support',
        description: 'Analyze single frames or full video clips. Our temporal engine detects motion inconsistencies invisible to the naked eye.',
        accent: 'purple' as const,
    },
    {
        icon: Brain,
        title: 'Advanced AI Engine',
        description: 'Multiple deep learning models work together to analyze content from different perspectives for robust detection.',
        accent: 'orange' as const,
    },
    {
        icon: Zap,
        title: 'Real-Time Performance',
        description: 'Optimized ONNX runtime inference ensures swift results without compromising on detection quality.',
        accent: 'cyan' as const,
    },
    {
        icon: Lock,
        title: 'Privacy First',
        description: 'All processing happens locally on our servers. Your media is analyzed securely and never shared.',
        accent: 'purple' as const,
    },
    {
        icon: Globe,
        title: 'Multi-Format Support',
        description: 'Supports JPG, PNG, WebP images and MP4, AVI, MOV video formats with automatic format detection.',
        accent: 'orange' as const,
    },
];

// Stats data
const stats = [
    { number: 'Fast', label: 'Detection Speed' },
    { number: '<1s', label: 'Processing Time' },
    { number: '3+', label: 'AI Models' },
    { number: 'Secure', label: 'Privacy Protected' },
];

// Solutions data - NEW
const solutions = [
    {
        icon: Shield,
        title: 'Deepfake Detection',
        description: 'AI-powered analysis to detect manipulated images and videos with forensic accuracy.',
        path: '/analyze',
        color: 'from-cyan-500 to-blue-500',
    },
    {
        icon: Users,
        title: 'Face Recognition',
        description: '1:1 face matching and 1:N identification using ArcFace embeddings.',
        path: '/face-match',
        color: 'from-purple-500 to-pink-500',
    },
    {
        icon: UserCheck,
        title: 'Liveness Detection',
        description: 'Anti-spoofing verification to ensure real person presence with webcam support.',
        path: '/liveness',
        color: 'from-green-500 to-emerald-500',
    },
    {
        icon: Cake,
        title: 'Age Estimation',
        description: 'Estimate age from facial features with confidence intervals and real-time webcam.',
        path: '/age-estimate',
        color: 'from-orange-500 to-amber-500',
    },
];

export default function HomePage() {
    const [showBanner, setShowBanner] = useState(true);

    return (
        <div className="home-page relative min-h-screen">
            {/* Data Collection Warning Banner */}
            {showBanner && (
                <div className="fixed top-16 left-0 right-0 z-50 px-4">
                    <div className="max-w-4xl mx-auto bg-gradient-to-r from-amber-500/20 to-orange-500/20 border border-amber-500/30 rounded-lg p-3 flex items-center gap-3 backdrop-blur-sm">
                        <AlertTriangle className="w-5 h-5 text-amber-400 flex-shrink-0" />
                        <p className="text-sm text-amber-200 flex-1">
                            <strong>Data Notice:</strong> Media uploaded to this platform may be collected for research and model retraining to help combat deepfakes and protect the community.
                        </p>
                        <button onClick={() => setShowBanner(false)} className="text-amber-400 hover:text-white transition-colors">
                            <X className="w-4 h-4" />
                        </button>
                    </div>
                </div>
            )}

            {/* Animated Background Orbs */}
            <AnimatedOrbs />

            {/* Hero Section */}
            <section className="hero relative z-10 pt-20 pb-32 px-4">
                <motion.div
                    className="container mx-auto max-w-6xl"
                    variants={containerVariants}
                    initial="hidden"
                    animate="visible"
                >
                    {/* Version Badge */}
                    <motion.div
                        variants={itemVariants}
                        className="flex justify-center mb-8"
                    >
                        <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-gradient-to-r from-cyan-500/10 to-purple-500/10 border border-cyan-500/20 backdrop-blur-sm">
                            <span className="relative flex h-2 w-2">
                                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-cyan-400 opacity-75"></span>
                                <span className="relative inline-flex rounded-full h-2 w-2 bg-cyan-500"></span>
                            </span>
                            <span className="text-sm text-cyan-300 font-medium">
                                v2.0 Now Available with Biometric Suite
                            </span>
                            <Sparkles className="w-4 h-4 text-purple-400" />
                        </div>
                    </motion.div>

                    {/* Main Heading */}
                    <motion.h1
                        variants={itemVariants}
                        className="text-5xl md:text-7xl font-bold text-center mb-6 leading-tight"
                    >
                        AI-Powered{' '}
                        <span className="bg-gradient-to-r from-cyan-400 via-purple-400 to-orange-400 bg-clip-text text-transparent">
                            Biometric Platform
                        </span>
                    </motion.h1>

                    {/* Subtitle */}
                    <motion.p
                        variants={itemVariants}
                        className="text-xl text-gray-400 text-center max-w-3xl mx-auto mb-10 leading-relaxed"
                    >
                        Deepfake detection, face recognition, liveness verification, and age estimation -
                        all powered by state-of-the-art AI models.
                    </motion.p>

                    {/* CTA Buttons */}
                    <motion.div
                        variants={itemVariants}
                        className="flex flex-col sm:flex-row gap-4 justify-center items-center"
                    >
                        <Link to="/analyze">
                            <motion.button
                                whileHover={{ scale: 1.05 }}
                                whileTap={{ scale: 0.95 }}
                                className="group px-8 py-4 rounded-xl font-bold text-lg bg-gradient-to-r from-cyan-500 to-purple-500 text-white shadow-lg shadow-cyan-500/25 hover:shadow-cyan-500/40 transition-all duration-300 flex items-center gap-2"
                            >
                                Start Analysis
                                <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                            </motion.button>
                        </Link>
                        <a href="#solutions">
                            <motion.button
                                whileHover={{ scale: 1.05 }}
                                whileTap={{ scale: 0.95 }}
                                className="px-8 py-4 rounded-xl font-bold text-lg border border-white/20 text-white hover:bg-white/10 backdrop-blur-sm transition-all duration-300"
                            >
                                View Solutions
                            </motion.button>
                        </a>
                    </motion.div>

                    {/* Hero Visual - Abstract 3D effect */}
                    <motion.div
                        initial={{ opacity: 0, y: 50 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 1, delay: 0.5 }}
                        className="mt-20 relative"
                    >
                        <div className="relative mx-auto max-w-4xl">
                            {/* Glowing ring effect */}
                            <div className="absolute inset-0 flex items-center justify-center">
                                <motion.div
                                    className="w-80 h-80 rounded-full border-2 border-cyan-500/30"
                                    animate={{ rotate: 360 }}
                                    transition={{ duration: 20, repeat: Infinity, ease: 'linear' }}
                                />
                            </div>
                            <div className="absolute inset-0 flex items-center justify-center">
                                <motion.div
                                    className="w-64 h-64 rounded-full border border-purple-500/20"
                                    animate={{ rotate: -360 }}
                                    transition={{ duration: 15, repeat: Infinity, ease: 'linear' }}
                                />
                            </div>

                            {/* Center icon */}
                            <div className="relative flex items-center justify-center h-80">
                                <motion.div
                                    animate={{
                                        boxShadow: [
                                            '0 0 20px rgba(0,217,255,0.3)',
                                            '0 0 60px rgba(168,85,247,0.4)',
                                            '0 0 20px rgba(0,217,255,0.3)',
                                        ]
                                    }}
                                    transition={{ duration: 3, repeat: Infinity }}
                                    className="w-32 h-32 rounded-3xl bg-gradient-to-br from-cyan-500/20 to-purple-500/20 backdrop-blur-xl border border-white/20 flex items-center justify-center"
                                >
                                    <Shield className="w-16 h-16 text-cyan-400" />
                                </motion.div>
                            </div>
                        </div>
                    </motion.div>
                </motion.div>
            </section>

            {/* Solutions Section - NEW */}
            <section id="solutions" className="relative z-10 py-24 px-4">
                <div className="container mx-auto max-w-6xl">
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        whileInView={{ opacity: 1, y: 0 }}
                        viewport={{ once: true }}
                        transition={{ duration: 0.6 }}
                        className="text-center mb-16"
                    >
                        <h2 className="text-4xl md:text-5xl font-bold mb-4">
                            Our{' '}
                            <span className="bg-gradient-to-r from-cyan-400 to-purple-400 bg-clip-text text-transparent">
                                Solutions
                            </span>
                        </h2>
                        <p className="text-gray-400 text-lg max-w-2xl mx-auto">
                            Comprehensive biometric services powered by cutting-edge AI
                        </p>
                    </motion.div>

                    <div className="grid md:grid-cols-2 gap-6">
                        {solutions.map((solution, index) => (
                            <motion.div
                                key={solution.title}
                                initial={{ opacity: 0, y: 20 }}
                                whileInView={{ opacity: 1, y: 0 }}
                                viewport={{ once: true }}
                                transition={{ duration: 0.5, delay: index * 0.1 }}
                            >
                                <Link to={solution.path}>
                                    <motion.div
                                        whileHover={{ scale: 1.02, y: -5 }}
                                        className="group relative overflow-hidden rounded-2xl bg-white/5 border border-white/10 backdrop-blur-sm p-6 hover:border-white/20 transition-all duration-300"
                                    >
                                        {/* Gradient overlay on hover */}
                                        <div className={`absolute inset-0 opacity-0 group-hover:opacity-10 transition-opacity bg-gradient-to-r ${solution.color}`} />

                                        <div className="relative z-10 flex items-start gap-4">
                                            <div className={`p-3 rounded-xl bg-gradient-to-r ${solution.color} bg-opacity-20`}>
                                                <solution.icon className="w-8 h-8 text-white" />
                                            </div>
                                            <div className="flex-1">
                                                <h3 className="text-xl font-bold text-white mb-2 group-hover:text-cyan-300 transition-colors">
                                                    {solution.title}
                                                </h3>
                                                <p className="text-gray-400 group-hover:text-gray-300 transition-colors">
                                                    {solution.description}
                                                </p>
                                            </div>
                                            <ArrowRight className="w-5 h-5 text-gray-500 group-hover:text-cyan-400 group-hover:translate-x-1 transition-all" />
                                        </div>
                                    </motion.div>
                                </Link>
                            </motion.div>
                        ))}
                    </div>
                </div>
            </section>

            {/* Stats Section */}
            <section className="relative z-10 py-16 px-4">
                <div className="container mx-auto max-w-6xl">
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 md:gap-6">
                        {stats.map((stat, index) => (
                            <StatCard
                                key={stat.label}
                                number={stat.number}
                                label={stat.label}
                                index={index}
                            />
                        ))}
                    </div>
                </div>
            </section>

            {/* Features Section */}
            <section id="features" className="relative z-10 py-24 px-4">
                <div className="container mx-auto max-w-6xl">
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        whileInView={{ opacity: 1, y: 0 }}
                        viewport={{ once: true }}
                        transition={{ duration: 0.6 }}
                        className="text-center mb-16"
                    >
                        <h2 className="text-4xl md:text-5xl font-bold mb-4">
                            Why Choose{' '}
                            <span className="bg-gradient-to-r from-cyan-400 to-purple-400 bg-clip-text text-transparent">
                                Deepwave?
                            </span>
                        </h2>
                        <p className="text-gray-400 text-lg max-w-2xl mx-auto">
                            Industry-leading deepfake detection powered by cutting-edge AI models
                        </p>
                    </motion.div>

                    <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
                        {features.map((feature, index) => (
                            <FeatureCard
                                key={feature.title}
                                icon={feature.icon}
                                title={feature.title}
                                description={feature.description}
                                index={index}
                                accentColor={feature.accent}
                            />
                        ))}
                    </div>
                </div>
            </section>

            {/* CTA Section */}
            <section className="relative z-10 py-24 px-4">
                <div className="container mx-auto max-w-4xl">
                    <motion.div
                        initial={{ opacity: 0, scale: 0.95 }}
                        whileInView={{ opacity: 1, scale: 1 }}
                        viewport={{ once: true }}
                        transition={{ duration: 0.6 }}
                        className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-cyan-500/10 via-purple-500/10 to-orange-500/10 border border-white/10 backdrop-blur-xl p-12 text-center"
                    >
                        {/* Background glow */}
                        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-96 h-96 bg-gradient-to-r from-cyan-500/20 to-purple-500/20 rounded-full blur-3xl" />

                        <div className="relative z-10">
                            <Cpu className="w-16 h-16 text-cyan-400 mx-auto mb-6" />
                            <h2 className="text-3xl md:text-4xl font-bold mb-4">
                                Ready to Detect Deepfakes?
                            </h2>
                            <p className="text-gray-400 text-lg mb-8 max-w-xl mx-auto">
                                Start analyzing your media files now with our powerful AI-driven detection system.
                            </p>
                            <Link to="/analyze">
                                <motion.button
                                    whileHover={{ scale: 1.05 }}
                                    whileTap={{ scale: 0.95 }}
                                    className="px-10 py-4 rounded-xl font-bold text-lg bg-gradient-to-r from-cyan-500 to-purple-500 text-white shadow-lg shadow-purple-500/25 hover:shadow-purple-500/40 transition-all duration-300"
                                >
                                    Get Started Free
                                </motion.button>
                            </Link>
                        </div>
                    </motion.div>
                </div>
            </section>

            {/* Footer */}
            <footer className="relative z-10 py-12 px-4 border-t border-white/10">
                <div className="container mx-auto max-w-6xl">
                    <div className="flex flex-col md:flex-row justify-between items-center gap-6">
                        <div className="flex items-center gap-2">
                            <Shield className="w-6 h-6 text-cyan-400" />
                            <span className="text-xl font-bold">Deepwave</span>
                        </div>

                        <div className="flex gap-6">
                            <a href="https://github.com/Monike123/Deepwave-_The_Third_Derivative" target="_blank" rel="noopener noreferrer" className="text-gray-400 hover:text-cyan-400 transition-colors">
                                <Github className="w-5 h-5" />
                            </a>
                            <a href="#" className="text-gray-400 hover:text-cyan-400 transition-colors">
                                <Twitter className="w-5 h-5" />
                            </a>
                            <a href="#" className="text-gray-400 hover:text-cyan-400 transition-colors">
                                <Linkedin className="w-5 h-5" />
                            </a>
                            <a href="#" className="text-gray-400 hover:text-cyan-400 transition-colors">
                                <Mail className="w-5 h-5" />
                            </a>
                        </div>

                        <p className="text-gray-500 text-sm">
                            © 2026 Deepwave. All rights reserved.
                        </p>
                    </div>
                </div>
            </footer>
        </div>
    );
}
